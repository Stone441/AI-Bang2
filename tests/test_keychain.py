import io
import json
import tempfile
import unittest
from unittest.mock import Mock,patch
from brain.keychain import MacKeychain,KeychainUnavailable,item_key,ReplaceOne
from brain.drive_oauth import DesktopClient,Consent,SCOPE,ISSUER,refresh_access,ReauthorizationRequired
from brain.confluence import SourceUnavailable,Delegation
from scripts.operator_bundle import load_reader
import test_bundle_oauth

class MemoryStore:
    def __init__(self):self.items={};self.reads=[]
    def get(self,*mapping):self.reads.append(mapping);return self.items.get(mapping)
    def put(self,*args):self.items[args[:-1]]=args[-1]

class CredentialStore(unittest.TestCase):
    def test_mapping_separates_source_tenant_actor_and_native_account(self):
        base=('slack','tenant','eng_b','UEMP')
        self.assertEqual(item_key(*base),item_key(*base))
        for change in [('jira','tenant','eng_b','UEMP'),('slack','other','eng_b','UEMP'),
                       ('slack','tenant','eng_a','UEMP'),('slack','tenant','eng_b','UOTHER')]:
            self.assertNotEqual(item_key(*base),item_key(*change))
        with self.assertRaises(ValueError):item_key('slack','tenant','eng_b','bad\naccount')
    def test_only_not_found_is_missing_denial_never_falls_back(self):
        store=object.__new__(MacKeychain);store.sec=Mock();store.cf=Mock()
        store.sec.SecKeychainFindGenericPassword.return_value=-25300
        self.assertIsNone(store.get('slack','tenant','eng_b','UEMP'))
        for status in (-25293,-25308,-50):
            store.sec.SecKeychainFindGenericPassword.return_value=status
            with self.assertRaises(KeychainUnavailable):store.get('slack','tenant','eng_b','UEMP')
    def test_native_write_failure_never_becomes_success(self):
        store=object.__new__(MacKeychain);store.sec=Mock();store.cf=Mock()
        store.sec.SecKeychainAddGenericPassword.return_value=-25293
        with self.assertRaises(KeychainUnavailable):store.put('slack','tenant','eng_b','UEMP','fixture-only')
        store.sec.SecKeychainItemModifyAttributesAndData.assert_not_called()
    def test_replace_one_does_not_delete_or_request_other_credentials(self):
        store=MemoryStore();store.put('jira','tenant','eng_b','native','fixture-jira')
        store.put('slack','tenant','eng_b','UEMP','fixture-slack')
        replacement=ReplaceOne(store,'jira')
        self.assertIsNone(replacement.get('jira','tenant','eng_b','native'))
        self.assertEqual(replacement.get('slack','tenant','eng_b','UEMP'),'fixture-slack')
        self.assertEqual(store.get('jira','tenant','eng_b','native'),'fixture-jira')
    def test_later_oauth_failure_preserves_saved_source_and_next_start_does_not_prompt_again(self):
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as folder:
            path,_,_=test_bundle_oauth.BundleOAuth().config(folder);store=MemoryStore()
            with patch('brain.drive_oauth.load_client',return_value=DesktopClient('synthetic.apps.googleusercontent.com','fixture')), \
                 patch('scripts.slack_query.hidden_token',return_value=Delegation('UEMP','Bearer fixture')) as prompt, \
                 patch('scripts.drive_query.complete_oauth_reader',side_effect=SourceUnavailable()),redirect_stdout(io.StringIO()):
                for _ in range(2):
                    with self.assertRaises(SourceUnavailable):load_reader(path,'eng_b',oauth_client='fixture',credential_store=store)
                self.assertEqual(prompt.call_count,1)
            self.assertEqual(len(store.items),1)
    def test_bad_bundle_never_reads_keychain(self):
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            path,_,_=test_bundle_oauth.BundleOAuth().config(folder)
            config=json.loads(path.read_text());config['identity_mapping_reviewed']=False;path.write_text(json.dumps(config))
            store=MemoryStore()
            with self.assertRaises(ValueError):load_reader(path,'eng_b',credential_store=store)
            self.assertEqual(store.reads,[])

