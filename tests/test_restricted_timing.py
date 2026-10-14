"""Private timing, offline delegates/model and fixture HTTP only."""
import copy
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from brain.contracts import Actor
from brain.discovery import ContainerDiscovery
from brain.timing import PrivateTiming, request_scope, span, acquire, install, attach_discovery
import test_source_review as model_setup
from test_container_discovery import setup
import test_http as http_setup
import test_source_review_dispatch_contract as contract_setup


class RestrictedTiming(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name).resolve() / 'timing'

    def recorder(self, **kwargs):
        recorder = PrivateTiming(self.directory, **kwargs)
        self.addCleanup(recorder.close)
        return recorder

    def records(self):
        return [json.loads(p.read_text()) for p in self.directory.glob('*.json')]

    def test_monotonic_nested_offsets_privacy_and_private_files(self):
        ticks = iter([100, 101, 102, 104, 106])
        app = SimpleNamespace(private_timing=self.recorder(clock=lambda: next(ticks)))
        secret = RuntimeError('secret-token secret-url secret-question secret-title')
        with request_scope(app, 'query'):
            with self.assertRaises(RuntimeError) as caught:
                with span('native_http', 'drive', endpoint='secret-endpoint'):
                    raise secret
        self.assertIs(caught.exception, secret)
        record = self.records()[0]
        root, child = record['spans']
        self.assertEqual(root['start_offset_seconds'], 1)
        self.assertEqual(root['duration_seconds'], 5)
        self.assertEqual(child['start_offset_seconds'], 2)
        self.assertEqual(child['duration_seconds'], 2)
        self.assertEqual(child['parent_span_id'], root['span_id'])
        self.assertEqual(child['outcome'], 'unavailable')
        self.assertEqual(child['endpoint'], 'other')
        self.assertNotIn('secret', json.dumps(record))
        self.assertEqual(self.directory.stat().st_mode & 0o777, 0o700)
        self.assertTrue(all(p.stat().st_mode & 0o777 == 0o600 for p in self.directory.glob('*.json')))

    def test_bound_and_clock_or_sink_failure_never_change_business(self):
        recorder = self.recorder(max_spans=2)
        app = SimpleNamespace(private_timing=recorder)
        calls = []
        with request_scope(app, 'query'):
            for i in range(10):
                with span('native_http', 'drive'):
                    calls.append(i)
        record = self.records()[0]
        self.assertEqual(calls, list(range(10)))
        self.assertEqual(len(record['spans']), 2)
        self.assertTrue(record['incomplete'])
        secret = PermissionError('private original error')
        with patch.object(recorder, 'save', side_effect=OSError('secret disk failure')):
            with self.assertRaises(PermissionError) as caught:
                with request_scope(app, 'query'):
                    raise secret
        self.assertIs(caught.exception, secret)
        with patch.object(recorder, 'clock', side_effect=ValueError('secret clock failure')):
            with request_scope(app, 'query'):
                calls.append('clock-independent')
        self.assertEqual(calls[-1], 'clock-independent')

    def test_unknown_category_and_backward_clock_mark_incomplete_only(self):
        ticks=iter([100,101,102,99,103])
        app=SimpleNamespace(private_timing=self.recorder(clock=lambda:next(ticks)))
        with request_scope(app,'query'):
            with span('private-title','private-source'):
                pass
            with span('commit'):
                pass
        record=self.records()[0]
        self.assertTrue(record['incomplete'])
        self.assertNotIn('private',json.dumps(record))

    def test_disabled_and_failed_scope_release_lock_and_context(self):
        lock = threading.RLock()
        with self.assertRaises(KeyboardInterrupt):
            with request_scope(SimpleNamespace(), 'query'):
                with acquire(lock):
                    raise KeyboardInterrupt()
        result = []
        def other():
            result.append(lock.acquire(blocking=False))
            if result[-1]: lock.release()
        thread=threading.Thread(target=other);thread.start();thread.join(2)
        self.assertEqual(result,[True])
        self.assertFalse(self.directory.exists())
        app=SimpleNamespace(private_timing=self.recorder())
        with request_scope(app,'preview'):
            with span('native_http','drive'):pass
        with span('native_http','drive'):pass
        self.assertEqual(len(self.records()),1)
        self.assertEqual(len(self.records()[0]['spans']),2)

    def test_original_context_manager_protocol_and_exception_suppression(self):
        observed=[];value=object()
        class ObservedLock:
            def __enter__(self):
                observed.append('enter');return value
            def __exit__(self,kind,error,traceback):
                observed.append(kind);return kind is PermissionError
        app=SimpleNamespace(private_timing=self.recorder())
        with request_scope(app,'query'):
            with acquire(ObservedLock()) as entered:
                self.assertIs(entered,value)
                raise PermissionError('original suppressed error')
        self.assertEqual(observed,['enter',PermissionError])
        record=self.records()[0]
        self.assertEqual(next(s for s in record['spans'] if s['category']=='lock_held')['outcome'],'deny')

    def test_background_cycles_have_separate_private_request_contexts(self):
        store,pilot,_,_=setup();self.addCleanup(store.db.close)
        actor=Actor('eng_b','pilot');worker=ContainerDiscovery(pilot,actor,bounded_queries=True)
        app=SimpleNamespace(engine=pilot.engine,world=pilot.authority,store=store)
        recorder=install(app,self.directory);self.addCleanup(recorder.close)
        attach_discovery(app,worker)
        results=worker.run_once()
        self.assertTrue(all(r['status']=='complete' for r in results.values()))
        records=self.records()
        self.assertEqual(len(records),4)
        self.assertEqual({r['operation'] for r in records},{'background_discovery'})
        self.assertEqual(len({r['request_id'] for r in records}),4)
        self.assertTrue(all(any(s['category']=='native_http' for s in r['spans']) for r in records))
        self.assertNotIn('Bearer',json.dumps(records))

    def test_public_directory_or_symlink_is_rejected_without_chmod(self):
        self.directory.mkdir(mode=0o755)
        with self.assertRaises(ValueError):PrivateTiming(self.directory)
        self.assertEqual(self.directory.stat().st_mode & 0o777,0o755)
        link=self.directory.parent/'link';link.symlink_to(self.directory, target_is_directory=True)
        with self.assertRaises(ValueError):PrivateTiming(link)

    def test_real_mock_parallel_lanes_keep_parent_request_and_phase(self):
        store,pilot,http,_=setup();self.addCleanup(store.db.close)
        actor=Actor('eng_b','pilot');worker=ContainerDiscovery(pilot,actor,bounded_queries=True)
        worker.run_once();worker.background_started=True
        app=SimpleNamespace(engine=pilot.engine,world=pilot.authority,store=store)
        recorder=install(app,self.directory);self.addCleanup(recorder.close)
        resources=store.resources();original=pilot.authority._checked_read
        entered={s:threading.Event() for s in http};release=threading.Event();errors=[]
        def read(actor,resource,reader,dynamic):
            entered[resource['source']].set()
            if not release.wait(3):raise RuntimeError('Test release missing')
            return original(actor,resource,reader,dynamic)
        def request():
            try:
                with request_scope(app,'query'), acquire(pilot.lock):
                    self.assertTrue(all(pilot.engine.checks(actor,resources,'a'*32,'review_dispatch')))
            except BaseException as error:errors.append(error)
        with patch.object(pilot.authority,'_checked_read',side_effect=read):
            thread=threading.Thread(target=request);thread.start()
            try:self.assertTrue(all(e.wait(2) for e in entered.values()))
            finally:release.set();thread.join(3)
        self.assertFalse(thread.is_alive());self.assertEqual(errors,[])
        record=self.records()[0];spans=record['spans']
        lanes=[s for s in spans if s['category']=='source_lane']
        self.assertEqual({s['source'] for s in lanes},set(http))
        self.assertTrue(all(s['authorization_phase']=='review_dispatch' for s in lanes))
        parents={s['span_id']:s for s in spans}
        self.assertTrue(all(parents[s['parent_span_id']]['category']=='authorization' for s in lanes))
        # The lanes were concurrently open, not serially added as wall time.
        self.assertLess(max(s['start_offset_seconds'] for s in lanes),
                        min(s['start_offset_seconds']+s['duration_seconds'] for s in lanes))
        self.assertTrue(any(s.get('endpoint')=='file_body' for s in spans))
        self.assertNotIn('Bearer',json.dumps(record))

    def test_instrumented_model_preserves_inputs_receipts_and_security_events(self):
        results=[]
        for enabled in (False,True):
            harness=model_setup.SourceReview();harness.setUp()
            try:
                engine,world=harness.engine();harness.dynamic_review()
                app=SimpleNamespace(engine=engine,world=world,store=engine.store)
                recorder=None
                if enabled:recorder=install(app,self.directory)
                try:
                    with request_scope(app,'query'):
                        answer=engine.query(Actor('eng_b'),'payment-service incident runbook')
                    events=[e['event_type'] for e in engine.audit.export()]
                    results.append((copy.deepcopy(harness.transport.calls),answer['claims'],events,
                                    harness.ledger.summary()['settled_micro_usd']))
                finally:
                    if recorder:recorder.close()
            finally:harness.tearDown();harness.doCleanups()
        self.assertEqual(results[0],results[1])
        record=self.records()[0]
        categories={s['category'] for s in record['spans']}
        self.assertTrue({'source_claims','model_input','model_transport','model_output','ledger','commit','retrieval'}<=categories)
        phases={s['authorization_phase'] for s in record['spans'] if s['category']=='authorization'}
        self.assertTrue({'before_model','model_dispatch','review_dispatch','before_dispatch'}<=phases)
        self.assertNotIn('SYNTHETIC',json.dumps(record))
        self.assertEqual(len([s for s in record['spans'] if s['category']=='model_transport']),1)

    def test_enabled_timing_keeps_late_change_contracts(self):
        directory=self.directory
        class Enabled(contract_setup.DispatchContract):
            def engine(inner):
                engine,world=super().engine()
                app=SimpleNamespace(engine=engine,world=world,store=engine.store)
                recorder=install(app,directory);inner.addCleanup(recorder.close)
                original=engine.query
                def query(*args,**kwargs):
                    with request_scope(app,'query'):return original(*args,**kwargs)
                engine.query=query
                return engine,world
        for method in ('test_change_during_quote_construction_blocks_dispatch_without_reservation',
                       'test_change_after_mock_review_blocks_delivery_but_preserves_usage'):
            result=unittest.TestResult();Enabled(method).run(result)
            self.assertEqual(result.errors,[]);self.assertEqual(result.failures,[])
        self.assertEqual(len(self.records()),8)

    def test_mock_timeout_preserves_unknown_budget_and_failure_events(self):
        from brain.deepseek import ModelRequestUnavailable
        results=[]
        for enabled in (False,True):
            harness=model_setup.SourceReview();harness.setUp()
            try:
                engine,world=harness.engine()
                app=SimpleNamespace(engine=engine,world=world,store=engine.store)
                recorder=install(app,self.directory) if enabled else None
                try:
                    with patch.object(harness.transport,'_send',side_effect=TimeoutError('private URL token question')):
                        with self.assertRaises(ModelRequestUnavailable):
                            with request_scope(app,'query'):
                                engine.query(Actor('eng_b'),'payment-service incident runbook')
                    events=engine.audit.export()
                    receipt=next(e['payload']['receipt'] for e in events if e['event_type']=='model_request_unavailable')
                    self.assertEqual(receipt['state'],'dispatched')
                    self.assertEqual(receipt['outcome'],'usage_unavailable')
                    self.assertIsNone(receipt['called'])
                    self.assertEqual(harness.ledger.summary()['pending_requests'],1)
                    self.assertEqual(engine.store.history('eng_b'),[])
                    results.append((harness.ledger.summary(),[e['event_type'] for e in events]))
                finally:
                    if recorder:recorder.close()
            finally:harness.tearDown();harness.doCleanups()
        self.assertEqual(results[0],results[1])
        record=self.records()[0]
        self.assertNotIn('private',json.dumps(record))
        self.assertEqual(next(s for s in record['spans'] if s['category']=='model_transport')['outcome'],'unavailable')

    def test_fixture_http_request_ids_lock_scopes_preview_and_no_timing_api(self):
        harness=http_setup.HTTP();harness.setUp()
        recorder=install(harness.app,self.directory)
        saved=threading.Event();original_save=recorder.save
        def save(state):
            original_save(state);saved.set()
        recorder.save=save
        try:
            harness.login()
            before=len(self.records())
            status,_=harness.request('/api/query',{'question':'payment-service'},extra={'Cookie':''})
            self.assertEqual(status,403);self.assertEqual(len(self.records()),before)
            status,answer=harness.request('/api/query',{'question':'payment-service incident runbook'})
            self.assertEqual(status,200)
            self.assertTrue(saved.wait(2));saved.clear()
            query=next(r for r in self.records() if r['operation']=='query')
            self.assertEqual(query['request_id'],answer['request_id'])
            self.assertEqual(query['spans'][0]['outcome'],'ok')
            self.assertEqual(len([s for s in query['spans'] if s['category']=='lock_wait']),2)
            self.assertNotIn('spans',answer);self.assertNotIn('timing',json.dumps(answer))
            eid=answer['evidence'][0]['evidence_id']
            self.assertEqual(harness.request('/api/evidence/'+eid)[0],200)
            self.assertTrue(saved.wait(2));saved.clear()
            self.assertEqual(harness.request('/api/history')[0],200)
            self.assertTrue(saved.wait(2));saved.clear()
            self.assertEqual({r['operation'] for r in self.records()},{'query','preview','history'})
            self.assertEqual(harness.request('/api/timing')[0],404)
        finally:
            harness.tearDown();recorder.close()


if __name__=='__main__':unittest.main()
