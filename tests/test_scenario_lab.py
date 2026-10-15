import http.client
import json
import threading
import unittest

from brain.scenario_lab import ScenarioLab,create_lab_server
from brain.server import App,create_server


class ScenarioLabTests(unittest.TestCase):
    def setUp(self):
        self.lab=ScenarioLab();self.addCleanup(self.lab.close)

    def server(self,lab=None):
        server=create_lab_server(lab or self.lab)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        return server

    def request(self,server,path,body=None,headers=None):
        connection=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=3)
        self.addCleanup(connection.close)
        connection.request('POST' if body is not None else 'GET',path,body=json.dumps(body) if body is not None else None,headers=headers or {})
        response=connection.getresponse();raw=response.read()
        return response, json.loads(raw) if response.getheader('Content-Type')=='application/json' else raw

    def test_real_engine_sequence_update_revocation_and_scoped_audit(self):
        for action in self.lab.actions:
            state=self.lab.step(action)
            self.assertTrue(state['steps'][-1]['passed'],action)
        self.assertIsNone(state['next_action'])
        self.assertEqual(self.lab.world.resources['C-01']['version'],2)
        self.assertEqual(len(self.lab.answers),3)
        self.assertTrue(self.lab.export()['chain']['valid'])
        self.assertNotIn('csrf',self.lab.export())

    def test_order_and_unknown_actions_do_not_mutate_world(self):
        for action in ('update','reset','delete','revoke'):
            with self.subTest(action=action),self.assertRaises(ValueError):self.lab.step(action)
        self.assertEqual(self.lab.steps,[]);self.assertEqual(self.lab.audit.export(),[])
        self.assertEqual(self.lab.world.resources['C-01']['version'],1)

    def test_labs_have_separate_memory_and_tokens(self):
        other=ScenarioLab();self.addCleanup(other.close)
        self.lab.step('baseline');self.lab.step('update')
        self.assertEqual(other.world.resources['C-01']['version'],1)
        self.assertEqual(other.audit.export(),[])
        self.assertNotEqual(self.lab.csrf,other.csrf)

    def test_failed_check_is_preserved_and_stops_progress(self):
        self.lab.world.revoked.add(('eng_a','C-01'))
        state=self.lab.step('baseline')
        self.assertFalse(state['steps'][0]['passed']);self.assertTrue(state['failure'])
        self.assertIsNone(state['next_action'])
        with self.assertRaises(ValueError):self.lab.step('update')
        self.assertFalse(self.lab.export()['steps'][0]['checks']['runbook_v1_returned'])

    def test_http_rejects_csrf_foreign_origin_and_arbitrary_source_writes(self):
        server=self.server();headers={'Content-Type':'application/json','X-CSRF-Token':self.lab.csrf}
        response,_=self.request(server,'/api/lab/step',{'action':'baseline'},{'Content-Type':'application/json'})
        self.assertEqual(response.status,403)
        response,_=self.request(server,'/api/lab/step',{'action':'baseline'},{**headers,'Origin':'https://evil.invalid'})
        self.assertEqual(response.status,403)
        response,_=self.request(server,'/api/lab/step',{'action':'baseline','resource_id':'C-03'},headers)
        self.assertEqual(response.status,400)
        response,_=self.request(server,'/api/lab/step',{'action':'delete'},headers)
        self.assertEqual(response.status,400)
        response,_=self.request(server,'/api/lab/state',headers={'Host':'evil.invalid'})
        self.assertEqual(response.status,403)
        self.assertEqual(self.lab.steps,[])
        self.assertEqual(self.lab.world.resources['C-01']['version'],1)

    def test_http_full_sequence_export_and_static_boundary(self):
        server=self.server();response,state=self.request(server,'/api/lab/state')
        self.assertEqual(response.status,200)
        for action in self.lab.actions:
            response,state=self.request(server,'/api/lab/step',{'action':action},
                {'Content-Type':'application/json','X-CSRF-Token':state['csrf']})
            self.assertEqual(response.status,200);self.assertTrue(state['steps'][-1]['passed'])
        response,transcript=self.request(server,'/api/lab/export')
        self.assertEqual(response.status,200);self.assertNotIn('csrf',transcript)
        self.assertEqual(len(transcript['steps']),4)
        response,html=self.request(server,'/')
        self.assertIn(b'Synthetic sources',html)
        self.assertIn("frame-ancestors 'none'",response.getheader('Content-Security-Policy'))
        response,_=self.request(server,'/../brain/scenario_lab.py')
        self.assertEqual(response.status,404)

    def test_unexpected_http_failure_stops_without_exposing_error_text(self):
        server=self.server()
        def fail(*args):raise RuntimeError('SECRET_ERROR_DETAILS')
        self.lab.engine.model.generate=fail
        response,body=self.request(server,'/api/lab/step',{'action':'baseline'},
            {'Content-Type':'application/json','X-CSRF-Token':self.lab.csrf})
        self.assertEqual(response.status,500);self.assertNotIn('SECRET_ERROR_DETAILS',json.dumps(body))
        self.assertIsNone(self.lab.state()['next_action'])
        self.assertTrue(self.lab.export()['failure'])
        self.assertNotIn('SECRET_ERROR_DETAILS',json.dumps(self.lab.export()))

    def test_employee_server_has_no_lab_routes(self):
        app=App();self.addCleanup(app.store.db.close)
        server=create_server(app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        response,_=self.request(server,'/api/lab/state')
        self.assertNotEqual(response.status,200)
        self.assertFalse(hasattr(app,'step'))
