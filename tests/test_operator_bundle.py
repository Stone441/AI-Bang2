import contextlib
import io
import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from brain.confluence import ConfluenceReader, Delegation, SourceUnavailable
from brain.operator_web import OperatorApp, main
from brain.server import create_server
from brain.store import Store
from scripts.operator_bundle import load_reader
from test_confluence_query import SourceTransport
from test_jira import JiraTransport, reader as jira_reader
from test_slack import SlackHTTP, reader as slack_reader
from test_drive import DriveHTTP, reader as drive_reader
import test_slack_operator
import test_drive_operator
import test_http


def setup_readers():
    cf=SourceTransport();jira=JiraTransport();slack=SlackHTTP();drive=DriveHTTP()
    readers={'confluence':ConfluenceReader('https://test.atlassian.net','pilot',['98564'],['123'],
              {'eng_b':Delegation('employee','Bearer employee')},cf),
             'jira':jira_reader(jira),'slack':slack_reader(slack),'drive':drive_reader(drive)}
    return readers, {'confluence':cf,'jira':jira,'slack':slack,'drive':drive}


class BundleConfiguration(unittest.TestCase):
    def config(self,folder):
        root=Path(folder);(root/'slack').mkdir();(root/'drive').mkdir()
        slack=test_slack_operator.SlackConfiguration().config(root/'slack')
        drive=test_drive_operator.DriveConfiguration().config(root/'drive')
        path=root/'bundle.json'
        path.write_text(json.dumps({'approved_synthetic_only':True,'identity_mapping_reviewed':True,
            'sources':{'slack':str(slack.relative_to(root)),'drive':str(drive.relative_to(root))}}))
        return path,slack,drive

    def test_bundle_prompts_missing_secrets_once_without_saving_and_reuses_environment(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict(os.environ,{},clear=True), \
             patch('scripts.drive_query.hidden_token',return_value=Delegation('employee','Bearer fixture')) as drive, \
             patch('scripts.slack_query.hidden_token',return_value=Delegation('UEMP','Bearer fixture')) as slack, \
             contextlib.redirect_stdout(io.StringIO()):
            path,sp,dp=self.config(folder);before={p:p.read_bytes() for p in (path,sp,dp)}
            readers=load_reader(path,'eng_b');drive.assert_called_once();slack.assert_called_once()
            self.assertEqual(set(readers),{'drive','slack'})
            self.assertEqual(before,{p:p.read_bytes() for p in before})
            with patch.dict(os.environ,{'AIBANG2_DRIVE_ENG_B':'Bearer fixture','AIBANG2_SLACK_ENG_B':'Bearer fixture'}):
                load_reader(path,'eng_b')
            self.assertEqual(drive.call_count,1);self.assertEqual(slack.call_count,1)

    def test_invalid_later_config_or_tenant_rejected_before_any_prompt(self):
        with tempfile.TemporaryDirectory() as folder, \
             patch('scripts.drive_query.hidden_token') as drive,patch('scripts.slack_query.hidden_token') as slack:
            path,sp,dp=self.config(folder);baseline=json.loads(sp.read_text())
            for change in [{'tenant':'another'},{'delegations':{}},{'approved_synthetic_only':False}]:
                sp.write_text(json.dumps(dict(baseline,**change)))
                with self.assertRaises(ValueError):load_reader(path,'eng_b')
                drive.assert_not_called();slack.assert_not_called()

    def test_unreviewed_or_unsupported_bundle_and_no_live_cli_do_not_load_credentials(self):
        with tempfile.TemporaryDirectory() as folder:
            path,_,_=self.config(folder);baseline=json.loads(path.read_text())
            for change in [{'identity_mapping_reviewed':False},{'sources':{'unknown':'missing','drive':'missing'}},
                           {'sources':{'slack':'missing'}},{'secret':'not-allowed'}]:
                path.write_text(json.dumps(dict(baseline,**change)))
                with self.assertRaises(ValueError):load_reader(path,'eng_b')
        with contextlib.redirect_stdout(io.StringIO()),patch('scripts.operator_bundle.load_reader') as load:
            self.assertEqual(main(['--source','multi','--config','missing']),2);load.assert_not_called()


class BundleStartup(unittest.TestCase):
    def setUp(self):
        self.readers,self.transports=setup_readers();self.store=Store();self.addCleanup(self.store.db.close)

    def test_every_native_identity_verified_before_bootstrap_without_content(self):
        app=OperatorApp(self.readers,self.store,'eng_b')
        self.assertEqual(app.actor.tenant,'pilot');self.assertTrue(app.bootstrap_ticket())
        for transport in self.transports.values():self.assertEqual(len(transport.calls),1)
        self.assertEqual(self.store.resources(),[])

    def test_missing_mapping_wrong_source_and_cross_tenant_fail_before_network(self):
        for problem in ('mapping','tenant','source'):
            readers=dict(self.readers)
            if problem=='mapping':readers['drive'].delegations.clear()
            if problem=='tenant':readers['drive'].tenant='another'
            if problem=='source':readers['drive']=readers['jira']
            with self.assertRaises(ValueError):OperatorApp(readers,self.store,'eng_b')
            self.assertTrue(all(not t.calls for t in self.transports.values()))
            self.readers,self.transports=setup_readers()

    def test_native_identity_mismatch_does_not_issue_browser_ticket_or_read_content(self):
        self.transports['slack'].identity['user_id']='USUBSTITUTED'
        with self.assertRaises(SourceUnavailable):OperatorApp(self.readers,self.store,'eng_b')
        self.assertEqual(self.store.resources(),[])
        self.assertEqual(self.store.db.execute('select count(*) from runs').fetchone()[0],0)
        for transport in self.transports.values():self.assertEqual(len(transport.calls),1)


class BundleHTTP(unittest.TestCase):
    request=test_http.HTTP.request
    def setUp(self):
        readers,self.transports=setup_readers();self.app=OperatorApp(readers,Store(),'eng_b')
        self.server=create_server(self.app);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start();self.cookie='';self.csrf=''
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.app.store.db.close()
    def login(self):
        status,body=self.request('/api/operator/login',{'ticket':self.app.bootstrap_ticket()})
        self.assertEqual(status,200);self.csrf=body['csrf']
    def query(self,**extra):
        self.app.sessions[next(iter(self.app.sessions))]['last_query']=0
        status,result=self.request('/api/query',dict(question='runbook payment-service retry safeguards pilot',**extra))
        self.assertEqual(status,200);return result

    def test_one_verified_http_session_four_sources_and_single_source_revocation(self):
        self.login();first=self.query()
        self.assertEqual({e['source'] for e in first['evidence']},set(self.transports))
        self.assertEqual(first['mode'],'confluence_drive_jira_slack_mock_http_fake_model')
        drive_evidence=next(e for e in first['evidence'] if e['source']=='drive')
        self.transports['drive'].status=403
        second=self.query()
        self.assertEqual({e['source'] for e in second['evidence']},{'confluence','jira','slack'})
        self.assertFalse(any(e['source']=='drive' for e in self.app.engine.model.calls[-1]['evidence']))
        for path in ['/api/history','/api/export/'+first['request_id']]:
            if path.startswith('/api/export/'):
                self.assertEqual(self.request(path)[0],404)
                continue
            result=self.request(path)[1];self.assertNotIn('general release NOT approved',json.dumps(result))
            self.assertTrue(any(r.get('unavailable') for r in result['history']))
        self.assertEqual(self.request('/api/evidence/'+drive_evidence['evidence_id']),self.request('/api/evidence/missing@1'))

    def test_browser_cannot_select_actor_or_add_source_or_use_revoked_history_in_followup(self):
        self.login();first=self.query()
        for field in ('user_id','role','source'):
            self.assertEqual(self.request('/api/query',{'question':'runbook',field:'admin'})[0],400)
        self.transports['slack'].channel['is_member']=False
        second=self.query()
        self.assertEqual({e['source'] for e in second['evidence']},{'confluence','drive','jira'})
        self.assertFalse(any(e['source']=='slack' for e in self.app.engine.model.calls[-1]['evidence']))
        self.assertNotIn('Synthetic follow-up retry safeguards reply',json.dumps(self.app.engine.model.calls[-1]))
        self.assertTrue(self.app.pilot.history(self.app.actor,first['request_id'])[0]['unavailable'])
