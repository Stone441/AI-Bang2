import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest
from brain.contracts import Actor
from brain.server import App
from brain.reviewer_access import ReviewAccounts, ReviewerApp
from brain.audit import event_hash


class ApplicationAudit(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'accounts.json'
        def row(name):
            salt=hashlib.md5(name.encode()).hexdigest()
            return dict(active=True,expires=time.time()+3600,revision='1'*16,salt=salt,
                        password_hash=ReviewAccounts.derive('test-password-long',salt))
        self.viewer='reviewer:first:'+'1'*16
        self.body=dict(schema=1,purpose='shared-synthetic-review',source_tenant='synthetic-demo',
            accounts={'first':dict(row('first'),source_actor='eng_b'),
                      'other':dict(row('other'),source_actor='eng_b')},
            application_auditors={'inspector':dict(row('inspector'),viewer_ids=[self.viewer],resource_scope='payment-service')})
        self.save(); self.base=App(); self.base.actor=Actor('eng_b')
        self.addCleanup(self.base.store.db.close)
        self.app=ReviewerApp(self.base,self.path)
        self.actor=self.app.authenticate(dict(username='inspector',password='test-password-long'))
        self.v=Actor(self.viewer,'reviewer-demo')
    def save(self):
        self.path.write_text(json.dumps(self.body)); self.path.chmod(0o600)
    def seed(self,rid,actor=None,resource_scope=None):
        self.app.register_request(actor or self.v,rid)
        self.base.audit.append('request_started','eng_b',rid,{'question':'payment-service?'})
        self.base.audit.append('request_failed','eng_b',rid,{'reason':'synthetic failure',**({'resource_scope':resource_scope,'resource_id':'x'} if resource_scope else {})})
    def test_explicit_auditor_has_no_knowledge_identity(self):
        self.assertTrue(self.app.can_audit(self.actor)); self.assertFalse(self.app.can_audit(self.v))
        self.assertEqual(self.app.session_details(self.actor)['demo_role'],'auditor')
        with self.assertRaises(PermissionError): self.app.registry.source_actor(self.actor)
        with self.assertRaises(PermissionError): self.app.engine.query(self.actor,'payment',request_id='x')
        with self.assertRaises(PermissionError): self.app.audit_inquire(self.v,{})
    def test_whole_early_failure_and_zero_evidence_lifecycle_and_snapshot(self):
        self.seed('early'); self.seed('hidden',Actor('reviewer:other:'+'1'*16,'reviewer-demo'))
        first=self.app.audit_inquire(self.actor,dict(application_identity=self.viewer,page_size=1))
        self.assertEqual(first['total'],3)
        self.seed('later')
        rest=self.app.audit_inquire(self.actor,dict(application_identity=self.viewer,page_size=100,
            as_of=first['as_of'],after=first['next_after']))
        events=first['events']+rest['events']
        self.assertEqual({e['request_id'] for e in events},{'early'})
        self.assertEqual({e['event_type'] for e in events},{'reviewer_query','request_started','request_failed'})
        for e in events:self.assertEqual(event_hash(e),e['hash'])
    def test_exact_identity_scope_and_registry_revocation(self):
        self.seed('good'); self.seed('bad',resource_scope='unrelated')
        events=self.app.audit_inquire(self.actor,{})['events']
        self.assertEqual({e['request_id'] for e in events},{'good'})
        for filters in ({'application_identity':'reviewer:other:'+'1'*16}, {'actor':'eng_b'},
                        {'resource_scope':'unrelated'}, {'sql':'SELECT *'}):
            with self.assertRaises((PermissionError,ValueError)):self.app.audit_inquire(self.actor,filters)
        self.body['application_auditors']['inspector']['active']=False; self.save()
        with self.assertRaises(PermissionError):self.app.audit_inquire(self.actor,{})
    def test_request_identity_immutable_and_revision_exact(self):
        self.seed('one'); self.app.register_request(self.v,'one')
        with self.assertRaises(PermissionError):self.app.register_request(Actor('reviewer:other:'+'1'*16,'reviewer-demo'),'one')
        self.body['accounts']['first']['revision']='2'*16;self.save()
        self.seed('new',Actor('reviewer:first:'+'2'*16,'reviewer-demo'))
        self.assertEqual({e['request_id'] for e in self.app.audit_inquire(self.actor,{})['events']},{'one'})

    def test_no_knowledge_history_or_preview_for_auditor(self):
        with self.assertRaises(PermissionError):self.app.engine.history_summaries(self.actor)
        with self.assertRaises(PermissionError):self.app.engine.evidence(self.actor,'anything')
        with self.assertRaises(PermissionError):self.app.registry.access_scope(self.actor)

    def test_unanchored_request_and_unrelated_actor_never_disclosed(self):
        self.seed('one')
        self.base.audit.append('request_failed','product_ops','one',{'reason':'must not leak'})
        with self.base.store.transaction() as db:
            db.execute('INSERT INTO reviewer_requests VALUES(?,?)',('unanchored',self.viewer))
        self.base.audit.append('request_started','eng_b','unanchored',{'question':'must not leak'})
        events=self.app.audit_inquire(self.actor,{})['events']
        self.assertEqual({e['request_id'] for e in events},{'one'})
        self.assertNotIn('product_ops',{e['actor'] for e in events})
        self.assertNotIn('reviewer:other:',json.dumps(events))

    def test_audit_failure_rolls_back_new_ownership(self):
        self.base.audit.fail=True
        with self.assertRaises(RuntimeError):self.app.register_request(self.v,'failed')
        self.base.audit.fail=False
        self.assertEqual(self.base.store.db.execute('SELECT count(*) FROM reviewer_requests').fetchone()[0],0)

    def test_new_registry_creator_resolves_only_exact_generated_revisions(self):
        from scripts.reviewer_accounts import create
        p=Path(self.tmp.name)/'new.json';cards=Path(self.tmp.name)/'cards'
        body=create(p,cards,'synthetic-demo',{'viewer':'eng_b'},audit_policy={
            'auditor':{'viewer_accounts':['viewer'],'resource_scope':'payment-service'}})
        registry=ReviewAccounts(p,'synthetic-demo',{'eng_b'})
        self.assertEqual(registry.read()['application_auditors']['auditor']['viewer_ids'],
                         ['reviewer:viewer:'+body['accounts']['viewer']['revision']])
        with self.assertRaises(ValueError):create(p,cards,'synthetic-demo',{'viewer':'eng_b'})
        invalid=Path(self.tmp.name)/'invalid.json'
        with self.assertRaises(ValueError):create(invalid,Path(self.tmp.name)/'invalid-cards','synthetic-demo',
            {'viewer':'eng_b'},audit_policy={'audit':{'viewer_accounts':['other'],'resource_scope':'payment-service'}})
        self.assertFalse(invalid.exists())

    def test_legacy_success_anchor_supported_without_rewriting_raw_events(self):
        with self.base.store.transaction() as db:
            db.execute('INSERT INTO reviewer_requests VALUES(?,?)',('legacy',self.viewer))
        anchor=self.base.audit.append('reviewer_query',self.viewer,'legacy',{'effective_source_actor':'eng_b'})
        self.base.audit.append('request_started','eng_b','legacy',{'question':'old question'})
        self.base.audit.append('evidence_used','eng_b','legacy',dict(resource_scope='payment-service',resource_id='C-02',source='confluence'))
        result=self.app.audit_inquire(self.actor,dict(resource_id='C-02',source='confluence'))
        self.assertEqual(len(result['events']),3)
        self.assertEqual(result['events'][0],anchor)

    def test_invalid_audit_configuration_never_grants_access(self):
        for change in ({'resource_scope':'all'},{'source_actor':'eng_b'},
                       {'viewer_ids':['reviewer:first:*']},{'demo_role':'engineer'}):
            original=dict(self.body['application_auditors']['inspector'])
            self.body['application_auditors']['inspector'].update(change);self.save()
            self.assertFalse(self.app.can_audit(self.actor))
            with self.assertRaises((ValueError,PermissionError)):self.app.audit_inquire(self.actor,{})
            self.body['application_auditors']['inspector']=original
        self.save()

    def test_early_identity_anchor_retains_exact_question_and_is_immutable(self):
        question='  Original question about payment-service?\nSecond line.  '
        self.app.register_request(self.v,'early-question',question=question)
        self.app.register_request(self.v,'early-question',question='replacement must not change audit')
        self.base.audit.append('request_failed',self.viewer,'early-question',{'reason':'refresh failed'})
        events=self.app.audit_inquire(self.actor,{})['events']
        anchors=[e for e in events if e['event_type']=='reviewer_query']
        self.assertEqual(len(anchors),1)
        self.assertEqual(anchors[0]['payload']['query'],question)
        self.assertEqual(event_hash(anchors[0]),anchors[0]['hash'])
        self.assertEqual({e['event_type'] for e in events},{'reviewer_query','request_failed'})
        self.assertNotIn('replacement must not change audit',json.dumps(events))

    def test_invalid_early_question_never_creates_ownership(self):
        for index,question in enumerate((None,42,'x'*4001)):
            with self.assertRaises(ValueError):
                self.app.register_request(self.v,'invalid-'+str(index),question=question)
        self.assertEqual(self.base.store.db.execute('SELECT count(*) FROM reviewer_requests').fetchone()[0],0)

    def test_direct_query_fallback_records_submitted_question(self):
        question='Who owns payment-service?'
        self.app.engine.query(self.v,question,request_id='direct-query')
        anchors=[e for e in self.base.audit.export() if e['event_type']=='reviewer_query'
                 and e['request_id']=='direct-query']
        self.assertEqual(len(anchors),1)
        self.assertEqual(anchors[0]['payload']['query'],question)
