"""Failure mechanisms and real HTTP state isolation, all offline/mock."""
import copy
import json
import threading
import time
import unittest
from unittest.mock import patch
from brain.contracts import Actor
from brain.engine import VersionChanged
from brain.confluence import SourceUnavailable
from brain.discovery import ContainerDiscovery
from brain.run_state import SessionRuns,runtime_status
from test_container_discovery import setup
import test_deepseek
import test_http


class OutputDiagnostics(unittest.TestCase):
    setUp=test_deepseek.DeepSeekBoundary.setUp
    tearDown=test_deepseek.DeepSeekBoundary.tearDown
    def test_classified_rejections_never_store_raw_reasoning(self):
        for category,change in [
            ('truncated',lambda r:r['choices'][0].update(finish_reason='length')),
            ('empty_content',lambda r:r['choices'][0]['message'].update(content='')),
            ('json',lambda r:r['choices'][0]['message'].update(content='{')),
            ('structure',lambda r:r['choices'][0]['message'].update(content='{}')),
            ('model_identifier',lambda r:r.update(model='secret-invalid-model'))]:
            with self.subTest(category=category):
                original=copy.deepcopy(self.transport.response);change(self.transport.response)
                self.transport.response['choices'][0]['message']['reasoning_content']='SECRET_REASONING'
                self.transport.response['usage']['completion_tokens_details']={'reasoning_tokens':10}
                events=[]
                from brain.deepseek import ModelUnavailable
                with self.assertRaises(ModelUnavailable):self.model.generate('Question',[self.evidence],request_id='a'*32,observe=lambda event,data:events.append((event,data)))
                diagnostic=events[-1][1]['diagnostic']
                self.assertEqual(diagnostic['validation_failure'],category)
                self.assertEqual(diagnostic['reasoning_tokens'],10)
                self.assertNotIn('SECRET',json.dumps(events))
                self.assertEqual(events[-1][1]['receipt']['state'],'settled')
                self.transport.response=original


class VersionRecovery(unittest.TestCase):
    def setUp(self):
        self.store,self.pilot,self.http,_=setup();self.addCleanup(self.store.db.close)
        self.actor=Actor('eng_b','pilot');self.clock=0
        self.worker=ContainerDiscovery(self.pilot,self.actor,clock=lambda:self.clock,bounded_queries=True)
        self.worker.run_once();self.worker.start();self.addCleanup(self.worker.close)
        self.resource=self.store.get('drive:FILE2')

    def change(self,text=None):
        file=self.http['drive'].content['FILE2'];version=int(file['metadata']['version'])+1
        self.http['drive'].content['FILE2']=self.http['drive'].file('FILE2',text or file['payload'].decode(),version)

    def test_same_body_version_advance_and_real_body_change(self):
        for text in (None,'[SYNTHETIC] novelty changed preventive work'):
            self.change(text);answer=self.pilot.query(self.actor,'novelty')
            current=next(e for e in answer['evidence'] if e['resource_id']=='drive:FILE2')
            self.assertEqual(current['version'],int(self.http['drive'].content['FILE2']['metadata']['version']))
            if text:self.assertEqual(current['text'],text)
            events=[e for e in self.pilot.audit.export() if e['request_id']==answer['request_id']]
            self.assertEqual(sum(e['event_type']=='version_recovery' and e['payload']['result']=='started' for e in events),1)

    def test_continuous_change_stops_after_one_recovery(self):
        self.change();original=self.pilot.authority.recover_versions
        def recover(*args):original(*args);self.change()
        with patch.object(self.pilot.authority,'recover_versions',side_effect=recover),self.assertRaises(VersionChanged):
            self.pilot.query(self.actor,'novelty')
        self.assertEqual(self.pilot.engine.model.calls,[])
        events=[e for e in self.pilot.audit.export() if e['event_type']=='version_recovery']
        self.assertEqual([e['payload']['result'] for e in events],['started','published','stopped'])

    def test_recovery_rechecks_access_and_identity(self):
        for kind in ('revoked','unknown'):
            self.change();original=self.pilot.authority.recover_versions
            def recover(*args):
                if kind=='revoked':self.http['drive'].fail_native.add('FILE2')
                else:self.http['drive'].identity_ok=False
                return original(*args)
            with patch.object(self.pilot.authority,'recover_versions',side_effect=recover),self.assertRaises(PermissionError):self.pilot.query(self.actor,'novelty')
            self.assertEqual(self.pilot.engine.model.calls,[])
            self.http['drive'].fail_native.clear();self.http['drive'].identity_ok=True

    def test_unknown_does_not_trigger_recovery(self):
        self.http['drive'].identity_ok=False
        with patch.object(self.pilot.authority,'recover_versions') as recover,self.assertRaises(SourceUnavailable):
            self.pilot.query(self.actor,'novelty')
        recover.assert_not_called();self.assertEqual(self.pilot.engine.model.calls,[])

    def test_post_model_change_stops_without_second_model_call(self):
        # Fake has no billable dispatch event; mark real dispatch explicitly via wrapper model.
        base=self.pilot.engine.model
        class Model:
            name='test'
            def generate_with_provenance(_self,question,evidence,rid,provenance,authorize,observe):
                observe('model_dispatch_attempted',{'stage':'answer'});result=base.generate(question,evidence)
                self.change();return result
        self.pilot.engine.model=Model()
        with patch.object(self.pilot.authority,'recover_versions') as recover,self.assertRaises(VersionChanged):self.pilot.query(self.actor,'novelty')
        recover.assert_not_called();self.assertEqual(len(base.calls),1)
        self.assertEqual(self.store.history(self.actor.user_id),[])


