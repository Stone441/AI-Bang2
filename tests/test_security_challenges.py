import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.security_challenges import run


class SecurityChallenges(unittest.TestCase):
    def test_all_probes_pass_but_live_model_resistance_stays_unmeasured(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'run';report=run(output)
            self.assertTrue(report['successful']);self.assertEqual(report['total'],8)
            self.assertEqual(report['semantic_injection_resistance'],'not_evaluated')
            injected=json.loads((output/'retrieved-instruction-and-link.json').read_text())
            self.assertTrue(injected['observation']['untrusted_instruction_reached_fake_model_as_data'])
            original=(output/'report.json').read_bytes()
            with self.assertRaises(FileExistsError):run(output)
            self.assertEqual((output/'report.json').read_bytes(),original)

    def test_failed_probe_is_saved_and_later_probes_still_run(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'run'
            with patch('scripts.security_challenges.Engine.query',side_effect=RuntimeError('no raw error text')):
                report=run(output)
            self.assertFalse(report['successful']);self.assertEqual(len(report['checks']),8)
            self.assertTrue((output/'audit-role-boundary.json').exists())
            self.assertNotIn('no raw error text',(output/'existence-probes.json').read_text())
