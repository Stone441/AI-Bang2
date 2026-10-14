"""Real engine/reviewer classes with mock native/model I/O, not HTTP proof."""
import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from brain.audit import verify_chain
from brain.budget import BudgetLedger
from brain.confluence import SourceUnavailable
from brain.contracts import Actor
from brain.deepseek import PRICE_DATE
from brain.isolated_query import IsolatedQueries, RequestAuthority
from brain.synthesis import DeepSeekWholeSourceReviewModel
import test_paired_authorization as paired


class Isolation(unittest.TestCase):
    prepare=paired.PairedAuthorization.prepare

    def setUp(self):
        self.store,self.pilot,self.http,self.actor=self.prepare(count=2)
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.ledger=BudgetLedger(str(Path(self.tmp.name)/'budget.sqlite'));self.addCleanup(self.ledger.close)
        self.calls=[];self.on_send=lambda:None
        outer=self
        class Transport:
            def _send(self,request):
                body=json.loads(request.data);outer.calls.append(body)
                outer.on_send()
                data=json.loads(body['messages'][1]['content'])
                return 200,{'model':'deepseek-flash',
                    'usage':{'prompt_tokens':100,'completion_tokens':20,'total_tokens':120},
                    'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':json.dumps(
                        {'selected':[p['alias'] for p in data['passages']],
                         'selection_safe':True,'question_covered':True})}}]}
        model=DeepSeekWholeSourceReviewModel('synthetic-not-a-key',self.ledger,
            synthetic_only=True,transport=Transport(),today=PRICE_DATE,reasoning_effort='none',output_tokens=8192)
        self.pilot.engine.model=model;self.pilot.engine.source_review_dispatch='single'
        self.executor=IsolatedQueries(self.pilot.engine)

    def ask(self,question='novelty'):
        with self.executor.request():return self.executor.query(self.actor,question)

    def test_three_queries_reach_model_together_without_shared_snapshots(self):
        barrier=threading.Barrier(3)
        original=copy.deepcopy(self.pilot.authority.snapshots)
        def send():
            self.assertFalse(self.pilot.lock._is_owned())
            self.assertFalse(self.store.lock._is_owned())
            barrier.wait(4)
        self.on_send=send
        with ThreadPoolExecutor(3) as pool:
            answers=list(pool.map(self.ask,['novelty']*3))
        self.assertEqual(len({a['request_id'] for a in answers}),3)
        self.assertTrue(all(a['review_status']=='accepted' for a in answers))
        self.assertEqual(self.pilot.authority.snapshots,original)
        self.assertEqual(self.ledger.summary()['pending_requests'],0)
        self.assertTrue(verify_chain(self.pilot.audit.export())['valid'])

    def test_final_publication_fence_lasts_until_response_scope_exits(self):
        entered,trying=threading.Event(),threading.Event()
        def publish():
            trying.set()
            with self.pilot.lock:entered.set()
        with self.executor.request():
            answer=self.executor.query(self.actor,'novelty')
            thread=threading.Thread(target=publish);thread.start()
            self.assertTrue(trying.wait(2));self.assertFalse(entered.wait(.05))
            self.assertTrue(answer['claims'])
        thread.join(2);self.assertTrue(entered.is_set())

    def test_disable_restore_aba_during_model_cannot_deliver_old_answer(self):
        def mutate():
            root=self.pilot.authority
            with root.state_lock:
                r=copy.deepcopy(root.resources['confluence:98565'])
                root.publish_resource(dict(r,active=False));root.publish_resource(r)
        self.on_send=mutate
        with self.assertRaises(SourceUnavailable):self.ask()
        self.assertEqual(self.store.history(self.actor.user_id),[])
        self.assertEqual(len(self.calls),1)
        self.assertEqual(self.ledger.summary()['pending_requests'],0)

    def test_new_candidate_during_model_is_not_ignored(self):
        def mutate():
            root=self.pilot.authority
            with root.state_lock:root.discovery.published_versions['confluence']['confluence:new']=1
        self.on_send=mutate
        with self.assertRaises(SourceUnavailable):self.ask()
        self.assertEqual(self.store.history(self.actor.user_id),[])

    def test_native_revocation_after_model_still_stops_dispatch(self):
        self.on_send=lambda:self.http['confluence'].fail_native.add('98565')
        with self.assertRaises(PermissionError):self.ask()
        self.assertEqual(self.store.history(self.actor.user_id),[])

    def test_construction_change_stops_before_model(self):
        original=self.pilot.engine.model.source_claims
        def construct(evidence):
            result=original(evidence)
            root=self.pilot.authority
            with root.state_lock:
                root.publish_resource(dict(root.resources['confluence:98565'],active=False))
            return result
        with patch.object(self.pilot.engine.model,'source_claims',side_effect=construct):
            with self.assertRaises(SourceUnavailable):self.ask()
        self.assertEqual(self.calls,[])

    def test_actor_scope_no_query_scope_and_empty_evidence(self):
        with self.assertRaises(RuntimeError):self.executor.query(self.actor,'novelty')
        with self.assertRaises(SourceUnavailable):
            RequestAuthority(self.pilot.authority,self.store,Actor('product_ops','pilot'))
        answer=self.ask('unfindablezebra')
        self.assertEqual(answer['claims'],[]);self.assertEqual(self.calls,[])

    def test_legacy_source_review_retains_both_pre_model_checks(self):
        self.pilot.engine.source_review_dispatch='legacy'
        answer=self.ask();events=[e for e in self.pilot.audit.export() if e['request_id']==answer['request_id']]
        phases={e['payload'].get('phase') for e in events if e['event_type']=='authorization_decided'}
        self.assertTrue({'before_model','model_dispatch','review_dispatch','before_dispatch'}<=phases)
        self.assertEqual(len(self.calls),1)

    def test_native_version_change_recovers_once_before_model(self):
        page=self.http['confluence'].content['98565']
        page['version']['number']=2
        page['body']['storage']['value']='<p>[SYNTHETIC] changed novelty</p>'
        answer=self.ask()
        self.assertEqual(answer['review_status'],'accepted')
        self.assertEqual(self.store.get('confluence:98565')['version'],2)
        self.assertEqual(len(self.calls),1)
        self.assertIn('changed novelty',json.dumps(answer))

    def test_unhealthy_coverage_after_model_stops_and_releases_fence(self):
        root=self.pilot.authority
        prior=copy.deepcopy(root.discovery.last)
        def unhealthy():
            with root.state_lock:root.discovery.last['drive']={'status':'failed'}
        self.on_send=unhealthy
        with self.assertRaises(SourceUnavailable):self.ask()
        self.assertEqual(self.store.history(self.actor.user_id),[])
        self.assertEqual(self.ledger.summary()['pending_requests'],0)
        self.assertFalse(root.state_lock._is_owned())
        self.assertFalse(self.store.lock._is_owned())
        with root.state_lock:root.discovery.last=prior
        self.on_send=lambda:None
        self.assertEqual(self.ask()['review_status'],'accepted')
