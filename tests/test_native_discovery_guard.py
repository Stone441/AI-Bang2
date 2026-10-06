import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock,patch
from brain.confluence import SourceUnavailable
from scripts.native_discovery_acceptance import main,saved_credentials,run


class NativeDiscoveryGuard(unittest.TestCase):
    def test_without_live_no_credentials_or_api(self):
        with redirect_stdout(io.StringIO()),patch('scripts.native_discovery_acceptance.run') as call:
            self.assertEqual(main(['--output','not-created']),2);call.assert_not_called()

    def test_existing_output_preserved_before_keychain_or_configuration(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp,patch('scripts.native_discovery_acceptance.prepare') as prepare,patch('scripts.native_discovery_acceptance.MacKeychain') as kc:
            p=Path(tmp)/'old';p.mkdir();(p/'actual.txt').write_text('unchanged')
            with self.assertRaises(FileExistsError):run(p,'missing','missing')
            self.assertEqual((p/'actual.txt').read_text(),'unchanged');prepare.assert_not_called();kc.assert_not_called()

    def test_missing_saved_credential_has_no_prompt_or_new_grant(self):
        reader=Mock();reader.tenant='pilot';kc=Mock();kc.get.return_value=None
        with patch('scripts.native_discovery_acceptance.refresh_access') as refresh:
            with self.assertRaises(ValueError):saved_credentials({'confluence':reader},{'confluence':{'delegations':{'eng_b':{'account_id':'employee'}}}},'missing',kc)
            refresh.assert_not_called();reader.transport.get.assert_not_called();kc.put.assert_not_called()

    def test_drive_refresh_failure_has_no_consent_or_keychain_write(self):
        reader=Mock();reader.tenant='pilot';kc=Mock();kc.get.return_value='synthetic-refresh'
        config={'drive':{'oauth_client_id':'client','oauth_operator':{'email':'synthetic@example.test'}}}
        with patch('scripts.native_discovery_acceptance.load_client',return_value=Mock(client_id='client')),patch('scripts.native_discovery_acceptance.refresh_access',side_effect=SourceUnavailable()),patch('scripts.native_discovery_acceptance.verify_account') as verify:
            with self.assertRaises(SourceUnavailable):saved_credentials({'drive':reader},config,'client',kc)
            verify.assert_not_called();kc.put.assert_not_called()
