"""Loopback HTTP with mock four-source and model I/O; no external requests."""
from concurrent.futures import ThreadPoolExecutor
import http.client
import json
from pathlib import Path
import threading
import unittest

from brain.operator_web import OperatorApp
from brain.server import create_server
from scripts.concurrent_allowance import ConcurrentPerformanceAdmission,ConcurrentGoalLedger
import test_isolated_query as isolated


class IsolatedHTTP(unittest.TestCase):
    prepare=isolated.Isolation.prepare

    def setUp(self):
        isolated.Isolation.setUp(self)
        self.app=OperatorApp(dict(self.pilot.authority.readers),self.store,'eng_b')
        self.app.pilot=self.pilot;self.app.engine=self.pilot.engine
        self.app.world=self.pilot.authority;self.app.audit=self.pilot.audit
        self.app.request_lock=self.pilot.lock;self.app.isolated_queries=self.executor
        self.gate=ConcurrentPerformanceAdmission(self.executor.query,self.ledger,
            Path(self.tmp.name)/'goal.json',plan_sha256='a'*64)
        self.addCleanup(self.gate.close)
        self.app.engine.model.ledger=ConcurrentGoalLedger(self.gate)
        self.app.engine.query=self.gate
        self.server=create_server(self.app,0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown();self.server.server_close();self.thread.join(3)

    def client(self):
        session={'cookie':'','csrf':''}
        def call(path,data=None):
            connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
            headers={'Cookie':session['cookie'],'X-CSRF-Token':session['csrf']}
            if data is not None:headers['Content-Type']='application/json'
            connection.request('POST' if data is not None else 'GET',path,
                json.dumps(data) if data is not None else None,headers)
            response=connection.getresponse();body=json.loads(response.read());status=response.status
            if response.getheader('Set-Cookie'):session['cookie']=response.getheader('Set-Cookie').split(';')[0]
            connection.close();return status,body
        status,body=call('/api/operator/login',{'ticket':self.app.renew_bootstrap_ticket()})
        self.assertEqual(status,200);session['csrf']=body['csrf']
        return call

    def test_three_sessions_overlap_and_keep_progress_answers_and_budget_separate(self):
        # Exercise HTTP isolation independently of the stricter AUTH036 ceiling.
        # A real full-context reservation is > USD0.30: three cannot fit USD0.50.
        self.app.engine.query=self.executor.query
        self.app.engine.model.ledger=self.ledger
        clients=[self.client() for _ in range(3)];barrier=threading.Barrier(3)
        self.on_send=lambda:barrier.wait(3)
        with ThreadPoolExecutor(3) as pool:
            futures=[pool.submit(client,'/api/query',{'question':'novelty'}) for client in clients]
            replies=[f.result(5) for f in futures]
        self.assertEqual([status for status,_ in replies],[200]*3)
        self.assertEqual(len({body['request_id'] for _,body in replies}),3)
        for client,(_,answer) in zip(clients,replies):
            status,runtime=client('/api/runtime');self.assertEqual(status,200)
            self.assertEqual(runtime['run']['request_id'],answer['request_id'])
            self.assertEqual(answer['actor'],'eng_b')
            self.assertEqual(answer['review_status'],'accepted')
        self.assertEqual(len(self.calls),3)
        self.assertEqual(self.ledger.summary()['pending_requests'],0)

    def test_goal_ceiling_rejects_second_full_context_reservation(self):
        first,second=self.client(),self.client()
        entered,release=threading.Event(),threading.Event()
        def send():
            entered.set()
            if not release.wait(3):raise RuntimeError('Test synchronization failed')
        self.on_send=send
        with ThreadPoolExecutor(1) as pool:
            pending=pool.submit(first,'/api/query',{'question':'novelty'})
            try:
                self.assertTrue(entered.wait(3))
                status,body=second('/api/query',{'question':'novelty'})
                self.assertEqual(status,503)
                self.assertEqual(body['code'],'trial_admission_paused')
            finally:release.set()
            self.assertEqual(pending.result(5)[0],200)
        self.assertEqual(len(self.calls),1)
        self.assertEqual(self.ledger.summary()['pending_requests'],0)

    def test_duplicate_session_still_409_and_runtime_is_responsive(self):
        client=self.client();entered=threading.Event();release=threading.Event()
        def send():
            entered.set()
            if not release.wait(3):raise RuntimeError('Test synchronization failed')
        self.on_send=send
        with ThreadPoolExecutor(1) as pool:
            first=pool.submit(client,'/api/query',{'question':'novelty'})
            try:
                self.assertTrue(entered.wait(3))
                status,body=client('/api/query',{'question':'novelty'})
                self.assertEqual(status,409);self.assertEqual(body['code'],'query_busy')
                self.assertEqual(client('/api/runtime')[0],200)
            finally:release.set()
            self.assertEqual(first.result(5)[0],200)
        self.assertEqual(len(self.calls),1)

    def test_client_identity_override_is_rejected_before_any_model_call(self):
        client=self.client()
        self.assertEqual(client('/api/query',{'question':'novelty','role':'security'})[0],400)
        self.assertEqual(self.calls,[])
