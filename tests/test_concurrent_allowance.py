import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import threading
import unittest
import subprocess
import sys
import test_source_review as source_review

from brain.budget import BudgetLedger, TrialAdmissionPaused
from scripts.concurrent_allowance import ConcurrentPerformanceAdmission, ConcurrentGoalLedger


class ConcurrentAllowance(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.path=self.root/'goal.json'
        self.ledger=BudgetLedger(str(self.root/'budget.sqlite'));self.addCleanup(self.ledger.close)
        self.old=self.ledger.reserve(20);self.ledger.dispatch(self.old)
        self.gate=ConcurrentPerformanceAdmission(lambda:None,self.ledger,self.path,plan_sha256='a'*64)
        self.addCleanup(self.gate.close);self.guarded=ConcurrentGoalLedger(self.gate)

    def reserve(self, amount=100):
        return self.guarded.reserve(amount,query_id='b'*32,model='deepseek-flash')

    def settle(self,rid,cost=1):
        self.guarded.settle(rid,cost,usage={'prompt_tokens':1,'completion_tokens':1,'total_tokens':2})
        self.guarded.model_outcome(rid,'accepted')

    def test_three_model_calls_overlap_and_settle_without_unknown(self):
        barrier=threading.Barrier(3)
        def query():
            rid=self.reserve();self.guarded.dispatch(rid)
            barrier.wait(3)  # Whole-query locking would time out here.
            self.settle(rid)
        self.gate.query=query
        with ThreadPoolExecutor(3) as pool:
            futures=[pool.submit(self.gate) for _ in range(3)]
            for f in futures:f.result(5)
        state=json.loads(self.path.read_text())
        self.assertEqual(state['model_calls_used'],3)
        self.assertEqual(state['attempts'],3)
        self.assertEqual(state['new_unknown_reservations'],[])
        self.assertEqual(state['original_pending_ids'],[self.old])

    def test_pending_upper_bounds_and_call_slots_cannot_be_oversubscribed(self):
        for case in ('calls','cost'):
            with self.subTest(case=case):
                # Fresh state per subcase avoids rebaselining the real gate.
                path=self.root/(case+'.json');ledger=BudgetLedger(str(self.root/(case+'.sqlite')))
                gate=ConcurrentPerformanceAdmission(lambda:None,ledger,path,plan_sha256='a'*64)
                guarded=ConcurrentGoalLedger(gate);reserved=threading.Event();release=threading.Event()
                count=59 if case=='calls' else 1
                for _ in range(count):
                    rid=ledger.reserve(400000 if case=='cost' else 1);ledger.dispatch(rid);ledger.settle(rid,400000 if case=='cost' else 1)
                def query(wait):
                    rid=guarded.reserve(75000 if case=='cost' else 1)
                    if wait:
                        reserved.set()
                        if not release.wait(3):raise RuntimeError('Test synchronization failed')
                    guarded.dispatch(rid);guarded.settle(rid,1)
                gate.query=query
                try:
                    with ThreadPoolExecutor(2) as pool:
                        first=pool.submit(gate,True)
                        try:
                            self.assertTrue(reserved.wait(3))
                            with self.assertRaises(TrialAdmissionPaused):pool.submit(gate,False).result(3)
                        finally:release.set()
                        first.result(3)
                    self.assertEqual(ledger.summary()['pending_requests'],0)
                finally:gate.close();ledger.close()

    def test_unknown_stops_prepared_dispatch_but_other_receipt_can_settle(self):
        barrier=threading.Barrier(3);unknown=threading.Event();results={}
        def query(role):
            rid=self.reserve();results[role]=rid
            if role!='prepared':self.guarded.dispatch(rid)
            barrier.wait(3)
            if role=='unknown':
                self.guarded.model_outcome(rid,'usage_unavailable');unknown.set()
            else:
                if not unknown.wait(3):raise RuntimeError('Test synchronization failed')
                if role=='prepared':
                    with self.assertRaises(TrialAdmissionPaused):self.guarded.dispatch(rid)
                else:self.settle(rid)
        self.gate.query=query
        with ThreadPoolExecutor(3) as pool:
            futures=[pool.submit(self.gate,role) for role in ('unknown','prepared','settled')]
            for f in futures:f.result(5)
        state=json.loads(self.path.read_text())
        self.assertEqual(set(state['new_unknown_reservations']),{results['unknown'],results['prepared']})
        self.assertEqual(state['model_calls_used'],2)
        with self.assertRaises(TrialAdmissionPaused):self.gate('another')

    def test_query_exit_and_restart_do_not_forgive_unfinished_reservations(self):
        self.gate.query=lambda:self.reserve()
        rid=self.gate()
        self.assertIn(rid,json.loads(self.path.read_text())['new_unknown_reservations'])
        self.gate.close()
        new=ConcurrentPerformanceAdmission(lambda:None,self.ledger,self.path,plan_sha256='a'*64)
        try:
            with self.assertRaises(TrialAdmissionPaused):new()
            self.assertEqual(self.ledger.summary()['pending_requests'],2)
        finally:new.close()

    def test_second_owner_unadmitted_calls_and_cross_query_dispatch_rejected(self):
        with self.assertRaises(BlockingIOError):
            ConcurrentPerformanceAdmission(lambda:None,self.ledger,self.path,plan_sha256='a'*64)
        with self.assertRaises(TrialAdmissionPaused):self.reserve()
        ready=threading.Event();release=threading.Event();ids=[]
        def query(owner):
            if owner:
                rid=self.reserve();ids.append(rid);ready.set()
                if not release.wait(3):raise RuntimeError('Test synchronization failed')
                self.guarded.cancel_before_dispatch(rid)
            else:
                if not ready.wait(3):raise RuntimeError('Test synchronization failed')
                try:
                    with self.assertRaises(TrialAdmissionPaused):self.guarded.dispatch(ids[0])
                    with self.assertRaises(RuntimeError):self.gate.close()
                finally:release.set()
        self.gate.query=query
        with ThreadPoolExecutor(2) as pool:
            futures=[pool.submit(self.gate,x) for x in (True,False)]
            for f in futures:f.result(5)
        self.assertEqual(json.loads(self.path.read_text())['model_calls_used'],0)
        self.assertEqual(self.ledger.summary()['pending_requests'],1)

    def test_process_crash_reclassifies_persisted_inflight_as_unknown(self):
        state=self.root/'crash.json';budget=self.root/'crash.sqlite'
        code='''
import os,sys
from brain.budget import BudgetLedger
from scripts.concurrent_allowance import ConcurrentPerformanceAdmission,ConcurrentGoalLedger
ledger=BudgetLedger(sys.argv[1])
gate=ConcurrentPerformanceAdmission(lambda:None,ledger,sys.argv[2],plan_sha256='a'*64)
guarded=ConcurrentGoalLedger(gate)
def query():
    rid=guarded.reserve(123,query_id='b'*32,model='deepseek-flash')
    guarded.dispatch(rid)
    os._exit(0)
gate.query=query
gate()
'''
        subprocess.run([sys.executable,'-c',code,str(budget),str(state)],check=True,timeout=5)
        before=json.loads(state.read_text())
        self.assertEqual(len(before['known_in_flight_reservations']),1)
        ledger=BudgetLedger(str(budget))
        gate=ConcurrentPerformanceAdmission(lambda:None,ledger,state,plan_sha256='a'*64)
        try:
            after=json.loads(state.read_text())
            self.assertEqual(after['new_unknown_reservations'],before['known_in_flight_reservations'])
            self.assertEqual(after['model_calls_used'],1)
            self.assertEqual(ledger.summary()['accounted_micro_usd'],123)
            with self.assertRaises(TrialAdmissionPaused):gate()
        finally:gate.close();ledger.close()


class ConcurrentModelIntegration(unittest.TestCase):
    setUp=source_review.SourceReview.setUp
    tearDown=source_review.SourceReview.tearDown
    candidate=source_review.SourceReview.candidate
    engine=source_review.SourceReview.engine
    verdicts=source_review.SourceReview.verdicts
    dynamic_review=source_review.SourceReview.dynamic_review

    def test_real_model_class_original_ledger_and_review_receipt(self):
        from brain.contracts import Actor
        engine,_=self.engine();self.dynamic_review()
        with tempfile.TemporaryDirectory() as directory:
            gate=ConcurrentPerformanceAdmission(engine.query,self.ledger,Path(directory)/'goal.json',plan_sha256='a'*64)
            engine.model.ledger=ConcurrentGoalLedger(gate)
            try:
                result=gate(Actor('eng_b'),'payment-service incident runbook')
                self.assertEqual(result['review_status'],'accepted')
                self.assertEqual(len(self.transport.calls),1)
                self.assertEqual(gate.state_extra()['model_calls_used'],1)
                self.assertEqual(self.ledger.summary()['pending_requests'],0)
                self.assertIs(engine.model.ledger.db,self.ledger.db)
            finally:gate.close()
