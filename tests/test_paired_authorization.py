import copy
import threading
import unittest
from unittest.mock import patch

from brain.confluence import SourceUnavailable
from brain.contracts import Actor
from brain.discovery import ContainerDiscovery
from brain.engine import FakeExtractiveModel
from scripts.validation_timing import Measurements
from test_container_discovery import setup


class PairedAuthorization(unittest.TestCase):
    def prepare(self, concurrency=2, count=3):
        store, pilot, http, _ = setup()
        self.addCleanup(store.db.close)
        for index in range(2, count):
            extra = copy.deepcopy(http['confluence'].content['98565'])
            extra['id'] = str(98564 + index)
            http['confluence'].content[extra['id']] = extra
        actor = Actor('eng_b', 'pilot')
        worker = ContainerDiscovery(pilot, actor, bounded_queries=True)
        worker.start()
        worker.run_once()
        self.addCleanup(worker.close)
        pilot.authority.read_concurrency = concurrency
        return store, pilot, http, actor

    def test_four_reads_join_before_fifth_and_preserve_context(self):
        store, pilot, _, actor = self.prepare(4, 5)
        authority = pilot.authority
        resources = [r for r in store.resources() if r['source'] == 'confluence']
        self.assertEqual(len(resources), 5)
        original = authority._checked_read
        entered, release = threading.Barrier(5), threading.Event()
        seen, result = [], []
        before = copy.deepcopy(authority.resources)
        measured = Measurements()
        def read(actor, resource, reader, dynamic):
            seen.append((resource['id'], measured.phase_name.get(), measured.authorization_name.get()))
            if len(seen) <= 4:
                entered.wait(2)
                if not release.wait(2): raise RuntimeError('Test synchronization failed')
            return original(actor, resource, reader, dynamic)
        def run():
            with pilot.lock, measured.phase('query'), measured.authorization_phase('review_dispatch'):
                result.extend(authority.check_many(actor, resources, phase='review_dispatch'))
        with patch.object(authority, '_checked_read', side_effect=read):
            thread = threading.Thread(target=run, daemon=True);thread.start()
            try:
                entered.wait(2)
                self.assertEqual(len(seen), 4)
                self.assertEqual(authority.resources, before)
                self.assertEqual(result, [])
            finally:
                release.set();thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual([d.result for d in result], ['allow']*5)
        self.assertTrue(all(p == 'query' and a == 'review_dispatch' for _, p, a in seen))

    def test_four_read_unknown_does_not_admit_fifth(self):
        store, pilot, _, actor = self.prepare(4, 5)
        authority = pilot.authority
        resources = sorted([r for r in store.resources() if r['source'] == 'confluence'], key=lambda r:r['id'])
        original, calls = authority._checked_read, []
        def read(actor, resource, reader, dynamic):
            calls.append(resource['id'])
            if resource['id'] == resources[0]['id']: raise RuntimeError('private failure')
            return original(actor, resource, reader, dynamic)
        with patch.object(authority, '_checked_read', side_effect=read), pilot.lock:
            decisions = authority.check_many(actor, resources, phase='review_dispatch')
        self.assertEqual([d.result for d in decisions], ['unknown', 'allow', 'allow', 'allow', 'unknown'])
        self.assertEqual(set(calls), {r['id'] for r in resources[:4]})
        self.assertEqual(decisions[-1].method, 'source-lane-not-attempted')

    def test_four_read_late_changes_still_stop_delivery(self):
        prepare = self.prepare
        with patch.object(self, 'prepare', side_effect=lambda: prepare(4, 5)):
            self.test_late_revocation_unknown_version_and_deletion_still_stop_delivery()

    def test_two_in_flight_then_join_preserves_order_context_and_content(self):
        store, pilot, _, actor = self.prepare()
        authority = pilot.authority
        resources = [r for r in store.resources() if r['source'] == 'confluence']
        original = authority._checked_read
        entered = threading.Barrier(3)
        release = threading.Event()
        seen = []
        result = []
        before = copy.deepcopy(authority.resources)
        measured = Measurements()
        def read(actor, resource, reader, dynamic):
            seen.append((resource['id'], measured.phase_name.get(), measured.authorization_name.get()))
            if len(seen) <= 2:
                entered.wait(2)
                if not release.wait(2):
                    raise RuntimeError('Test synchronization failed')
            return original(actor, resource, reader, dynamic)
        def run():
            with pilot.lock, measured.phase('query'), measured.authorization_phase('review_dispatch'):
                result.extend(authority.check_many(actor, resources, phase='review_dispatch'))
        with patch.object(authority, '_checked_read', side_effect=read):
            thread = threading.Thread(target=run, daemon=True)
            thread.start()
            try:
                entered.wait(2)
                self.assertEqual(len(seen), 2)
                self.assertEqual(authority.resources, before)
                self.assertEqual(result, [])
            finally:
                release.set()
                thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual([d.result for d in result], ['allow']*3)
        self.assertEqual({rid for rid, _, _ in seen}, {r['id'] for r in resources})
        self.assertTrue(all(p == 'query' and a == 'review_dispatch' for _, p, a in seen))

    def test_unknown_stops_next_pair_without_retry_or_missing_decision(self):
        store, pilot, _, actor = self.prepare()
        authority = pilot.authority
        resources = sorted([r for r in store.resources() if r['source'] == 'confluence'], key=lambda r:r['id'])
        original = authority._checked_read
        calls = []
        def read(actor, resource, reader, dynamic):
            calls.append(resource['id'])
            if resource['id'] == resources[0]['id']:
                raise RuntimeError('private failure details')
            return original(actor, resource, reader, dynamic)
        with patch.object(authority, '_checked_read', side_effect=read), pilot.lock:
            decisions = authority.check_many(actor, resources, phase='review_dispatch')
        self.assertEqual([d.result for d in decisions], ['unknown', 'allow', 'unknown'])
        self.assertEqual(set(calls), {r['id'] for r in resources[:2]})
        self.assertEqual(len(calls), 2)
        self.assertEqual(decisions[-1].method, 'source-lane-not-attempted')
        self.assertNotIn('private failure', str(decisions))

    def test_late_revocation_unknown_version_and_deletion_still_stop_delivery(self):
        for phase in ('review_dispatch', 'before_dispatch'):
            for outcome in ('deny', 'unknown', 'version', 'deleted'):
                with self.subTest(phase=phase, outcome=outcome):
                    store, pilot, http, actor = self.prepare()
                    def change():
                        source = http['confluence']
                        if outcome == 'deny': source.fail_native.add('98565')
                        elif outcome == 'unknown': source.identity_ok = False
                        elif outcome == 'version': source.content['98565']['version']['number'] += 1
                        else: del source.content['98565']
                    class StageModel(FakeExtractiveModel):
                        def generate_with_authorization(inner, question, evidence, rid, authorize):
                            if phase == 'review_dispatch': change()
                            authorize('review_dispatch')
                            return inner.generate(question, evidence)
                    pilot.engine.model = StageModel()
                    if phase == 'before_dispatch': pilot.engine.before_dispatch = change
                    with self.assertRaises((PermissionError, SourceUnavailable)):
                        pilot.query(actor, 'novelty')
                    self.assertEqual(store.history(actor.user_id), [])
                    self.assertFalse(any(e['event_type'] == 'response_committed' for e in pilot.audit.export()))
