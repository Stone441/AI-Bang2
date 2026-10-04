import copy
import unittest
from urllib.parse import urlsplit, parse_qs
from unittest.mock import Mock, patch

from brain.confluence import Delegation
from brain.contracts import Actor
from brain.slack import SlackReader, SlackTransport
from brain.delegated_query import DelegatedQueryPilot
from brain.store import Store

ROOT='C123/1791150000.000001'
REPLY='C123/1791150001.000002'


class SlackHTTP:
    def __init__(self):
        self.calls=[];self.status=200;self.error=None
        self.identity={'ok':True,'user_id':'UEMP','team_id':'T123'}
        self.channel={'id':'C123','name':'synthetic-payments','context_team_id':'T123',
            'is_im':False,'is_mpim':False,'is_shared':False,'is_ext_shared':False,
            'is_pending_ext_shared':False,'is_private':True,'is_member':True}
        self.messages={ROOT:{'type':'message','ts':ROOT.split('/')[1],
                            'text':'Synthetic incident retry safeguards root'},
            REPLY:{'type':'message','ts':REPLY.split('/')[1],'thread_ts':ROOT.split('/')[1],
                   'text':'Synthetic follow-up retry safeguards reply'}}

    def get(self,url,authorization):
        self.calls.append(url);p=urlsplit(url);q=parse_qs(p.query)
        if p.path.endswith('/auth.test'):return 200,copy.deepcopy(self.identity)
        if self.status!=200:return self.status,None
        if self.error:return 200,{'ok':False,'error':self.error}
        if p.path.endswith('/conversations.info'):return 200,{'ok':True,'channel':copy.deepcopy(self.channel)}
        key=q['channel'][0]+'/'+q['oldest'][0]
        return 200,{'ok':True,'messages':[copy.deepcopy(self.messages[key])] if key in self.messages else []}


def reader(transport):
    return SlackReader('https://test.slack.com','pilot','T123',{'C123':'private'},
        {ROOT:None,REPLY:ROOT.split('/')[1]}, {'eng_b':Delegation('UEMP','Bearer synthetic-test')},transport)