class ProgressHTTP(unittest.TestCase):
    setUp=test_http.HTTP.setUp
    tearDown=test_http.HTTP.tearDown
    request=test_http.HTTP.request
    login=test_http.HTTP.login
    def test_progress_bypasses_long_query_lock_and_is_session_private(self):
        self.login('eng_b')
        original=self.app.engine.model.generate;entered=threading.Event();release=threading.Event();results=[]
        def generate(*args):entered.set();release.wait(3);return original(*args)
        def query():results.append(self.request('/api/query',{'question':'payment-service'}))
        with patch.object(self.app.engine.model,'generate',side_effect=generate):
            thread=threading.Thread(target=query);thread.start()
            try:
                self.assertTrue(entered.wait(2));start=time.monotonic()
                status,state=self.request('/api/runtime');self.assertEqual(status,200)
                self.assertLess(time.monotonic()-start,1);self.assertEqual(state['run']['status'],'running')
                self.assertNotIn('payment-service',json.dumps(state['run']))
                for path in ('/','/app.js','/style.css','/api/health'):
                    self.assertEqual(self.request(path)[0],200)
                self.assertEqual(self.request('/api/query',{'question':'duplicate'})[0],409)
                self.assertEqual(self.request('/api/logout',{})[0],200)
                self.assertEqual(self.request('/api/runtime')[0],403)
            finally:release.set();thread.join(4)
        self.assertEqual(results[0][0],200)

    def test_session_status_has_no_object_metadata(self):
        self.login('eng_b');status,r=self.request('/api/runtime')
        self.assertEqual(status,200);self.assertEqual(len(r['sources']),4)
        self.assertTrue(all(s['configured'] and not s['used_in_answer'] and s['last_check_result']=='unconfirmed' for s in r['sources']))
        self.assertNotIn('title',json.dumps(r));self.assertNotIn('resource_id',json.dumps(r))
        first=self.app.session_runs.begin('session1');self.app.session_runs.phase('session1',first,'generation')
        self.assertIsNone(self.app.session_runs.snapshot('session2'))
        self.app.session_runs.discard('session1');self.app.session_runs.finish('session1',first,code='failed')
        self.assertIsNone(self.app.session_runs.snapshot('session1'))

class SubjectRelevance(unittest.TestCase):
    def test_shared_approval_words_do_not_create_a_subject_and_ids_keep_limits(self):
        from brain.retrieval import subject_related,tokens
        def r(id,title,text):return {'id':id,'title':title,'text':text}
        resources=[r('topic','Payment-service incident','PAY-102 code fix Done.'),
                   r('limit','Release','PAY-102 Done does not approve general customer release.'),
                   r('unrelated','Warehouse maintenance','Approved value silver; no customer release approval.'),
                   r('distractor','Authentication','Approved signing policy.')]
        self.assertEqual([r['id'] for r in subject_related(resources,tokens('For payment-service which code fix is complete and is general customer release approved?'))],['topic'])
        self.assertEqual([r['id'] for r in subject_related(resources,tokens('Which warehouse value is approved?'))],['unrelated'])
        self.assertEqual(subject_related(resources,tokens('Is general release approved?')),resources)

class MixedRecovery(unittest.TestCase):
    def test_nonbatch_mixed_version_and_deny_or_unknown_never_recovers(self):
        from brain.engine import Engine
        from brain.audit import Audit
        from brain.store import Store
        from brain.sources import FixtureWorld
        from brain.contracts import Decision,now
        world=FixtureWorld();store=Store();store.initialize(world);self.addCleanup(store.db.close)
        engine=Engine(store,world,Audit(store));resources=store.resources()[:2]
        for denied in (False,SourceUnavailable('unknown')):
            def check(actor,r,rid,phase):
                if r['id']==resources[0]['id']:raise VersionChanged([r])
                if isinstance(denied,Exception):raise denied
                return denied
            with patch.object(engine,'check',side_effect=check),self.assertRaises(SourceUnavailable):
                engine.checks(Actor('eng_b'),resources,'a'*32,'before_model')

