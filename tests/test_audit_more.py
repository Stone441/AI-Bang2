import copy
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from brain.audit import Audit,verify_chain,event_hash
from brain.audit_query import parse_inquiry
from brain.store import Store

class AuditIntegrity(unittest.TestCase):
    def setUp(self):self.store=Store();self.audit=Audit(self.store)
    def tearDown(self):self.store.db.close()
    def test_concurrent_append_and_tamper_boundaries(self):
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(lambda n:self.audit.append('request_started','eng_a',str(n),{'query':str(n)}),range(60)))
        original=self.audit.export();head={'through_seq':len(original),'head_hash':original[-1]['hash']}
        self.assertTrue(verify_chain(original,head)['valid'])
        edited=copy.deepcopy(original);edited[2]['payload']['query']='changed'
        middle=original[:3]+original[4:];tail=original[:-1]
        for corrupted in [edited,middle,tail]:self.assertFalse(verify_chain(corrupted,head)['valid'])
        rebuilt=copy.deepcopy(original);rebuilt[0]['payload']['query']='replacement'
        for i,e in enumerate(rebuilt):
            if i:e['previous_hash']=rebuilt[i-1]['hash']
            e['hash']=event_hash(e)
        self.assertTrue(verify_chain(rebuilt)['valid']) # Honest unanchored limitation.
        self.assertFalse(verify_chain(rebuilt,head)['valid'])
        self.assertFalse(verify_chain(original,head)['signature_verified'])
    def test_parser_timezone_range_and_rejection(self):
        end=datetime(2026,10,4,8,tzinfo=timezone.utc)
        filters=parse_inquiry('Show everything jdoe accessed related to payment-service in the last 30 days.',end)
        self.assertEqual(filters['start_time'],'2026-09-04T08:00:00+00:00')
        for q in ['SELECT * FROM audit','Show everything security accessed related to payment-service in the last 30 days.','Show everything jdoe accessed related to payment-service in the last 0 days.']:
            with self.assertRaises(ValueError):parse_inquiry(q,end)
