from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from scripts.restore_drive_authorization import restore


class DriveRenewal(unittest.TestCase):
    def test_store_only_after_existing_account_verified(self):
        reader = SimpleNamespace(tenant='synthetic', transport=object())
        config = {'oauth_operator': {'email': 'existing@example.invalid'}}
        client = SimpleNamespace(client_id='existing-client')
        store = Mock()
        store.get.return_value = 'old-refresh'
        grant = {'access_token': 'synthetic-access', 'refresh_token': 'synthetic-refresh'}
        with patch('scripts.restore_drive_authorization.authorize', return_value=grant) as consent, \
             patch('scripts.restore_drive_authorization.verify_account', side_effect=ValueError):
            with self.assertRaises(ValueError):
                restore(reader, config, client, store, Mock())
            self.assertTrue(consent.call_args.kwargs['offline'])
            store.put.assert_not_called()
        with patch('scripts.restore_drive_authorization.authorize', return_value=grant), \
             patch('scripts.restore_drive_authorization.verify_account') as verify:
            restore(reader, config, client, store, Mock())
            verify.assert_called_once_with('synthetic-access', 'existing@example.invalid', reader.transport)
            store.put.assert_called_once_with('drive', 'synthetic', 'eng_b',
                'existing-client|existing@example.invalid', 'synthetic-refresh')

    def test_missing_existing_grant_never_opens_consent(self):
        store = Mock()
        store.get.return_value = None
        with patch('scripts.restore_drive_authorization.authorize') as consent:
            with self.assertRaises(ValueError):
                restore(SimpleNamespace(tenant='synthetic'),
                    {'oauth_operator': {'email': 'existing@example.invalid'}},
                    SimpleNamespace(client_id='existing-client'), store, Mock())
            consent.assert_not_called()
            store.put.assert_not_called()