class SlackBoundary(unittest.TestCase):
    def setUp(self):self.transport=SlackHTTP();self.reader=reader(self.transport);self.actor=Actor('eng_b','pilot')

    def test_exact_root_and_reply_are_separate_evidence_with_backend_links(self):
        for native,endpoint in [(ROOT,'conversations.history'),(REPLY,'conversations.replies')]:
            d,c=self.reader.read(self.actor,native);self.assertEqual(d.result,'allow')
            self.assertEqual(c['text'],self.transport.messages[native]['text'])
            self.assertEqual(c['source_url'],'https://test.slack.com/archives/C123/p'+native.split('/')[1].replace('.',''))
            q=parse_qs(urlsplit(self.transport.calls[-1]).query)
            self.assertIn(endpoint,self.transport.calls[-1]);self.assertEqual(q['oldest'],q['latest'])
            self.assertEqual(q['limit'],['2' if native == REPLY else '1']);self.assertNotIn('synthetic-test',self.transport.calls[-1])
        self.assertIn('ts=',self.transport.calls[-1])

    def test_thread_parent_envelope_selects_only_allowlisted_target(self):
        original=self.transport.get
        def envelope(url,authorization):
            status,data=original(url,authorization)
            if 'conversations.replies?' in url:
                data['messages'].insert(0,copy.deepcopy(self.transport.messages[ROOT]))
            return status,data
        with patch.object(self.transport,'get',side_effect=envelope):
            d,c=self.reader.read(self.actor,REPLY)
            self.assertEqual(d.result,'allow');self.assertEqual(c['text'],self.transport.messages[REPLY]['text'])
            self.assertEqual(c['locator']['message_ts'],REPLY.split('/')[1])
        from brain.slack import select_message, SlackUnavailable
        target=copy.deepcopy(self.transport.messages[REPLY]);parent=copy.deepcopy(self.transport.messages[ROOT])
        for invalid in [[target,target],[dict(target,ts='1791150002.000003')], [parent], [parent,target,parent]]:
            with self.assertRaises(SlackUnavailable):select_message(invalid,REPLY.split('/')[1],ROOT.split('/')[1])

    def test_safe_diagnostic_codes_never_include_upstream_payload(self):
        self.transport.error='missing_scope'
        d,c=self.reader.read(self.actor,REPLY)
        self.assertEqual(d.method,'slack-api-missing-scope');self.assertIsNone(c)
        self.transport.error='token-secret-should-never-appear'
        self.assertEqual(self.reader.read(self.actor,REPLY)[0].method,'slack-api-unknown')

    def test_private_revocation_stops_before_message_request(self):
        self.transport.channel['is_member']=False
        d,c=self.reader.read(self.actor,REPLY);self.assertEqual(d.result,'deny');self.assertIsNone(c)
        self.assertEqual(len(self.transport.calls),2)

    def test_public_nonmembership_does_not_fabricate_source_revocation(self):
        self.reader.channels['C123']='public';self.transport.channel.update(is_private=False,is_member=False)
        self.assertEqual(self.reader.read(self.actor,ROOT)[0].result,'allow')

    def test_native_identity_wrong_workspace_and_bot_are_rejected_before_metadata(self):
        for identity in [dict(self.transport.identity,user_id='UADMIN'),
                         dict(self.transport.identity,team_id='TOTHER'),
                         dict(self.transport.identity,bot_id='B123'),{'ok':False,'error':'token_revoked'}]:
            self.transport.calls=[];self.transport.identity=identity
            d,c=self.reader.read(self.actor,ROOT);self.assertEqual(d.result,'unknown');self.assertIsNone(c)
            self.assertEqual(len(self.transport.calls),1)

    def test_unmapped_tenant_actor_and_message_cannot_fetch(self):
        for actor,native in [(Actor('eng_b','other'),ROOT),(Actor('admin','pilot'),ROOT),(self.actor,'C999/1791150000.000001')]:
            self.assertEqual(self.reader.read(actor,native)[0].result,'unknown')
        self.assertEqual(self.transport.calls,[])

    def test_unknown_and_denied_errors_remain_distinct(self):
        for error in ['channel_not_found','not_in_channel','invalid_auth','missing_scope','ratelimited']:
            self.transport.error=error;d,c=self.reader.read(self.actor,ROOT)
            self.assertEqual(d.result,'deny' if error in ('channel_not_found','not_in_channel') else 'unknown');self.assertIsNone(c)
        self.transport.error=None
        for status in (401,429,500):
            self.transport.status=status;self.assertEqual(self.reader.read(self.actor,ROOT)[0].result,'unknown')

    def test_shared_dm_wrong_channel_and_unknown_membership_fail_closed(self):
        baseline=copy.deepcopy(self.transport.channel)
        for change in [{'is_shared':True},{'is_ext_shared':True},{'is_pending_ext_shared':True},
                       {'is_im':True},{'is_mpim':True},{'context_team_id':'TOTHER'},
                       {'id':'COTHER'},{'is_member':None},{'is_private':False}]:
            self.transport.channel=dict(baseline,**change)
            d,c=self.reader.read(self.actor,ROOT);self.assertEqual(d.result,'unknown');self.assertIsNone(c)

    def test_deleted_message_denies_instead_of_returning_neighbor(self):
        del self.transport.messages[ROOT];self.assertEqual(self.reader.read(self.actor,ROOT)[0].result,'deny')
        self.transport.messages[ROOT]={'type':'message','text':'Neighbor','ts':'1791150002.000003'}
        self.assertEqual(self.reader.read(self.actor,ROOT)[0].result,'unknown')

    def test_message_edit_invalidates_old_fingerprint_even_without_edited_timestamp(self):
        _,old=self.reader.read(self.actor,ROOT);self.transport.messages[ROOT]['text']='Changed synthetic content'
        self.assertEqual(self.reader.read(self.actor,ROOT,old['version'])[0].result,'deny')
        self.assertNotEqual(self.reader.read(self.actor,ROOT)[1]['version'],old['version'])

    def test_attachments_cards_hidden_blocks_or_wrong_thread_do_not_enter_content(self):
        baseline=copy.deepcopy(self.transport.messages[ROOT])
        for change in [{'files':[{'id':'F1'}]},{'attachments':[{'text':'restricted'}]},
                       {'blocks':[{'type':'image','image_url':'https://evil.invalid'}]},
                       {'blocks':[{'type':'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':'hidden'}]}]}]},
                       {'thread_ts':'1791150002.000003'},{'subtype':'message_deleted'}]:
            self.transport.messages[ROOT]=dict(baseline,**change)
            d,c=self.reader.read(self.actor,ROOT);self.assertEqual(d.result,'unknown');self.assertIsNone(c)
        self.transport.messages[ROOT]=dict(baseline,blocks=[{'type':'rich_text','elements':[{'type':'rich_text_section','elements':[{'type':'text','text':baseline['text']}]}]}])
        self.assertEqual(self.reader.read(self.actor,ROOT)[0].result,'allow')

    def test_constructor_requires_canonical_native_allowlist_and_known_parent(self):
        for kwargs in [{'messages':{'../x':None}},{'messages':{REPLY:'1791150000.000001'}},
                       {'channels':{'D123':'private'}},{'site':'https://evil.invalid'},
                       {'messages':{ROOT:'1791150000.000001'}}]:
            args=dict(site='https://test.slack.com',tenant='pilot',team_id='T123',channels={'C123':'private'},messages={ROOT:None},delegations={})
            args.update(kwargs)
            with self.assertRaises(ValueError):SlackReader(**args)

    def test_auth_test_uses_post_header_and_no_secret_in_url(self):
        transport=SlackTransport()
        with patch.object(transport,'_send',return_value=(200,{'ok':True})) as send:
            transport.get('https://slack.com/api/auth.test','Bearer synthetic-test')
        request=send.call_args.args[0];self.assertEqual(request.get_method(),'POST')
        self.assertEqual(request.data,b'');self.assertNotIn('synthetic-test',request.full_url)


