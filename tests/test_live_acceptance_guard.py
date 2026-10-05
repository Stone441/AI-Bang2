import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.live_product_acceptance import run
from scripts.native_restricted_acceptance import run as run_restricted


class LiveAcceptanceGuard(unittest.TestCase):
    def test_restricted_cli_requires_live_without_touching_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'unused'
            result = subprocess.run([sys.executable, '-m', 'scripts.native_restricted_acceptance', '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('--live required', result.stderr)
            self.assertFalse(output.exists())

    def test_restricted_preserves_existing_directory_before_keychain_or_network(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            record = output / 'audit.json'
            record.write_text('original evidence')
            with patch('scripts.native_restricted_acceptance.MacKeychain') as keys, patch('scripts.native_restricted_acceptance.StatusTransport') as transport:
                with self.assertRaises(FileExistsError): run_restricted(output)
                keys.assert_not_called(); transport.assert_not_called()
            self.assertEqual(record.read_text(), 'original evidence')

    def test_cli_requires_live_before_any_output_or_credential_use(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'unused'
            result = subprocess.run([sys.executable, '-m', 'scripts.live_product_acceptance', '--output', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('--live required', result.stderr)
            self.assertFalse(output.exists())
            self.assertNotIn('Keychain credential', result.stdout)

    def test_existing_evidence_preserved_before_credential_access(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory); record = output / 'verification.json'
            record.write_text('{"previous":"actual evidence"}')
            with patch('scripts.live_product_acceptance.MacKeychain') as keys, patch('scripts.live_product_acceptance.load_reader') as readers:
                with self.assertRaises(FileExistsError): run(output)
                keys.assert_not_called(); readers.assert_not_called()
            self.assertEqual(record.read_text(), '{"previous":"actual evidence"}')
