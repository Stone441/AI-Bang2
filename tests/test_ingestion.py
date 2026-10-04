import copy
import json
import unittest
from brain.ingestion import Ingestion
from brain.store import Store
from brain.sources import FixtureWorld
from brain.engine import Engine
from brain.audit import Audit
from brain.contracts import Actor,now

class Incremental(unittest.TestCase):
    def setUp(self):
        self.w=FixtureWorld(); self.s=Store();self.s.initialize(self.w);self.i=Ingestion(self.s,self.w);self.e=Engine(self.s,self.w,Audit(self.s))
    def tearDown(self):self.s.db.close()
    def test_four_source_update_one_object_only(self):
        for rid in ['C-01','J-01','S-01','D-01']:
            with self.subTest(rid=rid):
                event=self.w.mutate(rid,'content',version=2,text='payment-service updated evidence '+rid,source_updated_at=now())
                result=self.i.process(event)
                self.assertEqual(result['processed_objects'],1)
                a=self.e.query(Actor('eng_a'),'payment-service updated')
                evidence=next(e for e in a['evidence'] if e['resource_id']==rid)
                self.assertEqual(evidence['version'],2)
                self.assertIn('updated evidence',evidence['text'])
        self.assertEqual(self.i.processed_objects,4)
        self.assertEqual(self.s.get('C-02')['version'],1)
    def test_duplicate_out_of_order_retry_atomic(self):
        event=self.w.mutate('C-01','content',version=2,text='payment-service v2',source_updated_at=now())
        self.i.fail_after_prepare=True
        with self.assertRaises(RuntimeError): self.i.process(event)
        self.assertEqual(self.s.get('C-01')['version'],1)
        self.assertEqual(self.s.db.execute('SELECT count(*) FROM versions WHERE id=?',('C-01',)).fetchone()[0],1)
        self.assertEqual(self.s.db.execute('SELECT cursor FROM sync WHERE source=?',('confluence',)).fetchone()[0],0)
        # Known stale evidence must not be advertised as latest while indexing is incomplete.
        self.assertNotIn('C-01',{x['resource_id'] for x in self.e.query(Actor('eng_a'),'latest runbook')['evidence']})
        self.i.fail_after_prepare=False
        self.assertEqual(self.i.process(event)['state'],'published')
        self.assertEqual(self.i.process(event)['state'],'duplicate')
        old=copy.deepcopy(event);old['event_id']=99;old['snapshot']['version']=1;old['snapshot']['text']='old content'
        self.i.process(old)
        self.assertEqual(self.s.get('C-01')['version'],2)
        self.assertEqual(self.s.db.execute('SELECT attempts FROM jobs WHERE event_id=?',(event['event_id'],)).fetchone()[0],2)
    def test_revoke_no_reindex_delete_immediate_and_history_version(self):
        before=self.e.query(Actor('eng_a'),'runbook')
        event=self.w.mutate('C-01','content',version=2,text='runbook changed',source_updated_at=now());self.i.process(event)
        with self.assertRaises(PermissionError):self.e.evidence(Actor('eng_a'),'C-01@1')
        self.assertTrue(self.e.safe_history(Actor('eng_a'),before['request_id'])[0]['unavailable'])
        count=self.i.processed_objects
        self.i.process(self.w.mutate('C-01','revoke',user_id='eng_a'))
        self.assertEqual(self.i.processed_objects,count)
        self.w.mutate('D-01','delete')
        with self.assertRaises(PermissionError): self.e.evidence(Actor('eng_a'),'D-01@1')
        self.i.poll('drive')
        self.assertIsNone(self.s.get('D-01'))
    def test_failed_poll_resumes_from_checkpoint(self):
        event=self.w.mutate('D-01','content',version=2,text='new root cause',source_updated_at=now())
        self.i.fail_after_prepare=True
        with self.assertRaises(RuntimeError):self.i.poll('drive')
        self.i.fail_after_prepare=False
        self.assertEqual(len(self.i.poll('drive')),1)
        self.assertEqual(self.i.poll('drive'),[])
    def test_out_of_order_success_cannot_skip_failed_job(self):
        first=self.w.mutate('C-01','content',version=2,text='first',source_updated_at=now())
        second=self.w.mutate('C-02','content',version=2,text='second',source_updated_at=now())
        self.i.process(second)
        self.assertEqual(self.s.db.execute('SELECT cursor FROM sync WHERE source=?',('confluence',)).fetchone()[0],0)
        self.i.poll('confluence')
        self.assertEqual(self.s.get('C-01')['version'],2)
        self.assertEqual(self.s.db.execute('SELECT cursor FROM sync WHERE source=?',('confluence',)).fetchone()[0],second['event_id'])
    def test_create_each_source_and_delete_without_rebuild(self):
        for rid in ['C-01','J-01','S-01','D-01']:
            r=copy.deepcopy(self.w.resources[rid]);r['id']=rid+'-new';r['native_id']+='-new';r['source_url']+='-new';r['text']='new-object-unique searchable evidence';r['source_updated_at']=now()
            event=self.w.create(r);self.i.process(event)
            self.assertIn(r['id'],{e['resource_id'] for e in self.e.query(Actor('eng_a'),'new-object-unique')['evidence']})
            self.i.process(self.w.mutate(r['id'],'delete'))
            self.assertNotIn(r['id'],{e['resource_id'] for e in self.e.query(Actor('eng_a'),'new-object-unique')['evidence']})
