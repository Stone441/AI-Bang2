import copy
import hashlib
import json
import unittest
from unittest.mock import patch, Mock
from email.message import Message
from urllib.parse import urlsplit, parse_qs

from brain.drive import DriveReader, DriveTransport, BASE
from brain.confluence import Delegation, SourceUnavailable
from brain.contracts import Actor
from brain.store import Store
from brain.delegated_query import DelegatedQueryPilot


class DriveHTTP:
    def __init__(self):
        self.calls=[];self.status=200;self.media_status=200;self.after=None;self.metadata_reads=0
        self.identity={'user':{'me':True,'permissionId':'employee'}}
        self.payload=b'SYNTHETIC: payment-service pilot approved; general release NOT approved.'
        self.metadata={'id':'FILE1','name':'Synthetic release approval.txt','mimeType':'text/plain',
            'version':'1','modifiedTime':'2026-10-05T00:00:00Z','trashed':False,'parents':['FOLDER1'],
            'spaces':['drive'],'size':str(len(self.payload)),
            'md5Checksum':hashlib.md5(self.payload).hexdigest(),'headRevisionId':'REV1',
            'capabilities':{'canDownload':True}}
    def get(self,url,authorization):
        self.calls.append(url)
        if '/about?' in url:return 200,copy.deepcopy(self.identity)
        self.metadata_reads+=1
        if self.status!=200:return self.status,None
        if self.after and self.metadata_reads>1:
            if isinstance(self.after,int):return self.after,None
            return 200,copy.deepcopy(self.after)
        return 200,copy.deepcopy(self.metadata)
    def media(self,native,authorization):
        self.calls.append('media:'+native);return self.media_status,self.payload


def reader(transport):
    return DriveReader('pilot',{'FILE1':'FOLDER1'}, {'eng_b':Delegation('employee','Bearer synthetic-token')},transport)


class DriveBoundary(unittest.TestCase):
    def setUp(self):self.transport=DriveHTTP();self.reader=reader(self.transport);self.actor=Actor('eng_b','pilot')
    def test_exact_file_content_revision_and_canonical_link(self):
        d,c=self.reader.read(self.actor,'FILE1');self.assertEqual(d.result,'allow')
        self.assertEqual(c['text'],self.transport.payload.decode());self.assertEqual(c['version'],1)
        self.assertEqual(c['locator']['revision_id'],'REV1')
        self.assertEqual(c['source_url'],'https://drive.google.com/file/d/FILE1/view')
        self.assertEqual(len(self.transport.calls),4)
        self.assertEqual(parse_qs(urlsplit(self.transport.calls[0]).query)['fields'],['user(permissionId,me)'])
    def test_wrong_identity_cannot_read_metadata_or_content(self):
        for identity in [{'user':{'me':True,'permissionId':'admin'}},{'user':{'me':False,'permissionId':'employee'}},{}]:
            self.transport.identity=identity;self.transport.calls=[]
            self.assertEqual(self.reader.read(self.actor,'FILE1')[0].result,'unknown')
            self.assertEqual(len(self.transport.calls),1)
    def test_unmapped_actor_tenant_or_file_never_network(self):
        for actor,native in [(Actor('eng_b','other'),'FILE1'),(Actor('ops','pilot'),'FILE1'),(self.actor,'FILE2')]:
            self.assertEqual(self.reader.read(actor,native)[0].result,'unknown')
        self.assertEqual(self.transport.calls,[])
    def test_native_denial_and_unknown_are_distinct(self):
        for status in (403,404,401,429,500):
            self.transport.status=status;self.transport.calls=[]
            self.assertEqual(self.reader.read(self.actor,'FILE1')[0].result,'deny' if status in (403,404) else 'unknown')
            self.assertFalse(any(c.startswith('media:') for c in self.transport.calls))
    def test_trashed_or_download_restricted_stops_before_body(self):
        for change in [{'trashed':True},{'capabilities':{'canDownload':False}}]:
            t=DriveHTTP();t.metadata.update(change)
            self.assertEqual(reader(t).read(self.actor,'FILE1')[0].result,'deny')
            self.assertEqual(len(t.calls),2)
    def test_unsupported_type_parent_shared_drive_and_missing_metadata_fail_closed(self):
        for change in [{'mimeType':'application/vnd.google-apps.document'},{'mimeType':'application/vnd.google-apps.shortcut'},
                       {'parents':['OTHER']},{'driveId':'SHARED'},{'spaces':['appDataFolder']},
                       {'version':True},{'version':'9223372036854775808'},{'size':'1000001'},
                       {'capabilities':{}},{'modifiedTime':'2026-10-05'},{'headRevisionId':None},{'md5Checksum':'bad'}]:
            t=DriveHTTP();t.metadata.update(change)
            self.assertEqual(reader(t).read(self.actor,'FILE1')[0].result,'unknown')
            self.assertEqual(len(t.calls),2)
    def test_edit_version_denies_old_revision_before_body(self):
        self.transport.metadata['version']='2'
        self.assertEqual(self.reader.read(self.actor,'FILE1',1)[0].result,'deny')
        self.assertFalse(any(c.startswith('media:') for c in self.transport.calls))
    def test_body_checksum_size_invalid_utf8_or_control_character_fails_closed(self):
        for payload in [b'changed',b'\xff',b'control\x00']:
            t=DriveHTTP();t.payload=payload
            if payload!=b'changed':
                t.metadata.update(size=str(len(payload)),md5Checksum=hashlib.md5(payload).hexdigest())
            self.assertEqual(reader(t).read(self.actor,'FILE1')[0].result,'unknown')
    def test_body_and_post_read_revocation_never_release_content(self):
        for step in ('media','after'):
            t=DriveHTTP()
            if step=='media':t.media_status=403
            else:t.after=403
            d,c=reader(t).read(self.actor,'FILE1');self.assertEqual(d.result,'deny');self.assertIsNone(c)
    def test_concurrent_edit_does_not_mix_versions(self):
        self.transport.after=dict(self.transport.metadata,version='2')
        d,c=self.reader.read(self.actor,'FILE1');self.assertEqual(d.result,'unknown');self.assertIsNone(c)
    def test_no_arbitrary_url_or_implicit_file_list(self):
        for files in [{'https://evil.test':'FOLDER1'},{'FILE1':'../folder'},{}]:
            with self.assertRaises(ValueError):DriveReader('pilot',files,{})
    def test_transport_media_is_fixed_origin_bounded_and_utf8_only(self):
        t=DriveTransport(max_bytes=2);response=Mock();response.status=200;response.headers=Message()
        response.headers['Content-Type']='text/plain; charset=utf-8';response.read.return_value=b'abc'
        context=Mock();context.__enter__=Mock(return_value=response);context.__exit__=Mock(return_value=False)
        with patch.object(t.opener,'open',return_value=context) as opened:
            with self.assertRaises(SourceUnavailable):t.media('FILE1','Bearer synthetic-token')
            req=opened.call_args.args[0];self.assertEqual(req.full_url,BASE+'/files/FILE1?alt=media')
            self.assertEqual(response.read.call_args.args,(3,))
        with patch.object(t.opener,'open') as opened:
            with self.assertRaises(SourceUnavailable):t.media('../evil','Bearer synthetic-token')
            opened.assert_not_called()


