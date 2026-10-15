import hashlib
import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from brain.budget import BudgetLedger, BudgetExceeded, TrialAdmissionPaused
from scripts.attributed_allowance import AttributedAdmission, AttributedGoalLedger, migration_plan, apply_migration


class AttributedBudget(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name)/'ledger.sqlite')
        self.ledger = BudgetLedger(self.path)
        self.old = self.ledger.reserve(50)
        self.ledger.dispatch(self.old)
        self.prior = {'authorization': 'test-policy', 'settled_stop_threshold_micro_usd': 100,
                      'max_model_calls': 3, 'baseline_model_calls': 1, 'attempts': 0,
                      'baseline': self.ledger.summary(), 'original_pending_ids': [self.old]}

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def grant(self, name, prior=None, external=None):
        plan = migration_plan(self.ledger, name, prior or self.prior, external_reservations=external or {})
        apply_migration(self.ledger, plan, expected_plan_sha256=hashlib.sha256(plan.encode()).hexdigest())
        return AttributedAdmission(lambda: None, self.ledger, name, policy='test-policy', cost_limit=100, max_calls=3)

    def call(self, gate, cost, settle=True):
        def query():
            guard = AttributedGoalLedger(gate)
            rid = guard.reserve(cost)
            guard.dispatch(rid)
            if settle: guard.settle(rid, cost)
            return rid
        gate.query = query
        return gate()

    def test_cross_grant_restart_and_failed_calls_do_not_double_count(self):
        a, b = self.grant('a'), self.grant('b')
        self.call(a, 70)
        self.call(b, 40)
        a = AttributedAdmission(lambda: None, self.ledger, 'a', policy='test-policy', cost_limit=100, max_calls=3)
        self.assertEqual(a.public_status()['settled_usd'], .000070)
        self.call(a, 30)
        self.assertEqual(b.public_status()['model_calls_used'], 1)
        with self.assertRaises(TrialAdmissionPaused): self.call(a, 1)
        self.assertEqual(self.ledger.summary()['settled_micro_usd'], 140)

    def test_new_unknown_stops_own_grant_old_unknown_retained(self):
        a, b = self.grant('a'), self.grant('b')
        rid = self.call(a, 40, settle=False)
        with self.assertRaises(TrialAdmissionPaused): self.call(a, 1)
        with self.assertRaises(TrialAdmissionPaused): self.call(b, 1)
        self.assertEqual(b.public_status()['settled_usd'], 0)
        self.assertEqual(self.ledger.summary()['pending_requests'], 2)
        self.ledger.settle(rid, 20)
        self.call(a, 80)

    def test_concurrent_process_connections_cannot_cross_grant_ceiling(self):
        self.grant('a')
        def reserve(_):
            ledger = BudgetLedger(self.path)
            try:
                gate = AttributedAdmission(lambda: None, ledger, 'a', policy='test-policy', cost_limit=100, max_calls=3)
                return self.call(gate, 60)
            except TrialAdmissionPaused: return None
            finally: ledger.close()
        with ThreadPoolExecutor(2) as pool: result = list(pool.map(reserve, range(2)))
        self.assertEqual(sum(r is not None for r in result), 1)

    def test_migration_freezes_history_exact_external_evidence_and_stale_plan(self):
        human = self.ledger.reserve(30); self.ledger.dispatch(human); self.ledger.settle(human, 30)
        external = self.ledger.reserve(40); self.ledger.dispatch(external); self.ledger.settle(external, 40)
        conservative = self.grant('conservative')
        self.assertEqual(conservative.public_status()['settled_usd'], .000070)
        explicit = self.grant('exact', external={external: {'owner': 'team-live17', 'evidence_sha256': 'a'*64}})
        self.assertEqual(explicit.public_status()['settled_usd'], .000030)
        plan = migration_plan(self.ledger, 'stale', self.prior)
        self.call(explicit, 1)
        with self.assertRaises(ValueError): apply_migration(self.ledger, plan, expected_plan_sha256=hashlib.sha256(plan.encode()).hexdigest())
        with self.assertRaises(ValueError): AttributedAdmission(lambda: None, self.ledger, 'exact', policy='test-policy', cost_limit=101, max_calls=3)

    def test_historical_new_unknown_never_forgiven_by_migration(self):
        unknown = self.ledger.reserve(30); self.ledger.dispatch(unknown)
        gate = self.grant('a')
        with self.assertRaises(TrialAdmissionPaused): self.call(gate, 1)
        self.assertEqual(self.ledger.summary()['pending_requests'], 2)

    def test_global_ceiling_still_applies_and_ownership_is_immutable(self):
        a = self.grant('a')
        rid = self.call(a, 1)
        with self.assertRaises(Exception):
            self.ledger.db.execute("UPDATE reservation_grants SET grant_id='other' WHERE reservation_id=?", (rid,))
        external = self.ledger.reserve(self.ledger.summary()['available_micro_usd'])
        with self.assertRaises(BudgetExceeded): self.call(a, 1)
        self.assertIsNotNone(external)

    def test_rejected_and_failed_dispatched_calls_consume_call_slots(self):
        gate = self.grant('a')
        def rejected():
            guard = AttributedGoalLedger(gate)
            rid = guard.reserve(1, query_id='a'*32, model='deepseek-flash')
            guard.dispatch(rid)
            guard.settle(rid, 0)
            guard.model_outcome(rid, 'output_rejected')
            raise RuntimeError('fixture rejected output')
        gate.query = rejected
        for _ in range(3):
            with self.assertRaises(RuntimeError): gate()
        with self.assertRaises(TrialAdmissionPaused): gate()
        self.assertEqual(gate.public_status()['model_calls_used'], 3)
        self.assertEqual(gate.public_status()['settled_usd'], 0)

    def test_restart_connection_retains_grant_unknown_and_frozen_usage(self):
        gate = self.grant('a')
        self.call(gate, 10)
        rid = self.call(gate, 20, settle=False)
        self.ledger.close()
        self.ledger = BudgetLedger(self.path)
        gate = AttributedAdmission(lambda: None, self.ledger, 'a', policy='test-policy', cost_limit=100, max_calls=3)
        self.assertEqual(gate.public_status()['model_calls_used'], 2)
        with self.assertRaises(TrialAdmissionPaused): self.call(gate, 1)
        self.ledger.settle(rid, 20)
        self.call(gate, 70)

    def test_migration_rejects_forged_frozen_cost_or_unknown_external(self):
        rid = self.ledger.reserve(40); self.ledger.dispatch(rid); self.ledger.settle(rid, 40)
        body = json.loads(migration_plan(self.ledger, 'a', self.prior))
        body['frozen_cost'] = 0
        forged = json.dumps(body, sort_keys=True, separators=(',', ':'))
        with self.assertRaises(ValueError):
            apply_migration(self.ledger, forged, expected_plan_sha256=hashlib.sha256(forged.encode()).hexdigest())
        with self.assertRaises(ValueError):
            migration_plan(self.ledger, 'a', self.prior, external_reservations={self.old: {'owner': 'external', 'evidence_sha256': 'a'*64}})
        self.assertEqual(self.ledger.summary()['settled_micro_usd'], 40)

    def test_new_grant_cannot_dispatch_other_grant_reservation(self):
        a, b = self.grant('a'), self.grant('b')
        def query():
            rid = AttributedGoalLedger(a).reserve(10)
            b.query = lambda: AttributedGoalLedger(b).dispatch(rid)
            with self.assertRaises(TrialAdmissionPaused): b()
            AttributedGoalLedger(a).cancel_before_dispatch(rid)
        a.query = query
        a()
        self.assertEqual(a.public_status()['model_calls_used'], 0)

    def test_external_new_prepared_or_dispatched_unknown_blocks_all_grants(self):
        gate = self.grant('a')
        external = self.ledger.reserve(20)
        self.assertFalse(gate.public_status()['allowed'])
        with self.assertRaises(TrialAdmissionPaused): self.call(gate, 1)
        self.ledger.dispatch(external)
        with self.assertRaises(TrialAdmissionPaused): self.call(gate, 1)
        self.assertEqual(gate.public_status()['settled_usd'], 0)
        self.assertEqual(self.ledger.summary()['pending_requests'], 2)
        self.ledger.settle(external, 20)
        self.call(gate, 1)
        self.assertEqual(gate.public_status()['settled_usd'], .000001)

    def test_external_unknown_between_reserve_and_dispatch_pauses_dispatch(self):
        gate = self.grant('a')
        def query():
            guard = AttributedGoalLedger(gate)
            own = guard.reserve(10)
            external = self.ledger.reserve(20)
            with self.assertRaises(TrialAdmissionPaused): guard.dispatch(own)
            with self.ledger.transaction():
                state = self.ledger.db.execute('SELECT state FROM reservations WHERE id=?', (own,)).fetchone()[0]
            self.assertEqual(state, 'prepared')
            guard.cancel_before_dispatch(own)
            self.ledger.cancel_before_dispatch(external)
        gate.query = query
        gate()
        self.assertEqual(gate.public_status()['model_calls_used'], 0)
        self.assertEqual(self.ledger.summary()['pending_requests'], 1)

    def test_public_status_reports_global_exhaustion_without_own_charge(self):
        gate = self.grant('a')
        remaining = self.ledger.summary()['available_micro_usd']
        rid = self.ledger.reserve(remaining)
        self.ledger.dispatch(rid)
        self.ledger.settle(rid, remaining)
        self.assertEqual(gate.public_status()['reason'], 'global_budget_unavailable')
        self.assertFalse(gate.public_status()['allowed'])
        self.assertEqual(gate.public_status()['settled_usd'], 0)
