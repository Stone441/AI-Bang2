import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.confluence_probe import load_reader, main
from brain.contracts import Actor


class ProbeConfiguration(unittest.TestCase):
    def config(self, folder):
        path = Path(folder) / 'config.json'
        path.write_text(json.dumps({'approved_synthetic_only': True,
                                    'site': 'https://test.atlassian.net', 'tenant': 'pilot',
                                    'page_ids': ['98564'], 'space_ids': ['123'],
                                    'delegations': {'eng_b': {'account_id': 'employee',
                                      'authorization_env': 'AIBANG2_CONFLUENCE_ENG_B'}}}))
        return path

    def test_missing_credentials_do_not_make_network_request(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {}, clear=True):
            reader = load_reader(self.config(folder))
            with patch.object(reader.transport, 'get') as get:
                self.assertEqual(reader.read(Actor('eng_b', 'pilot'), '98564')[0].result, 'unknown')
                get.assert_not_called()

    def test_without_live_flag_never_loads_configuration(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch('scripts.confluence_probe.load_reader') as load:
            self.assertEqual(main(['--config', 'missing', '--actor', 'eng_b', '--page', '98564']), 2)
            load.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())['mode'], 'not_run')

    def test_configuration_errors_do_not_print_secret(self):
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as folder:
            path = self.config(folder); data = json.loads(path.read_text())
            data['delegations']['eng_b']['authorization'] = 'Bearer secret-test'
            path.write_text(json.dumps(data))
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(['--config', str(path), '--actor', 'eng_b',
                                       '--page', '98564', '--live']), 2)
        self.assertNotIn('secret-test', output.getvalue())
        self.assertEqual(json.loads(output.getvalue())['mode'], 'not_run')


if __name__ == '__main__':
    unittest.main()
