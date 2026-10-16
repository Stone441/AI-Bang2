import copy
import unittest
from test_sectioned_answer import SectionedAnswer
from brain.contracts import Actor
from scripts.quote_scope_probe import install_probe

class QuoteScopeProbe(unittest.TestCase):
    def setUp(self):
        self.fixture=SectionedAnswer();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
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
