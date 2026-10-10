"""Review-only contract, offline mocked transport. No online-quality inference."""
import json,unittest
from dataclasses import replace
from unittest.mock import patch
from brain.contracts import Actor
from brain.engine import Engine
from brain.sources import FixtureWorld
from brain.store import Store
from brain.audit import Audit
from brain.deepseek import PRICE_DATE,ModelOutputRejected
from brain.synthesis import DeepSeekReviewAllSourcesModel
import test_synthesis as setup_tests


class SourceReview(unittest.TestCase):
    setUp=setup_tests.GroundedSynthesis.setUp
    tearDown=setup_tests.GroundedSynthesis.tearDown

    def candidate(self):
        return DeepSeekReviewAllSourcesModel('synthetic-not-a-key',self.ledger,
            synthetic_only=True,transport=self.transport,today=PRICE_DATE,
            reasoning_effort='none',output_tokens=8192)

    def engine(self):
        world=FixtureWorld()
        for r in world.resources.values():r['text']='[SYNTHETIC] '+r['text']
        store=Store();store.initialize(world);self.addCleanup(store.db.close)
        return Engine(store,world,Audit(store),self.candidate(),mode='fixture_mock_source_review'),world

    def verdicts(self,body,*,covered=True):
        return {'question_covered':covered,'filtered_answer_complete':True,
            'verdicts':[{'index':i,'supported':True,'responsive':c['evidence_ids']==['C-01@1']}
                        for i,c in enumerate(body['claims'])]}

    def dynamic_review(self,*,covered=True):
        calls=self.transport.calls
        def send(request):
            body=json.loads(request.data);calls.append(body)
            output=self.verdicts(json.loads(body['messages'][1]['content']),covered=covered)
            return 200,{'model':'deepseek-flash','usage':{'prompt_tokens':100,'completion_tokens':20,'total_tokens':120},
                'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':json.dumps(output)}}]}
        self.transport._send=send

    def test_all_sources_reach_review_and_only_one_actual_receipt_is_exposed(self):
        engine,world=self.engine();self.dynamic_review()
        answer=engine.query(Actor('eng_b'),'payment-service incident runbook')
        inputs=json.loads(self.transport.calls[0]['messages'][1]['content'])
        self.assertEqual({i['evidence_id'] for i in inputs['evidence']},
                         {i for c in inputs['claims'] for i in c['evidence_ids']})
        source=next(e for e in inputs['evidence'] if e['evidence_id']=='C-01@1')
        self.assertEqual(''.join(c['text'] for c in inputs['claims'] if c['evidence_ids']==['C-01@1']),source['text'])
        self.assertEqual(answer['claims'][0]['text'],source['text'])
        self.assertEqual(answer['claim_format'],'reviewed_source_v1')
        self.assertEqual(answer['review_status'],'accepted')
        self.assertNotIn('model_call',answer)
        self.assertTrue(answer['model_review']['called']);self.assertEqual(len(self.transport.calls),1)
        self.assertEqual(self.transport.calls[0]['max_tokens'],8192)
        self.assertEqual(self.transport.calls[0]['thinking'],{'type':'disabled'})
        world.revoked.add(('eng_b','C-01'))
        self.assertTrue(engine.safe_history(Actor('eng_b'),answer['request_id'])[0]['unavailable'])

    def test_long_source_is_never_truncated_including_trailing_scope(self):
        text='[SYNTHETIC] '+('Long source content. '*75)+'Critical scope: pilot only, GA not approved.'
        e=replace(self.evidence,text=text)
        claims=self.candidate().source_claims([e])
        self.assertEqual(''.join(c['text'] for c in claims),text)
        self.assertTrue(all(12<=len(c['text'])<=600 for c in claims))
        self.assertEqual(claims[-1]['text'][-44:],text[-44:])
        self.transport.outputs=[{'question_covered':True,'filtered_answer_complete':True,
            'verdicts':[{'index':i,'supported':True,'responsive':i==0} for i in range(len(claims))]}]
        answer=self.candidate().generate_with_authorization('What is the source scope?',
            [e],self.rid,lambda phase:None)
        self.assertEqual(''.join(c['text'] for c in answer['claims']),text)


    def test_missing_supported_part_still_blocks_and_stores_no_answer(self):
        engine,_=self.engine();self.dynamic_review(covered=False)
        with self.assertRaises(ModelOutputRejected):engine.query(Actor('eng_b'),'payment-service incident runbook')
        self.assertEqual(engine.store.history('eng_b'),[])
        self.assertEqual(len(self.transport.calls),1)

    def test_unsupported_or_unapproved_filtering_blocks(self):
        quote=self.evidence.text
        for output in [{'question_covered':True,'verdicts':[{'index':0,'supported':False,'responsive':True}]},
                       {'question_covered':True,'verdicts':[{'index':0,'supported':True,'responsive':False}]}]:
            with self.subTest(output=output):
                self.transport.calls.clear();self.transport.outputs=[output]
                with self.assertRaises(ModelOutputRejected):
                    self.candidate().generate_with_authorization('What is approved?',[self.evidence],self.rid,lambda phase:None)

    def test_revocation_before_review_never_dispatches_and_after_review_never_delivers(self):
        for moment in ('before','after'):
            with self.subTest(moment=moment):
                engine,world=self.engine();self.transport.calls.clear();self.dynamic_review()
                checks=engine.checks;send=self.transport._send
                def check(actor,resources,rid,phase):
                    if moment=='before' and phase=='review_dispatch':world.revoked.add(('eng_b','C-01'))
                    return checks(actor,resources,rid,phase)
                def dispatch(request):
                    result=send(request)
                    if moment=='after':world.revoked.add(('eng_b','C-01'))
                    return result
                with patch.object(engine,'checks',side_effect=check),patch.object(self.transport,'_send',side_effect=dispatch):
                    with self.assertRaises(PermissionError):engine.query(Actor('eng_b'),'payment-service incident runbook')
                self.assertEqual(len(self.transport.calls),0 if moment=='before' else 1)
                self.assertEqual(engine.store.history('eng_b'),[])

    def test_saved_reviewed_quote_cannot_become_a_paraphrase(self):
        engine,_=self.engine();self.dynamic_review()
        answer=engine.query(Actor('eng_b'),'payment-service incident runbook')
        answer['claims'][0]['text']='Unquoted paraphrase; latest ordering is not established.'
        engine.store.db.execute('UPDATE runs SET body=? WHERE id=?',(json.dumps(answer),answer['request_id']))
        self.assertTrue(engine.safe_history(Actor('eng_b'),answer['request_id'])[0]['unavailable'])
