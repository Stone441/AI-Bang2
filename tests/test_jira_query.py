import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from brain.contracts import Actor
from scripts.jira_query import load_reader, main
from test_jira import JiraTransport


class JiraOperatorConfiguration(unittest.TestCase):
    def config(self, folder):
        path = Path(folder) / 'config.json'
        path.write_text(json.dumps({'approved_synthetic_only': True,
            'site': 'https://test.atlassian.net', 'tenant': 'pilot',
            'issues': {'10003': 'KAN-3'}, 'project_ids': ['10000'], 'comment_ids': {},
            'delegations': {'eng_b': {'account_id': 'employee', 'authorization_env': 'AIBANG2_JIRA_ENG_B'}}}))
        return path

    def test_no_live_flag_never_loads_config_or_credentials(self):
        with contextlib.redirect_stdout(io.StringIO()), patch('scripts.jira_query.load_reader') as load:
            self.assertEqual(main(['--config', 'missing', '--actor', 'eng_b', '--resource', '10003']), 2)
            load.assert_not_called()

    def test_missing_credentials_do_not_call_api(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True):
            r = load_reader(self.config(directory))
            with patch.object(r.transport, 'get') as get:
                self.assertEqual(r.read(Actor('eng_b', 'pilot'), '10003')[0].result, 'unknown')
                get.assert_not_called()

    def test_confluence_token_reference_and_inline_secret_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.config(directory); config = json.loads(path.read_text())
            for mapping in [{'account_id': 'employee', 'authorization_env': 'AIBANG2_CONFLUENCE_ENG_B'},
                            {'account_id': 'employee', 'authorization_env': 'AIBANG2_JIRA_ENG_B', 'authorization': 'secret-test'}]:
                config['delegations']['eng_b'] = mapping; path.write_text(json.dumps(config))
                with self.assertRaises(ValueError): load_reader(path)

    def test_hidden_entry_does_not_save_or_export_credential(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {}, clear=True), \
             patch('scripts.confluence_probe.sys.stdin.isatty', return_value=True), \
             patch('scripts.confluence_probe.getpass.getpass', side_effect=['engineer@example.com', 'secret-test']):
            path = self.config(directory); before = path.read_bytes()
            r = load_reader(path, 'eng_b')
            self.assertTrue(r.delegations['eng_b'].authorization.startswith('Basic '))
            self.assertNotIn('secret-test', repr(r.delegations['eng_b']))
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(list(Path(directory).iterdir()), [path])
            self.assertNotIn('AIBANG2_JIRA_ENG_B', os.environ)

    def test_probe_outputs_no_title_text_or_authorization(self):
        with tempfile.TemporaryDirectory() as directory:
            r = load_reader(self.config(directory)); r.transport = JiraTransport()
            from brain.confluence import Delegation
            r.delegations['eng_b'] = Delegation('employee', 'Bearer employee')
            output = io.StringIO()
            with contextlib.redirect_stdout(output), patch('scripts.jira_query.load_reader', return_value=r):
                self.assertEqual(main(['--config', 'mock', '--actor', 'eng_b', '--resource', '10003', '--live']), 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result['decision']['result'], 'allow')
            self.assertEqual(result['mode'], 'jira_mock_http_probe')
            for secret in ['Bearer', 'Maya', 'Payment-service', 'GA not approved']:
                self.assertNotIn(secret, output.getvalue())

    def test_query_cannot_write_database_outside_ignored_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.config(directory); output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(['--config', str(path), '--actor', 'eng_b', '--question', 'runbook',
                                       '--db', str(Path(directory) / 'outside.sqlite'), '--live']), 2)
            self.assertEqual(json.loads(output.getvalue())['mode'], 'not_run')
            self.assertFalse((Path(directory) / 'outside.sqlite').exists())


if __name__ == '__main__': unittest.main()