class DriveEngine(unittest.TestCase):
    def setUp(self):
        self.transport=DriveHTTP();self.store=Store();self.addCleanup(self.store.db.close)
        self.pilot=DelegatedQueryPilot({'drive':reader(self.transport)},self.store);self.actor=Actor('eng_b','pilot')
    def test_revocation_protects_followup_history_preview_and_model_retains_index(self):
        first=self.pilot.query(self.actor,'payment-service pilot approved')
        self.assertTrue(first['evidence']);self.transport.status=403
        follow=self.pilot.query(self.actor,'payment-service pilot approved',first['request_id'])
        self.assertEqual(follow['evidence'],[]);self.assertEqual(self.pilot.engine.model.calls[-1]['evidence'],[])
        self.assertTrue(self.pilot.history(self.actor,first['request_id'])[0]['unavailable'])
        with self.assertRaises(PermissionError):self.pilot.evidence(self.actor,first['evidence'][0]['evidence_id'])
        self.assertEqual(self.store.get('drive:FILE1')['version'],1)
    def test_incremental_edit_switches_only_file_and_invalidates_old_history(self):
        first=self.pilot.query(self.actor,'payment-service pilot')
        self.transport.metadata.update(version='2',headRevisionId='REV2')
        second=self.pilot.query(self.actor,'payment-service pilot')
        self.assertEqual(second['evidence'][0]['version'],2)
        self.assertTrue(self.pilot.history(self.actor,first['request_id'])[0]['unavailable'])
    def test_late_revocation_before_model_never_sends_old_file(self):
        check=self.pilot.authority.check_read
        def revoke(actor,resource):self.transport.status=403;return check(actor,resource)
        with patch.object(self.pilot.authority,'check_read',side_effect=revoke):
            result=self.pilot.query(self.actor,'payment-service pilot')
        self.assertEqual(result['evidence'],[])
        self.assertFalse(any(c['evidence'] for c in self.pilot.engine.model.calls))


class FourSourceEngine(unittest.TestCase):
    def test_four_sources_share_query_and_drive_revoke_preserves_other_evidence(self):
        from test_confluence_query import SourceTransport
        from brain.confluence import ConfluenceReader
        from test_jira import JiraTransport, reader as jira_reader
        from test_slack import SlackHTTP, reader as slack_reader
        cf=ConfluenceReader('https://test.atlassian.net','pilot',['98564'],['123'],
                            {'eng_b':Delegation('employee','Bearer employee')},SourceTransport())
        drive=DriveHTTP();store=Store();self.addCleanup(store.db.close)
        pilot=DelegatedQueryPilot({'confluence':cf,'jira':jira_reader(JiraTransport()),
            'slack':slack_reader(SlackHTTP()),'drive':reader(drive)},store)
        actor=Actor('eng_b','pilot')
        first=pilot.query(actor,'runbook payment-service retry safeguards pilot')
        self.assertEqual({e['source'] for e in first['evidence']},{'confluence','jira','slack','drive'})
        self.assertEqual(first['mode'],'confluence_drive_jira_slack_mock_http_fake_model')
        drive.status=403
        second=pilot.query(actor,'runbook payment-service retry safeguards pilot')
        self.assertEqual({e['source'] for e in second['evidence']},{'confluence','jira','slack'})
        self.assertNotIn('general release NOT approved',json.dumps(pilot.engine.model.calls[-1]))
        self.assertTrue(pilot.history(actor,first['request_id'])[0]['unavailable'])
