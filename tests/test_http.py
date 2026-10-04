import http.client
import json
import threading
import unittest
from brain.server import App,create_server

class HTTP(unittest.TestCase):
    def setUp(self):
        self.app=App();self.server=create_server(self.app)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.cookie='';self.csrf=''
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join();self.app.store.db.close()
    def request(self,path,data=None,extra=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        headers={'Cookie':self.cookie,'X-CSRF-Token':self.csrf}
        if data is not None: headers['Content-Type']='application/json'
        headers.update(extra or {})
        c.request('POST' if data is not None else 'GET',path,json.dumps(data) if data is not None else None,headers)
        r=c.getresponse();raw=r.read();status=r.status
        cookie=r.getheader('Set-Cookie')
        if cookie:self.cookie=cookie.split(';')[0]
        result=json.loads(raw) if r.getheader('Content-Type')=='application/json' else raw
        c.close();return status,result
    def login(self,user='eng_a'):
        status,result=self.request('/api/demo/login',{'user':user});self.assertEqual(status,200);self.csrf=result['csrf']
    def test_http_frontend_identity_and_query(self):
        self.assertEqual(self.request('/')[0],200)
        self.assertEqual(self.request('/api/query',{'question':'payment-service'})[0],403)
        self.login()
        self.assertEqual(self.request('/api/query',{'question':'payment-service','role':'admin'})[0],400)
        status,a=self.request('/api/query',{'question':'payment-service incident'})
        self.assertEqual(status,200);self.assertTrue(a['evidence'])
        self.assertEqual(self.request('/api/evidence/'+a['evidence'][0]['evidence_id'])[0],200)
        self.assertEqual(self.request('/api/audit/events',{})[0],403)
        self.assertEqual(self.app.audit.export()[-2]['event_type'],'response_dispatch_attempted')
    def test_csrf_host_and_evidence_protection(self):
        self.login('contractor')
        self.assertEqual(self.request('/api/query',{'question':'pilot'},{'X-CSRF-Token':'wrong'})[0],403)
        self.assertEqual(self.request('/api/demo/login',{'user':'security'},{'Origin':'https://evil.example'})[0],403)
        self.assertEqual(self.request('/api/health',extra={'Host':'evil.example'})[0],403)
        self.assertEqual(self.request('/api/evidence/C-03@1'),self.request('/api/evidence/missing@1'))
        self.assertEqual(self.request('/api/sources/status')[0],403)
        self.assertEqual(self.request('/api/admin/sync',{})[0],404)
    def test_local_authority_file_update_and_restart(self):
        import tempfile
        from pathlib import Path
        from brain.sources import FixtureWorld
        from brain.contracts import now,Actor
        from brain.store import Store
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'source.json'; db=Path(directory)/'state.sqlite'
            app=App(Store(str(db)),source)
            world=FixtureWorld();world.refresh(source)
            world.mutate('C-01','content',version=2,text='Runbook payment-service revised',source_updated_at=now());world.save(source)
            app.refresh()
            self.assertEqual(app.store.get('C-01')['version'],2)
            world.mutate('S-01','revoke',user_id='eng_a');world.save(source);app.refresh()
            with self.assertRaises(PermissionError):app.engine.evidence(Actor('eng_a'),'S-01@1')
            app.store.db.close()
            resumed=App(Store(str(db)),source);resumed.refresh()
            self.assertEqual(resumed.store.get('C-01')['version'],2)
            with self.assertRaises(PermissionError):resumed.engine.evidence(Actor('eng_a'),'S-01@1')
            resumed.store.db.close()
    def test_source_file_revocation_during_generation_is_seen(self):
        import tempfile
        from pathlib import Path
        from brain.sources import FixtureWorld
        from brain.contracts import Actor
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'source.json';app=App(source_path=source)
            def revoke_on_disk():
                world=FixtureWorld();world.refresh(source);world.mutate('S-01','revoke',user_id='eng_a');world.save(source)
            app.engine.before_dispatch=revoke_on_disk
            with self.assertRaises(PermissionError):app.engine.query(Actor('eng_a'),'payment-service incident')
            self.assertFalse(any(e['event_type']=='response_committed' for e in app.audit.export()))
            app.store.db.close()
