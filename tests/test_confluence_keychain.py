import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from brain.confluence import Delegation, SourceUnavailable
from brain.keychain import KeychainUnavailable
from brain.operator_web import main
from scripts.confluence_probe import load_reader


class ConfluenceKeychain(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'config.json'
        self.path.write_text(json.dumps({'approved_synthetic_only': True,
            'site': 'https://test.atlassian.net', 'tenant': 'test-pilot',
            'page_ids': ['98564'], 'space_ids': ['123'],
            'delegations': {'product_ops': {'account_id': 'native-product',
                                         'authorization_env': 'AIBANG2_CONFLUENCE_PRODUCT_OPS'}}}))
        self.keys = Mock()
        self.output = io.StringIO()

    def load(self):
        with contextlib.redirect_stdout(self.output):
            return load_reader(self.path, 'product_ops', credential_store=self.keys)

    def test_saved_credential_reused_without_tty_and_native_identity_checked(self):
        self.keys.get.return_value = 'Bearer fixture-saved'
        with patch('scripts.confluence_probe.hidden_delegation') as hidden, patch('brain.confluence.JsonTransport.get', return_value=(200, {'type': 'known', 'accountId': 'native-product'})) as native:
            reader = self.load()
            hidden.assert_not_called()
            self.assertEqual(native.call_count, 1)
        self.keys.get.assert_called_once_with('confluence', 'test-pilot', 'product_ops', 'native-product')
        self.keys.put.assert_not_called()
        self.assertEqual(reader.delegations['product_ops'].account_id, 'native-product')
        self.assertNotIn('fixture-saved', self.output.getvalue())

    def test_new_hidden_credential_persisted_only_after_native_identity(self):
        self.keys.get.return_value = None
        with patch('scripts.confluence_probe.hidden_delegation', return_value=Delegation('native-product', 'Bearer fixture-new')), patch('brain.confluence.JsonTransport.get', return_value=(200, {'type': 'known', 'accountId': 'native-product'})) as native:
            self.keys.put.side_effect = lambda *args: self.assertEqual(native.call_count, 1)
            self.load()
        self.keys.put.assert_called_once_with('confluence', 'test-pilot', 'product_ops', 'native-product', 'Bearer fixture-new')
        self.assertNotIn('fixture-new', self.output.getvalue())

    def test_wrong_native_account_never_saved_or_falls_back(self):
        for saved in (None, 'Bearer fixture-wrong'):
            with self.subTest(saved=saved):
                self.keys.reset_mock()
                self.keys.get.return_value = saved
                with patch('scripts.confluence_probe.hidden_delegation', return_value=Delegation('native-product', 'Bearer fixture-new')) as hidden, patch('brain.confluence.JsonTransport.get', return_value=(200, {'type': 'known', 'accountId': 'native-engineer'})) as native:
                    with self.assertRaises(SourceUnavailable):
                        self.load()
                    self.assertEqual(native.call_count, 1)
                    if saved:
                        hidden.assert_not_called()
                self.keys.put.assert_not_called()

    def test_keychain_access_denied_never_prompts_or_calls_source(self):
        self.keys.get.side_effect = KeychainUnavailable()
        with patch('scripts.confluence_probe.hidden_delegation') as hidden, patch('brain.confluence.JsonTransport.get') as native:
            with self.assertRaises(KeychainUnavailable):
                self.load()
            hidden.assert_not_called()
            native.assert_not_called()
        self.keys.put.assert_not_called()

    def test_invalid_allowlist_rejected_before_keychain_access(self):
        config = json.loads(self.path.read_text())
        config['page_ids'] = ['../not-approved']
        self.path.write_text(json.dumps(config))
        with self.assertRaises(ValueError):
            self.load()
        self.keys.get.assert_not_called()
        self.keys.put.assert_not_called()

    def test_operator_cli_reuses_saved_key_and_separates_tenant_and_account_databases(self):
        self.keys.get.return_value = 'Bearer fixture-saved'
        runtime = Path(self.directory.name) / 'runtime'
        config = json.loads(self.path.read_text())
        for tenant, account in [('test-pilot', 'native-product'), ('test-pilot', 'native-product'),
                                ('other-pilot', 'native-product'), ('test-pilot', 'other-product')]:
            config['tenant'] = tenant
            config['delegations']['product_ops']['account_id'] = account
            self.path.write_text(json.dumps(config))
            server = Mock(server_port=8100)
            server.serve_forever.side_effect = KeyboardInterrupt
            with contextlib.redirect_stdout(self.output), patch('brain.operator_web.create_server', return_value=server), patch('brain.operator_web.Path', return_value=runtime), patch('brain.keychain.MacKeychain', return_value=self.keys), patch('scripts.confluence_probe.hidden_delegation') as hidden, patch('brain.confluence.JsonTransport.get', return_value=(200, {'type': 'known', 'accountId': account})):
                self.assertEqual(main(['--config', str(self.path), '--actor', 'product_ops',
                                       '--live', '--credential-store', 'macos-keychain']), 0)
                hidden.assert_not_called()
            server.serve_forever.assert_called_once()
            server.server_close.assert_called_once()
        files = list(runtime.glob('confluence-*-web.sqlite'))
        self.assertEqual(len(files), 3)  # Identical identity reuses; tenant/account changes isolate.
        self.assertTrue(all(f.stat().st_mode & 0o777 == 0o600 for f in files))
        self.keys.put.assert_not_called()
        self.assertNotIn('fixture-saved', self.output.getvalue())
