import json
import tempfile
import unittest
from pathlib import Path
from brain.budget import BudgetLedger, TrialAdmissionPaused
from scripts.delivery_trial import Admission

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
