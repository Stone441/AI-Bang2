import tempfile
import unittest
from pathlib import Path
from brain.budget import BudgetLedger, BudgetExceeded


class BudgetReservations(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.path = str(Path(self.tmp.name) / 'budget.sqlite')
        self.ledger = BudgetLedger(self.path, 100)

    def tearDown(self):
        self.ledger.close(); self.tmp.cleanup()

    def test_two_connections_cannot_double_allocate_remaining_budget(self):
        other = BudgetLedger(self.path, 100)
        try:
            self.ledger.reserve(60)
            with self.assertRaises(BudgetExceeded): other.reserve(60)
            other.reserve(40)
            self.assertEqual(self.ledger.summary()['available_micro_usd'], 0)
        finally: other.close()

    def test_dispatched_unknown_charge_survives_restart_and_cannot_cancel(self):
        rid = self.ledger.reserve(100); self.ledger.dispatch(rid)
        self.ledger.close(); self.ledger = BudgetLedger(self.path, 100)
        with self.assertRaises(ValueError): self.ledger.cancel_before_dispatch(rid)
        with self.assertRaises(BudgetExceeded): self.ledger.reserve(1)
        self.assertEqual(self.ledger.summary()['pending_requests'], 1)

    def test_cancel_only_before_dispatch_and_no_double_dispatch(self):
        rid = self.ledger.reserve(100); self.ledger.cancel_before_dispatch(rid)
        self.assertEqual(self.ledger.summary()['available_micro_usd'], 100)
        with self.assertRaises(ValueError): self.ledger.dispatch(rid)
        rid = self.ledger.reserve(20); self.ledger.dispatch(rid)
        with self.assertRaises(ValueError): self.ledger.dispatch(rid)

    def test_settle_idempotent_but_conflicting_actual_not_allowed(self):
        rid = self.ledger.reserve(70); self.ledger.dispatch(rid); self.ledger.settle(rid, 30)
        self.ledger.settle(rid, 30)
        with self.assertRaises(ValueError): self.ledger.settle(rid, 29)
        self.assertEqual(self.ledger.summary()['available_micro_usd'], 70)

    def test_estimate_overrun_is_durable_and_budget_blocks_further_spending(self):
        rid = self.ledger.reserve(80); self.ledger.dispatch(rid)
        with self.assertRaises(BudgetExceeded): self.ledger.settle(rid, 110)
        self.assertEqual(self.ledger.summary()['settled_micro_usd'], 110)
        with self.assertRaises(BudgetExceeded): self.ledger.reserve(1)

    def test_no_limit_increase_or_bool_amounts(self):
        with self.assertRaises(ValueError): BudgetLedger(self.path, 101)
        with self.assertRaises(ValueError): BudgetLedger(':memory:', 20_000_001)
        for amount in (True, 0, -1, 1.1):
            with self.assertRaises(ValueError): self.ledger.reserve(amount)
        rid = self.ledger.reserve(1); self.ledger.dispatch(rid)
        with self.assertRaises(ValueError): self.ledger.settle(rid, True)

    def test_estimate_violation_freezes_even_if_total_below_ceiling(self):
        rid = self.ledger.reserve(10); self.ledger.dispatch(rid)
        with self.assertRaises(BudgetExceeded): self.ledger.settle(rid, 11)
        self.assertEqual(self.ledger.summary()['settled_micro_usd'], 11)
        self.assertTrue(self.ledger.summary()['blocked_for_review'])
        with self.assertRaises(BudgetExceeded): self.ledger.reserve(1)


if __name__ == '__main__': unittest.main()
