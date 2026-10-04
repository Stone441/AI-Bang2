import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from brain.confluence import Delegation, SourceUnavailable
from brain.drive_oauth import DesktopClient
from scripts.operator_bundle import load_reader
import test_operator_bundle


class BundleOAuth(unittest.TestCase):
    def config(self, folder):
        path, slack, drive = test_operator_bundle.BundleConfiguration().config(folder)
        drive.write_text(json.dumps({'approved_synthetic_only':True,'tenant':'pilot','files':{'FILE1':'FOLDER1'},
            'oauth_operator':{'actor':'eng_b','email':'synthetic@example.com'},
            'oauth_client_id':'synthetic.apps.googleusercontent.com'}))
        return path, slack, drive

    def test_oauth_and_manual_sources_share_reviewed_actor_without_manual_drive_token(self):
        def complete(reader, config, client_path, actor, *, client=None):
            self.assertEqual(actor,'eng_b'); self.assertEqual(client.client_id,config['oauth_client_id'])
            reader.delegations[actor]=Delegation('employee','Bearer synthetic')
            return reader
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,{},clear=True), \
             patch('brain.drive_oauth.load_client',return_value=DesktopClient('synthetic.apps.googleusercontent.com','fixture')) as client, \
             patch('scripts.drive_query.complete_oauth_reader',side_effect=complete) as oauth, \
             patch('scripts.drive_query.hidden_token') as drive_prompt, \
             patch('scripts.slack_query.hidden_token',return_value=Delegation('UEMP','Bearer synthetic')) as slack_prompt, \
             contextlib.redirect_stdout(io.StringIO()):
            path,slack,drive=self.config(folder);before={p:p.read_bytes() for p in (path,slack,drive)}
            readers=load_reader(path,'eng_b',oauth_client='private-client.json')
            self.assertEqual(set(readers),{'drive','slack'})
            self.assertTrue(all('eng_b' in r.delegations for r in readers.values()))
            self.assertEqual(before,{p:p.read_bytes() for p in before})
            client.assert_called_once(); oauth.assert_called_once(); slack_prompt.assert_called_once()
            drive_prompt.assert_not_called()

    def test_all_mapping_and_tenant_errors_precede_private_client_and_input(self):
        with tempfile.TemporaryDirectory() as folder, patch('brain.drive_oauth.load_client') as client, \
             patch('scripts.drive_query.complete_oauth_reader') as oauth, \
             patch('scripts.slack_query.hidden_token') as slack_prompt:
            path,slack,drive=self.config(folder);base_drive=json.loads(drive.read_text());base_slack=json.loads(slack.read_text())
            for target,base,change in ((drive,base_drive,{'oauth_operator':{'actor':'eng_a','email':'synthetic@example.com'}}),
                                      (drive,base_drive,{'oauth_client_id':'https://untrusted.example'}),
                                      (slack,base_slack,{'tenant':'another'}),
                                      (slack,base_slack,{'delegations':{}})):
                target.write_text(json.dumps(dict(base,**change)))
                with self.assertRaises(ValueError):load_reader(path,'eng_b',oauth_client='private-client.json')
                target.write_text(json.dumps(base))
                client.assert_not_called(); oauth.assert_not_called(); slack_prompt.assert_not_called()

    def test_private_client_failure_precedes_other_source_prompts(self):
        with tempfile.TemporaryDirectory() as folder, patch('brain.drive_oauth.load_client',side_effect=ValueError('invalid')), \
             patch('scripts.slack_query.hidden_token') as prompt:
            path,_,_=self.config(folder)
            with self.assertRaises(ValueError):load_reader(path,'eng_b',oauth_client='private-client.json')
            prompt.assert_not_called()

    def test_missing_drive_or_denied_consent_never_becomes_partial_bundle(self):
        with tempfile.TemporaryDirectory() as folder, patch('brain.drive_oauth.load_client',return_value=DesktopClient('synthetic.apps.googleusercontent.com','fixture')), \
             patch('scripts.drive_query.complete_oauth_reader',side_effect=SourceUnavailable()), \
             patch('scripts.slack_query.hidden_token',return_value=Delegation('UEMP','Bearer synthetic')), \
             contextlib.redirect_stdout(io.StringIO()):
            path,_,_=self.config(folder)
            with self.assertRaises(SourceUnavailable):load_reader(path,'eng_b',oauth_client='private-client.json')
            config=json.loads(path.read_text());config['sources']={'confluence':'missing','jira':'missing'}
            path.write_text(json.dumps(config))
            with self.assertRaises(ValueError):load_reader(path,'eng_b',oauth_client='private-client.json')

    def test_operator_cli_routes_multi_oauth_and_verifies_all_native_identities(self):
        from brain.operator_web import main
        from brain.store import Store
        readers,transports=test_operator_bundle.setup_readers()
        store=Store(); server=MagicMock(); server.server_port=8087
        server.serve_forever.side_effect=KeyboardInterrupt
        with patch('brain.operator_web.create_server',return_value=server), \
             patch('brain.operator_web.Store',return_value=store), patch('brain.operator_web.os.chmod'), \
             patch('scripts.operator_bundle.load_reader',return_value=readers) as load, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--source','multi','--config','reviewed.json','--actor','eng_b',
                                   '--oauth-client','private-client.json','--live']),0)
        load.assert_called_once_with('reviewed.json',prompt_actor='eng_b',oauth_client='private-client.json')
        self.assertTrue(all(len(t.calls)==1 for t in transports.values()))
        self.assertEqual(server.application.actor.user_id,'eng_b')
