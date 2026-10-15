"""Persistent worker lifecycle using real adapters and offline platform responses."""
import json
import threading
import unittest
from unittest.mock import patch

from brain.audit import verify_chain
from brain.confluence import SourceUnavailable
from brain.contracts import Actor
from brain.discovery import ContainerDiscovery
from test_container_discovery import setup
from test_jira import document


class ContinuousSources(unittest.TestCase):
    def setUp(self):
        self.store,self.pilot,self.http,_=setup()
        self.addCleanup(self.store.db.close)
        self.actor=Actor('eng_b','pilot');self.clock=0
        self.worker=ContainerDiscovery(self.pilot,self.actor,clock=lambda:self.clock,bounded_queries=True)
        self.finished=threading.Event()
        finish=self.worker._finish_cycle
        def observed(source,*args):
            finish(source,*args)
            if source=='slack':self.finished.set()
        observer=patch.object(self.worker,'_finish_cycle',side_effect=observed)
        observer.start();self.addCleanup(observer.stop)
        self.worker.start();self.addCleanup(self.worker.close)
        self.assertTrue(self.finished.wait(4),'Initial background cycle did not complete')
        self.thread=self.worker.thread

    def cycle(self):
        self.finished.clear();self.clock+=10000
        self.assertTrue(self.finished.wait(4),'Background polling failed to continue')
        self.assertIs(self.worker.thread,self.thread)
        self.assertTrue(self.thread.is_alive())

    def test_four_source_updates_publish_on_same_worker_without_query_refresh(self):
        old=self.pilot.query(self.actor,'novelty')
        for revision in (2,3):
            text=f'[SYNTHETIC] novelty revision{revision} limited pilot; general availability not approved'
            cf=self.http['confluence'].content['98565']
            cf['version']['number']=revision;cf['body']['storage']['value']='<p>'+text+'</p>'
            self.http['jira'].content['10015']['fields']['description']=document(text)
            self.http['slack'].content[self.http['slack'].newts]['text']=text
            self.http['drive'].content['FILE2']=self.http['drive'].file('FILE2',text,revision)
            self.cycle()
            self.assertEqual({r['status'] for r in self.worker.last.values()},{'complete'})
            # Check publication BEFORE asking, so synchronous query recovery cannot hide a broken worker.
            for source,native in [('confluence','98565'),('jira','10015'),('slack',self.http['slack'].channel['id']+'/'+self.http['slack'].newts),('drive','FILE2')]:
                self.assertIn('revision'+str(revision),self.store.get(source+':'+native)['text'])
            answer=self.pilot.query(self.actor,'novelty')
            for source in self.http:
                self.assertTrue(any(e['source']==source and 'revision'+str(revision) in e['text'] for e in answer['evidence']))
        self.assertTrue(self.pilot.history(self.actor,old['request_id'])[0]['unavailable'])
        self.assertTrue(verify_chain(self.pilot.audit.export())['valid'])

    def test_failed_source_blocks_then_recovers_without_restart(self):
        self.http['jira'].identity_ok=False;self.cycle()
        self.assertEqual(self.worker.last['jira']['status'],'failed')
        with self.assertRaises(SourceUnavailable):self.pilot.query(self.actor,'novelty')
        self.assertEqual(self.pilot.engine.model.calls,[])
        self.http['jira'].identity_ok=True;self.cycle()
        answer=self.pilot.query(self.actor,'novelty')
        self.assertEqual({e['source'] for e in answer['evidence']},set(self.http))


class NativeBoundaryMatrix(unittest.TestCase):
    """Source API semantics are mocked; these are not real-account acceptance results."""
    def test_each_source_revocation_protects_model_history_and_preview(self):
        for source,native in [('confluence','98564'),('jira','10004'),('slack',None),('drive','FILE1')]:
            with self.subTest(source=source):
                store,pilot,http,_=setup()
                try:
                    actor=Actor('eng_b','pilot')
                    first=pilot.query(actor,'baseline')
                    target=next(e for e in first['evidence'] if e['source']==source)
                    other=next(e for e in first['evidence'] if e['source']!=source)
                    http[source].fail_native.add(native or http['slack'].root)
                    answer=pilot.query(actor,'baseline')
                    self.assertNotIn(source,{e['source'] for e in answer['evidence']})
                    self.assertNotIn(source,{e['source'] for e in pilot.engine.model.calls[-1]['evidence']})
                    self.assertTrue(pilot.history(actor,first['request_id'])[0]['unavailable'])
                    with self.assertRaises(PermissionError):pilot.evidence(actor,target['evidence_id'])
                    self.assertEqual(pilot.evidence(actor,other['evidence_id'])['text'],other['text'])
                    http[source].fail_native.clear()
                    self.assertIn(source,{e['source'] for e in pilot.query(actor,'baseline')['evidence']})
                finally:store.db.close()

    def test_each_source_identity_mismatch_never_uses_another_identity(self):
        for source in ('confluence','jira','slack','drive'):
            with self.subTest(source=source):
                store,pilot,http,_=setup()
                try:
                    actor=Actor('eng_b','pilot');pilot.query(actor,'baseline')
                    http[source].identity_ok=False
                    answer=pilot.query(actor,'baseline')
                    self.assertNotIn(source,{e['source'] for e in answer['evidence']})
                    self.assertNotIn(source,{e['source'] for e in pilot.engine.model.calls[-1]['evidence']})
                    self.assertNotIn('Bearer',json.dumps(answer))
                finally:store.db.close()
