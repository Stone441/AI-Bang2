"""Four-source discovery uses offline HTTP mocks, never actual account credentials."""
import copy
import hashlib
import io
import json
import unittest
from contextlib import redirect_stdout
from urllib.parse import urlsplit,parse_qs,urlencode
from urllib.error import HTTPError
from unittest.mock import Mock,patch

from brain.audit import verify_chain
from brain.confluence import ConfluenceReader,Delegation,JsonTransport,SourceRateLimited
from brain.contracts import Actor
from brain.delegated_query import DelegatedQueryPilot
from brain.discovery import ContainerDiscovery,AUTH017,SLACK_OLDEST,SLACK_TEAM
from brain.drive import DriveReader
from brain.jira import JiraReader
from brain.operator_web import main
from brain.slack import SlackReader
from brain.store import Store
from test_jira import document


class DiscoveryHTTP:
    def __init__(self,source):
        self.source=source;self.calls=[];self.pages=None;self.list_status=200;self.identity_ok=True
        self.fail_native=set();self.root=SLACK_OLDEST;self.newts='1791142153.000001';self.replyts='1791142154.000001'
        self.content={};self.channel={'id':AUTH017['slack'],'name':'synthetic-payments','context_team_id':SLACK_TEAM,
            'is_im':False,'is_mpim':False,'is_shared':False,'is_ext_shared':False,
            'is_pending_ext_shared':False,'is_private':True,'is_member':True}
        if source=='confluence':
            for i,word in [('98564','baseline'),('98565','novelty')]:
                self.content[i]={'id':i,'spaceId':AUTH017[source],'status':'current',
                    'title':'[SYNTHETIC] '+word,'version':{'number':1,'createdAt':'2026-10-06T00:00:00Z'},
                    'body':{'storage':{'representation':'storage','value':'<p>[SYNTHETIC] '+word+' payment-service discovery</p>'}}}
        elif source=='jira':
            for i,key,word in [('10004','KAN-4','baseline'),('10015','KAN-6','novelty')]:
                self.content[i]={'id':i,'key':key,'fields':{'project':{'id':AUTH017[source]},'summary':'[SYNTHETIC] '+word,
                    'description':document('[SYNTHETIC] '+word+' payment-service discovery'),
                    'status':{'name':'In Progress'},'assignee':None,'updated':'2026-10-06T00:00:00Z'}}
        elif source=='slack':
            for ts,word in [(self.root,'baseline'),(self.newts,'novelty')]:
                self.content[ts]={'ts':ts,'type':'message','text':'[SYNTHETIC] '+word+' payment-service discovery'}
        else:
            for i,word in [('FILE1','baseline'),('FILE2','novelty')]:
                self.content[i]=self.file(i,'[SYNTHETIC] '+word+' payment-service discovery')

    @staticmethod
    def file(native,text,version=1):
        payload=text.encode()
        return {'metadata':{'id':native,'name':'[SYNTHETIC] '+native,'mimeType':'text/plain','parents':[AUTH017['drive']],
            'version':str(version),'modifiedTime':'2026-10-06T00:00:00Z','trashed':False,'spaces':['drive'],
            'size':str(len(payload)),'md5Checksum':hashlib.md5(payload).hexdigest(),'headRevisionId':'REV'+str(version),
            'capabilities':{'canDownload':True}},'payload':payload}

    def get(self,url,authorization):
        self.calls.append(url);p=urlsplit(url);q=parse_qs(p.query);path=p.path
        if path.endswith('/user/current'):return 200,{'type':'known','accountId':'employee' if self.identity_ok else 'admin'}
        if path.endswith('/myself'):return 200,{'active':True,'accountType':'atlassian','accountId':'employee' if self.identity_ok else 'admin'}
        if path.endswith('/auth.test'):return 200,{'ok':True,'team_id':SLACK_TEAM,'user_id':'UEMP' if self.identity_ok else 'UADMIN'}
        if path.endswith('/about'):return 200,{'user':{'me':True,'permissionId':'employee' if self.identity_ok else 'admin'}}
        if path.endswith('/conversations.info'):return 200,{'ok':True,'channel':copy.deepcopy(self.channel)}
        listing=('/spaces/' in path or path.endswith('/search/jql') or path.endswith('/files') or
                 (path.endswith('/conversations.history') and q.get('latest') is None) or
                 (path.endswith('/conversations.replies') and q.get('latest') is None))
        if listing:
            if self.list_status!=200:return self.list_status,None
            if self.pages is not None:
                cursor=q.get('cursor',q.get('nextPageToken',q.get('pageToken',[''])))[0]
                return 200,copy.deepcopy(self.pages[cursor])
            if self.source=='confluence':return 200,{'results':[dict(v,body={}) for v in self.content.values()]}
            if self.source=='jira':return 200,{'issues':list(copy.deepcopy(self.content).values()),'isLast':True}
            if self.source=='drive':return 200,{'files':[copy.deepcopy(v['metadata']) for v in self.content.values()],'incompleteSearch':False}
            if path.endswith('/conversations.replies'):
                return 200,{'ok':True,'messages':[copy.deepcopy(v) for v in self.content.values() if v.get('thread_ts')==q['ts'][0] or v['ts']==q['ts'][0]]}
            return 200,{'ok':True,'messages':[copy.deepcopy(v) for v in self.content.values() if not v.get('thread_ts')]}
        native=q['oldest'][0] if self.source=='slack' else path.rsplit('/',1)[1]
        if native in self.fail_native:return 404,None
        if self.source=='slack':
            if native not in self.content:return 200,{'ok':True,'messages':[]}
            return 200,{'ok':True,'messages':[copy.deepcopy(self.content[native])]}
        if native not in self.content:return 404,None
        data=self.content[native]
        return 200,copy.deepcopy(data['metadata'] if self.source=='drive' else data)

    def media(self,native,authorization):
        self.calls.append('media:'+native)
        return (404,None) if native in self.fail_native else (200,self.content[native]['payload'])


