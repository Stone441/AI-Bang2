import json
import tempfile
import unittest
from pathlib import Path
from brain.budget import BudgetLedger, TrialAdmissionPaused
from scripts.delivery_trial import Admission, HumanRetestAdmission, HumanOpenAdmission, rejected_generation_diagnostic, main

class PrivateGenerationDiagnostic(unittest.TestCase):
    def test_review_fallback_cannot_expand_into_other_paths_or_efforts(self):
        for kwargs in ({'review_reasoning_effort':'high'},
                       {'review_reasoning_effort':'low','human':False,'answer_style':'source-review'},
                       {'review_reasoning_effort':'low','human':True,'answer_style':'synthesis'}):
            with self.subTest(kwargs=kwargs),self.assertRaises(ValueError):main(**kwargs)
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


class OpenHumanAllowance(unittest.TestCase):
    setUp=DeliveryAllowance.setUp
    tearDown=DeliveryAllowance.tearDown
    def setup_prior(self):
        prior=HumanRetestAdmission(lambda:'answer',self.ledger,self.path,human=True)
        prior();prior();self.original_bytes=self.path.read_bytes()
        self.open_path=Path(self.tmp.name)/'open-human.json'
        return HumanOpenAdmission(lambda:'answer',self.ledger,self.open_path,human=True,previous_state_path=self.path)
    def test_no_count_or_call_limit_keeps_prior_counter_and_baseline(self):
        gate=self.setup_prior();original=json.loads(self.original_bytes)
        for _ in range(5):self.assertEqual(gate(),'answer')
        for _ in range(3):
            r=self.ledger.reserve(1000);self.ledger.dispatch(r);self.ledger.settle(r,1000)
        self.assertEqual(gate(),'answer')
        restarted=HumanOpenAdmission(lambda:'answer',self.ledger,self.open_path,human=True)
        self.assertEqual(restarted(),'answer')
        state=json.loads(self.open_path.read_text());self.assertEqual(state['attempts'],9)
        self.assertIsNone(state['max_attempts']);self.assertIsNone(state['max_model_calls'])
        self.assertEqual(state['baseline'],original['baseline'])
        self.assertEqual(state['baseline_model_calls'],original['baseline_model_calls'])
        self.assertEqual(state['original_pending_ids'],[self.legacy])
        self.assertEqual(self.path.read_bytes(),self.original_bytes)
        self.assertTrue(restarted.public_status()['allowed'])
    def test_original_cost_stop_and_new_unknown_still_block(self):
        gate=self.setup_prior();r=self.ledger.reserve(100000);self.ledger.dispatch(r);self.ledger.settle(r,100000)
        with self.assertRaises(TrialAdmissionPaused):gate()
        self.assertEqual(gate.public_status()['reason'],'cost_limit')
        # Separate new-unknown control without refunding any dispatched request.
        with tempfile.TemporaryDirectory() as folder:
            ledger=BudgetLedger(str(Path(folder)/'ledger.sqlite'))
            prior_path=Path(folder)/'prior.json';HumanRetestAdmission(lambda:None,ledger,prior_path,human=True)
            opened=HumanOpenAdmission(lambda:None,ledger,Path(folder)/'open.json',human=True,previous_state_path=prior_path)
            r=ledger.reserve(1000);ledger.dispatch(r)
            with self.assertRaises(TrialAdmissionPaused):opened()
            self.assertEqual(opened.public_status()['reason'],'usage_unconfirmed');self.assertEqual(ledger.summary()['pending_requests'],1);ledger.close()
    def test_open_requires_human_and_single_review(self):
        for human,style in [(False,'source-review'),(True,'synthesis'),(True,'reviewed-excerpts')]:
            with self.assertRaises(ValueError):main(human=human,answer_style=style,human_open=True)
        with self.assertRaises(ValueError):HumanOpenAdmission(lambda:None,self.ledger,Path(self.tmp.name)/'not-created.json')
