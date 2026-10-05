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

    def test_hidden_input_does_not_persist_or_export_token(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{},clear=True), \
                patch('scripts.confluence_probe.sys.stdin.isatty',return_value=True), \
                patch('scripts.confluence_probe.getpass.getpass',side_effect=['engineer@example.com','test-secret']):
            path=self.config(folder);before=path.read_bytes()
            reader=load_reader(path,prompt_actor='eng_b')
            import base64
            expected='Basic '+base64.b64encode(b'engineer@example.com:test-secret').decode()
            self.assertEqual(reader.delegations['eng_b'].authorization,expected)
            self.assertNotIn('test-secret',repr(reader.delegations['eng_b']))
            self.assertEqual(path.read_bytes(),before)
            self.assertNotIn('AIBANG2_CONFLUENCE_ENG_B',os.environ)
            self.assertEqual(list(Path(folder).iterdir()),[path])

    def test_noninteractive_or_unmapped_prompt_never_reads_secret(self):
        with tempfile.TemporaryDirectory() as folder,patch('scripts.confluence_probe.getpass.getpass') as prompt:
            path=self.config(folder)
            with patch('scripts.confluence_probe.sys.stdin.isatty',return_value=False):
                with self.assertRaises(ValueError):load_reader(path,prompt_actor='eng_b')
            with patch('scripts.confluence_probe.sys.stdin.isatty',return_value=True):
                with self.assertRaises(ValueError):load_reader(path,prompt_actor='unknown')
            prompt.assert_not_called()

    def test_echo_fallback_never_reads_token(self):
        import getpass
        with tempfile.TemporaryDirectory() as folder, \
                patch('scripts.confluence_probe.sys.stdin.isatty',return_value=True), \
                patch('scripts.confluence_probe.getpass.getpass',side_effect=getpass.GetPassWarning('unsafe echo')) as prompt:
            with self.assertRaises(ValueError):load_reader(self.config(folder),prompt_actor='eng_b')
            self.assertEqual(prompt.call_count,1)

    def test_invalid_email_is_retried_before_requesting_token_and_never_echoed(self):
        from scripts.confluence_probe import hidden_delegation
        output=io.StringIO()
        with patch('scripts.confluence_probe.sys.stdin.isatty',return_value=True), \
             patch('scripts.confluence_probe.getpass.getpass',side_effect=['not-an-email','engineer@example.com','secret-test']) as prompt, \
             contextlib.redirect_stdout(output):
            result=hidden_delegation('employee')
        self.assertEqual(prompt.call_count,3)
        self.assertEqual(prompt.call_args_list[1].args[0],'Atlassian email (hidden): ')
        self.assertIn('[email_invalid]',output.getvalue())
        self.assertNotIn('not-an-email',output.getvalue())
        self.assertNotIn('secret-test',repr(result)+output.getvalue())

    def test_empty_or_multiline_token_retries_only_token_and_keeps_email(self):
        from scripts.confluence_probe import hidden_delegation
        output=io.StringIO()
        with patch('scripts.confluence_probe.sys.stdin.isatty',return_value=True), \
             patch('scripts.confluence_probe.getpass.getpass',side_effect=['engineer@example.com','','secret\nother','secret-test']) as prompt, \
             contextlib.redirect_stdout(output):
            result=hidden_delegation('employee')
        self.assertEqual(prompt.call_count,4)
        self.assertTrue(all('Scoped API token' in call.args[0] for call in prompt.call_args_list[1:]))
        self.assertIn('[token_empty]',output.getvalue());self.assertIn('[token_multiline]',output.getvalue())
        self.assertNotIn('secret',output.getvalue()+repr(result))

    def test_invalid_hidden_input_has_bounded_retry_and_fixed_reason(self):
        from scripts.confluence_probe import hidden_delegation
        from brain.credential_input import HiddenInputUnavailable
        for value,reason in [('', 'token_empty'),('x'*4097,'token_too_long'),('private\nkey','token_multiline')]:
            output=io.StringIO()
            with self.subTest(reason=reason),patch('scripts.confluence_probe.sys.stdin.isatty',return_value=True), \
                 patch('scripts.confluence_probe.getpass.getpass',side_effect=['engineer@example.com',value,value,value]) as prompt, \
                 contextlib.redirect_stdout(output),self.assertRaises(HiddenInputUnavailable) as caught:
                hidden_delegation('employee')
            self.assertEqual(prompt.call_count,4);self.assertEqual(caught.exception.code,reason)
            self.assertNotIn('engineer@example.com',output.getvalue())
            if value:self.assertNotIn(value,output.getvalue()+str(caught.exception))

    def test_input_eof_is_safe_and_does_not_start_an_echo_fallback(self):
        from scripts.confluence_probe import hidden_delegation
        from brain.credential_input import HiddenInputUnavailable
        with patch('scripts.confluence_probe.sys.stdin.isatty',return_value=True), \
             patch('scripts.confluence_probe.getpass.getpass',side_effect=EOFError('private-detail')) as prompt, \
             self.assertRaises(HiddenInputUnavailable) as caught:
            hidden_delegation('employee')
        self.assertEqual(caught.exception.code,'input_ended');self.assertEqual(prompt.call_count,1)
        self.assertNotIn('private-detail',str(caught.exception))


if __name__ == '__main__':
    unittest.main()
