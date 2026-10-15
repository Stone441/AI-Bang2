import copy
import json
from pathlib import Path
import tempfile
import unittest

from brain.audit import Audit
from brain.budget import BudgetLedger
from brain.contracts import Actor, Evidence
from brain.deepseek import ModelUnavailable, PRICE_DATE
from brain.engine import Engine
from brain.sectioned_answer import DeepSeekSectionedSynthesisModel, validate_answer_parts
from brain.sources import FixtureWorld
from brain.store import Store
from test_synthesis import SequentialTransport


class SectionedAnswer(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.ledger=BudgetLedger(str(Path(self.tmp.name)/'budget.sqlite'));self.addCleanup(self.ledger.close)
        self.world=FixtureWorld()
        for r in self.world.resources.values():r['text']='[SYNTHETIC] '+r['text']
        self.store=Store();self.addCleanup(self.store.db.close);self.store.initialize(self.world)
        self.question='Is PAY-102 complete, can we offer payment-retry to all customers, and when is GA?'
        self.parts=[{'question':'Is PAY-102 complete','status':'supported','claim_indices':[0]},
                    {'question':'can we offer payment-retry to all customers','status':'supported','claim_indices':[1]},
                    {'question':'when is GA','status':'insufficient','claim_indices':[]}]
        self.claims=[];self.evidence=[]
        for rid,text in [('J-02','PAY-102 code fix is Done; code completion does not approve general release.'),
                         ('C-02','Payment-retry is limited to the controlled pilot; GA is not approved.')]:
            r=self.world.resources[rid];eid=rid+'@1'
            self.evidence.append(Evidence(eid,rid,1,r['source'],r['title'],r['locator'],r['text'],r['source_updated_at'],'2026-10-14',r['source_url']))
            self.claims.append({'text':text,'evidence_ids':[eid],'supports':[{'evidence_id':eid,'quote':r['text']}]})
        draft={'claims':self.claims,'answer_parts':self.parts}
        self.transport=SequentialTransport(draft,[{'index':i,'supported':True,'responsive':True} for i in range(2)])
        self.transport.outputs[1].update(parts_supported=True,premise_handled=True,conflicts_handled=True,filtered_answer_complete=True)
        self.model=DeepSeekSectionedSynthesisModel('synthetic-not-a-key',self.ledger,synthetic_only=True,transport=self.transport,today=PRICE_DATE)

    def engine(self,**kwargs):
        return Engine(self.store,self.world,Audit(self.store),self.model,mode='fixture_mock_model_synthesis',**kwargs)

    def test_two_calls_review_parts_and_preserve_quotes_receipts_and_insufficiency(self):
        stages=[]
        answer=self.model.generate_with_authorization(self.question,self.evidence,'a'*32,stages.append)
        self.assertEqual(answer['answer_parts'],self.parts);self.assertEqual(answer['claims'],self.claims)
        self.assertEqual(stages,['review_dispatch']);self.assertEqual(len(self.transport.calls),2)
        self.assertNotEqual(answer['model_call']['reservation_id'],answer['model_review']['reservation_id'])
        body=json.loads(self.transport.calls[1]['messages'][1]['content'])
        self.assertEqual(body['answer_parts'],self.parts)
        self.assertEqual(body['evidence'][0]['text'],self.evidence[0].text)

    def test_invalid_partition_or_unsupported_quote_never_reaches_review(self):
        cases=[]
        for mutation in ('duplicate','missing_claim','bool_index','invented_question','bad_status','insufficient_with_claim'):
            parts=copy.deepcopy(self.parts)
            if mutation=='duplicate':parts[1]['claim_indices']=[0,1]
            elif mutation=='missing_claim':parts[1].update(status='insufficient',claim_indices=[])
            elif mutation=='bool_index':parts[0]['claim_indices']=[True]
            elif mutation=='invented_question':parts[0]['question']='Why was GA rejected?'
            elif mutation=='bad_status':parts[0]['status']='approved'
            else:parts[2]['claim_indices']=[0]
            cases.append({'claims':self.claims,'answer_parts':parts})
        invented=copy.deepcopy(self.claims);invented[0]['supports'][0]['quote']='This quote is not in any document.'
        cases.append({'claims':invented,'answer_parts':self.parts})
        for draft in cases:
            with self.subTest(draft=draft):
                self.transport.calls.clear();self.transport.outputs[0]=draft
                with self.assertRaises(ModelUnavailable):self.model.generate_with_authorization(self.question,self.evidence,'b'*32,lambda _:None)
                self.assertEqual(len(self.transport.calls),1)

    def test_bad_coverage_wrong_part_or_dropped_claim_rejects_draft(self):
        for field in ('question_covered','parts_supported','responsive'):
            with self.subTest(field=field):
                review=copy.deepcopy(self.transport.outputs[1])
                if field=='responsive':review['verdicts'][0]['responsive']=False
                else:review[field]=False
                self.transport.calls.clear();old=self.transport.outputs[1];self.transport.outputs[1]=review
                engine=self.engine()
                with self.assertRaises(ModelUnavailable):engine.query(Actor('eng_b'),self.question)
                self.assertEqual(self.store.history('eng_b'),[])
                self.assertEqual(len(self.transport.calls),2)
                self.transport.outputs[1]=old

    def test_reasoning_review_requires_explicit_true_and_rejects_unknown_fields(self):
        for field in ('premise_handled','conflicts_handled'):
            for value in (False,None,'true',1):
                with self.subTest(field=field,value=value):
                    review=copy.deepcopy(self.transport.outputs[1]);review[field]=value
                    original=self.transport.outputs[1];self.transport.outputs[1]=review;self.transport.calls.clear()
                    with self.assertRaises(ModelUnavailable):
                        self.model.generate_with_authorization(self.question,self.evidence,'e'*32,lambda _:None)
                    self.transport.outputs[1]=original
            review=copy.deepcopy(self.transport.outputs[1]);del review[field]
            original=self.transport.outputs[1];self.transport.outputs[1]=review;self.transport.calls.clear()
            with self.assertRaises(ModelUnavailable):
                self.model.generate_with_authorization(self.question,self.evidence,'e'*32,lambda _:None)
            self.transport.outputs[1]=original
        self.transport.outputs[1]['unexpected']='approve'
        self.transport.calls.clear()
        with self.assertRaises(ModelUnavailable):
            self.model.generate_with_authorization(self.question,self.evidence,'e'*32,lambda _:None)

    def test_reasoning_rejection_removes_draft_from_history_and_final_answer(self):
        for field in ('premise_handled','conflicts_handled'):
            with self.subTest(field=field):
                original=self.transport.outputs[1][field];self.transport.outputs[1][field]=False
                self.transport.calls.clear()
                answer=self.engine(evidence_on_model_rejection=True).query(Actor('eng_b'),self.question)
                self.assertEqual(answer['answer_status'],'evidence_only')
                self.assertNotIn('answer_parts',answer)
                self.assertFalse(any(c['text']==self.claims[1]['text'] for c in answer['claims']))
                self.assertEqual(self.engine().safe_history(Actor('eng_b'),answer['request_id']),[answer])
                self.transport.outputs[1][field]=original

    def test_all_insufficient_parts_still_require_independent_review(self):
        self.transport.outputs=[{'claims':[],'answer_parts':[dict(p,status='insufficient',claim_indices=[]) for p in self.parts]},
            {'verdicts':[],'question_covered':True,'parts_supported':True,'premise_handled':True,'conflicts_handled':True}]
        result=self.model.generate_with_authorization(self.question,self.evidence,'c'*32,lambda _:None)
        self.assertEqual(result['claims'],[]);self.assertEqual(result['review_status'],'accepted')
        self.assertEqual(len(self.transport.calls),2)

    def test_no_evidence_never_calls_model(self):
        result=self.model.generate_with_authorization(self.question,[],'d'*32,lambda _:None)
        self.assertEqual(result['claims'],[]);self.assertNotIn('answer_parts',result)
        self.assertEqual(self.transport.calls,[])

    def test_engine_audit_history_and_revocation_keep_part_contract(self):
        engine=self.engine();actor=Actor('eng_b');answer=engine.query(actor,self.question)
        self.assertEqual(answer['answer_kind'],'sectioned_synthesis');self.assertEqual(answer['answer_parts'],self.parts)
        self.assertEqual(engine.safe_history(actor,answer['request_id']),[answer])
        generation=next(e for e in engine.audit.export() if e['event_type']=='generation_completed')
        self.assertEqual(generation['payload']['answer_parts'],self.parts)
        self.world.revoked.add(('eng_b','C-02'))
        hidden=engine.safe_history(actor,answer['request_id'])[0]
        self.assertTrue(hidden['unavailable']);self.assertNotIn('answer_parts',hidden)

    def test_rejected_review_falls_back_to_sources_without_draft_parts(self):
        self.transport.outputs[1]['parts_supported']=False
        answer=self.engine(evidence_on_model_rejection=True).query(Actor('eng_b'),self.question)
        self.assertEqual(answer['answer_status'],'evidence_only');self.assertNotIn('answer_parts',answer)
        self.assertFalse(any(c['text']==self.claims[1]['text'] for c in answer['claims']))

    def test_revocation_between_draft_and_review_blocks_second_send(self):
        self.transport.after_draft=lambda:self.world.revoked.add(('eng_b','C-02'))
        with self.assertRaises(PermissionError):self.engine().query(Actor('eng_b'),self.question)
        self.assertEqual(len(self.transport.calls),1);self.assertEqual(self.store.history('eng_b'),[])

    def test_history_revalidates_part_mapping_and_preserves_original_record(self):
        engine=self.engine();actor=Actor('eng_b');answer=engine.query(actor,self.question)
        corrupt=copy.deepcopy(answer);corrupt['request_id']='f'*32
        corrupt['answer_parts'][0]['claim_indices']=[99]
        self.store.save_run(corrupt['request_id'],actor.user_id,corrupt)
        self.assertTrue(engine.safe_history(actor,corrupt['request_id'])[0]['unavailable'])
        self.assertEqual(self.store.run(corrupt['request_id'],actor.user_id),corrupt)

    def test_cli_requires_real_model_flag_before_reading_credentials(self):
        from contextlib import redirect_stdout
        from io import StringIO
        from brain.operator_web import main
        with redirect_stdout(StringIO()):
            self.assertEqual(main(['--config','does-not-exist','--answer-style','sectioned-synthesis']),2)
