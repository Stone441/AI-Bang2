import copy
import unittest
import test_sectioned_answer
from brain.contracts import Actor
from scripts.quote_scope_probe import install_probe

class QuoteScopeProbe(unittest.TestCase):
    def setUp(self):
        self.fixture=test_sectioned_answer.SectionedAnswer();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        f=self.fixture
        self.case={'source_resource_id':f.evidence[0].resource_id,'source_version':f.evidence[0].version,
            'claim':copy.deepcopy(f.claims[0]),'parts':[{'question':f.question,'status':'supported','claim_indices':[0],'gap_claim_indices':[]}]}
        self.verdict={'question_covered':True,'filtered_answer_complete':True,'verdicts':[{'index':0,'supported':True,'responsive':True}],
            'parts_supported':True,'premise_handled':True,'conflicts_handled':True,
            'part_verdicts':[{'index':0,'requested_information_provided':True,'gap_explanation_supported':True}]}
    def test_single_path_reproduces_failure_without_transport(self):
        f=self.fixture;engine=f.engine();install_probe(engine,f.model,self.case);engine.source_review_dispatch='single'
        with self.assertRaisesRegex(ValueError,'audited source-review'):engine.query(Actor('eng_b'),f.question)
        self.assertEqual(f.transport.calls,[])
    def test_probe_uses_authorized_path_one_review_and_no_draft_answer(self):
        f=self.fixture;f.transport.outputs=[self.verdict];engine=f.engine();install_probe(engine,f.model,self.case)
        answer=engine.query(Actor('eng_b'),f.question)
        self.assertEqual(len(f.transport.calls),1);self.assertEqual(answer['claims'],[])
    def test_negative_verdict_is_preserved_as_rejection(self):
        f=self.fixture;bad=copy.deepcopy(self.verdict);bad['verdicts'][0]['supported']=False
        f.transport.outputs=[bad];engine=f.engine(evidence_on_model_rejection=True);install_probe(engine,f.model,self.case)
        answer=engine.query(Actor('eng_b'),f.question)
        self.assertEqual(len(f.transport.calls),1);self.assertEqual(answer['claims'],[])
        self.assertEqual(answer['answer_status'],'evidence_only')

    def test_changed_or_missing_source_stops_before_review(self):
        f=self.fixture
        for field,value in [('source_version',-1),('source_resource_id','missing')]:
            case={**self.case,field:value};engine=f.engine();probe=install_probe(engine,f.model,case)
            stages=[]
            with self.assertRaisesRegex(RuntimeError,'unavailable or changed'):
                probe.generate_with_provenance(f.question,f.evidence,'a'*32,None,stages.append)
            self.assertEqual(stages,[]);self.assertEqual(f.transport.calls,[])

    def test_review_authorization_denial_stops_before_transport(self):
        f=self.fixture;engine=f.engine();probe=install_probe(engine,f.model,self.case);stages=[]
        def deny(phase):
            stages.append(phase)
            raise PermissionError('revoked')
        with self.assertRaises(PermissionError):
            probe.generate_with_provenance(f.question,f.evidence,'b'*32,None,deny)
        self.assertEqual(stages,['review_dispatch']);self.assertEqual(f.transport.calls,[])

    def test_isolated_adapter_routes_real_engine_call_without_full_source_payload(self):
        import json
        f=self.fixture;f.transport.outputs=[{'quote_supported':True}]
        engine=f.engine();install_probe(engine,f.model,self.case,isolated=True)
        answer=engine.query(Actor('eng_b'),f.question)
        self.assertEqual(len(f.transport.calls),1);self.assertEqual(answer['claims'],[])
        body=json.loads(f.transport.calls[0]['messages'][1]['content'])
        self.assertEqual(set(body),{'claim','quotations'})
        self.assertEqual(body['quotations'],[self.case['claim']['supports'][0]['quote']])

    def test_isolated_negative_adapter_retains_explicit_rejection_diagnostic(self):
        f=self.fixture;f.transport.outputs=[{'quote_supported':False}]
        engine=f.engine(evidence_on_model_rejection=True)
        install_probe(engine,f.model,self.case,isolated=True)
        answer=engine.query(Actor('eng_b'),f.question)
        self.assertEqual(len(f.transport.calls),1)
        self.assertEqual(answer['answer_status'],'evidence_only')
        rejected=next(e for e in engine.audit.export() if e['event_type']=='model_output_rejected')
        self.assertIs(rejected['payload']['diagnostic']['review_quote_supported'],False)
        self.assertEqual(rejected['payload']['diagnostic']['validation_detail'],'quote_review_unsupported')
