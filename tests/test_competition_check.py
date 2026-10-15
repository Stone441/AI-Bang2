import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from scripts.competition_check import run


class CompetitionCheck(unittest.TestCase):
    def test_existing_evidence_is_preserved_without_running_anything(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory);(output/'report.json').write_text('original failure')
            with patch('scripts.competition_check.subprocess.run') as execute:
                with self.assertRaises(FileExistsError):run(output)
            execute.assert_not_called()
            self.assertEqual((output/'report.json').read_text(),'original failure')

    def test_failure_is_retained_and_remaining_checks_still_run(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'new'
            effects=[SimpleNamespace(returncode=1),OSError('node missing')]+[SimpleNamespace(returncode=0)]*17
            with patch('scripts.competition_check.revision',return_value='test'),patch('scripts.competition_check.dirty',return_value=True),patch('scripts.competition_check.subprocess.run',side_effect=effects):
                self.assertFalse(run(output))
            report=json.loads((output/'report.json').read_text())
            self.assertEqual(len(report['checks']),19)
            self.assertEqual([c['status'] for c in report['checks'][:2]],['failed','failed'])
            self.assertFalse(report['successful'])
            self.assertEqual(report['live_api'],'not_run')
            self.assertIn('node missing',(output/'four-source-lifecycle.log').read_text())