class PersistentDrive(unittest.TestCase):
    def test_offline_opt_in_keeps_fixed_scope_and_requires_refresh_token(self):
        from urllib.parse import parse_qs,urlsplit,urlencode
        client=DesktopClient('fixture.apps.googleusercontent.com','fixture-secret')
        flow=Consent(client,12345,offline=True);q=parse_qs(urlsplit(flow.url('fixture@example.com')).query)
        self.assertEqual(q['access_type'],['offline']);self.assertEqual(q['scope'],[SCOPE])
        self.assertEqual(q['include_granted_scopes'],['false'])
        flow.callback('/oauth/callback?'+urlencode({'state':flow.state,'code':'fixture','iss':ISSUER}),'127.0.0.1:12345')
        transport=Mock();transport.exchange.return_value=(200,{'token_type':'Bearer','scope':SCOPE,'expires_in':3600,'access_token':'fixture-access','refresh_token':'fixture-refresh'})
        self.assertEqual(flow.exchange(transport),{'access_token':'fixture-access','refresh_token':'fixture-refresh'})
    def test_refresh_denied_or_expanded_scope_cannot_become_access(self):
        client=DesktopClient('fixture.apps.googleusercontent.com','fixture-secret');transport=Mock()
        transport.exchange.return_value=(400,{'error':'invalid_grant','error_description':'never-show-this'})
        with self.assertRaises(ReauthorizationRequired) as e:refresh_access(client,'fixture-refresh',transport=transport)
        self.assertNotIn('never-show-this',str(e.exception))
        transport.exchange.return_value=(200,{'token_type':'Bearer','scope':SCOPE+' other','expires_in':3600,'access_token':'fixture-access'})
        with self.assertRaises(SourceUnavailable):refresh_access(client,'fixture-refresh',transport=transport)
    def test_reuse_still_verifies_native_identity_and_never_prompts(self):
        from scripts.drive_query import complete_oauth_reader
        reader=Mock();reader.tenant='tenant';reader.delegations={};store=MemoryStore()
        client=DesktopClient('fixture.apps.googleusercontent.com','fixture-secret')
        store.put('drive','tenant','eng_b',client.client_id+'|fixture@example.com','fixture-refresh')
        config={'oauth_operator':{'email':'fixture@example.com'}}
        with patch('brain.drive_oauth.refresh_access',return_value='fixture-access'), \
             patch('brain.drive_oauth.verify_account',return_value=Delegation('NATIVE','Bearer fixture-access')) as verify, \
             patch('brain.drive_oauth.authorize') as consent:
            complete_oauth_reader(reader,config,'unused','eng_b',client=client,credential_store=store)
            verify.assert_called_once_with('fixture-access','fixture@example.com',reader.transport)
            consent.assert_not_called()
        self.assertEqual(reader.delegations['eng_b'].account_id,'NATIVE')
    def test_wrong_native_identity_never_saves_new_refresh(self):
        from scripts.drive_query import complete_oauth_reader
        reader=Mock();reader.tenant='tenant';reader.delegations={};store=MemoryStore()
        client=DesktopClient('fixture.apps.googleusercontent.com','fixture-secret')
        with patch('brain.drive_oauth.authorize',return_value={'access_token':'fixture-access','refresh_token':'fixture-refresh'}), \
             patch('brain.drive_oauth.verify_account',side_effect=SourceUnavailable()):
            with self.assertRaises(SourceUnavailable):complete_oauth_reader(reader,{'oauth_operator':{'email':'fixture@example.com'}},'unused','eng_b',client=client,credential_store=store)
        self.assertEqual(store.items,{});self.assertEqual(reader.delegations,{})
