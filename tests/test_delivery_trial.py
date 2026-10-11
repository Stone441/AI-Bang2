import json
import tempfile
import unittest
from pathlib import Path
from brain.budget import BudgetLedger, TrialAdmissionPaused
from scripts.delivery_trial import Admission, HumanRetestAdmission, rejected_generation_diagnostic, main

class PrivateGenerationDiagnostic(unittest.TestCase):
    def test_bounds_visible_claim_fields_and_excludes_reasoning(self):
        output={'reasoning_content':'PRIVATE REASONING','claims':[{'text':'x'*800,
            'evidence_ids':['E1'],'supports':[{'evidence_id':'E1','quote':'q'*2000,
            'reasoning':'PRIVATE REASONING'}],'extra':'PRIVATE EXTRA'}]*6}
        diagnostic=rejected_generation_diagnostic(output)
        self.assertEqual(diagnostic['claim_count'],6)
        self.assertEqual(len(diagnostic['claims']),4)
        self.assertEqual(len(diagnostic['claims'][0]['text']),600)
        self.assertEqual(len(diagnostic['claims'][0]['supports'][0]['quote']),1200)
        self.assertNotIn('PRIVATE',json.dumps(diagnostic))

class DeliveryAllowance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.ledger=BudgetLedger(str(Path(self.tmp.name)/'ledger.sqlite'))
        self.legacy=self.ledger.reserve(324404)
        self.ledger.dispatch(self.legacy)
        self.path=Path(self.tmp.name)/'new-trial.json'
    def tearDown(self):
        self.ledger.close(); self.tmp.cleanup()
    def test_nine_automatic_then_three_human_and_restart_does_not_reset(self):
        gate=Admission(lambda: 'answer',self.ledger,self.path)
        for _ in range(9):self.assertEqual(gate(),'answer')
        with self.assertRaises(TrialAdmissionPaused):gate()
        human=Admission(lambda: 'answer',self.ledger,self.path,human=True)
        for _ in range(3):self.assertEqual(human(),'answer')
        with self.assertRaises(TrialAdmissionPaused):human()
        restarted=Admission(lambda:None,self.ledger,self.path,human=True)
        with self.assertRaises(TrialAdmissionPaused):restarted()
        state=json.loads(self.path.read_text())
        self.assertEqual(state['attempts'],12)
        self.assertEqual(state['original_pending_ids'],[self.legacy])
        self.assertEqual(self.ledger.summary()['pending_requests'],1)
    def test_new_unknown_stops_admission_and_is_never_refunded(self):
        gate=Admission(lambda:None,self.ledger,self.path)
        new=self.ledger.reserve(1000);self.ledger.dispatch(new)
        with self.assertRaises(TrialAdmissionPaused):gate()
        self.assertEqual(json.loads(self.path.read_text())['attempts'],0)
        self.assertEqual(self.ledger.summary()['pending_requests'],2)
    def test_settled_threshold_stops_new_query_but_inflight_finishes(self):
        calls=[]
        def query():
            r=self.ledger.reserve(1000000);self.ledger.dispatch(r)
            self.ledger.settle(r,1000000);calls.append('finished');return 'answer'
        gate=Admission(query,self.ledger,self.path)
        self.assertEqual(gate(),'answer')
        with self.assertRaises(TrialAdmissionPaused):gate()
        self.assertEqual(calls,['finished'])
        self.assertEqual(json.loads(self.path.read_text())['attempts'],1)


class HumanRetestAllowance(unittest.TestCase):
    setUp=DeliveryAllowance.setUp
    tearDown=DeliveryAllowance.tearDown
    # Reuse ledger setup, but define only this authorization's tests.
    def gate(self,query=lambda:'answer'):
        return HumanRetestAdmission(query,self.ledger,self.path,human=True)
    def test_two_human_questions_restart_keeps_limit_and_old_unknown(self):
        with self.assertRaises(ValueError):HumanRetestAdmission(lambda:None,self.ledger,self.path)
        self.assertEqual(self.gate()(),'answer')
        restarted=self.gate();self.assertEqual(restarted(),'answer')
        with self.assertRaises(TrialAdmissionPaused):self.gate()()
        state=json.loads(self.path.read_text())
        self.assertEqual(state['attempts'],2);self.assertEqual(state['max_attempts'],2)
        self.assertEqual(state['original_pending_ids'],[self.legacy])
        self.assertEqual(self.ledger.summary()['pending_requests'],1)
    def test_cost_threshold_100k_inflight_finishes_then_stops(self):
        def query():
            r=self.ledger.reserve(100000);self.ledger.dispatch(r);self.ledger.settle(r,100000)
            return 'finished'
        gate=self.gate(query);self.assertEqual(gate(),'finished')
        with self.assertRaises(TrialAdmissionPaused):gate()
        self.assertEqual(json.loads(self.path.read_text())['attempts'],1)
    def test_new_unknown_stops_and_stays_reserved(self):
        gate=self.gate();r=self.ledger.reserve(1000);self.ledger.dispatch(r)
        with self.assertRaises(TrialAdmissionPaused):gate()
        self.assertEqual(json.loads(self.path.read_text())['attempts'],0)
        self.assertEqual(self.ledger.summary()['pending_requests'],2)
    def test_model_call_limit_stops_even_before_two_questions(self):
        gate=self.gate()
        for _ in range(2):
            r=self.ledger.reserve(1000);self.ledger.dispatch(r);self.ledger.settle(r,1000)
        with self.assertRaises(TrialAdmissionPaused):gate()
        self.assertEqual(json.loads(self.path.read_text())['model_calls_used'],2)
        self.assertEqual(gate.public_status()['reason'],'model_call_limit')
    def test_retest_cannot_launch_automatic_or_two_call_styles(self):
        for human,style in [(False,'source-review'),(True,'synthesis'),(True,'reviewed-excerpts')]:
            with self.assertRaises(ValueError):main(human=human,answer_style=style,human_retest=True)
