import contextlib
import io
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from brain.operator_web import OperatorApp
from brain.server import create_server
from brain.store import Store
from scripts.slack_query import load_reader, hidden_token
import test_http
from test_slack import SlackHTTP, reader, ROOT


class SlackConfiguration(unittest.TestCase):
    def config(self,folder):
        path=Path(folder)/'config.json'
        path.write_text(json.dumps({'approved_synthetic_only':True,'site':'https://test.slack.com',
            'tenant':'pilot','team_id':'T123','channels':{'C123':'private'},'messages':{ROOT:None},
            'delegations':{'eng_b':{'account_id':'UEMP','authorization_env':'AIBANG2_SLACK_ENG_B'}}}))
        return path

    def test_hidden_token_once_without_email_or_file_writes(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{},clear=True), \
             patch('scripts.slack_query.sys.stdin.isatty',return_value=True), \
             patch('scripts.slack_query.getpass.getpass',return_value='synthetic-token') as prompt:
            path=self.config(folder);before=path.read_bytes();r=load_reader(path,'eng_b')
            prompt.assert_called_once();self.assertEqual(path.read_bytes(),before)
            self.assertEqual(list(Path(folder).iterdir()),[path]);self.assertEqual(dict(os.environ),{})
            self.assertNotIn('synthetic-token',repr(r.delegations['eng_b']))

    def test_no_tty_or_echo_warning_never_falls_back(self):
        import getpass
        with patch('scripts.slack_query.sys.stdin.isatty',return_value=False), \
             patch('scripts.slack_query.getpass.getpass') as prompt:
            with self.assertRaises(ValueError):hidden_token('UEMP')
            prompt.assert_not_called()
        with patch('scripts.slack_query.sys.stdin.isatty',return_value=True), \
             patch('scripts.slack_query.getpass.getpass',side_effect=getpass.GetPassWarning):
            with self.assertRaises(getpass.GetPassWarning):hidden_token('UEMP')

    def test_inline_secret_wrong_namespace_and_unverified_user_fail_before_prompt(self):
        with tempfile.TemporaryDirectory() as folder:
            path=self.config(folder);baseline=json.loads(path.read_text())
            for change in [{'authorization':'secret-test'},{'authorization_env':'AIBANG2_JIRA_ENG_B'},
                           {'account_id':'REPLACE_WITH_VERIFIED_USER_ID'}]:
                config=json.loads(json.dumps(baseline));config['delegations']['eng_b'].update(change)
                path.write_text(json.dumps(config))
                with patch('scripts.slack_query.hidden_token') as prompt:
                    with self.assertRaises(ValueError):load_reader(path,'eng_b')
                    prompt.assert_not_called()

    def test_default_operator_cli_never_loads_slack_config_or_credentials(self):
        from brain.operator_web import main
        with contextlib.redirect_stdout(io.StringIO()),patch('scripts.slack_query.load_reader') as load:
            self.assertEqual(main(['--source','slack','--config','missing']),2)
            load.assert_not_called()


class SlackOperatorHTTP(unittest.TestCase):
    request=test_http.HTTP.request
    def setUp(self):
        self.transport=SlackHTTP();self.app=OperatorApp(reader(self.transport),Store(),'eng_b')
        self.server=create_server(self.app);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start();self.cookie='';self.csrf=''
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.app.store.db.close()
    def login(self):
        status,body=self.request('/api/operator/login',{'ticket':self.app.bootstrap_ticket()})
        self.assertEqual(status,200);self.csrf=body['csrf']
    def test_web_session_reuses_token_and_checks_slack_identity_on_every_query(self):
        self.login()
        with patch('scripts.slack_query.hidden_token') as prompt:
            for _ in range(2):
                self.app.sessions[next(iter(self.app.sessions))]['last_query']=0
                before=len(self.transport.calls);status,answer=self.request('/api/query',{'question':'retry safeguards'})
                self.assertEqual(status,200);self.assertEqual(answer['mode'],'slack_mock_http_fake_model')
                self.assertTrue(any(u.endswith('/auth.test') for u in self.transport.calls[before:]))
                self.assertNotIn('Bearer',json.dumps(answer))
            prompt.assert_not_called()
    def test_private_revocation_in_same_browser_session_protects_history_export_and_preview(self):
        self.login();first=self.request('/api/query',{'question':'retry safeguards'})[1]
        self.transport.channel['is_member']=False
        self.app.sessions[next(iter(self.app.sessions))]['last_query']=0
        next_answer=self.request('/api/query',{'question':'retry safeguards'})[1]
        self.assertEqual(next_answer['evidence'],[]);self.assertEqual(self.app.engine.model.calls[-1]['evidence'],[])
        for path in ['/api/history','/api/export/'+first['request_id']]:
            if path.startswith('/api/export/'):
                self.assertEqual(self.request(path)[0],404)
                continue
            result=self.request(path)[1];self.assertNotIn('follow-up',json.dumps(result))
            self.assertTrue(any(r.get('unavailable') for r in result['history']))
        self.assertEqual(self.request('/api/evidence/'+first['evidence'][0]['evidence_id']),
                         self.request('/api/evidence/missing@1'))
