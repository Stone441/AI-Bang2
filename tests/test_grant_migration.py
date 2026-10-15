import json
from pathlib import Path
import tempfile
import unittest
from brain.budget import BudgetLedger
from scripts.grant_migration import prepare,apply
from scripts.performance_allowance import PerformanceAdmission


class GrantMigration(unittest.TestCase):
    def test_plan_is_read_only_and_apply_rejects_changed_legacy_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);db=root/'ledger.sqlite';state=root/'state.json';plan=root/'plan.json'
            ledger=BudgetLedger(str(db))
            PerformanceAdmission(lambda:None,ledger,state,plan_sha256='a'*64)
            prior=state.read_bytes();summary=ledger.summary()
            signature=prepare(db,state,'human',plan)
            self.assertEqual(ledger.summary(),summary)
            self.assertEqual(state.read_bytes(),prior)
            self.assertIsNone(ledger.db.execute("SELECT name FROM sqlite_master WHERE name='allowance_grants'").fetchone())
            with self.assertRaises(FileExistsError):prepare(db,state,'human',plan)
            state.write_bytes(prior+b' ')
            with self.assertRaises(ValueError):apply(db,state,plan,signature)
            state.write_bytes(prior)
            apply(db,state,plan,signature)
            self.assertEqual(ledger.summary(),summary)
            self.assertEqual(state.read_bytes(),prior)
            self.assertEqual(ledger.db.execute('SELECT id FROM allowance_grants').fetchone(),('human',))
            ledger.close()
