import copy
import json
import unittest
from dataclasses import replace

import test_sectioned_answer
from brain.contracts import Actor
from brain.deepseek import ModelOutputRejected, PRICE_DATE, OutputValidationError
from brain.isolated_quote_review import IsolatedQuoteReview, DeepSeekIsolatedSectionedModel


class IsolatedQuoteTests(unittest.TestCase):
    def setUp(self):
        self.f=test_sectioned_answer.SectionedAnswer();self.f.setUp();self.addCleanup(self.f.doCleanups)
        f=self.f
        self.original_review=copy.deepcopy(f.transport.outputs[1])
        f.transport.outputs=[f.transport.outputs[0],{'quote_supported':True},
                             {'quote_supported':True},self.original_review]
        f.model=DeepSeekIsolatedSectionedModel('synthetic-not-a-key',f.ledger,
            synthetic_only=True,transport=f.transport,today=PRICE_DATE)

    def test_payload_excludes_question_full_source_metadata_and_other_claim(self):
        f=self.f;original=f.evidence[0]
        evidence=replace(original,text=original.text+' SECRET-FULL-SOURCE',title='SECRET-TITLE',
            locator={'hint':'SECRET-LOCATOR'})
        reviewer=IsolatedQuoteReview('synthetic-not-a-key',f.ledger,synthetic_only=True,
            today=PRICE_DATE,claim=f.claims[0])
        messages=reviewer.messages('SECRET-QUESTION',[evidence,f.evidence[1]])
        body=json.loads(messages[1]['content'])
        self.assertEqual(body,{'claim':f.claims[0]['text'],
            'quotations':[f.claims[0]['supports'][0]['quote']]})
        encoded=json.dumps(messages)
        for secret in ('SECRET-FULL-SOURCE','SECRET-TITLE','SECRET-LOCATOR','SECRET-QUESTION',f.evidence[1].text):
            self.assertNotIn(secret,encoded)

    def test_strict_boolean_rejection_and_shape(self):
        f=self.f;reviewer=IsolatedQuoteReview('synthetic-not-a-key',f.ledger,
            synthetic_only=True,today=PRICE_DATE,claim=f.claims[0])
        for output in ({'quote_supported':False},{'quote_supported':'true'},
                       {'quote_supported':1},{'quote_supported':None},{},
                       {'quote_supported':True,'extra':True}):
            with self.subTest(output=output),self.assertRaises(OutputValidationError):
                reviewer.parse_output(output,f.evidence)
        self.assertEqual(reviewer.parse_output({'quote_supported':True},f.evidence),[f.claims[0]])

    def test_full_flow_reauthorizes_every_review_and_preserves_full_review(self):
        f=self.f;stages=[];events=[]
        result=f.model.generate_with_authorization(f.question,f.evidence,'c'*32,
            stages.append,observe=lambda event,payload:events.append((event,payload)))
        self.assertEqual(stages,['review_dispatch']*3)
        self.assertEqual(len(f.transport.calls),4)
        self.assertEqual(result['claims'],f.claims)
        self.assertEqual(len(result['model_quote_reviews']),2)
        receipts=[result['model_call'],*result['model_quote_reviews'],result['model_review']]
        self.assertEqual(len({r['reservation_id'] for r in receipts}),4)
        full=json.loads(f.transport.calls[-1]['messages'][1]['content'])
        self.assertEqual([e['text'] for e in full['evidence']],[e.text for e in f.evidence])
        self.assertEqual(full['answer_parts'],f.parts)
        accepted=[p for e,p in events if e=='model_output_accepted']
        self.assertEqual([p.get('review_kind') for p in accepted],
                         [None,'isolated_quote','isolated_quote','whole_source'])

    def test_quote_rejection_stops_before_other_reviews_and_exposes_no_draft(self):
        f=self.f;f.transport.outputs[1]={'quote_supported':False}
        engine=f.engine(evidence_on_model_rejection=True)
        answer=engine.query(Actor('eng_b'),f.question)
        self.assertEqual(len(f.transport.calls),2)
        self.assertEqual(answer['answer_status'],'evidence_only')
        self.assertEqual(answer['claims'],[])
        self.assertNotIn('model_quote_reviews',answer)
        events=engine.audit.export()
        rejection=next(e for e in events if e['event_type']=='model_output_rejected')
        self.assertEqual(rejection['payload']['diagnostic']['validation_detail'],'quote_review_unsupported')
        self.assertIs(rejection['payload']['diagnostic']['review_quote_supported'],False)

    def test_full_source_rejection_still_rejects_after_all_quotes_pass(self):
        f=self.f;f.transport.outputs[-1]['conflicts_handled']=False
        answer=f.engine(evidence_on_model_rejection=True).query(Actor('eng_b'),f.question)
        self.assertEqual(len(f.transport.calls),4)
        self.assertEqual(answer['claims'],[])
        self.assertEqual(answer['answer_status'],'evidence_only')

    def test_denial_between_reviews_prevents_next_call(self):
        f=self.f;stages=[]
        def authorize(phase):
            stages.append(phase)
            if len(stages)==2:raise PermissionError('revoked')
        with self.assertRaises(PermissionError):
            f.model.generate_with_authorization(f.question,f.evidence,'d'*32,authorize)
        self.assertEqual(len(f.transport.calls),2)

    def test_receipts_survive_engine_and_reject_missing_or_duplicate(self):
        f=self.f
        answer=f.engine().query(Actor('eng_b'),f.question)
        self.assertEqual(len(answer['model_quote_reviews']),2)
        self.assertEqual(answer['review_status'],'accepted')
        original=f.model.generate_with_authorization
        for kind in ('missing','duplicate'):
            f.transport.calls.clear()
            def tampered(*args,**kwargs):
                result=original(*args,**kwargs)
                if kind=='missing':del result['model_quote_reviews']
                else:result['model_quote_reviews'][0]=result['model_review']
                return result
            f.model.generate_with_authorization=tampered
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                f.engine().query(Actor('eng_b'),f.question)
            f.model.generate_with_authorization=original

    def test_empty_claims_skip_quote_calls_but_keep_whole_source_review(self):
        f=self.f
        f.transport.outputs=[{'answer_parts':[{'question':f.question,'resolution':'unavailable','claims':[]}]},
            {'verdicts':[],'question_covered':True,'filtered_answer_complete':True,
             'parts_supported':True,'premise_handled':True,'conflicts_handled':True,
             'part_verdicts':[{'index':0,'requested_information_provided':False,'gap_explanation_supported':True}]}]
        answer=f.engine().query(Actor('eng_b'),f.question)
        self.assertEqual(len(f.transport.calls),2)
        self.assertEqual(answer['model_quote_reviews'],[])
        self.assertEqual(answer['review_status'],'accepted')
