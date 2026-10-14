"""Real loopback queue behavior with fixture data/fake model, no external I/O."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
import threading
import time
import unittest
from brain.server import App,create_server

class QueryQueue(unittest.TestCase):
    def setUp(self):
        self.app=App();self.server=create_server(self.app)
        self.worker=threading.Thread(target=self.server.serve_forever,daemon=True);self.worker.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown();self.server.server_close();self.worker.join(3);self.app.store.db.close()

    def client(self):
        session={}
        def call(path,data=None):
            c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=4)
            headers={'Cookie':session.get('cookie',''),'X-CSRF-Token':session.get('csrf','')}
            if data is not None:headers['Content-Type']='application/json'
            c.request('POST' if data is not None else 'GET',path,json.dumps(data) if data is not None else None,headers)
            r=c.getresponse();status=r.status;body=json.loads(r.read())
            if r.getheader('Set-Cookie'):session['cookie']=r.getheader('Set-Cookie').split(';')[0]
            c.close();return status,body
        status,body=call('/api/demo/login',{'user':'eng_a'});self.assertEqual(status,200)
        session['csrf']=body['csrf'];return call,session

    def queued(self,client):
        until=time.monotonic()+2
        while time.monotonic()<until:
            status,body=client('/api/runtime')
            if body['run'] and body['run']['phase']=='queued':return body['run']
            time.sleep(.005)
        self.fail('Request never exposed queued status before lock acquisition')

    def test_three_queued_requests_visible_distinct_and_serialized(self):
        clients=[self.client()[0] for _ in range(3)]
        original=self.app.engine.query;calls=[]
        def query(*args,**kw):
            calls.append(kw['request_id']);return original(*args,**kw)
        self.app.engine.query=query
        with ThreadPoolExecutor(3) as pool:
            with self.app.store.lock:
                futures=[pool.submit(c,'/api/query',{'question':'payment-service'}) for c in clients]
                runs=[self.queued(c) for c in clients]
                self.assertEqual(len({r['request_id'] for r in runs}),3)
                self.assertEqual(calls,[])
                self.assertEqual(clients[0]('/api/query',{'question':'payment-service'})[0],409)
            responses=[f.result(4) for f in futures]
        self.assertEqual([s for s,_ in responses],[200]*3)
        for c,r,(_,answer) in zip(clients,runs,responses):
            self.assertEqual(r['request_id'],answer['request_id'])
            self.assertEqual(c('/api/runtime')[1]['run']['status'],'completed')
        self.assertEqual(len(calls),3)

    def test_logout_while_queued_never_invokes_engine(self):
        client,_=self.client();calls=[]
        self.app.engine.query=lambda *a,**k:calls.append(k)
        with ThreadPoolExecutor(1) as pool:
            with self.app.store.lock:
                future=pool.submit(client,'/api/query',{'question':'payment-service'})
                self.queued(client)
                self.assertEqual(client('/api/logout',{})[0],200)
            self.assertEqual(future.result(4)[0],503)
        self.assertEqual(calls,[])

    def test_invalid_request_is_rejected_without_waiting_or_creating_run(self):
        client,_=self.client()
        with self.app.store.lock:
            self.assertEqual(client('/api/query',{'question':'payment-service','role':'admin'})[0],400)
            self.assertIsNone(client('/api/runtime')[1]['run'])
