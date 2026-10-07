import copy
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from brain.audit import Audit, verify_chain
from brain.budget import BudgetLedger
from brain.contracts import Actor
from brain.deepseek import DeepSeekEvidenceModel, ModelUnavailable, PRICE_DATE, PriceReviewRequired
from brain.engine import Engine
from brain.sources import FixtureWorld
from brain.store import Store
from brain.synthesis import DeepSeekSynthesisModel


class ModelStages(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.ledger=BudgetLedger(str(Path(self.tmp.name)/'budget.sqlite'))
        self.world=FixtureWorld()
        for r in self.world.resources.values():r['text']='[SYNTHETIC] '+r['text']
        self.store=Store();self.store.initialize(self.world);self.audit=Audit(self.store)
        self.calls=[];self.failure=None
        class Transport:
            def _send(_,request):
                self.calls.append(json.loads(request.data))
                if self.failure=='timeout':raise TimeoutError('private upstream details')
                content=json.loads(self.calls[-1]['messages'][1]['content'])
                if 'claims' in content:
                    output={'question_covered':self.failure!='review','verdicts':[{'index':0,'supported':True,'responsive':True}]}
                elif 'claims' in self.calls[-1]['messages'][0]['content']:
                    e=content['evidence'][0]
                    output={'claims':[{'text':'Source-backed excerpt.', 'evidence_ids':[e['evidence_id']],
                        'supports':[{'evidence_id':e['evidence_id'],'quote':e['text'][:200]}]}]}
                else:output={'evidence_ids':[content['evidence'][0]['evidence_id']]}
                return 200, {'model':'deepseek-flash','usage':{'prompt_tokens':100,'completion_tokens':20,'total_tokens':120},
                            'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':json.dumps(output)}}]}
        self.transport=Transport()

    def tearDown(self):
        self.store.db.close();self.ledger.close();self.tmp.cleanup()

    def run_case(self,case):
        self.failure=case
        cls=DeepSeekSynthesisModel if case=='review' else DeepSeekEvidenceModel
        model=cls('synthetic-not-a-key',self.ledger,synthetic_only=True,transport=self.transport,today=PRICE_DATE)
        if case=='price':model._today=lambda:PRICE_DATE+timedelta(days=1)
        if case=='guard':
            for r in self.world.resources.values():r['text']=r['text'].replace('[SYNTHETIC] ','')
            self.store.db.close();self.store=Store();self.store.initialize(self.world);self.audit=Audit(self.store)
        if case=='budget':self.ledger.reserve(BudgetLedger.APPROVED_MAX)
        engine=Engine(self.store,self.world,self.audit,model)
        # Retain an old immutable event before new lifecycle events.
        original=self.audit.append('evidence_used','eng_b','legacy',{'stage':'sent_to_model','evidence_id':'legacy@1'})
        answer=None;error=None
        try:answer=engine.query(Actor('eng_b'),'payment-service incident retry')
        except Exception as exc:error=type(exc).__name__
        events=self.audit.export()
        self.assertEqual(events[0],original)
        self.assertTrue(verify_chain(events)['valid'])
        return {'case':case,'mode':'fixture_mock_model','transport_calls':len(self.calls),'error_type':error,
                'events':events,'answer':answer,'budget':self.ledger.summary(),
                'receipts':[self.ledger.model_receipt(r[0]) for r in self.ledger.db.execute('select reservation_id from model_calls')]}

    def test_price_guard_and_budget_failure_have_prepared_input_but_no_send(self):
        # Each case has its own stores/ledger; no resetting the real runtime ledger.
        for case,reason in [('price','model_price_review_required'),('guard','model_input_rejected'),('budget','model_budget_unavailable')]:
            with self.subTest(case=case):
                harness=ModelStages();harness.setUp()
                try:
                    result=harness.run_case(case);events=result['events'][1:]
                    self.assertEqual(result['transport_calls'],0)
                    self.assertTrue(any(e['payload'].get('stage')=='prepared_for_answer' for e in events))
                    self.assertFalse(any(e['event_type'].startswith('model_') for e in events))
                    self.assertEqual(events[-1]['event_type'],'request_failed')
                    self.assertEqual(events[-1]['payload']['reason'],reason)
                    self.assertIsNone(result['answer']);self.assertEqual(result['receipts'],[])
                finally:harness.tearDown()

    def test_success_has_ordered_intent_attempt_usage_output_and_answer(self):
        result=self.run_case('success')
        kinds=[e['event_type'] for e in result['events'][1:]]
        expected=['model_dispatch_intent','model_dispatch_attempted','model_usage_received','model_output_accepted','generation_completed','response_committed']
        self.assertEqual([k for k in kinds if k in expected],expected)
        self.assertEqual(result['transport_calls'],1)
        receipt=next(e['payload']['receipt'] for e in result['events'] if e['event_type']=='model_usage_received')
        self.assertEqual(receipt['state'],'settled');self.assertEqual(receipt['outcome'],'pending')
        self.assertTrue(receipt['called']);self.assertEqual(receipt['total_tokens'],120)
        self.assertIsNotNone(result['answer'])

    def test_timeout_is_attempted_unknown_not_no_send_or_valid_receipt(self):
        result=self.run_case('timeout');kinds=[e['event_type'] for e in result['events']]
        self.assertEqual(result['transport_calls'],1)
        self.assertIn('model_dispatch_attempted',kinds);self.assertNotIn('model_usage_received',kinds)
        self.assertNotIn('response_committed',kinds)
        self.assertIsNone(result['receipts'][0]['called'])
        self.assertEqual(result['budget']['pending_requests'],1)
        self.assertNotIn('private upstream details',json.dumps(result))

    def test_review_failure_keeps_both_usage_receipts_but_never_returns_answer(self):
        result=self.run_case('review');events=result['events']
        self.assertEqual(result['transport_calls'],2)
        self.assertEqual([e['payload']['stage'] for e in events if e['event_type']=='model_usage_received'],['answer','review'])
        self.assertTrue(any(e['payload'].get('stage')=='prepared_for_review' for e in events))
        self.assertTrue(any(e['event_type']=='model_output_rejected' and e['payload']['stage']=='review' for e in events))
        self.assertFalse(any(e['event_type'] in ('generation_completed','response_committed') for e in events))
        by_id={r['reservation_id']:r for r in result['receipts']}
        for event in events:
            if event['event_type']=='model_output_accepted':
                self.assertEqual(by_id[event['payload']['reservation_id']]['outcome'],'accepted')
            if event['event_type']=='model_output_rejected':
                self.assertEqual(by_id[event['payload']['reservation_id']]['outcome'],'output_rejected')
        self.assertEqual(result['budget']['pending_requests'],0)
        self.assertIsNone(result['answer'])

    def test_http_return_attempt_only_after_success_and_never_on_price_failure(self):
        import threading
        import test_http
        from brain.server import App, create_server
        app=App(store=self.store);app.world=self.world;app.audit=self.audit
        model=DeepSeekEvidenceModel('synthetic-not-a-key',self.ledger,synthetic_only=True,
                                  transport=self.transport,today=PRICE_DATE)
        app.engine=Engine(self.store,self.world,self.audit,model)
        self.server=create_server(app);self.cookie='';self.csrf=''
        thread=threading.Thread(target=self.server.serve_forever,daemon=True);thread.start()
        request=lambda path,data=None:test_http.HTTP.request(self,path,data)
        try:
            status,login=request('/api/demo/login',{'user':'eng_b'})
            self.assertEqual(status,200);self.csrf=login['csrf']
            status,answer=request('/api/query',{'question':'payment-service incident'})
            self.assertEqual(status,200)
            delivered=[e for e in self.audit.export() if e['event_type']=='response_dispatch_attempted']
            self.assertEqual(len(delivered),1);self.assertEqual(delivered[0]['request_id'],answer['request_id'])
            model._today=lambda:PRICE_DATE+timedelta(days=1)
            for session in app.sessions.values():session['last_query']=0
            status,error=request('/api/query',{'question':'payment-service incident'})
            self.assertEqual(status,503);self.assertEqual(error['code'],'model_price_review_required')
            self.assertEqual(len(self.calls),1)
            self.assertEqual(len([e for e in self.audit.export() if e['event_type']=='response_dispatch_attempted']),1)
            self.assertEqual(self.audit.export()[-1]['event_type'],'request_failed')
        finally:self.server.shutdown();self.server.server_close();thread.join()
