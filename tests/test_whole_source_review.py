"""Whole-source selector contract; mocks do not prove semantic quality."""
import json
import unittest
from dataclasses import replace
from unittest.mock import patch
from brain.contracts import Actor
from brain.deepseek import PRICE_DATE
from brain.synthesis import WholeSourceReview, DeepSeekWholeSourceReviewModel
import test_source_review as source_tests
import test_compact_source_review as compact_tests
import test_source_review_dispatch_contract as dispatch_tests


class WholeReview(unittest.TestCase):
    setUp = source_tests.SourceReview.setUp
    tearDown = source_tests.SourceReview.tearDown
    change = staticmethod(dispatch_tests.DispatchContract.change)
    test_construction_and_after_review_changes_still_stop = compact_tests.CompactReview.test_construction_and_after_review_changes_still_stop

    def candidate(self):
        return DeepSeekWholeSourceReviewModel('synthetic-not-a-key', self.ledger,
            synthetic_only=True, transport=self.transport, today=PRICE_DATE,
            reasoning_effort='none', output_tokens=8192)

    def engine(self):
        engine, world = source_tests.SourceReview.engine(self)
        engine.source_review_dispatch='single';engine.history_read_mode='batch'
        return engine, world

    def reviewer(self, evidence, question='What is the archive mitigation?'):
        reviewer=WholeSourceReview('synthetic-not-a-key',self.ledger,synthetic_only=True,
            today=PRICE_DATE,claims=self.candidate().source_claims(evidence))
        reviewer.messages(question,evidence)
        return reviewer

    def dynamic(self):
        def send(request):
            payload=json.loads(request.data);self.transport.calls.append(payload)
            body=json.loads(payload['messages'][1]['content'])
            output={'selected':[p['alias'] for p in body['passages']],
                    'selection_safe':True,'question_covered':True}
            return 200,{'model':'deepseek-flash',
                'usage':{'prompt_tokens':100,'completion_tokens':20,'total_tokens':120},
                'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':json.dumps(output)}}]}
        self.transport._send=send

    def test_full_source_table_scope_and_contradiction_preserved(self):
        text='[SYNTHETIC] Archive runbook: inspect the queue.\nEntity\tScope\tStatus\n归档\tpilot\tProposed\n'+('Context. '*200)+'Approval withdrawn; do not execute.'
        evidence=[replace(self.evidence,title='Archive runbook',text=text)]
        reviewer=self.reviewer(evidence)
        body=json.loads(reviewer.messages('What is the archive mitigation?',evidence)[1]['content'])
        self.assertEqual(body['must_include'],['P0'])
        self.assertEqual(body['passages'][0]['text'],text)
        claims=reviewer.parse_output({'selected':['P0'],'selection_safe':True,'question_covered':True},evidence)
        self.assertEqual(''.join(c['text'] for c in claims),text)
        altered=[replace(evidence[0],text=text.replace('withdrawn','confirmed'))]
        with self.assertRaises(ValueError):reviewer.parse_output({'selected':['P0'],'selection_safe':True,'question_covered':True},altered)

    def test_rejects_unsafe_incomplete_unknown_duplicate_or_unprepared_selection(self):
        reviewer=self.reviewer([self.evidence])
        valid={'selected':['P0'],'selection_safe':True,'question_covered':True}
        bad=[dict(valid,selection_safe=False),dict(valid,question_covered=False),dict(valid,selection_safe=1),
             dict(valid,selected=[]),dict(valid,selected=['P1']),dict(valid,selected=['P0','P0']),
             dict(valid,selected=[0]),dict(valid,selected=['https://example.test']),dict(valid,extra='injected')]
        for output in bad:
            with self.subTest(output=output):
                with self.assertRaises(ValueError):reviewer.parse_output(output,[self.evidence])
        unprepared=WholeSourceReview('synthetic-not-a-key',self.ledger,synthetic_only=True,
            today=PRICE_DATE,claims=self.candidate().source_claims([self.evidence]))
        with self.assertRaises(ValueError):unprepared.parse_output(valid,[self.evidence])

    def test_required_actions_cannot_be_replaced_by_status(self):
        action=replace(self.evidence,evidence_id='archive@7',title='Archive runbook',text='[SYNTHETIC] Inspect the archive queue and follow the approved failover procedure.')
        status=replace(self.evidence,evidence_id='status@2',title='Archive release',text='[SYNTHETIC] Archive pilot approved. GA is not approved.')
        reviewer=self.reviewer([action,status])
        with self.assertRaisesRegex(ValueError,'operational evidence omitted'):
            reviewer.parse_output({'selected':['P1'],'selection_safe':True,'question_covered':True},[action,status])
        claims=reviewer.parse_output({'selected':['P0','P1'],'selection_safe':True,'question_covered':True},[action,status])
        self.assertEqual([c['text'] for c in claims],[action.text,status.text])

    def test_engine_one_receipt_history_rechecks_and_diagnostic_is_bounded(self):
        engine,world=self.engine();self.dynamic()
        result=engine.query(Actor('eng_b'),'payment-service incident runbook')
        self.assertEqual(result['review_status'],'accepted')
        self.assertEqual(len(self.transport.calls),1)
        self.assertTrue(result['model_review']['called'])
        self.assertEqual(engine.safe_history(Actor('eng_b'),result['request_id']),[result])
        event=next(e for e in engine.audit.export() if e['event_type']=='model_output_accepted')
        self.assertIs(event['payload']['diagnostic']['review_selection_safe'],True)
        self.assertTrue(event['payload']['diagnostic']['review_selected_aliases'])
        world.revoked.add(('eng_b','C-01'))
        self.assertTrue(engine.safe_history(Actor('eng_b'),result['request_id'])[0]['unavailable'])