def setup():
    transports={s:DiscoveryHTTP(s) for s in AUTH017}
    delegations={u:Delegation('employee','Bearer synthetic-not-a-secret') for u in ('eng_b','product_ops')}
    readers={
        'confluence':ConfluenceReader('https://test.atlassian.net','pilot',['98564'],[AUTH017['confluence']],delegations,transports['confluence']),
        'jira':JiraReader('https://test.atlassian.net','pilot',{'10004':'KAN-4'},[AUTH017['jira']],delegations,transports['jira']),
        'slack':SlackReader('https://test.slack.com','pilot',SLACK_TEAM,{AUTH017['slack']:'private'},
            {AUTH017['slack']+'/'+SLACK_OLDEST:None},{u:Delegation('UEMP','Bearer synthetic-not-a-secret') for u in delegations},transports['slack']),
        'drive':DriveReader('pilot',{'FILE1':AUTH017['drive']},delegations,transports['drive'])}
    store=Store();pilot=DelegatedQueryPilot(readers,store)
    return store,pilot,transports,readers


class DiscoveryBoundary(unittest.TestCase):
    def setUp(self):
        self.store,self.pilot,self.http,self.readers=setup();self.addCleanup(self.store.db.close)
        self.actor=Actor('eng_b','pilot');self.clock_value=0
        self.discovery=ContainerDiscovery(self.pilot,self.actor,clock=lambda:self.clock_value)

    def cycle(self):
        self.clock_value+=10000
        return self.discovery.run_once()

    def test_default_fixed_ids_then_four_source_discovery_becomes_answerable(self):
        self.assertEqual(self.pilot.query(self.actor,'novelty')['evidence'],[])
        result=self.cycle()
        self.assertEqual({r['status'] for r in result.values()},{'complete'})
        self.assertTrue(all(r['answerable_at'] is None for r in result.values()))
        answer=self.pilot.query(self.actor,'novelty')
        self.assertEqual({e['source'] for e in answer['evidence']},set(AUTH017))
        self.assertTrue(verify_chain(self.pilot.audit.export())['valid'])
        self.assertEqual(self.readers['confluence'].page_ids,frozenset(['98564']))
        self.assertEqual(self.readers['drive'].native_ids,frozenset(['FILE1']))
        for e in answer['evidence']:self.assertEqual(self.pilot.evidence(self.actor,e['evidence_id'])['text'],e['text'])
        for e in answer['evidence']:
            phases={v['payload']['phase'] for v in self.pilot.audit.export() if v['event_type']=='authorization_decided' and v['payload']['resource_id']==e['resource_id']}
            self.assertTrue({'source_refresh','before_model','model_dispatch','before_dispatch'}<=phases)

    def test_product_ops_cannot_inherit_discovery_even_with_native_read_token(self):
        self.cycle()
        self.assertEqual(self.pilot.query(Actor('product_ops','pilot'),'novelty')['evidence'],[])
        rid='confluence:98565';decision=self.pilot.authority.check_read(Actor('product_ops','pilot'),rid)
        self.assertEqual(decision.result,'unknown')

    def test_updates_deletes_and_old_history_without_rebuilding_other_sources(self):
        self.cycle();old=self.pilot.query(self.actor,'novelty');cf=next(e for e in old['evidence'] if e['source']=='confluence')
        other=self.store.get('jira:10015')['version']
        page=self.http['confluence'].content['98565'];page['version']['number']=2
        page['body']['storage']['value']='<p>[SYNTHETIC] changed novelty</p>'
        self.http['drive'].fail_native.add('FILE2')
        self.cycle()
        self.assertEqual(self.store.get('confluence:98565')['version'],2)
        self.assertEqual(self.store.get('jira:10015')['version'],other)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM versions WHERE id=?',('confluence:98565',)).fetchone()[0],2)
        self.assertIsNone(self.store.get('drive:FILE2'))
        with self.assertRaises(PermissionError):self.pilot.evidence(self.actor,cf['evidence_id'])
        self.assertTrue(self.pilot.history(self.actor,old['request_id'])[0]['unavailable'])
        self.assertNotIn('drive',{e['source'] for e in self.pilot.query(self.actor,'novelty')['evidence']})

    def test_pagination_uses_fixed_endpoint_and_rejects_external_or_changed_container_next(self):
        t=self.http['confluence'];rows=list(t.content.values());endpoint='/wiki/api/v2/spaces/131227/pages'
        t.pages={'':{'results':[rows[0]],'_links':{'next':endpoint+'?cursor=page2&limit=50&status=current'}},'page2':{'results':[rows[1]]}}
        self.assertEqual(self.cycle()['confluence']['list_pages'],2)
        before=self.discovery.last['confluence']['last_successful_checkpoint_at']
        for url in ['https://evil.example'+endpoint+'?cursor=x',endpoint.replace('131227','999')+'?cursor=x',endpoint+'?cursor=x&body-format=storage']:
            t.pages['']['_links']['next']=url
            report=self.cycle()['confluence']
            self.assertEqual(report['status'],'failed');self.assertEqual(report['reason'],'invalid_cursor')
            self.assertEqual(report['last_successful_checkpoint_at'],before)
        self.assertFalse(any('evil.example' in call for call in t.calls))

    def test_wrong_container_identity_channel_and_scope_fail_closed(self):
        for source in AUTH017:
            self.http[source].identity_ok=False
        report=self.cycle();self.assertTrue(all(r['status']=='failed' for r in report.values()))
        self.assertEqual(self.store.resources(),[])
        for source in AUTH017:self.assertEqual(len(self.http[source].calls),1)
        for actor,scope in [(Actor('product_ops','pilot'),AUTH017),(Actor('eng_b','other'),AUTH017),(self.actor,dict(AUTH017,drive='OTHER'))]:
            with self.assertRaises(ValueError):ContainerDiscovery(self.pilot,actor,scope=scope)
        self.http['slack'].identity_ok=True;self.http['slack'].channel['is_shared']=True
        self.assertEqual(self.cycle()['slack']['reason'],'channel_unavailable')

    def test_title_marker_is_not_synthetic_provenance_and_non_candidates_no_body(self):
        t=self.http['confluence'];t.content['98565']['body']['storage']['value']='<p>private raw body</p>'
        t.content['98566']=dict(copy.deepcopy(t.content['98565']),id='98566',title='Unmarked metadata')
        self.cycle()
        self.assertIsNone(self.store.get('confluence:98565'))
        self.assertNotIn('98565',self.pilot.authority.discovered_ids['eng_b']['confluence'])
        self.assertFalse(any('/pages/98566' in call for call in t.calls))
        answer=self.pilot.query(self.actor,'private raw body');self.assertEqual(answer['evidence'],[])
        self.assertNotIn('private raw body',json.dumps([call['evidence'] for call in self.pilot.engine.model.calls]))
        self.assertNotIn('private raw body',json.dumps(self.discovery.last))

    def test_drive_incomplete_and_cross_parent_never_publish_or_advance_checkpoint(self):
        t=self.http['drive'];t.pages={'':{'files':[],'incompleteSearch':True}}
        self.assertEqual(self.cycle()['drive']['reason'],'incomplete_search')
        metadata=copy.deepcopy(t.content['FILE2']['metadata']);metadata['parents']=['OTHER']
        t.pages={'':{'files':[metadata]}}
        self.assertEqual(self.cycle()['drive']['reason'],'container_mismatch')
        self.assertIsNone(self.store.get('drive:FILE2'))
        self.assertFalse(any(call.startswith('media:') for call in t.calls))

    def test_jira_project_substitution_and_comment_scope_never_discovered(self):
        t=self.http['jira'];data=copy.deepcopy(t.content['10015']);data['fields']['project']['id']='999'
        t.pages={'':{'issues':[data],'isLast':True}}
        self.assertEqual(self.cycle()['jira']['reason'],'container_mismatch')
        self.assertFalse(any('/issue/10015' in call for call in t.calls))
        self.assertFalse(any('/comment/' in call for call in t.calls))

    def test_slack_thread_requires_current_synthetic_parent_and_exact_reply_reads(self):
        t=self.http['slack'];t.content[t.newts]['reply_count']=1
        t.content[t.replyts]={'ts':t.replyts,'thread_ts':t.newts,'type':'message','text':'[SYNTHETIC] thread novelty'}
        self.cycle();native=AUTH017['slack']+'/'+t.replyts
        self.assertIn(native,self.pilot.authority.discovered_ids['eng_b']['slack'])
        self.assertEqual(self.pilot.authority.readers['slack'].messages[native],t.newts)
        self.assertTrue(any('conversations.replies' in c for c in t.calls))
        t.content[t.newts]['text']='unmarked parent';self.cycle()
        self.assertEqual(self.discovery.last['slack']['reason'],'parent_unavailable')
        self.assertNotIn('thread novelty',json.dumps(self.pilot.query(self.actor,'thread novelty')['evidence']))

    def test_rate_limit_backoff_restart_and_checkpoint_do_not_skip_failures(self):
        self.cycle();before=self.discovery.last['jira']['last_successful_checkpoint_at']
        self.http['jira'].list_status=429;self.clock_value+=60;report=self.discovery.run_once()['jira']
        self.assertEqual(report['reason'],'rate_limited');self.assertEqual(report['last_successful_checkpoint_at'],before)
        count=len(self.http['jira'].calls);self.discovery.run_once();self.assertEqual(len(self.http['jira'].calls),count)
        self.http['jira'].list_status=200;self.clock_value+=report['retry_after_seconds'];self.discovery.run_once()
        self.assertEqual(self.discovery.last['jira']['status'],'complete')
        fresh=DelegatedQueryPilot(self.readers,self.store)
        restarted=ContainerDiscovery(fresh,self.actor,clock=lambda:0)
        self.assertEqual(fresh.query(self.actor,'novelty')['evidence'],[])
        restarted.run_once();self.assertEqual({e['source'] for e in fresh.query(self.actor,'novelty')['evidence']},set(AUTH017))

    def test_version_collision_rolls_back_catalog_and_publication(self):
        self.cycle();old=self.store.get('confluence:98565');checkpoint=self.discovery.last['confluence']['last_successful_checkpoint_at']
        self.http['confluence'].content['98565']['body']['storage']['value']='<p>[SYNTHETIC] mutated unchanged version</p>'
        result=self.cycle()['confluence']
        self.assertEqual(result['reason'],'version_collision')
        self.assertEqual(self.store.get('confluence:98565')['text'],old['text'])
        self.assertEqual(result['last_successful_checkpoint_at'],checkpoint)
        with self.assertRaisesRegex(ValueError,'Content version collision'):self.pilot.query(self.actor,'novelty')

    def test_bounded_object_backlog_rotates_and_never_claims_complete(self):
        t=self.http['confluence']
        for i in range(99000,99110):
            page=copy.deepcopy(t.content['98565']);page['id']=str(i);t.content[str(i)]=page
        rows=list(t.content.values())
        t.pages={'':{'results':rows[:50],'_links':{'next':'/wiki/api/v2/spaces/131227/pages?cursor=p2'}},
                 'p2':{'results':rows[50:100],'_links':{'next':'/wiki/api/v2/spaces/131227/pages?cursor=p3'}},
                 'p3':{'results':rows[100:]}}
        report=self.cycle()['confluence']
        self.assertEqual(report['status'],'backlog');self.assertEqual(report['exact_read_attempts'],100)
        self.assertIsNone(report['last_successful_checkpoint_at'])
        self.assertIsNone(self.store.get('confluence:99109'))
        self.cycle();self.assertIsNotNone(self.store.get('confluence:99109'))
        self.assertEqual(self.discovery.last['confluence']['status'],'backlog')

    def test_page_cap_cursor_loop_and_audit_failure_cannot_advance_checkpoint(self):
        t=self.http['confluence'];t.pages={'':{'results':[],'_links':{'next':'/wiki/api/v2/spaces/131227/pages?cursor=p1'}}}
        for i in range(1,11):t.pages['p'+str(i)]={'results':[],'_links':{'next':'/wiki/api/v2/spaces/131227/pages?cursor=p'+str(i+1)}}
        result=self.cycle()['confluence']
        self.assertEqual(result['reason'],'page_backlog');self.assertEqual(result['list_pages'],10)
        self.assertIsNone(result['last_successful_checkpoint_at'])
        t.pages['p1']['_links']['next']='/wiki/api/v2/spaces/131227/pages?cursor=p1'
        self.assertEqual(self.cycle()['confluence']['reason'],'cursor_loop')
        t.pages=None;self.pilot.audit.fail=True
        with self.assertRaises(RuntimeError):self.cycle()
        self.assertIsNone(self.store.get('confluence:98565'))
        row=self.store.db.execute("SELECT body FROM discovery_state WHERE source='confluence'").fetchone()
        self.assertIsNone(json.loads(row[0])['last_successful_checkpoint_at'])

    def test_unknown_exact_read_disables_known_resource_without_overwriting_old_version(self):
        self.cycle();old=self.store.get('drive:FILE2');checkpoint=self.discovery.last['drive']['last_successful_checkpoint_at']
        transport=self.http['drive'];original=transport.get
        def unavailable(url,authorization):
            if '/files/FILE2?' in url:return 500,None
            return original(url,authorization)
        with patch.object(transport,'get',side_effect=unavailable):
            result=self.cycle()['drive']
            self.assertEqual(result['reason'],'native_read_unknown')
            self.assertIsNone(self.store.get('drive:FILE2'))
            self.assertEqual(result['last_successful_checkpoint_at'],checkpoint)
            self.assertFalse(any(e['source']=='drive' for e in self.pilot.query(self.actor,'novelty')['evidence']))
        self.cycle();self.assertEqual(self.store.get('drive:FILE2')['version'],old['version'])

    def test_poller_lifecycle_stops_before_store_close_and_keeps_queries_serial(self):
        import threading
        ready=threading.Event();original=self.discovery.run_once
        def cycle():
            result=original();ready.set();return result
        with patch.object(self.discovery,'run_once',side_effect=cycle):
            self.discovery.start()
            self.assertTrue(ready.wait(2));self.discovery.close()
        self.assertFalse(self.discovery.thread.is_alive())
        self.assertEqual({e['source'] for e in self.pilot.query(self.actor,'novelty')['evidence']},set(AUTH017))

    def test_cli_opt_in_invalid_identity_or_single_source_before_credentials(self):
        for args in [[],['--source','multi','--actor','product_ops']]:
            with redirect_stdout(io.StringIO()),patch('brain.operator_web.create_server') as create:
                self.assertEqual(main(['--config','missing','--live','--discovery-auth017',*args]),2)
                create.assert_not_called()

    def test_original_index_time_stays_stable_and_native_versions_cannot_regress(self):
        self.cycle();old=self.store.get('confluence:98565')
        self.pilot.query(self.actor,'novelty');self.cycle()
        self.assertEqual(self.store.get('confluence:98565')['indexed_at'],old['indexed_at'])
        page=self.http['confluence'].content['98565'];page['version']['number']=2
        page['body']['storage']['value']='<p>[SYNTHETIC] newer novelty</p>';self.cycle()
        page['version']['number']=1;page['body']['storage']['value']=old['text']
        self.assertEqual(self.cycle()['confluence']['reason'],'version_regressed')
        self.assertEqual(self.store.get('confluence:98565')['version'],2)
        with self.assertRaisesRegex(ValueError,'Source version regressed'):self.pilot.query(self.actor,'novelty')

    def test_discovered_long_window_has_server_provenance_through_mock_model(self):
        import tempfile
        from pathlib import Path
        from brain.budget import BudgetLedger
        from brain.deepseek import DeepSeekEvidenceModel,PRICE_DATE
        page=self.http['confluence'].content['98565']
        page['body']['storage']['value']='<p>[SYNTHETIC] '+('housekeeping '*2000)+'latewindowfact'+(' appendix'*1000)+'</p>'
        self.cycle();calls=[]
        class ModelTransport:
            def _send(_,request):
                data=json.loads(request.data);calls.append(data)
                ids=[e['evidence_id'] for e in json.loads(data['messages'][1]['content'])['evidence']]
                return 200,{'model':'deepseek-flash','usage':{'prompt_tokens':100,'completion_tokens':20,'total_tokens':120},
                            'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':json.dumps({'evidence_ids':ids})}}]}
        with tempfile.TemporaryDirectory() as tmp:
            ledger=BudgetLedger(str(Path(tmp)/'mock-ledger.sqlite'))
            try:
                self.pilot.engine.model=DeepSeekEvidenceModel('synthetic-not-a-key',ledger,synthetic_only=True,transport=ModelTransport(),today=PRICE_DATE)
                answer=self.pilot.query(self.actor,'latewindowfact')
                self.assertTrue(any('#' in e['evidence_id'] and '[SYNTHETIC]' not in e['text'] for e in answer['evidence']))
                self.assertEqual(len(calls),1)
                for e in json.loads(calls[0]['messages'][1]['content'])['evidence']:
                    self.assertEqual(set(e),{'evidence_id','text'})
                self.assertEqual(answer['model_call']['outcome'],'accepted')
            finally:ledger.close()

    def test_numeric_retry_after_retained_without_reading_error_body(self):
        t=JsonTransport();t.opener=Mock();body=Mock()
        t.opener.open.side_effect=HTTPError('https://test.atlassian.net',429,'rate',{'Retry-After':'300'},body)
        with self.assertRaises(SourceRateLimited) as caught:t.get('https://test.atlassian.net','Bearer synthetic')
        self.assertEqual(caught.exception.retry_after,300);body.read.assert_not_called()


if __name__=='__main__':unittest.main()