class DetailedModelDiagnostics(unittest.TestCase):
    setUp=test_deepseek.DeepSeekBoundary.setUp
    tearDown=test_deepseek.DeepSeekBoundary.tearDown
    def test_quote_claim_review_failures_are_distinct_and_settled(self):
        from brain.synthesis import DeepSeekSynthesisModel,EvidenceReview
        from brain.deepseek import ModelOutputRejected,PRICE_DATE
        valid={'text':'GA is not approved.','evidence_ids':[self.evidence.evidence_id],
               'supports':[{'evidence_id':self.evidence.evidence_id,'quote':self.evidence.text}]}
        quote=copy.deepcopy(valid);quote['supports'][0]['quote']='This is invented.'
        claim=copy.deepcopy(valid);claim['text']='PAY-999 GA is not approved.'
        for category,model,output,stage in [
            ('quote',DeepSeekSynthesisModel,{'claims':[quote]},'answer'),
            ('claim',DeepSeekSynthesisModel,{'claims':[claim]},'answer'),
            ('review',EvidenceReview,{'verdicts':[{'index':0,'supported':False,'responsive':True}],'question_covered':True},'review')]:
            with self.subTest(category=category):
                kwargs={'claims':[valid]} if model is EvidenceReview else {}
                provider=model('synthetic-not-a-key',self.ledger,synthetic_only=True,transport=self.transport,today=PRICE_DATE,**kwargs)
                self.transport.response['choices'][0]['message']['content']=json.dumps(output)
                self.transport.response['id']='sensitive-response-id'
                events=[]
                from brain.deepseek import DeepSeekEvidenceModel
                with self.assertRaises(ModelOutputRejected):DeepSeekEvidenceModel.generate(provider,'Question',[self.evidence],request_id='b'*32,stage=stage,observe=lambda e,d:events.append((e,d)))
                self.assertEqual(events[-1][1]['diagnostic']['validation_failure'],category)
                self.assertEqual(events[-1][1]['receipt']['state'],'settled')
                self.assertNotIn('sensitive-response-id',json.dumps(events))
                self.assertEqual(len(events[-1][1]['diagnostic']['response_id_sha256']),64)

    def test_unavailable_usage_retains_unknown_and_logs_safe_diagnostic(self):
        from brain.deepseek import ModelRequestUnavailable
        self.transport.response.pop('usage');events=[]
        with self.assertRaises(ModelRequestUnavailable):self.model.generate('Question',[self.evidence],request_id='c'*32,observe=lambda e,d:events.append((e,d)))
        self.assertEqual(events[-1][0],'model_request_unavailable')
        self.assertEqual(events[-1][1]['diagnostic']['validation_failure'],'transport_or_usage')
        self.assertEqual(self.ledger.summary()['pending_requests'],1)

class FakeInvocationRecovery(unittest.TestCase):
    setUp=VersionRecovery.setUp
    change=VersionRecovery.change
    def test_even_unobserved_fake_model_invocation_cannot_recover_after_call(self):
        self.pilot.engine.before_dispatch=lambda:self.change()
        with patch.object(self.pilot.authority,'recover_versions') as recover,self.assertRaises(VersionChanged):
            self.pilot.query(self.actor,'novelty')
        recover.assert_not_called();self.assertEqual(len(self.pilot.engine.model.calls),1)

class SnapshotErrorCategory(unittest.TestCase):
    setUp=VersionRecovery.setUp
    def test_expired_snapshot_is_refreshing_but_unknown_is_not(self):
        from brain.confluence import SourceRefreshing
        self.clock=121
        with self.assertRaises(SourceRefreshing):self.worker.query_snapshot(self.actor)
        self.worker.last['drive']={'status':'failed'}
        try:self.worker.query_snapshot(self.actor)
        except SourceUnavailable as error:self.assertNotIsInstance(error,SourceRefreshing)
        else:self.fail('Failed source must stop')

class ModelErrorHTTP(unittest.TestCase):
    setUp=test_http.HTTP.setUp
    tearDown=test_http.HTTP.tearDown
    request=test_http.HTTP.request
    login=test_http.HTTP.login
    def test_trial_budget_and_unknown_model_errors_have_actionable_safe_codes(self):
        from brain.budget import BudgetExceeded,TrialAdmissionPaused
        from brain.deepseek import ModelOutputRejected,ModelRequestUnavailable
        self.login()
        for cls,code in [(BudgetExceeded,'model_budget_unavailable'),(TrialAdmissionPaused,'trial_admission_paused'),
                         (ModelOutputRejected,'model_output_unavailable'),(ModelRequestUnavailable,'model_request_unavailable')]:
            with self.subTest(code=code),patch.object(self.app.engine,'query',side_effect=cls('PRIVATE_VENDOR_DETAIL')):
                self.app.sessions[next(iter(self.app.sessions))]['last_query']=0
                status,body=self.request('/api/query',{'question':'payment-service'})
                self.assertEqual(status,503);self.assertEqual(body['code'],code)
                self.assertRegex(body['request_id'],r'^[0-9a-f]{32}$');self.assertNotIn('PRIVATE_VENDOR_DETAIL',json.dumps(body))
