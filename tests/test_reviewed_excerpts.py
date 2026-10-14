"""Offline transport only; these checks do not prove live selection quality."""
import unittest
from brain.contracts import Actor
from brain.engine import Engine
from brain.store import Store
from brain.audit import Audit
from brain.sources import FixtureWorld
from brain.deepseek import ModelOutputRejected,PRICE_DATE
from brain.synthesis import DeepSeekReviewedExcerptsModel,validate_claim
import test_synthesis as synthesis_tests


class ReviewedExcerpts(unittest.TestCase):
    setUp=synthesis_tests.GroundedSynthesis.setUp
    tearDown=synthesis_tests.GroundedSynthesis.tearDown

    def candidate(self):
        return DeepSeekReviewedExcerptsModel('synthetic-not-a-key',self.ledger,
            synthetic_only=True,transport=self.transport,today=PRICE_DATE,
            reasoning_effort='none',output_tokens=8192)

    def test_exact_quote_then_separate_review_with_no_paraphrase(self):
        quote='Pilot approved for ten customers. GA is not approved.'
        self.transport.outputs[0]={'selections':[{'evidence_id':self.evidence.evidence_id,'quote':quote}]}
        checks=[];answer=self.candidate().generate_with_authorization('What is approved?',
            [self.evidence],self.rid,checks.append)
        self.assertEqual(answer['claims'][0]['text'],quote)
        self.assertEqual(answer['claims'][0]['supports'][0]['quote'],quote)
        self.assertEqual(checks,['review_dispatch'])
        self.assertEqual(len(self.transport.calls),2)
        self.assertNotEqual(answer['model_call']['reservation_id'],answer['model_review']['reservation_id'])

    def test_missing_coverage_blocks_even_when_quotes_are_real(self):
        self.transport.outputs[0]={'selections':[{'evidence_id':self.evidence.evidence_id,
            'quote':'Pilot approved for ten customers. GA is not approved.'}]}
        self.transport.outputs[1]['question_covered']=False
        with self.assertRaises(ModelOutputRejected):
            self.candidate().generate_with_authorization('Which actions are approved?',
                [self.evidence],self.rid,lambda phase:None)
        self.assertEqual(len(self.transport.calls),2)

    def test_forged_quote_and_unknown_reference_block_before_review(self):
        for eid,quote in [(self.evidence.evidence_id,'GA is now approved for everyone.'),
                          ('missing','Pilot approved for ten customers.')]:
            with self.subTest(eid=eid),self.assertRaises(ValueError):
                self.candidate().parse_output({'selections':[{'evidence_id':eid,'quote':quote}]},[self.evidence])

    def test_engine_retains_current_authorization_and_saved_answer_recheck(self):
        world=FixtureWorld()
        for resource in world.resources.values():resource['text']='[SYNTHETIC] '+resource['text']
        store=Store();store.initialize(world);self.addCleanup(store.db.close)
        engine=Engine(store,world,Audit(store),self.candidate(),mode='fixture_mock_model_reviewed_excerpts')
        quote=engine.evidence(Actor('eng_b'),'C-01@1')['text']
        self.transport.outputs[0]={'selections':[{'evidence_id':'C-01@1','quote':quote}]}
        answer=engine.query(Actor('eng_b'),'payment-service runbook')
        self.assertEqual(answer['answer_kind'],'reviewed_excerpts')
        self.assertEqual(answer['claims'][0]['text'],quote)
        world.revoked.add(('eng_b','C-01'))
        self.assertTrue(engine.safe_history(Actor('eng_b'),answer['request_id'])[0]['unavailable'])

    def test_scoped_unknown_clause_does_not_hide_a_positive_latest_assertion(self):
        claim=dict(self.claim)
        claim['text']='The latest approved mitigation is not established in the accessible evidence; the pilot is approved for ten customers.'
        validate_claim(claim,[self.evidence])
        claim['text']+=' The latest mitigation is the pilot.'
        with self.assertRaises(ValueError):validate_claim(claim,[self.evidence])

    def test_negative_scope_cannot_swallow_a_positive_temporal_clause(self):
        claim=dict(self.claim)
        claim['text']='The latest pilot is approved but GA is not established in the accessible evidence.'
        with self.assertRaises(ValueError):validate_claim(claim,[self.evidence])
