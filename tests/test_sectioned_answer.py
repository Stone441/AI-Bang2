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
    def test_partition_diagnostics_preserve_exact_substring_boundary(self):
        from brain.deepseek import OutputValidationError
        valid={'question':'PAY-102','status':'supported','claim_indices':[0]}
        self.assertEqual(validate_answer_parts([valid],[{}],'Status of PAY-102?'),[valid])
        for changed,detail in [
            ({**valid,'question':'PRIVATE fabricated question'},'part_question_not_substring'),
            ({**valid,'question':''},'part_question_shape'),
            ({**valid,'extra':'PRIVATE'},'part_metadata_shape'),
            ({**valid,'status':'PRIVATE'},'part_status_or_indices')]:
            with self.assertRaises(OutputValidationError) as caught:
                validate_answer_parts([changed],[{}],'Status of PAY-102?')
            diagnostic=caught.exception.diagnostic()
            self.assertIn(detail,str(diagnostic))
            self.assertNotIn('PRIVATE',str(diagnostic))

    def test_review_example_contains_complete_required_wire_schema(self):
        from brain.sectioned_answer import SectionedAnswerReview
        from brain.synthesis import EvidenceReview
        text=SectionedAnswerReview.output_instructions
        example=json.JSONDecoder().raw_decode(text[text.index('{'):])[0]
        self.assertEqual(set(example),{'question_covered','filtered_answer_complete','verdicts',
            'parts_supported','premise_handled','conflicts_handled','part_verdicts'})
        self.assertEqual(set(example['part_verdicts'][0]),
            {'index','requested_information_provided','gap_explanation_supported'})
        self.assertNotIn('part_verdicts',EvidenceReview.output_instructions)
        self.assertIn('verdicts:[]',text)

    def test_quote_scope_review_keeps_both_selected_quotes_and_full_evidence(self):
        from brain.sectioned_answer import SectionedAnswerReview, QUOTE_SUPPORT_CONTRACT
        reviewer=SectionedAnswerReview('synthetic-not-a-key',self.ledger,synthetic_only=True,transport=self.transport,
            claims=self.claims,parts=self.parts,today=PRICE_DATE)
        messages=reviewer.messages(self.question,self.evidence)
        body=json.loads(messages[1]['content'])
        self.assertEqual(body['claims'],self.claims)
        self.assertEqual(len(body['evidence']),len(self.evidence))
        for actual,original in zip(body['evidence'],self.evidence):
            self.assertEqual(actual['text'],original.text)
        self.assertIn(QUOTE_SUPPORT_CONTRACT,messages[0]['content'])
        self.assertIn(QUOTE_SUPPORT_CONTRACT,self.model.messages(self.question,self.evidence)[0]['content'])
        for field in ('supported','responsive'):
            rejected=copy.deepcopy(self.transport.outputs[1])
            rejected['verdicts'][0][field]=False
            with self.assertRaises(ValueError):reviewer.parse_output(rejected,self.evidence)
        self.assertEqual(reviewer.parse_output(self.transport.outputs[1],self.evidence),self.claims)

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
        draft={'answer_parts':[{'question':p['question'],'status':p['status'],
            'claims':[{'text':self.claims[i]['text'],'supports':self.claims[i]['supports']}
                      for i in p['claim_indices']]} for p in self.parts]}
        self.transport=SequentialTransport(draft,[{'index':i,'supported':True,'responsive':True} for i in range(2)])
        self.transport.outputs[1]['part_verdicts']=[{'index':i,'requested_information_provided':p['status']=='supported','gap_explanation_supported':True} for i,p in enumerate(self.parts)]
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
            {'verdicts':[],'question_covered':True,'parts_supported':True,'premise_handled':True,'conflicts_handled':True,'part_verdicts':[{'index':i,'requested_information_provided':False,'gap_explanation_supported':True} for i in range(len(self.parts))]}]
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

    def test_rejected_insufficiency_does_not_turn_unrelated_sources_into_answer_claims(self):
        question='What confirmed Q4 revenue did payment-service Atlantis generate?'
        self.transport.outputs=[{'claims':[], 'answer_parts':[
            {'question':question,'status':'insufficient','claim_indices':[]}]},
            {'verdicts':[],'question_covered':False,'parts_supported':True,
             'premise_handled':True,'conflicts_handled':True,'part_verdicts':[{'index':i,'requested_information_provided':False,'gap_explanation_supported':True} for i in range(len(self.parts))]}]
        engine=self.engine(evidence_on_model_rejection=True)
        answer=engine.query(Actor('eng_b'),question)
        self.assertEqual(answer['answer_status'],'evidence_only')
        self.assertEqual(answer['claims'],[])
        self.assertTrue(answer['evidence'])
        self.assertNotIn('answer_parts',answer)
        self.assertEqual(len(self.transport.calls),2)
        self.assertEqual(engine.safe_history(Actor('eng_b'),answer['request_id']),[answer])
        self.world.revoked.add(('eng_b',answer['evidence'][0]['resource_id']))
        self.assertTrue(engine.safe_history(Actor('eng_b'),answer['request_id'])[0]['unavailable'])

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

    def test_nested_parts_derive_indices_and_citation_ids_before_independent_review(self):
        self.transport.outputs[0]={'answer_parts':[
            {'question':'Is PAY-102 complete','status':'supported','claims':[
                {'text':self.claims[0]['text'],'supports':self.claims[0]['supports']}]},
            {'question':'can we offer payment-retry to all customers','status':'supported','claims':[
                {'text':self.claims[1]['text'],'supports':self.claims[1]['supports']}]},
            {'question':'when is GA','status':'insufficient','claims':[]}]}
        stages=[]
        answer=self.model.generate_with_authorization(self.question,self.evidence,'1'*32,stages.append)
        self.assertEqual(answer['answer_parts'],self.parts)
        self.assertEqual(answer['claims'],self.claims)
        self.assertEqual(stages,['review_dispatch'])
        review=json.loads(self.transport.calls[1]['messages'][1]['content'])
        self.assertEqual(review['claims'],self.claims)
        self.assertEqual(review['answer_parts'],self.parts)

    def test_nested_four_source_values_preserve_real_ids_and_exact_qualified_quotes(self):
        question='What are the Confluence, Jira, Slack and Drive probe values?'
        evidence=[];parts=[]
        for source in ('confluence','jira','slack','drive'):
            eid=source+':synthetic-long-native-resource@123456789#0:200'
            text='[SYNTHETIC] VALIDATION-20261015: '+source+' probe value is amber.'
            evidence.append(Evidence(eid,source+':synthetic-long-native-resource',123456789,source,
                'Synthetic probe',{'text_window':{'start':0,'end':len(text)}},text,
                '2026-10-15','2026-10-15','https://example.com'))
            parts.append({'question':source.capitalize() if source!='slack' else 'Slack',
                'status':'supported','claims':[{'text':source+' probe value for VALIDATION-20261015 is amber.',
                    'supports':[{'evidence_id':eid,'quote':text}]}]})
        parts[0]['question']='Confluence';parts[1]['question']='Jira';parts[3]['question']='Drive'
        output={'answer_parts':parts}
        claims=self.model.parse_output(output,evidence)
        metadata=self.model.validated_metadata(question,output,claims)
        self.assertEqual([p['claim_indices'] for p in metadata['answer_parts']],[[0],[1],[2],[3]])
        self.assertEqual([c['evidence_ids'] for c in claims],[[e.evidence_id] for e in evidence])
        self.assertEqual([c['supports'][0]['quote'] for c in claims],[e.text for e in evidence])

    def test_nested_shape_limits_and_unsafe_citations_never_reach_review(self):
        valid={'answer_parts':[{'question':self.question,'status':'supported','claims':[
            {'text':self.claims[0]['text'],'supports':self.claims[0]['supports']}]}]}
        mutations=[]
        for kind in ('mixed','extra_claim_field','unknown_id','insufficient','too_many','invented_question'):
            output=copy.deepcopy(valid);part=output['answer_parts'][0]
            if kind=='mixed':output['claims']=self.claims
            elif kind=='extra_claim_field':part['claims'][0]['evidence_ids']=['J-02@1']
            elif kind=='unknown_id':part['claims'][0]['supports'][0]['evidence_id']='restricted@1'
            elif kind=='insufficient':part['status']='insufficient'
            elif kind=='too_many':part['claims']*=5
            else:part['question']='invented question'
            mutations.append(output)
        for output in mutations:
            with self.subTest(output=output):
                self.transport.outputs[0]=output;self.transport.calls.clear()
                with self.assertRaises(ModelUnavailable):
                    self.model.generate_with_authorization(self.question,self.evidence,'2'*32,lambda _:None)
                self.assertEqual(len(self.transport.calls),1)

    def test_rejected_claim_diagnostic_identifies_field_without_rejected_text(self):
        cases=('identifier_quote','claim_text_length','citation_ids','support_shape')
        for detail in cases:
            claim=copy.deepcopy(self.claims[0])
            if detail=='identifier_quote':claim['text']='PRIVATE-98765 code fix is done.'
            elif detail=='claim_text_length':claim['text']='PRIVATE'*100
            elif detail=='citation_ids':claim['evidence_ids']=['PRIVATE-98765@1']
            else:claim['supports'][0]['PRIVATE']='PRIVATE-98765'
            self.transport.outputs[0]={'claims':[claim],'answer_parts':[
                {'question':self.question,'status':'supported','claim_indices':[0]}]}
            self.transport.calls.clear();events=[]
            with self.assertRaises(ModelUnavailable):
                self.model.generate_with_authorization(self.question,self.evidence,'3'*32,lambda _:None,
                    observe=lambda event,payload:events.append((event,payload)))
            diagnostic=events[-1][1]['diagnostic']
            self.assertEqual(events[-1][0],'model_output_rejected')
            self.assertEqual(diagnostic.get('validation_detail'),detail)
            self.assertEqual(diagnostic.get('claim_index'),0)
            self.assertNotIn('PRIVATE',json.dumps(diagnostic))
            self.assertEqual(len(self.transport.calls),1)

    def test_citation_failure_subreasons_are_fixed_and_never_include_ids(self):
        from brain.synthesis import validate_claim
        from brain.deepseek import OutputValidationError
        cases = [('shape', 42, []),
                 ('unknown_id', ['PRIVATE-98765@1'], []),
                 ('duplicate_id', ['J-02@1', 'J-02@1'], []),
                 ('support_count', ['J-02@1'], [])]
        for expected, ids, supports in cases:
            with self.subTest(expected=expected):
                claim = dict(text='Done', evidence_ids=ids, supports=supports)
                with self.assertRaises(OutputValidationError) as caught:
                    validate_claim(claim, self.evidence)
                diagnostic = caught.exception.diagnostic()
                self.assertEqual(diagnostic['validation_detail'], 'citation_ids')
                self.assertEqual(diagnostic['citation_issue'], expected)
                self.assertNotIn('PRIVATE', json.dumps(diagnostic))

    def compact_output(self):
        return {'answer_parts':[{'question':p['question'], 'claims':[
            {'text':self.claims[i]['text'], 'supports':{
                s['evidence_id']:s['quote'] for s in self.claims[i]['supports']}}
            for i in p['claim_indices']]} for p in self.parts]}

    def test_compact_wire_derives_same_canonical_claims_and_reviewed_partitions(self):
        self.transport.outputs[0]=self.compact_output()
        answer=self.model.generate_with_authorization(self.question,self.evidence,'4'*32,lambda _:None)
        self.assertEqual(answer['claims'],self.claims)
        self.assertEqual(answer['answer_parts'],self.parts)
        review=json.loads(self.transport.calls[1]['messages'][1]['content'])
        self.assertEqual(review['claims'],self.claims)
        self.assertEqual(review['answer_parts'],self.parts)
        self.assertEqual(len(self.transport.calls),2)

    def test_compact_wire_never_repairs_duplicate_json_evidence_keys(self):
        self.transport.outputs[0]=self.compact_output()
        original=self.transport._send
        def duplicate(request):
            code,response=original(request)
            message=response['choices'][0]['message']
            key=json.dumps('J-02@1')+':'
            extra=key+json.dumps(self.claims[0]['supports'][0]['quote'])+','
            message['content']=message['content'].replace(key,extra+key,1)
            return code,response
        self.transport._send=duplicate
        events=[]
        with self.assertRaises(ModelUnavailable):
            self.model.generate_with_authorization(self.question,self.evidence,'5'*32,lambda _:None,
                observe=lambda event,payload:events.append((event,payload)))
        self.assertEqual(len(self.transport.calls),1)
        self.assertEqual(events[-1][1]['diagnostic']['validation_detail'],'json_duplicate_field')

    def test_compact_wire_bad_ids_quotes_and_mixed_status_fail_before_review(self):
        for kind in ('unknown','quote','nonstring','extra','legacy_status'):
            with self.subTest(kind=kind):
                output=self.compact_output();part=output['answer_parts'][0];claim=part['claims'][0]
                if kind=='unknown':claim['supports']={'restricted@1':'never supplied quotation'}
                elif kind=='quote':claim['supports']['J-02@1']='Invented approval for every customer.'
                elif kind=='nonstring':claim['supports']['J-02@1']=['wrong type']
                elif kind=='extra':claim['evidence_ids']=['J-02@1']
                else:part['status']='insufficient'
                self.transport.outputs[0]=output;self.transport.calls.clear()
                with self.assertRaises(ModelUnavailable):
                    self.model.generate_with_authorization(self.question,self.evidence,'6'*32,lambda _:None)
                self.assertEqual(len(self.transport.calls),1)

    def typed_gap_output(self):
        draft=self.compact_output()
        for part in draft['answer_parts']:
            part['resolution']='answered' if part['claims'] else 'unavailable'
        draft['answer_parts'][2]['claims']=[{
            'text':'No general release date is confirmed.',
            'supports':{'C-02@1':'No general release date is confirmed.'}}]
        self.transport.outputs[0]=draft
        self.transport.outputs[1]['verdicts'].append({'index':2,'supported':True,'responsive':True})
        return draft

    def test_gap_explanation_retains_citation_without_claiming_value_is_answered(self):
        self.typed_gap_output()
        engine=self.engine();actor=Actor('eng_b')
        answer=engine.query(actor,self.question)
        gap=answer['answer_parts'][2]
        self.assertEqual(gap,{'question':'when is GA','status':'insufficient','claim_indices':[], 'gap_claim_indices':[2]})
        self.assertEqual(answer['claims'][2]['text'],'No general release date is confirmed.')
        self.assertEqual(engine.safe_history(actor,answer['request_id']),[answer])
        generation=next(e for e in engine.audit.export() if e['event_type']=='generation_completed')
        self.assertEqual(generation['payload']['answer_parts'][2],gap)
        self.world.revoked.add(('eng_b','C-02'))
        self.assertTrue(engine.safe_history(actor,answer['request_id'])[0]['unavailable'])

    def test_unknown_value_mislabelled_answered_is_rejected_without_reclassification(self):
        draft=self.typed_gap_output()
        draft['answer_parts'][2]['resolution']='answered'
        answer=self.engine(evidence_on_model_rejection=True).query(Actor('eng_b'),self.question)
        self.assertEqual(answer['answer_status'],'evidence_only')
        self.assertNotIn('answer_parts',answer)
        self.assertEqual(len(self.transport.calls),2)
        self.assertEqual(draft['answer_parts'][2]['resolution'],'answered')

    def test_legacy_wire_cannot_bypass_independent_completeness_verdict(self):
        # Correct facts alone used to pass; a separate per-part disagreement must now reject.
        self.transport.outputs[1]['part_verdicts'][0]['requested_information_provided']=False
        with self.assertRaises(ModelUnavailable):
            self.model.generate_with_authorization(self.question,self.evidence,'7'*32,lambda _:None)
        self.assertEqual(len(self.transport.calls),2)

    def test_invalid_or_missing_part_verdict_rejects_even_with_all_global_checks_true(self):
        original=copy.deepcopy(self.transport.outputs[1])
        for kind in ('missing','short','duplicate_index','bool_index','unknown_value','string_true','gap_false','extra'):
            with self.subTest(kind=kind):
                review=copy.deepcopy(original)
                if kind=='missing':del review['part_verdicts']
                elif kind=='short':review['part_verdicts'].pop()
                elif kind=='duplicate_index':review['part_verdicts'][1]['index']=0
                elif kind=='bool_index':review['part_verdicts'][0]['index']=False
                elif kind=='unknown_value':review['part_verdicts'][0]['requested_information_provided']=None
                elif kind=='string_true':review['part_verdicts'][0]['requested_information_provided']='true'
                elif kind=='gap_false':review['part_verdicts'][2]['gap_explanation_supported']=False
                else:review['part_verdicts'][0]['extra']=True
                self.transport.outputs[1]=review;self.transport.calls.clear()
                with self.assertRaises(ModelUnavailable):
                    self.model.generate_with_authorization(self.question,self.evidence,'8'*32,lambda _:None)

    def test_gap_indices_never_bypass_partition_or_quote_validation(self):
        self.typed_gap_output()
        output=self.transport.outputs[0]
        claims=self.model.parse_output(output,self.evidence)
        parts=self.model.validated_metadata(self.question,output,claims)['answer_parts']
        for kind in ('overlap','duplicate','bool','out_of_range','supported_gap','unassigned','nonlist'):
            with self.subTest(kind=kind):
                bad=copy.deepcopy(parts)
                if kind=='overlap':bad[2]['gap_claim_indices']=[0,2]
                elif kind=='duplicate':bad[2]['gap_claim_indices']=[2,2]
                elif kind=='bool':bad[2]['gap_claim_indices']=[True]
                elif kind=='out_of_range':bad[2]['gap_claim_indices']=[3]
                elif kind=='supported_gap':bad[0]['gap_claim_indices']=[2]
                elif kind=='unassigned':bad[2]['gap_claim_indices']=[]
                else:bad[2]['gap_claim_indices']='2'
                with self.assertRaises(ValueError):validate_answer_parts(bad,claims,self.question)
        output['answer_parts'][2]['claims'][0]['supports']['C-02@1']='A fabricated missing prerequisite.'
        with self.assertRaises(ModelUnavailable):
            self.model.generate_with_authorization(self.question,self.evidence,'9'*32,lambda _:None)
        self.assertEqual(len(self.transport.calls),1)

    def test_typed_wire_requires_known_resolution_and_nonempty_answer(self):
        original=self.typed_gap_output()
        for resolution in ('supported','unknown',True,None):
            bad=copy.deepcopy(original);bad['answer_parts'][0]['resolution']=resolution
            with self.assertRaises(ValueError):self.model.unpack_output(bad)
        bad=copy.deepcopy(original);bad['answer_parts'][0]['claims']=[]
        claims=self.model.parse_output(bad,self.evidence)
        with self.assertRaises(ValueError):self.model.validated_metadata(self.question,bad,claims)

    def test_gap_absence_requires_explicit_evidence_in_both_stage_contracts(self):
        from brain.sectioned_answer import SectionedAnswerReview
        generator=self.model.messages(self.question,self.evidence)[0]['content']
        reviewer=SectionedAnswerReview('synthetic-not-a-key',self.ledger,synthetic_only=True,
            today=PRICE_DATE,claims=self.claims,parts=self.parts).messages(self.question,self.evidence)[0]['content']
        for prompt in (generator,reviewer):
            self.assertIn('Do not infer absence from silence',prompt)
            self.assertIn('exceeds its quoted scope',prompt)
        self.typed_gap_output()
        self.transport.outputs[1]['part_verdicts'][2]['gap_explanation_supported']=False
        answer=self.engine(evidence_on_model_rejection=True).query(Actor('eng_b'),self.question)
        self.assertEqual(answer['answer_status'],'evidence_only')
        self.assertNotIn('answer_parts',answer)

    def test_part_review_failure_diagnostics_are_fixed_and_do_not_store_rejected_text(self):
        original=copy.deepcopy(self.transport.outputs[1])
        for detail in ('part_review_reasoning','part_review_shape','part_review_completeness','part_review_gap_support'):
            with self.subTest(detail=detail):
                review=copy.deepcopy(original)
                if detail=='part_review_reasoning':review['parts_supported']='PRIVATE-BAD-TEXT'
                elif detail=='part_review_shape':review['part_verdicts'][0]['index']='PRIVATE-BAD-TEXT'
                elif detail=='part_review_completeness':review['part_verdicts'][0]['requested_information_provided']=False
                else:review['part_verdicts'][0]['gap_explanation_supported']='PRIVATE-BAD-TEXT'
                self.transport.outputs[1]=review;self.transport.calls.clear();events=[]
                with self.assertRaises(ModelUnavailable):
                    self.model.generate_with_authorization(self.question,self.evidence,'a'*32,lambda _:None,
                        observe=lambda event,payload:events.append((event,payload)))
                diagnostic=events[-1][1]['diagnostic']
                self.assertEqual(diagnostic['validation_detail'],detail)
                self.assertNotIn('PRIVATE',json.dumps(diagnostic))
