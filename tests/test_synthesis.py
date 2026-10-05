import contextlib
import copy
import io
import json
import tempfile
import threading
import unittest
from pathlib import Path

from brain.audit import Audit
from brain.budget import BudgetLedger
from brain.contracts import Actor, Evidence
from brain.deepseek import ModelUnavailable, PRICE_DATE, cost_upper
from brain.engine import Engine
from brain.sources import FixtureWorld
from brain.store import Store
from brain.synthesis import DeepSeekSynthesisModel, validate_claim


class SequentialTransport:
    def __init__(self, draft, verdicts):
        self.outputs=[draft, {'verdicts':verdicts, 'question_covered':True}]
        self.calls=[]
        self.after_draft=None

    def _send(self, request):
        self.calls.append(json.loads(request.data))
        output=self.outputs[len(self.calls)-1]
        if len(self.calls)==1 and self.after_draft:self.after_draft()
        return 200, {'model':'deepseek-flash',
                     'usage':{'prompt_tokens':100,'completion_tokens':20,'total_tokens':120},
                     'choices':[{'finish_reason':'stop','message':{'role':'assistant',
                         'content':json.dumps(output)}}]}


class GroundedSynthesis(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.ledger=BudgetLedger(str(Path(self.tmp.name)/'budget.sqlite'))
        self.evidence=Evidence('drive:test@1','drive:test',1,'drive','Synthetic',{},
            '[SYNTHETIC] Pilot approved for ten customers. GA is not approved.',
            '2026-10-05','2026-10-05','https://example.com')
        self.claim={'text':'Approval is limited to a ten-customer pilot; GA remains unapproved.',
            'evidence_ids':[self.evidence.evidence_id],
            'supports':[{'evidence_id':self.evidence.evidence_id,
                'quote':'Pilot approved for ten customers. GA is not approved.'}]}
        self.transport=SequentialTransport({'claims':[self.claim]},[{'index':0,'supported':True}])
        self.model=DeepSeekSynthesisModel('synthetic-not-a-key',self.ledger,synthetic_only=True,
            transport=self.transport,today=PRICE_DATE)
        self.rid='a'*32

    def tearDown(self):
        self.ledger.close();self.tmp.cleanup()

    def test_two_separately_budgeted_calls_preserve_support_and_current_authorization(self):
        stages=[]
        result=self.model.generate_with_authorization('Is GA approved?',[self.evidence],self.rid,stages.append)
        self.assertEqual(stages,['review_dispatch'])
        self.assertEqual(result['claims'],[self.claim])
        self.assertEqual(result['claim_format'],'grounded_synthesis_v1')
        self.assertEqual(result['review_status'],'accepted')
        self.assertNotEqual(result['model_call']['reservation_id'],result['model_review']['reservation_id'])
        self.assertEqual(self.ledger.summary()['settled_micro_usd'],2*cost_upper(100,20))
        self.assertEqual(len(self.transport.calls),2)
        review=json.loads(self.transport.calls[1]['messages'][1]['content'])
        self.assertEqual(review['evidence'][0]['text'],self.evidence.text)
        self.assertEqual(review['claims'],[self.claim])

    def test_unknown_citation_or_invented_quote_rejected_before_review(self):
        for mutation in ('id','quote','missing','extra'):
            with self.subTest(mutation=mutation):
                claim=copy.deepcopy(self.claim)
                if mutation=='id':claim['evidence_ids']=['restricted@1']
                elif mutation=='quote':claim['supports'][0]['quote']='GA is approved for every customer.'
                elif mutation=='missing':claim['supports']=[]
                else:claim['role']='admin'
                self.transport.outputs[0]={'claims':[claim]};self.transport.calls=[]
                with self.assertRaises(ModelUnavailable):
                    self.model.generate_with_authorization('Question',[self.evidence],self.rid,lambda _:None)
                self.assertEqual(len(self.transport.calls),1)

    def test_review_rejects_false_unknown_duplicate_incomplete_or_boolean_index(self):
        for verdicts in ([{'index':0,'supported':False}],[],[{'index':0,'supported':'true'}],
                         [{'index':True,'supported':True}],[{'index':1,'supported':True}],
                         [{'index':0,'supported':True},{'index':0,'supported':True}]):
            with self.subTest(verdicts=verdicts):
                self.transport.calls=[];self.transport.outputs[1]={'verdicts':verdicts, 'question_covered':True}
                with self.assertRaises(ModelUnavailable):
                    self.model.generate_with_authorization('Question',[self.evidence],self.rid,lambda _:None)
        self.assertEqual(self.ledger.summary()['pending_requests'],0)
        outcomes=[r[0] for r in self.ledger.db.execute('select outcome from model_calls')]
        self.assertEqual(outcomes.count('output_rejected'),6)

    def test_revocation_between_draft_and_review_prevents_second_network_request(self):
        def deny(_):raise PermissionError('Unavailable')
        with self.assertRaises(PermissionError):
            self.model.generate_with_authorization('Question',[self.evidence],self.rid,deny)
        self.assertEqual(len(self.transport.calls),1)

    def test_supported_but_incomplete_answer_or_unknown_coverage_is_rejected(self):
        # A factual pilot answer omits the requested operational safeguards.
        for coverage in (False, None, 'true', 1, 'missing'):
            with self.subTest(coverage=coverage):
                review={'verdicts':[{'index':0,'supported':True}]}
                if coverage!='missing':review['question_covered']=coverage
                self.transport.outputs[1]=review;self.transport.calls=[]
                with self.assertRaises(ModelUnavailable):
                    self.model.generate_with_authorization(
                        'Is GA approved, and what operational safeguards are required?',
                        [self.evidence],self.rid,lambda _:None)
                self.assertEqual(len(self.transport.calls),2)
        self.assertEqual(self.ledger.summary()['pending_requests'],0)
        outcomes=[r[0] for r in self.ledger.db.execute('select outcome from model_calls')]
        self.assertEqual(outcomes.count('output_rejected'),5)

    def test_empty_evidence_and_empty_claims_do_not_start_review(self):
        result=self.model.generate_with_authorization('Question',[],self.rid,lambda _:self.fail('No stage'))
        self.assertFalse(result['model_call']['called']);self.assertEqual(self.transport.calls,[])
        self.transport.outputs[0]={'claims':[]}
        result=self.model.generate_with_authorization('Question',[self.evidence],self.rid,lambda _:self.fail('No stage'))
        self.assertEqual(result['claims'],[]);self.assertEqual(len(self.transport.calls),1)

    def test_direct_generation_requires_server_stage_callback(self):
        with self.assertRaises(ModelUnavailable):self.model.generate('Question',[self.evidence])
        with self.assertRaises(ModelUnavailable):
            self.model.generate_with_authorization('Question',[self.evidence],self.rid,None)
        self.assertEqual(self.transport.calls,[])

    def test_engine_review_revocation_or_return_revocation_fail_closed(self):
        for revoked_stage in (None,'review','return'):
            with self.subTest(stage=revoked_stage):
                world=FixtureWorld()
                for r in world.resources.values():r['text']='[SYNTHETIC] '+r['text']
                store=Store();store.initialize(world);audit=Audit(store)
                engine=Engine(store,world,audit,self.model,mode='fixture_mock_model_synthesis')
                supplied=[]
                original=self.transport._send
                def send(request):
                    data=json.loads(request.data);content=json.loads(data['messages'][1]['content'])
                    if not supplied:
                        supplied.extend(content['evidence'])
                        chosen=supplied[0]
                        self.transport.outputs[0]={'claims':[{'text':'A supported paraphrase.',
                            'evidence_ids':[chosen['evidence_id']],
                            'supports':[{'evidence_id':chosen['evidence_id'],'quote':chosen['text']}]}]}
                        if revoked_stage=='review':world.revoked.add(('eng_b',chosen['evidence_id'].rsplit('@',1)[0]))
                    elif revoked_stage=='return':
                        world.revoked.add(('eng_b',supplied[0]['evidence_id'].rsplit('@',1)[0]))
                    return original(request)
                self.transport.calls=[];self.transport._send=send
                try:
                    if revoked_stage:
                        with self.assertRaises(PermissionError):engine.query(Actor('eng_b'),'payment-service retry incident')
                        self.assertFalse(any(e['event_type']=='response_committed' for e in audit.export()))
                        self.assertEqual(len(self.transport.calls),1 if revoked_stage=='review' else 2)
                    else:
                        answer=engine.query(Actor('eng_b'),'payment-service retry incident')
                        self.assertEqual(answer['review_status'],'accepted')
                        self.assertTrue(answer['claims'][0]['supports'])
                        generation=next(e['payload'] for e in audit.export() if e['event_type']=='generation_completed')
                        self.assertEqual(generation['model_review'],answer['model_review'])
                        self.assertTrue(any(e['event_type']=='evidence_used' and
                            e['payload']['stage']=='sent_to_review' for e in audit.export()))
                        self.assertEqual(engine.safe_history(Actor('eng_b'))[0]['model_review'],answer['model_review'])
                        world.revoked.add(('eng_b',supplied[0]['evidence_id'].rsplit('@',1)[0]))
                        self.assertTrue(engine.safe_history(Actor('eng_b'))[0]['unavailable'])
                    self.assertNotIn('S-01@1',[e['evidence_id'] for e in supplied])
                finally:
                    self.transport._send=original;store.db.close()

    def test_fake_synthesis_cli_fails_before_platform_access(self):
        from brain.operator_web import main
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--config','missing','--answer-style','synthesis','--live']),2)

    def test_exact_quote_provenance_does_not_itself_prove_entailment(self):
        claim=copy.deepcopy(self.claim);claim['text']='GA is approved.'
        self.assertEqual(validate_claim(claim,[self.evidence]),claim)
        self.transport.outputs[0]={'claims':[claim]}
        self.transport.outputs[1]={'verdicts':[{'index':0,'supported':False}], 'question_covered':True}
        with self.assertRaises(ModelUnavailable):
            self.model.generate_with_authorization('Question',[self.evidence],self.rid,lambda _:None)

    def test_review_timeout_keeps_second_reservation_and_first_actual_charge(self):
        original=self.transport._send
        def timeout_on_review(request):
            if self.transport.calls:raise TimeoutError('private upstream response')
            return original(request)
        self.transport._send=timeout_on_review
        with self.assertRaises(ModelUnavailable) as caught:
            self.model.generate_with_authorization('Question',[self.evidence],self.rid,lambda _:None)
        self.assertNotIn('private',str(caught.exception))
        summary=self.ledger.summary()
        self.assertEqual(summary['pending_requests'],1)
        self.assertEqual(summary['accounted_micro_usd'],self.model.reservation+cost_upper(100,20))

    def test_operator_http_synthesis_history_export_and_same_session_revocation(self):
        import test_operator_web
        import test_http
        from brain.server import create_server
        app,source=test_operator_web.setup_app()
        original_get=source.get
        def get(url,authorization):
            status,body=original_get(url,authorization)
            if body and 'body' in body:
                body['body']['storage']['value']='<p>[SYNTHETIC] Controlled pilot only. GA is not approved.</p>'
            return status,body
        source.get=get
        claim={'text':'Approval covers a controlled pilot, not GA.',
               'evidence_ids':['confluence:98564@1'],
               'supports':[{'evidence_id':'confluence:98564@1',
                            'quote':'Controlled pilot only. GA is not approved.'}]}
        self.transport.outputs[0]={'claims':[claim]}
        app.engine.model=self.model;app.engine.mode='confluence_mock_http_mock_model_synthesis'
        self.server=create_server(app)
        thread=threading.Thread(target=self.server.serve_forever,daemon=True);thread.start()
        self.cookie='';self.csrf=''
        request=lambda path,data=None:test_http.HTTP.request(self,path,data)
        try:
            self.assertEqual(request('/api/query',{'question':'pilot'})[0],403)
            self.assertEqual(self.transport.calls,[])
            status,login=request('/api/operator/login',{'ticket':app.bootstrap_ticket()})
            self.assertEqual(status,200);self.csrf=login['csrf']
            self.assertEqual(request('/api/query',{'question':'pilot','role':'admin'})[0],400)
            status,answer=request('/api/query',{'question':'pilot'})
            self.assertEqual(status,200);self.assertEqual(answer['claims'],[claim])
            self.assertEqual(answer['review_status'],'accepted');self.assertEqual(len(self.transport.calls),2)
            for path in ('/api/history','/api/export/'+answer['request_id']):
                if path.startswith('/api/export/'):
                    self.assertEqual(request(path)[0],404)
                    continue
                status,body=request(path);self.assertEqual(status,200)
                self.assertEqual(body['history'][0]['claims'],[claim])
                self.assertEqual(body['history'][0]['model_review'],answer['model_review'])
            source.allowed.clear()
            for session in app.sessions.values():session['last_query']=0
            status,after=request('/api/query',{'question':'pilot'})
            self.assertEqual(status,200);self.assertEqual(after['claims'],[])
            self.assertEqual(len(self.transport.calls),2)
            self.assertEqual(request('/api/evidence/confluence:98564@1')[0],403)
            for path in ('/api/history','/api/export/'+answer['request_id']):
                if path.startswith('/api/export/'):
                    self.assertEqual(request(path)[0],404)
                    continue
                status,body=request(path);self.assertEqual(status,200)
                old=next(r for r in body['history'] if r['request_id']==answer['request_id'])
                self.assertTrue(old['unavailable'])
                self.assertNotIn('supports',old);self.assertNotIn('model_review',old)
        finally:
            self.server.shutdown();self.server.server_close();thread.join();app.store.db.close()
