"""Schema, provenance and one-call integration; mock semantics, not quality proof."""
import json
from brain.contracts import Actor
from brain.deepseek import PRICE_DATE
from brain.synthesis import DeepSeekExplainedSourceReviewModel, ExplainedSourceReview, PREMISE_NOTICES
import test_whole_source_review as whole

class PremiseReview(whole.WholeReview):
    def candidate(self):
        return DeepSeekExplainedSourceReviewModel('synthetic-not-a-key',self.ledger,
            synthetic_only=True,transport=self.transport,today=PRICE_DATE,
            reasoning_effort='none',output_tokens=8192)

    def dynamic(self):
        super().dynamic();original=self.transport._send
        def send(request):
            status,response=original(request)
            message=response['choices'][0]['message'];out=json.loads(message['content'])
            out.update(premise_status=getattr(self,'premise_status','not_applicable'),
                       premise_sources=out['selected'][:1] if getattr(self,'premise_status','not_applicable')!='not_applicable' else [])
            message['content']=json.dumps(out);return status,response
        self.transport._send=send

    def test_schema_rejects_missing_unknown_unselected_duplicate_and_inconsistent_sources(self):
        r=ExplainedSourceReview('synthetic-not-a-key',self.ledger,synthetic_only=True,
            today=PRICE_DATE,claims=self.candidate().source_claims([self.evidence]))
        prompt=r.messages('Why was this rejected?',[self.evidence])
        self.assertIn('missing approval as rejection',prompt[0]['content'])
        valid={'selected':['P0'],'selection_safe':True,'question_covered':True,
               'premise_status':'not_established','premise_sources':['P0']}
        r.parse_output(valid,[self.evidence])
        self.assertEqual(r.premise_review['evidence_ids'],[self.evidence.evidence_id])
        cases=[{k:v for k,v in valid.items() if k!='premise_status'},dict(valid,premise_status='rejected'),
               dict(valid,premise_sources=['P1']),dict(valid,premise_sources=['P0','P0']),
               dict(valid,premise_sources=[]),dict(valid,premise_status='not_applicable'),
               dict(valid,selection_safe=False),dict(valid,question_covered=False),dict(valid,premise_status=['contradicted'])]
        for case in cases:
            with self.subTest(case=case):
                with self.assertRaises(ValueError):r.parse_output(case,[self.evidence])

    def test_notice_is_fixed_and_audited_with_one_receipt_and_current_history(self):
        self.premise_status='not_established';engine,world=self.engine();self.dynamic()
        answer=engine.query(Actor('eng_b'),'payment-service incident runbook')
        self.assertEqual(answer['uncertainties'][0],PREMISE_NOTICES['not_established'])
        self.assertEqual(answer['premise_review']['status'],'not_established')
        self.assertEqual(len(self.transport.calls),1)
        self.assertEqual(engine.safe_history(Actor('eng_b'),answer['request_id']),[answer])
        generation=next(e for e in engine.audit.export() if e['event_type']=='generation_completed')
        self.assertEqual(generation['payload']['premise_review'],answer['premise_review'])
        world.revoked.add(('eng_b','C-01'))
        self.assertTrue(engine.safe_history(Actor('eng_b'),answer['request_id'])[0]['unavailable'])
