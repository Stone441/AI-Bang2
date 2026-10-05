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
        with tempfile.TemporaryDirectory() as directory, patch('scripts.native_product_acceptance.MacKeychain') as keys, patch('scripts.native_product_acceptance.ConfluenceReader') as reader, patch('scripts.native_product_acceptance.DelegatedQueryPilot') as pilot:
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
            result = json.loads((output / 'verification.json').read_text())
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(result['native_decisions']['engineering']['result'], 'allow')
            self.assertNotIn('fixture-only', (output / 'verification.json').read_text())
