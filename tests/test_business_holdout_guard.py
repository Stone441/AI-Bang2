import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.business_holdout import run


class HoldoutGuard(unittest.TestCase):
    def test_large_cap_budget_stops_before_credentials(self):
        original = Path.read_text
        def read(path, *args, **kwargs):
            if path == Path('.runtime/operator-bundle.json'):
                return json.dumps({'approved_synthetic_only': True, 'identity_mapping_reviewed': True,
                                   'sources': {'jira': 'fixture-jira.json'}})
            return original(path, *args, **kwargs)
        with tempfile.TemporaryDirectory() as tmp:
            cases = Path(tmp) / 'cases.json'
            cases.write_text(json.dumps([{}] * 12))
            with patch('scripts.business_holdout.Path.read_text', new=read), \
                 patch('scripts.business_holdout.Path.is_file', return_value=True), \
                 patch('scripts.business_holdout.check_price_review'), \
                 patch('scripts.business_holdout.BudgetLedger') as ledger, \
                 patch('scripts.business_holdout.MacKeychain') as keys:
                ledger.return_value.summary.return_value = {
                    'blocked_for_review': False, 'available_micro_usd': 7_600_000}
                with self.assertRaisesRegex(ValueError, 'Original budget unavailable'):
                    run(cases, Path(tmp) / 'output', True, 'low', 4096)
                keys.assert_not_called()
                ledger.return_value.reserve.assert_not_called()
                ledger.return_value.close.assert_called_once()

    def test_existing_evidence_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            cases = Path(tmp) / 'cases.json'
            cases.write_text(json.dumps([{}] * 12))
            target = Path(tmp) / 'output'
            target.mkdir()
            (target / 'original').write_text('keep')
            with patch('scripts.business_holdout.MacKeychain') as keys, \
                 patch('scripts.business_holdout.check_price_review') as price:
                with self.assertRaises(FileExistsError):
                    run(cases, target, True, 'low', 4096)
                keys.assert_not_called()
                price.assert_not_called()
                self.assertEqual((target / 'original').read_text(), 'keep')
