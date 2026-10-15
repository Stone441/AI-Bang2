import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import performance_trial


class ReleaseStateRoot(unittest.TestCase):
    def test_fixed_code_uses_original_private_state_without_new_consent(self):
        from brain import operator_web, drive_oauth
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve()
            for relative in ('.runtime/deepseek-budget.sqlite',
                    '.runtime/delivery-trial-20261011/.runtime/multi-auth017-web.sqlite'):
                p=root/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'owned existing fixture')
            old_cwd=Path.cwd();old_private=performance_trial.PRIVATE
            try:
                with patch.object(operator_web,'main',return_value=0) as launch,patch.object(drive_oauth,'authorize'),patch.object(operator_web,'create_server'):
                    self.assertEqual(performance_trial.main(['--state-root',str(root),
                        '--human-team-trial','--attributed-grant','checked-human']),0)
                argv=launch.call_args.args[0]
                self.assertEqual(argv[argv.index('--config')+1],str(root/'.runtime/operator-bundle.json'))
                self.assertEqual(argv[argv.index('--oauth-client')+1],str(root/'.runtime/drive-oauth-client.json'))
                self.assertEqual((performance_trial.PRIVATE/'.runtime/deepseek-budget.sqlite').resolve(),root/'.runtime/deepseek-budget.sqlite')
            finally:
                os.chdir(old_cwd);performance_trial.PRIVATE=old_private

    def test_attributed_flag_cannot_enable_unapproved_automatic_mode(self):
        with self.assertRaises(SystemExit):performance_trial.main(['--attributed-grant','human'])
