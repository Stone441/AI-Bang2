"""Deterministic offline interleavings; no credentials, sockets or model charges."""
import copy
import threading
import unittest
from unittest.mock import patch

from brain.audit import verify_chain
from brain.contracts import Actor
from brain.discovery import ContainerDiscovery
from test_container_discovery import setup


class DiscoveryContentionTests(unittest.TestCase):
    def setUp(self):
        self.store,self.pilot,self.http,_=setup()
        self.addCleanup(self.store.db.close)
        self.actor=Actor('eng_b','pilot');self.clock=0
        self.worker=ContainerDiscovery(self.pilot,self.actor,clock=lambda:self.clock)
        self.worker.run_once()
        self.answer=self.pilot.query(self.actor,'novelty')
        self.eid=next(e['evidence_id'] for e in self.answer['evidence'] if e['source']=='confluence')

    def blocked_cycle(self, operation):
        entered=threading.Event();release=threading.Event();finished=threading.Event();errors=[]
        transport=self.http['confluence'];original=transport.get
        def delayed(url,authorization):
            if '/spaces/' in url:
                entered.set()
                if not release.wait(4):raise RuntimeError('Test release missing')
            return original(url,authorization)
        def request():
            try:operation()
            except BaseException as error:errors.append(error)
            finally:finished.set()
        self.clock+=60
        with patch.object(transport,'get',side_effect=delayed):
            worker=threading.Thread(target=self.worker.run_once,daemon=True);worker.start()
            try:
                self.assertTrue(entered.wait(2))
                client=threading.Thread(target=request,daemon=True);client.start()
                completed=finished.wait(1)
            finally:
                release.set();worker.join(3)
                if 'client' in locals():client.join(3)
        self.assertFalse(worker.is_alive());self.assertFalse(client.is_alive())
        self.assertTrue(completed,'Request blocked behind discovery native listing')
        return errors

    def test_preview_does_not_wait_for_discovery_native_listing(self):
        results=[]
        self.assertEqual(self.blocked_cycle(lambda:results.append(self.pilot.evidence(self.actor,self.eid))),[])
        self.assertIn('novelty',results[0]['text'])
        self.assertTrue(verify_chain(self.pilot.audit.export())['valid'])

    def test_revoked_preview_and_history_still_check_native_during_discovery(self):
        self.http['confluence'].fail_native.add('98565')
        results=[]
        def request():
            with self.assertRaises(PermissionError):self.pilot.evidence(self.actor,self.eid)
            results.extend(self.pilot.history(self.actor,self.answer['request_id']))
        self.assertEqual(self.blocked_cycle(request),[])
        self.assertTrue(results[0]['unavailable'])

    def test_query_uses_complete_prior_snapshot_while_discovery_reads(self):
        self.worker.bounded_queries=True;self.worker.start()
        self.addCleanup(self.worker.close)
        answers=[]
        self.assertEqual(self.blocked_cycle(lambda:answers.append(self.pilot.query(self.actor,'novelty'))),[])
        events=[e for e in self.pilot.audit.export() if e['request_id']==answers[0]['request_id']]
        for evidence in answers[0]['evidence']:
            phases={e['payload'].get('phase') for e in events if e['event_type']=='authorization_decided'
                    and e['payload']['resource_id']==evidence['resource_id']}
            self.assertTrue({'before_model','model_dispatch','before_dispatch'}<=phases)
        self.assertTrue(verify_chain(self.pilot.audit.export())['valid'])

    def test_unknown_during_parallel_query_never_dispatches_model(self):
        self.worker.bounded_queries=True;self.worker.start();self.addCleanup(self.worker.close)
        self.http['jira'].identity_ok=False;self.pilot.engine.model.calls.clear()
        from brain.confluence import SourceUnavailable
        def request():
            with self.assertRaises(SourceUnavailable):self.pilot.query(self.actor,'novelty')
        self.assertEqual(self.blocked_cycle(request),[])
        self.assertEqual(self.pilot.engine.model.calls,[])

    def test_stale_fetch_cannot_overwrite_new_numeric_or_fingerprint_version(self):
        for source,native in [('confluence','98565'),('jira','10015')]:
            with self.subTest(source=source):
                entered=threading.Event();release=threading.Event();original=self.worker._reader
                def reader(kind,mappings,transport=None):
                    result=original(kind,mappings,transport)
                    if kind==source and transport is not None:
                        read=result.read
                        def delayed(actor,nid,*args):
                            value=copy.deepcopy(read(actor,nid,*args))
                            if nid==native:
                                entered.set()
                                if not release.wait(3):raise RuntimeError('Test release missing')
                            return value
                        result.read=delayed
                    return result
                self.clock+=10000
                with patch.object(self.worker,'_reader',side_effect=reader):
                    thread=threading.Thread(target=self.worker.run_once,daemon=True);thread.start()
                    try:
                        self.assertTrue(entered.wait(2))
                        content=self.http[source].content[native]
                        if source=='confluence':
                            content['version']['number']+=1
                            content['body']['storage']['value']='<p>[SYNTHETIC] newer novelty</p>'
                        else:content['fields']['status']['name']='Done'
                        self.pilot.query(self.actor,'novelty')
                        newer=self.store.get(source+':'+native)
                    finally:release.set();thread.join(3)
                self.assertFalse(thread.is_alive())
                self.assertEqual(self.store.get(source+':'+native)['version'],newer['version'])
                self.assertEqual(self.worker.last[source]['status'],'failed')

    def test_http_health_and_preview_do_not_wait_for_background_network(self):
        import http.client
        import json
        from urllib.parse import quote
        from brain.operator_web import OperatorApp
        from brain.server import create_server
        app=OperatorApp(self.pilot.authority.readers,self.store,'eng_b')
        app.pilot=self.pilot;app.engine=self.pilot.engine;app.world=self.pilot.authority
        app.audit=self.pilot.audit;app.request_lock=self.pilot.lock
        server=create_server(app,0);server_thread=threading.Thread(target=server.serve_forever,daemon=True)
        server_thread.start();self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        connection=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=2)
        self.addCleanup(connection.close)
        connection.request('POST',app.login_path,json.dumps({'ticket':app.bootstrap_ticket()}),{'Content-Type':'application/json'})
        login=connection.getresponse();cookie=login.getheader('Set-Cookie').split(';')[0];login.read()
        self.assertEqual(login.status,200)
        results=[]
        def request():
            for path in ['/api/health','/api/evidence/'+quote(self.eid,safe='')]:
                connection.request('GET',path,headers={'Cookie':cookie})
                response=connection.getresponse();response.read();results.append(response.status)
        self.assertEqual(self.blocked_cycle(request),[]);self.assertEqual(results,[200,200])

    def test_stop_in_flight_prevents_publication_and_fresh_worker_recovers(self):
        checkpoint=self.worker.last['confluence']['last_successful_checkpoint_at']
        self.assertEqual(self.blocked_cycle(self.worker.stop_event.set),[])
        self.assertEqual(self.worker.last['confluence']['status'],'failed')
        self.assertEqual(self.worker.last['confluence']['last_successful_checkpoint_at'],checkpoint)
        fresh=ContainerDiscovery(self.pilot,self.actor,clock=lambda:self.clock)
        self.assertEqual(fresh.published_versions,{})
        self.assertEqual({r['status'] for r in fresh.run_once().values()},{'complete'})

    def test_failed_publication_report_invalidates_prior_eligibility(self):
        original=self.pilot.audit.append
        def fail(event,actor,rid,payload):
            if event=='source_changed' and payload.get('status')=='complete':raise RuntimeError('Audit failure')
            return original(event,actor,rid,payload)
        self.clock+=60
        with patch.object(self.pilot.audit,'append',side_effect=fail):self.worker.run_once()
        self.assertEqual(self.worker.last['confluence']['status'],'failed')
        self.assertNotIn('confluence',self.worker.published_at)


if __name__=='__main__':unittest.main()
