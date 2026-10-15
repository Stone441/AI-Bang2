import hashlib
import http.client
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from brain.contracts import Actor
from brain.server import App, create_server
from brain.reviewer_access import ReviewerApp, ReviewAccounts


class ReviewerAccess(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)/'accounts.json'
        self.password = 'synthetic-test-password'
        self.rows = {}
        for name, role in [('first','eng_b'),('second','eng_b'),('partner','contractor')]:
            salt = hashlib.md5(name.encode()).hexdigest()
            self.rows[name] = dict(source_actor=role, active=True, expires=time.time()+3600,
                                  revision='1'*16, salt=salt,
                                  password_hash=ReviewAccounts.derive(self.password,salt))
        self.save()
        self.base = App(); self.base.actor = Actor('eng_b')
        self.app = ReviewerApp(self.base, self.path)
        self.server = create_server(self.app)
        self.thread = threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def save(self):
        self.path.write_text(json.dumps(dict(schema=1, purpose='shared-synthetic-review',
            source_tenant='synthetic-demo', accounts=self.rows)))
        self.path.chmod(0o600)

    def stop(self):
        self.server.shutdown();self.server.server_close();self.thread.join(3)
        self.base.store.db.close();self.tmp.cleanup()

    def client(self, username=None):
        session = {}
        def call(path, data=None, extra=None):
            c = http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
            h = {'Cookie':session.get('cookie',''),'X-CSRF-Token':session.get('csrf','')}
            if data is not None:h['Content-Type']='application/json'
            h.update(extra or {})
            c.request('POST' if data is not None else 'GET',path,json.dumps(data) if data is not None else None,h)
            r=c.getresponse(); code=r.status; cookie=r.getheader('Set-Cookie'); body=json.loads(r.read());c.close()
            if cookie:session['cookie']=cookie.split(';')[0]
            if 'csrf' in body:session['csrf']=body['csrf']
            return code,body
        if username:self.assertEqual(call('/api/reviewer/login',dict(username=username,password=self.password))[0],200)
        return call

    def test_opt_in_private_timing_reaches_reviewer_http_without_public_endpoint(self):
        from brain.timing import install
        directory = Path(self.tmp.name).resolve() / 'timing'
        self.assertIsNone(self.app.private_timing)
        recorder = install(self.base, directory)
        saved = threading.Event()
        original_save = recorder.save
        def save(state):
            original_save(state)
            saved.set()
        recorder.save = save
        try:
            call = self.client('first')
            code, answer = call('/api/query', {'question':'payment-service'})
            self.assertEqual(code, 200)
            self.assertTrue(saved.wait(2))
            records = [json.loads(p.read_text()) for p in directory.glob('*.json')]
            query = next(r for r in records if r['operation'] == 'query')
            self.assertEqual(query['request_id'], answer['request_id'])
            self.assertTrue(query['spans'])
            self.assertNotIn('spans', json.dumps(answer))
            self.assertEqual(call('/api/timing')[0], 404)
        finally:
            recorder.close()

    def test_password_role_and_history_isolation_and_audit_attribution(self):
        a,b=self.client('first'),self.client('second')
        status,result=a('/api/query',{'question':'payment-service'})
        self.assertEqual(status,200)
        rid=result['request_id']
        self.assertEqual(len(a('/api/history/recent')[1]['history']),1)
        self.assertEqual(b('/api/history/recent')[1]['history'],[])
        self.assertEqual(b('/api/history?request_id='+rid)[0],403)
        self.assertEqual(len(a('/api/history?request_id='+rid)[1]['history']),1)
        self.assertTrue(result['evidence'])
        eid=result['evidence'][0]['evidence_id']
        from urllib.parse import quote
        self.assertEqual(a('/api/evidence/'+quote(eid,safe=''))[0],200)
        self.assertEqual(b('/api/evidence/'+quote(eid,safe=''))[0],403)
        self.assertEqual(a('/api/audit/events',{})[0],403)
        self.assertEqual(a('/api/sources/status')[0],403)
        events=self.base.audit.export()
        linked=[e for e in events if e['event_type']=='reviewer_query' and e['request_id']==rid]
        self.assertEqual(linked[0]['actor'],'reviewer:first:'+'1'*16)
        self.assertEqual(linked[0]['payload']['effective_source_actor'],'eng_b')
        self.assertTrue(any(e['actor']=='eng_b' and e['request_id']==rid for e in events))

    def test_personal_login_preserves_principal_history_and_password(self):
        original = self.client('first')
        status, result = original('/api/query', {'question':'payment-service'})
        self.assertEqual(status, 200)
        actor = original('/api/session')[1]['actor']
        self.rows['first'].update(login_name='engineer_blair', display_name='Blair')
        self.save()
        renamed = self.client('engineer_blair')
        session = renamed('/api/session')[1]
        self.assertEqual(session['actor'], actor)
        self.assertEqual(session['display_name'], 'Blair')
        self.assertEqual(len(renamed('/api/history?request_id='+result['request_id'])[1]['history']), 1)
        self.assertEqual(self.client()('/api/reviewer/login', dict(username='first', password=self.password))[0], 403)
        self.assertEqual(self.app.registry.source_actor(Actor(actor, 'reviewer-demo')).user_id, 'eng_b')

    def test_duplicate_personal_login_rejected(self):
        self.rows['first']['login_name'] = 'second'
        self.save()
        with self.assertRaises(ValueError):
            self.app.registry.read()

    def test_distinct_roles_are_server_assigned_and_cannot_be_forged(self):
        c=self.client('partner')
        self.assertEqual(c('/api/query',{'question':'payment-service','role':'eng_b'})[0],400)
        c('/api/query',{'question':'payment-service'})
        events=[e for e in self.base.audit.export() if e['event_type']=='request_started']
        self.assertEqual(events[-1]['actor'],'contractor')
        self.assertEqual(self.client()('/api/reviewer/login',dict(username='partner',password=self.password,role='eng_b'))[0],403)

    def test_revocation_expiry_and_password_rotation_invalidate_session(self):
        c=self.client('first');self.rows['first']['active']=False;self.save()
        self.assertEqual(c('/api/session')[0],403)
        self.rows['first']['active']=True;self.save();c=self.client('first')
        self.rows['first']['revision']='2'*16;self.save()
        self.assertEqual(c('/api/session')[0],403)
        c=self.client('first');self.rows['first']['expires']=0;self.save()
        self.assertEqual(c('/api/session')[0],403)

    def test_unknown_and_wrong_password_generic_and_rate_limited(self):
        c=self.client()
        wrong=c('/api/reviewer/login',dict(username='first',password='wrong-password'))
        missing=c('/api/reviewer/login',dict(username='nobody',password='wrong-password'))
        self.assertEqual(wrong,missing)
        self.app.registry.failures['*']=[time.monotonic()]*30
        self.assertEqual(c('/api/reviewer/login',dict(username='first',password=self.password))[0],403)
        self.assertFalse(self.app.sessions)

    def test_unmapped_role_or_registry_permission_fails_closed(self):
        self.rows['first']['source_actor']='administrator';self.save()
        with self.assertRaises(ValueError):ReviewerApp(self.base,self.path)
        self.rows['first']['source_actor']='eng_b';self.save()
        c=self.client('first');self.path.chmod(0o644)
        self.assertEqual(c('/api/session')[0],403)

    def test_current_permission_checks_still_apply_to_saved_evidence(self):
        c=self.client('first');status,result=c('/api/query',{'question':'payment-service'})
        self.assertEqual(status,200)
        from unittest.mock import patch
        with patch.object(self.base.engine,'evidence',side_effect=PermissionError('Unavailable')):
            from urllib.parse import quote
            self.assertEqual(c('/api/evidence/'+quote(result['evidence'][0]['evidence_id'],safe=''))[0],403)

    def test_https_origin_cookie_and_cross_site_controls(self):
        hosted=create_server(self.app,public_origin='https://review.example.test')
        t=threading.Thread(target=hosted.serve_forever,daemon=True);t.start()
        try:
            c=http.client.HTTPConnection('127.0.0.1',hosted.server_port)
            c.request('POST','/api/reviewer/login',json.dumps(dict(username='first',password=self.password)),
                      {'Host':'review.example.test','Origin':'https://review.example.test','Content-Type':'application/json'})
            r=c.getresponse();self.assertEqual(r.status,200);self.assertIn('; Secure',r.getheader('Set-Cookie'));r.read();c.close()
            for headers in ({'Host':'evil.test'},{'Host':'review.example.test','Origin':'https://evil.test'}):
                c=http.client.HTTPConnection('127.0.0.1',hosted.server_port);c.request('GET','/api/health',headers=headers)
                r=c.getresponse();self.assertEqual(r.status,403);r.read();c.close()
        finally:hosted.shutdown();hosted.server_close();t.join(3)
        with self.assertRaises(ValueError):create_server(self.app,public_origin='http://review.example.test')
