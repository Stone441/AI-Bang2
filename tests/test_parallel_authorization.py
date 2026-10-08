import threading
import unittest
from unittest.mock import patch

from brain.contracts import Actor
from brain.discovery import ContainerDiscovery
from scripts.validation_timing import Measurements
from test_container_discovery import setup


class ParallelAuthorizationTests(unittest.TestCase):
    def test_four_source_lanes_are_bounded_request_local_and_join_before_updates(self):
        store,pilot,_,_=setup();self.addCleanup(store.db.close)
        actor=Actor('eng_b','pilot');worker=ContainerDiscovery(pilot,actor,bounded_queries=True)
        worker.start();worker.run_once();self.addCleanup(worker.close)
        resources=store.resources();authority=pilot.authority;original=authority._checked_read
        entered={s:threading.Event() for s in authority.readers};release=threading.Event()
        guard=threading.Lock();active={s:0 for s in entered};maximum=dict(active);calls=[];errors=[]
        measured=Measurements()
        def read(actor,resource,reader,dynamic):
            source=resource['source']
            with guard:
                active[source]+=1;maximum[source]=max(maximum[source],active[source])
                calls.append((source,measured.phase_name.get(),measured.authorization_name.get()))
            entered[source].set()
            try:
                if not release.wait(3):raise RuntimeError('Test release missing')
                return original(actor,resource,reader,dynamic)
            finally:
                with guard:active[source]-=1
        results=[];before=dict(authority.resources)
        def request():
            try:
                with pilot.lock,measured.phase('query'),measured.authorization_phase('review_dispatch'):
                    results.extend(authority.check_many(actor,resources,phase='review_dispatch'))
            except BaseException as error:errors.append(error)
        with patch.object(authority,'_checked_read',side_effect=read):
            thread=threading.Thread(target=request,daemon=True);thread.start()
            try:
                self.assertTrue(all(event.wait(2) for event in entered.values()))
                self.assertEqual(authority.resources,before)
                self.assertEqual(results,[])
            finally:release.set();thread.join(3)
        self.assertFalse(thread.is_alive());self.assertEqual(errors,[])
        self.assertEqual(maximum,{s:1 for s in entered})
        self.assertEqual(len(calls),len(resources))
        self.assertTrue(all(p=='query' and phase=='review_dispatch' for _,p,phase in calls))
        self.assertTrue(all(d.result=='allow' for d in results))

    def test_source_exception_preserves_ordered_decisions_and_stops_lane(self):
        from brain.confluence import SourceUnavailable
        store,pilot,_,_=setup();self.addCleanup(store.db.close)
        actor=Actor('eng_b','pilot');worker=ContainerDiscovery(pilot,actor,bounded_queries=True)
        worker.start();worker.run_once();self.addCleanup(worker.close)
        original=pilot.authority._checked_read;calls=[]
        def read(actor,resource,reader,dynamic):
            calls.append(resource['id'])
            if resource['source']=='jira':raise RuntimeError('Unsafe vendor detail must not escape')
            return original(actor,resource,reader,dynamic)
        with patch.object(pilot.authority,'_checked_read',side_effect=read):
            with self.assertRaises(SourceUnavailable):pilot.query(actor,'novelty')
        self.assertEqual(pilot.engine.model.calls,[])
        self.assertEqual(sum(r.startswith('jira:') for r in calls),1)
        events=pilot.audit.export()
        rid=next(e['request_id'] for e in reversed(events) if e['event_type']=='request_started')
        decisions=[e['payload'] for e in events if e['request_id']==rid and e['event_type']=='authorization_decided']
        self.assertTrue(any(e['source']=='confluence' and e['result']=='allow' for e in decisions))
        self.assertTrue(any(e['source']=='jira' and e['result']=='unknown' for e in decisions))
        self.assertNotIn('Unsafe vendor',str(events))

    def test_review_and_return_use_new_native_checks_after_revocation_or_unknown(self):
        from brain.confluence import SourceUnavailable
        from brain.engine import FakeExtractiveModel
        for phase in ('review_dispatch','before_dispatch'):
            for outcome in ('deny','unknown'):
                with self.subTest(phase=phase,outcome=outcome):
                    store,pilot,http,_=setup()
                    actor=Actor('eng_b','pilot');worker=ContainerDiscovery(pilot,actor,bounded_queries=True)
                    worker.start();worker.run_once()
                    def change():
                        if outcome=='deny':http['confluence'].fail_native.add('98565')
                        else:http['confluence'].identity_ok=False
                    class StageModel(FakeExtractiveModel):
                        def generate_with_authorization(inner,question,evidence,rid,authorize):
                            if phase=='review_dispatch':change()
                            authorize('review_dispatch')
                            return inner.generate(question,evidence)
                    pilot.engine.model=StageModel()
                    if phase=='before_dispatch':pilot.engine.before_dispatch=change
                    try:
                        with self.assertRaises((PermissionError,SourceUnavailable)):pilot.query(actor,'novelty')
                        events=pilot.audit.export()
                        rid=next(e['request_id'] for e in reversed(events) if e['event_type']=='request_started')
                        self.assertFalse(any(e['request_id']==rid and e['event_type']=='response_committed' for e in events))
                        self.assertTrue(any(e['request_id']==rid and e['payload'].get('phase')==phase
                                            and e['payload'].get('result')==outcome for e in events))
                        self.assertEqual(store.history('eng_b'),[])
                    finally:worker.close();store.db.close()


if __name__=='__main__':unittest.main()