class SlackEngine(unittest.TestCase):
    def setUp(self):
        self.transport=SlackHTTP();self.store=Store();self.addCleanup(self.store.db.close)
        self.pilot=DelegatedQueryPilot({'slack':reader(self.transport)},self.store)
        self.actor=Actor('eng_b','pilot')

    def test_same_session_revocation_protects_history_citations_and_model(self):
        first=self.pilot.query(self.actor,'retry safeguards');self.assertEqual(len(first['evidence']),2)
        self.transport.channel['is_member']=False
        result=self.pilot.query(self.actor,'retry safeguards',first['request_id'])
        self.assertEqual(result['evidence'],[]);self.assertEqual(self.pilot.engine.model.calls[-1]['evidence'],[])
        self.assertTrue(self.pilot.history(self.actor,first['request_id'])[0]['unavailable'])
        with self.assertRaises(PermissionError):self.pilot.evidence(self.actor,first['evidence'][0]['evidence_id'])
        self.assertIsNotNone(self.store.get('slack:'+ROOT))

    def test_thread_update_switches_only_reply_and_hides_old_answer(self):
        first=self.pilot.query(self.actor,'retry safeguards');before=self.store.get('slack:'+ROOT)['version']
        self.transport.messages[REPLY]['text']='Synthetic retry safeguards NEWREPLY'
        self.assertTrue(self.pilot.history(self.actor,first['request_id'])[0]['unavailable'])
        current=self.pilot.query(self.actor,'retry safeguards NEWREPLY')
        self.assertTrue(any('NEWREPLY' in e['text'] for e in current['evidence']))
        self.assertEqual(self.store.get('slack:'+ROOT)['version'],before)

    def test_final_model_dispatch_permission_check_blocks_late_revocation(self):
        original=self.pilot.authority.check_read;count=0
        def check(actor,rid):
            nonlocal count
            count+=1
            if count==5:self.transport.channel['is_member']=False
            return original(actor,rid)
        with patch.object(self.pilot.authority,'check_read',side_effect=check):
            with self.assertRaises(PermissionError):self.pilot.query(self.actor,'retry safeguards')
        self.assertEqual(self.pilot.engine.model.calls,[])
        self.assertTrue(any(e['event_type']=='request_failed' for e in self.pilot.audit.export()))


class SlackCombined(unittest.TestCase):
    def test_slack_revocation_keeps_jira_evidence_without_using_old_slack(self):
        from test_jira import JiraTransport, reader as jira_reader
        transport=SlackHTTP();store=Store();self.addCleanup(store.db.close)
        pilot=DelegatedQueryPilot({'slack':reader(transport),'jira':jira_reader(JiraTransport())},store)
        actor=Actor('eng_b','pilot');first=pilot.query(actor,'retry safeguards')
        self.assertEqual({e['source'] for e in first['evidence']},{'slack','jira'})
        transport.channel['is_member']=False
        second=pilot.query(actor,'retry safeguards',first['request_id'])
        self.assertEqual({e['source'] for e in second['evidence']},{'jira'})
        self.assertNotIn('follow-up',str(pilot.engine.model.calls[-1]))
        self.assertTrue(pilot.history(actor,first['request_id'])[0]['unavailable'])
