import json
import tempfile
import unittest
from pathlib import Path
from brain.contracts import Decision
from unittest.mock import patch

from scripts.native_product_acceptance import run


class ProductAcceptance(unittest.TestCase):
    def test_existing_evidence_refuses_before_credential_access(self):
        with tempfile.TemporaryDirectory() as directory, patch('scripts.native_product_acceptance.MacKeychain') as keys:
            with self.assertRaises(FileExistsError):
                run(Path(directory))
            keys.assert_not_called()

    def test_unexpected_native_engineering_allow_fails_without_query(self):
        # A wrongly granted native page must fail acceptance, never be hidden by UI role.
        # This offline test must reach native denial checks without local credentials/config.
        config = {'approved_synthetic_only': True, 'page_ids': ['164283'],
                  'site': 'https://fixture.invalid', 'tenant': 'aibang2-live-pilot',
                  'space_ids': ['fixture-space'],
                  'delegations': {'product_ops': {'account_id': 'fixture-product'}}}
        original_read = Path.read_text
        def read_config(path, *args, **kwargs):
            if path == Path('.runtime/confluence-product.json'):
                return json.dumps(config)
            return original_read(path, *args, **kwargs)
        with tempfile.TemporaryDirectory() as directory, patch('scripts.native_product_acceptance.Path.read_text', new=read_config), patch('scripts.native_product_acceptance.MacKeychain') as keys, patch('scripts.native_product_acceptance.ConfluenceReader') as reader, patch('scripts.native_product_acceptance.DelegatedQueryPilot') as pilot:
            keys.return_value.get.return_value = 'Bearer fixture-only'
            reader.return_value.tenant = 'aibang2-live-pilot'
            reader.return_value.read.side_effect = [
                (Decision('allow', 'fixture-time', 'mock', 0), {'text': 'unexpected runbook'}),
                (Decision('deny', 'fixture-time', 'mock', 0), None),
                (Decision('allow', 'fixture-time', 'mock', 0), {'text': 'controlled pilot'}),
            ]
            output = Path(directory) / 'new-evidence'
            self.assertFalse(run(output))
            pilot.assert_not_called()
            keys.return_value.get.assert_called_once_with('confluence', 'aibang2-live-pilot', 'product_ops', 'fixture-product')
            self.assertEqual(reader.return_value.read.call_count, 3)
            result = json.loads((output / 'verification.json').read_text())
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['native_decisions']['engineering']['result'], 'allow')
            self.assertNotIn('fixture-only', (output / 'verification.json').read_text())
