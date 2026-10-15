import json
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from brain.contracts import Actor
from brain.run_state import runtime_status


class SourceFreshnessStatus(unittest.TestCase):
    def setUp(self):
        self.actor=Actor('eng_b','pilot')
        self.worker=SimpleNamespace(actor=self.actor,clock=lambda:100.0,
            last={'jira':{'status':'complete','observed_at':'2026-10-14T01:00:00Z',
                         'last_successful_checkpoint_at':'2026-10-14T01:00:05Z'}},
            published_at={'jira':90.0},due={'jira':150.0},checking=frozenset(),
            stop_event=threading.Event(),thread=Mock(is_alive=Mock(return_value=True)))
        self.app=SimpleNamespace(auth_kind='operator',world=SimpleNamespace(
            readers={'jira':SimpleNamespace(delegations={'eng_b':None})},discovery=self.worker),
            engine=SimpleNamespace(mode='multi_mock_http_fake_model',model=SimpleNamespace(name='fake'),query=lambda:None))

    def source(self,actor=None):
        return next(s for s in runtime_status(self.app,actor or self.actor,None)['sources'] if s['source']=='jira')

    def test_complete_publication_reports_age_deadline_and_distinct_success_time(self):
        row=self.source()
        self.assertEqual(row['snapshot_status'],'current')
        self.assertEqual(row['snapshot_age_seconds'],10.0)
        self.assertEqual(row['snapshot_max_age_seconds'],120)
        self.assertEqual(row['next_check_in_seconds'],50.0)
        self.assertEqual(row['last_successful_check_at'],'2026-10-14T01:00:05Z')
        self.assertNotEqual(row['last_check_at'],row['last_successful_check_at'])

    def test_dead_or_stopped_worker_cannot_report_current(self):
        self.worker.thread.is_alive.return_value=False
        self.assertEqual(self.source()['snapshot_status'],'unconfirmed')
        self.worker.thread.is_alive.return_value=True;self.worker.stop_event.set()
        self.assertEqual(self.source()['snapshot_status'],'unconfirmed')

    def test_expired_failed_and_backlogged_snapshots_are_not_current(self):
        self.worker.published_at['jira']=-21
        self.assertEqual(self.source()['snapshot_status'],'unconfirmed')
        for state in ('failed','backlog'):
            self.worker.published_at['jira']=90;self.worker.last['jira']['status']=state
            self.assertEqual(self.source()['snapshot_status'],'unconfirmed')
            self.assertEqual(self.source()['last_check_result'],state)

    def test_other_identity_cannot_obtain_source_timing_metadata(self):
        row=self.source(Actor('product_ops','pilot'))
        for key in ('last_check_at','last_successful_check_at','snapshot_age_seconds','next_check_in_seconds'):
            self.assertIsNone(row[key])
        self.assertNotIn('title',json.dumps(row));self.assertNotIn('resource_id',json.dumps(row))


class PreviewFreshness(unittest.TestCase):
    def test_current_preview_exposes_distinct_times_only_after_authorization(self):
        from brain.audit import Audit
        from brain.contracts import now
        from brain.engine import Engine
        from brain.sources import FixtureWorld
        from brain.store import Store
        world=FixtureWorld();store=Store();self.addCleanup(store.db.close)
        store.initialize(world);engine=Engine(store,world,Audit(store));actor=Actor('eng_a')
        before=now();preview=engine.evidence(actor,'C-01@1');after=now()
        resource=store.get('C-01')
        self.assertEqual(preview['source_updated_at'],resource['source_updated_at'])
        self.assertEqual(preview['indexed_at'],resource['indexed_at'])
        self.assertLessEqual(before,preview['checked_at']);self.assertLessEqual(preview['checked_at'],after)
        self.assertEqual(engine.model.calls,[])
        world.mutate('C-01','revoke',user_id='eng_a')
        with self.assertRaises(PermissionError):engine.evidence(actor,'C-01@1')
