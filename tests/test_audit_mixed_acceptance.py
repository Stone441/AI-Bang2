import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from brain.audit import Audit
from scripts.audit_mixed_acceptance import run


class MixedAuditAcceptance(unittest.TestCase):
    def test_existing_output_refused_before_running_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            record = output / 'audit.json'
            record.write_text('original')
            with patch('scripts.audit_mixed_acceptance.FixtureWorld') as world:
                with self.assertRaises(FileExistsError):
                    run(output)
                world.assert_not_called()
            self.assertEqual(record.read_text(), 'original')

    def test_oracle_detects_omitted_failure_event_before_signing(self):
        original = Audit.inquire

        def omit_failure(audit, actor, filters):
            result = original(audit, actor, filters)
            result['events'] = [e for e in result['events'] if e['event_type'] != 'request_failed']
            return result

        with tempfile.TemporaryDirectory() as directory:
            with patch.object(Audit, 'inquire', omit_failure), patch('scripts.audit_mixed_acceptance.subprocess.run') as signer, patch('scripts.audit_mixed_acceptance.revision', return_value='test-only'):
                report = run(Path(directory) / 'result')
                signer.assert_not_called()
            self.assertEqual(report['status'], 'failed')
            self.assertEqual(report['reason'], 'AssertionError')


if __name__ == '__main__':
    unittest.main()
