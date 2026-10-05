import json
import tempfile
import threading
import unittest
from pathlib import Path

from brain.budget import BudgetLedger
from brain.deepseek import DeepSeekEvidenceModel, ModelUnavailable, PRICE_DATE
from brain.engine import Engine
from brain.audit import Audit, verify_chain
from brain.contracts import Actor, Evidence
from brain.store import Store
from brain.sources import FixtureWorld
import test_deepseek


class ModelReceipts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.path = str(Path(self.tmp.name) / 'budget.sqlite')
        self.ledger = BudgetLedger(self.path); self.transport = test_deepseek.Transport()
        self.model = DeepSeekEvidenceModel('synthetic-not-a-key', self.ledger, synthetic_only=True,
                                           transport=self.transport, today=PRICE_DATE)
        self.evidence = Evidence('drive:test@1','drive:test',1,'drive','Synthetic',{},
                                 '[SYNTHETIC] GA not approved.','2026-10-05','2026-10-05','https://example.com')
        self.query_id = 'a' * 32

    def tearDown(self):
        self.ledger.close(); self.tmp.cleanup()

    def test_success_receipt_persists_usage_and_query_without_secret_or_content(self):
        draft = self.model.generate_for_request('Private-looking question for synthetic test', [self.evidence], self.query_id)
        receipt = draft['model_call']; self.assertEqual(receipt['query_id'], self.query_id)
        self.assertEqual(receipt['outcome'], 'accepted'); self.assertTrue(receipt['called'])
        self.assertEqual((receipt['prompt_tokens'],receipt['completion_tokens'],receipt['total_tokens']), (100,20,120))
        self.ledger.close(); self.ledger = BudgetLedger(self.path)
        self.assertEqual(self.ledger.model_receipt(receipt['reservation_id']), receipt)
        persisted = '\n'.join(self.ledger.db.iterdump())
        for forbidden in ('synthetic-not-a-key','Private-looking question','GA not approved','https://example.com'):
            self.assertNotIn(forbidden, persisted)

    def test_context_insert_failure_rolls_back_reservation_and_never_sends(self):
        self.ledger.db.execute("CREATE TRIGGER fail_model_context BEFORE INSERT ON model_calls BEGIN SELECT RAISE(ABORT,'test failure'); END")
        with self.assertRaises(Exception): self.model.generate_for_request('Question',[self.evidence],self.query_id)
        self.assertEqual(self.ledger.summary()['pending_requests'],0)
        self.assertEqual(self.transport.calls,[])

    def test_unknown_failure_keeps_joinable_context_across_restart(self):
        self.transport.error = True
        with self.assertRaises(ModelUnavailable): self.model.generate_for_request('Question',[self.evidence],self.query_id)
        reservation = self.ledger.db.execute('SELECT id FROM reservations').fetchone()[0]
        self.ledger.close(); self.ledger = BudgetLedger(self.path)
        receipt = self.ledger.model_receipt(reservation)
        self.assertEqual(receipt['query_id'],self.query_id); self.assertEqual(receipt['outcome'],'usage_unavailable')
        self.assertEqual(receipt['state'],'dispatched'); self.assertIsNone(receipt['total_tokens'])
        self.assertIsNone(receipt['called']); self.assertTrue(receipt['dispatch_recorded'])
        self.assertEqual(self.ledger.summary()['accounted_micro_usd'],self.model.reservation)

    def test_rejected_output_still_records_known_usage_and_charge(self):
        self.transport.response['choices'][0]['message']['content']='{"evidence_ids":["forged@1"]}'
        with self.assertRaises(ModelUnavailable): self.model.generate_for_request('Question',[self.evidence],self.query_id)
        reservation = self.ledger.db.execute('SELECT id FROM reservations').fetchone()[0]
        receipt = self.ledger.model_receipt(reservation)
        self.assertEqual(receipt['outcome'],'output_rejected'); self.assertEqual(receipt['state'],'settled')
        self.assertEqual(receipt['total_tokens'],120)

    def test_legacy_reservation_is_not_falsely_attributed(self):
        rid = self.ledger.reserve(100); self.ledger.dispatch(rid); self.ledger.settle(rid,10)
        self.ledger.close(); self.ledger = BudgetLedger(self.path)
        self.assertIsNone(self.ledger.model_receipt(rid)); self.assertEqual(self.ledger.summary()['settled_micro_usd'],10)

    def test_usage_reconciliation_conflict_rolls_back_and_context_never_changes(self):
        draft = self.model.generate_for_request('Question',[self.evidence],self.query_id); receipt=draft['model_call']
        with self.assertRaises(ValueError):
            self.ledger.settle(receipt['reservation_id'],receipt['accounted_upper_micro_usd'],
                               usage={'prompt_tokens':101,'completion_tokens':20,'total_tokens':121})
        with self.assertRaises(ValueError): self.ledger.model_outcome(receipt['reservation_id'],'output_rejected')
        self.assertEqual(self.ledger.model_receipt(receipt['reservation_id']),receipt)

    def test_empty_evidence_has_no_budget_receipt_or_external_call(self):
        draft = self.model.generate_for_request('Question',[],self.query_id)
        self.assertFalse(draft['model_call']['called']); self.assertEqual(self.transport.calls,[])
        self.assertEqual(self.ledger.db.execute('SELECT count(*) FROM model_calls').fetchone()[0],0)

    def test_bad_correlation_never_reserves_or_sends(self):
        for request_id in ('', 'client-admin', True):
            with self.assertRaises(ValueError): self.model.generate_for_request('Question',[self.evidence],request_id)
        self.assertEqual(self.transport.calls,[])
        self.assertEqual(self.ledger.summary()['accounted_micro_usd'],0)

    def test_engine_request_is_joinable_on_model_failure(self):
        world = FixtureWorld()
        for resource in world.resources.values(): resource['text']='[SYNTHETIC] '+resource['text']
        store=Store(); store.initialize(world); audit=Audit(store)
        self.transport.error=True
        try:
            with self.assertRaises(ModelUnavailable): Engine(store,world,audit,self.model).query(Actor('eng_b'),'payment-service retry')
            events=audit.export(); started=next(e for e in events if e['event_type']=='request_started')
            row=self.ledger.db.execute('SELECT reservation_id,query_id FROM model_calls').fetchone()
            self.assertEqual(row[1],started['request_id'])
            self.assertTrue(any(e['event_type']=='request_failed' and e['request_id']==row[1] for e in events))
            self.assertTrue(verify_chain(events)['valid'])
        finally: store.db.close()

    def test_engine_success_receipt_matches_audit_request_and_budget(self):
        world=FixtureWorld()
        for resource in world.resources.values(): resource['text']='[SYNTHETIC] '+resource['text']
        store=Store(); store.initialize(world); audit=Audit(store)
        def send(request):
            evidence=json.loads(json.loads(request.data)['messages'][1]['content'])['evidence']
            response=dict(self.transport.response)
            response['choices']=[{'finish_reason':'stop','message':{'role':'assistant',
                                'content':json.dumps({'evidence_ids':[evidence[0]['evidence_id']]})}}]
            return 200,response
        self.transport._send=send
        try:
            answer=Engine(store,world,audit,self.model).query(Actor('eng_b'),'payment-service retry')
            event=next(e for e in audit.export() if e['event_type']=='generation_completed')
            receipt=event['payload']['model_call']
            self.assertEqual(receipt['query_id'],answer['request_id'])
            self.assertEqual(receipt,self.ledger.model_receipt(receipt['reservation_id']))
            self.assertEqual(answer['model_call'],receipt)
            self.assertEqual(Engine(store,world,audit,self.model).safe_history(Actor('eng_b'))[0]['model_call'],receipt)
            self.assertTrue(verify_chain(audit.export())['valid'])
        finally: store.db.close()

    def test_answer_and_history_preserve_no_call_without_inferred_token_usage(self):
        world=FixtureWorld(); store=Store(); store.initialize(world); audit=Audit(store)
        try:
            engine=Engine(store,world,audit,self.model)
            answer=engine.query(Actor('eng_b'),'unfindablexyz')
            self.assertEqual(answer['model_call'],{'called':False,'reason':'no_authorized_evidence'})
            self.assertEqual(engine.safe_history(Actor('eng_b'))[0]['model_call'],answer['model_call'])
            self.assertEqual(self.transport.calls,[])
        finally: store.db.close()

    def test_public_receipt_rejects_false_usage_and_strips_unrelated_provider_fields(self):
        from brain.model_receipt import public_receipt
        receipt=self.model.generate_for_request('Question',[self.evidence],self.query_id)['model_call']
        projected=public_receipt(dict(receipt,credential='must-not-return',accounting_basis='vendor invoice'),self.query_id)
        self.assertNotIn('credential',projected)
        self.assertIn('not vendor invoice',projected['accounting_basis'])
        for changed in ({'query_id':'b'*32},{'called':1},{'total_tokens':121},
                        {'completion_tokens':True},{'state':'dispatched'},
                        {'accounted_upper_micro_usd':receipt['reserved_micro_usd']+1}):
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                public_receipt(dict(receipt,**changed),self.query_id)

    def test_http_receipt_is_returned_with_answer_but_withheld_with_revoked_history(self):
        from brain.server import App, create_server
        from unittest.mock import patch
        import test_http
        world=FixtureWorld()
        for resource in world.resources.values(): resource['text']='[SYNTHETIC] '+resource['text']
        with patch('brain.server.FixtureWorld',return_value=world): self.app=App()
        self.app.engine.model=self.model
        def send(request):
            evidence=json.loads(json.loads(request.data)['messages'][1]['content'])['evidence']
            response=dict(self.transport.response)
            response['choices']=[{'finish_reason':'stop','message':{'role':'assistant',
                                'content':json.dumps({'evidence_ids':[evidence[0]['evidence_id']]})}}]
            return 200,response
        self.transport._send=send
        self.server=create_server(self.app); self.cookie=''; self.csrf=''
        thread=threading.Thread(target=self.server.serve_forever,daemon=True); thread.start()
        request=lambda path,data=None:test_http.HTTP.request(self,path,data)
        try:
            status,login=request('/api/demo/login',{'user':'eng_b'}); self.assertEqual(status,200)
            self.csrf=login['csrf']
            status,answer=request('/api/query',{'question':'payment-service retry'})
            self.assertEqual(status,200); self.assertTrue(answer['model_call']['called'])
            for path in ('/api/history','/api/export/'+answer['request_id']):
                status,body=request(path); self.assertEqual(status,200)
                self.assertEqual(body['history'][0]['model_call'],answer['model_call'])
                self.assertNotIn('synthetic-not-a-key',json.dumps(body))
            self.app.world.mutate(answer['evidence'][0]['resource_id'],'revoke',user_id='eng_b')
            for path in ('/api/history','/api/export/'+answer['request_id']):
                body=request(path)[1]; self.assertTrue(body['history'][0]['unavailable'])
                self.assertNotIn('model_call',body['history'][0]); self.assertNotIn('claims',body['history'][0])
        finally:
            self.server.shutdown(); self.server.server_close(); thread.join(); self.app.store.db.close()
