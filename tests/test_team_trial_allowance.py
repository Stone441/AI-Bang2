import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from brain.budget import BudgetLedger, TrialAdmissionPaused
from scripts.performance_allowance import PerformanceAdmission, GoalLedger
from scripts.team_trial_allowance import TeamTrialAdmission


class TeamAllowance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ledger = BudgetLedger(str(self.root/'ledger.sqlite'))
        self.old = self.ledger.reserve(100)
        self.ledger.dispatch(self.old)
        self.previous = self.root/'goal.json'
        old = PerformanceAdmission(lambda: None, self.ledger, self.previous, plan_sha256='a'*64)
        old.attempts = 60
        old.save()
        self.original = self.previous.read_bytes()
        self.path = self.root/'human.json'

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def gate(self):
        return TeamTrialAdmission(lambda: None, self.ledger, self.path,
                                  previous_state_path=self.previous, human=True)

    def call(self, gate, cost=1, upper=None, settle=True):
        guard = GoalLedger(gate)
        rid = guard.reserve(upper or cost)
        guard.dispatch(rid)
        if settle:
            guard.settle(rid, cost)
        return rid

    def test_exhausted_attempts_do_not_block_human_restart_preserves_usage(self):
        gate = self.gate()
        gate.query = lambda: self.call(gate)
        for _ in range(65):
            gate()
        again = self.gate()
        self.assertTrue(again.public_status()['allowed'])
        self.assertEqual(again.state_extra()['model_calls_used'], 65)
        self.assertEqual(again.public_status()['settled_usd'], .000065)
        self.assertEqual(self.previous.read_bytes(), self.original)
        self.assertEqual(again.pending, {self.old})
        self.assertEqual(again.public_status()['settlement_remaining_usd'], .999935)

    def test_each_model_stage_preserves_cost_reservation_limit(self):
        gate = self.gate()
        def query():
            self.call(gate, 900000)
            self.call(gate, 1, upper=100001)
        gate.query = query
        with self.assertRaises(TrialAdmissionPaused):
            gate()
        self.assertEqual(gate.state_extra()['model_calls_used'], 1)
        gate.query = lambda: self.call(gate, 100000)
        gate()
        self.assertFalse(gate.public_status()['allowed'])
        with self.assertRaises(TrialAdmissionPaused):
            gate()
        with self.assertRaises(TrialAdmissionPaused):
            GoalLedger(gate).reserve(1)

    def test_new_unknown_stops_queries_and_restart(self):
        gate = self.gate()
        gate.query = lambda: self.call(gate, settle=False)
        gate()
        with self.assertRaises(TrialAdmissionPaused):
            gate()
        with self.assertRaises(ValueError):
            self.gate()
        self.assertEqual(self.previous.read_bytes(), self.original)

    def test_new_unknown_cannot_be_absorbed_at_initialization(self):
        rid = self.ledger.reserve(1)
        self.ledger.dispatch(rid)
        with self.assertRaises(ValueError):
            self.gate()
        self.assertFalse(self.path.exists())

    def test_explicit_human_mode_and_unchanged_policy_required(self):
        with self.assertRaises(ValueError):
            TeamTrialAdmission(lambda: None, self.ledger, self.path, previous_state_path=self.previous)
        gate = self.gate()
        body = json.loads(self.path.read_text())
        body['settled_stop_threshold_micro_usd'] = 2_000_000
        self.path.write_text(json.dumps(body))
        with self.assertRaises(ValueError):
            self.gate()
        self.assertEqual(self.previous.read_bytes(), self.original)
