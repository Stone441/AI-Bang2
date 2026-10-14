import json
from pathlib import Path
import tempfile
import unittest
from brain.budget import BudgetLedger, TrialAdmissionPaused
from scripts.performance_allowance import PerformanceAdmission, GoalLedger
import test_source_review as source_review_tests


class GoalModelIntegration(unittest.TestCase):
    setUp = source_review_tests.SourceReview.setUp
    tearDown = source_review_tests.SourceReview.tearDown
    candidate = source_review_tests.SourceReview.candidate
    engine = source_review_tests.SourceReview.engine
    verdicts = source_review_tests.SourceReview.verdicts
    dynamic_review = source_review_tests.SourceReview.dynamic_review

    def test_real_source_review_constructor_and_receipt_use_guarded_original_ledger(self):
        from brain.contracts import Actor
        engine, _ = self.engine()
        self.dynamic_review()
        with tempfile.TemporaryDirectory() as directory:
            gate = PerformanceAdmission(engine.query, self.ledger, Path(directory)/'goal.json', plan_sha256='a'*64)
            engine.model.ledger = GoalLedger(gate)
            result = gate(Actor('eng_b'), 'payment-service incident runbook')
            self.assertEqual(result['review_status'], 'accepted')
            self.assertEqual(len(self.transport.calls), 1)
            self.assertEqual(gate.state_extra()['model_calls_used'], 1)
            self.assertEqual(self.ledger.summary()['pending_requests'], 0)
            self.assertIs(engine.model.ledger.db, self.ledger.db)


class GoalLimits(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'goal.json'
        self.ledger = BudgetLedger(str(Path(self.tmp.name)/'original.sqlite'))
        self.old = self.ledger.reserve(324404)
        self.ledger.dispatch(self.old)
        self.plan = 'a'*64

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def gate(self, query):
        return PerformanceAdmission(query, self.ledger, self.path, plan_sha256=self.plan)

    def call(self, gate, cost=1000, upper=None):
        guarded = GoalLedger(gate)
        rid = guarded.reserve(upper or cost, query_id='b'*32, model='deepseek-flash')
        guarded.dispatch(rid)
        guarded.settle(rid, cost, usage={'prompt_tokens': 1, 'completion_tokens': 1, 'total_tokens': 2})
        guarded.model_outcome(rid, 'accepted')
        return rid

    def test_restart_preserves_baseline_old_unknown_and_plan(self):
        gate = self.gate(lambda: self.call(gate))
        gate()
        restarted = self.gate(lambda: self.call(restarted))
        restarted()
        state = json.loads(self.path.read_text())
        self.assertEqual(state['model_calls_used'], 2)
        self.assertEqual(state['original_pending_ids'], [self.old])
        self.assertEqual(self.ledger.summary()['pending_requests'], 1)
        with self.assertRaises(ValueError):
            PerformanceAdmission(lambda: None, self.ledger, self.path, plan_sha256='c'*64)
        self.assertEqual(json.loads(self.path.read_text()), state)

    def test_second_model_stage_cannot_cross_sixty_call_limit(self):
        gate = self.gate(lambda: None)
        # Model-stage bound is separate from query/attempt bound. Reserve and
        # settle externally to simulate 59 prior actual calls in this goal.
        for _ in range(59):
            rid = self.ledger.reserve(1)
            self.ledger.dispatch(rid)
            self.ledger.settle(rid, 1)
        def query():
            self.call(gate, 1)
            self.call(gate, 1)
        gate.query = query
        with self.assertRaises(TrialAdmissionPaused):
            gate()
        self.assertEqual(json.loads(self.path.read_text())['model_calls_used'], 60)
        self.assertEqual(self.ledger.summary()['pending_requests'], 1)
        self.assertEqual(gate.public_status()['reason'], 'model_call_limit')

    def test_cost_bound_checked_before_each_reservation(self):
        gate = self.gate(lambda: None)
        def query():
            self.call(gate, 400000)
            self.call(gate, 1, upper=100001)
        gate.query = query
        with self.assertRaises(TrialAdmissionPaused):
            gate()
        self.assertEqual(json.loads(self.path.read_text())['model_calls_used'], 1)
        self.assertEqual(self.ledger.summary()['settled_micro_usd'], 400000)
        self.assertEqual(self.ledger.summary()['pending_requests'], 1)

    def test_unknown_first_call_blocks_next_stage_and_next_question(self):
        gate = self.gate(lambda: None)
        def query():
            rid = GoalLedger(gate).reserve(1000, query_id='b'*32, model='deepseek-flash')
            self.ledger.dispatch(rid)
            self.ledger.model_outcome(rid, 'usage_unavailable')
            self.call(gate)
        gate.query = query
        with self.assertRaises(TrialAdmissionPaused):
            gate()
        with self.assertRaises(TrialAdmissionPaused):
            gate()
        self.assertEqual(json.loads(self.path.read_text())['model_calls_used'], 1)
        self.assertEqual(self.ledger.summary()['pending_requests'], 2)
        self.assertEqual(gate.public_status()['reason'], 'usage_unconfirmed')

    def test_unadmitted_model_and_changed_policy_are_rejected(self):
        gate = self.gate(lambda: None)
        with self.assertRaises(TrialAdmissionPaused):
            GoalLedger(gate).reserve(1000)
        body = json.loads(self.path.read_text())
        body['max_model_calls'] = 61
        self.path.write_text(json.dumps(body))
        with self.assertRaises(ValueError):
            self.gate(lambda: None)
        self.assertEqual(self.ledger.summary()['pending_requests'], 1)
