import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.quality_acceptance import run


class QualityAcceptance(unittest.TestCase):
    def test_existing_output_refuses_before_key_or_price_check(self):
        with tempfile.TemporaryDirectory() as tmp, patch('scripts.quality_acceptance.MacKeychain') as keys, patch('scripts.quality_acceptance.check_price_review') as price:
            target=Path(tmp);(target/'original').write_text('keep')
            with self.assertRaises(FileExistsError):run(target,True)
            self.assertEqual((target/'original').read_text(),'keep')
            keys.assert_not_called();price.assert_not_called()

    def test_frozen_original_budget_stops_before_credential_access(self):
        original=Path.read_text
        def read(path,*args,**kwargs):
            if path==Path('.runtime/operator-bundle.json'):
                return json.dumps({'approved_synthetic_only':True,'identity_mapping_reviewed':True,'sources':{'jira':'fixture-jira.json'}})
            if path==Path('.runtime/fixture-jira.json'):
                return json.dumps({'tenant':'fixture-tenant'})
            return original(path,*args,**kwargs)
        with tempfile.TemporaryDirectory() as tmp, patch('scripts.quality_acceptance.Path.read_text',new=read), patch('scripts.quality_acceptance.Path.is_file',return_value=True), patch('scripts.quality_acceptance.check_price_review'), patch('scripts.quality_acceptance.BudgetLedger') as ledger, patch('scripts.quality_acceptance.MacKeychain') as keys:
            ledger.return_value.summary.return_value={'blocked_for_review':True,'available_micro_usd':20_000_000}
            self.assertFalse(run(Path(tmp)/'new',True))
            keys.assert_not_called()
            ledger.return_value.reserve.assert_not_called()
            ledger.return_value.close.assert_called_once()
            report=json.loads((Path(tmp)/'new/verification.json').read_text())
            self.assertEqual(report['status'],'failed')
            self.assertEqual(report['failure_type'],'ValueError')
