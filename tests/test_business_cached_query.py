import unittest

from brain.confluence import SourceUnavailable
from brain.contracts import Actor
from brain.delegated_query import DelegatedQueryPilot
from brain.discovery import ContainerDiscovery
from test_container_discovery import setup


class BusinessCachedQueryTests(unittest.TestCase):
    def setUp(self):
        self.store,self.pilot,self.http,self.readers=setup()
        self.actor=Actor('eng_b','pilot');self.clock=0
        self.worker=ContainerDiscovery(self.pilot,self.actor,clock=lambda:self.clock,bounded_queries=True)
        self.worker.start();self.worker.run_once()
        self.addCleanup(self.store.db.close);self.addCleanup(self.worker.close)

    def test_background_query_avoids_all_object_refresh_and_keeps_native_boundaries(self):
        answer=self.pilot.query(self.actor,'novelty')
        events=[e for e in self.pilot.audit.export() if e['request_id']==answer['request_id']]
        self.assertFalse(any(e['payload'].get('phase')=='source_refresh' for e in events))
        self.assertTrue(any(e['payload'].get('phase')=='retrieval_snapshot_prefilter' for e in events))
        for evidence in answer['evidence']:
            phases={e['payload'].get('phase') for e in events
                    if e['event_type']=='authorization_decided'
                    and e['payload']['resource_id']==evidence['resource_id']}
            self.assertTrue({'before_model','model_dispatch','before_dispatch'}<=phases)

    def test_revocation_cannot_reuse_worker_snapshot_or_old_history(self):
        first=self.pilot.query(self.actor,'novelty')
        eid=next(e['evidence_id'] for e in first['evidence'] if e['source']=='confluence')
        self.http['confluence'].fail_native.add('98565')
        current=self.pilot.query(self.actor,'novelty')
        self.assertNotIn('confluence:98565',{e['resource_id'] for e in current['evidence']})
        with self.assertRaises(PermissionError):self.pilot.evidence(self.actor,eid)
        self.assertTrue(self.pilot.history(self.actor,first['request_id'])[0]['unavailable'])

    def test_current_native_unknown_stops_full_answer_before_model(self):
        self.http['confluence'].identity_ok=False
        with self.assertRaises(SourceUnavailable):self.pilot.query(self.actor,'novelty')
        self.assertEqual(self.pilot.engine.model.calls,[])

    def test_multiple_windows_share_only_the_same_stage_resource_check(self):
        page=self.http['confluence'].content['98565']
        page['version']['number']=2
        page['body']['storage']['value']='<p>[SYNTHETIC] '+('novelty discovery. '*500)+'</p>'
        self.clock+=10000;self.worker.run_once()
        answer=self.pilot.query(self.actor,'novelty')
        windows=[e for e in answer['evidence'] if e['resource_id']=='confluence:98565']
        self.assertGreater(len(windows),1)
        events=[e for e in self.pilot.audit.export() if e['request_id']==answer['request_id']
                and e['event_type']=='authorization_decided' and e['payload']['resource_id']=='confluence:98565']
        for phase in ('before_model','model_dispatch','before_dispatch'):
            self.assertEqual(sum(e['payload']['phase']==phase for e in events),1)

    def test_native_new_counterevidence_recovers_once_and_invalidates_old_history(self):
        first=self.pilot.query(self.actor,'novelty')
        old=next(e for e in first['evidence'] if e['source']=='confluence')
        self.pilot.engine.model.calls.clear()
        page=self.http['confluence'].content['98565']
        page['version']['number']=2
        page['body']['storage']['value']='<p>[SYNTHETIC] novelty discovery was cancelled</p>'
        recovered=self.pilot.query(self.actor,'novelty')
        self.assertEqual(len(self.pilot.engine.model.calls),1)
        self.assertTrue(any('discovery was cancelled' in e['text'] and e['version']==2 for e in recovered['evidence']))
        events=self.pilot.audit.export()
        request=next(e['request_id'] for e in reversed(events) if e['event_type']=='request_started')
        self.assertTrue(any(e['event_type']=='version_recovery' and e['request_id']==request and e['payload']['result']=='published' for e in events))
        self.assertTrue(any(e['request_id']==request and e['payload'].get('method')=='confluence-version-changed' for e in events))
        with self.assertRaises(PermissionError):self.pilot.evidence(self.actor,old['evidence_id'])
        self.assertTrue(self.pilot.history(self.actor,first['request_id'])[0]['unavailable'])
        self.clock+=10000
        self.worker.run_once()
        current=self.pilot.query(self.actor,'novelty')
        self.assertTrue(any('discovery was cancelled' in e['text'] and e['version']==2 for e in current['evidence']))

    def test_failed_backlogged_expired_or_stopped_worker_is_not_no_evidence(self):
        for state in ('failed','backlog','expired','stopped'):
            with self.subTest(state=state):
                self.worker.last['confluence']['status']='complete';self.clock=0
                if state in ('failed','backlog'):self.worker.last['confluence']['status']=state
                if state=='expired':self.clock=121
                if state=='stopped':self.worker.stop_event.set()
                with self.assertRaises(SourceUnavailable):self.pilot.query(self.actor,'unfindable')
                self.assertEqual(self.pilot.engine.model.calls,[])
        self.assertEqual(self.store.history('eng_b'),[])

    def test_restart_needs_new_publication_and_other_actor_does_not_inherit_snapshot(self):
        self.assertEqual(self.pilot.query(Actor('product_ops','pilot'),'novelty')['evidence'],[])
        fresh=DelegatedQueryPilot(self.readers,self.store)
        worker=ContainerDiscovery(fresh,self.actor,clock=lambda:0)
        self.assertEqual(worker.published_versions,{})
        # This process-local snapshot is not restored from successful DB checkpoints.
        self.assertIsNone(worker.query_snapshot(self.actor))
        worker.close()

    def test_http_waiting_for_worker_does_not_hold_store_lock(self):
        import http.client
        import threading
        from brain.operator_web import OperatorApp
        from brain.server import create_server
        self.worker.close()
        app=OperatorApp(self.readers,self.store,'eng_b')
        attempting=threading.Event();worker_holding=threading.Event();committed=threading.Event()
        class ObservedLock:
            def __enter__(inner):attempting.set();app.pilot.lock.acquire()
            def __exit__(inner,*args):app.pilot.lock.release()
        app.request_lock=ObservedLock()
        server=create_server(app,0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        def publish():
            with app.pilot.lock:
                worker_holding.set()
                if attempting.wait(2):
                    with self.store.transaction() as db:db.execute('SELECT 1')
                    committed.set()
        writer=threading.Thread(target=publish,daemon=True);writer.start()
        self.assertTrue(worker_holding.wait(2))
        connection=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=3)
        self.addCleanup(connection.close)
        # Health intentionally bypasses query locks; History retains the lock order.
        import time
        app.sessions['lock-test']={'actor':app.actor,'csrf':'test','expires':time.monotonic()+60,'last_query':0}
        connection.request('GET','/api/history',headers={'Cookie':server.session_cookie_name+'=lock-test'});response=connection.getresponse();response.read()
        writer.join(2)
        self.assertFalse(writer.is_alive());self.assertTrue(committed.is_set());self.assertEqual(response.status,200)


if __name__=='__main__':unittest.main()
