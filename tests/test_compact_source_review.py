import json
from dataclasses import replace
import unittest
from unittest.mock import patch

from brain.contracts import Actor
from brain.deepseek import PRICE_DATE
from brain.synthesis import CompactSourcePassageReview, DeepSeekCompactSourceReviewModel, SourcePassageReview
import test_source_review as source_tests
import test_source_review_dispatch_contract as dispatch_tests


class CompactReview(unittest.TestCase):
    setUp = source_tests.SourceReview.setUp
    tearDown = source_tests.SourceReview.tearDown
    engine = source_tests.SourceReview.engine
    change = staticmethod(dispatch_tests.DispatchContract.change)

    def candidate(self):
        return DeepSeekCompactSourceReviewModel('synthetic-not-a-key', self.ledger,
            synthetic_only=True, transport=self.transport, today=PRICE_DATE,
            reasoning_effort='none', output_tokens=8192)

    def reviewer(self, evidence, *, compact=True, claims=None):
        cls = CompactSourcePassageReview if compact else SourcePassageReview
        return cls('synthetic-not-a-key', self.ledger, synthetic_only=True,
            today=PRICE_DATE, claims=claims if claims is not None else self.candidate().source_claims(evidence))

    def dynamic(self):
        def send(request):
            payload = json.loads(request.data)
            self.transport.calls.append(payload)
            body = json.loads(payload['messages'][1]['content'])
            verdicts = [{'index': claim['index'], 'supported': True,
                         'responsive': passage['evidence_id'] == 'C-01@1'}
                        for passage in body['passages'] for claim in passage['claims']]
            return 200, {'model': 'deepseek-flash',
                'usage': {'prompt_tokens': 100, 'completion_tokens': 20, 'total_tokens': 120},
                'choices': [{'finish_reason': 'stop', 'message': {'role': 'assistant', 'content': json.dumps({
                    'question_covered': True, 'filtered_answer_complete': True, 'verdicts': verdicts})}}]}
        self.transport._send = send

    def test_lossless_grouping_preserves_table_unicode_scope_and_contradiction(self):
        text = '[SYNTHETIC] Entity\tScope\tApproval\n服务甲\tpilot\tApproved\n'+('background\n'*150)+'GA not approved. Later approval withdrawn.'
        e = replace(self.evidence, text=text, locator={'row': 'entire table'})
        compact = self.reviewer([e]).messages('Which scope is approved?', [e])
        old = self.reviewer([e], compact=False).messages('Which scope is approved?', [e])
        body = json.loads(compact[1]['content'])
        self.assertEqual(''.join(c['text'] for c in body['passages'][0]['claims']), text)
        self.assertEqual(body['passages'][0]['source_context'], {'title': e.title, 'locator': e.locator})
        self.assertEqual([c['index'] for c in body['passages'][0]['claims']], list(range(len(body['passages'][0]['claims']))))
        self.assertLess(len(json.dumps(compact)), len(json.dumps(old)))
        self.assertEqual(self.transport.calls, [])

    def test_missing_reordered_or_rewritten_source_parts_are_rejected_locally(self):
        e = replace(self.evidence, text='[SYNTHETIC] '+('Different scope clauses. '*70)+'GA prohibited.')
        claims = self.candidate().source_claims([e])
        for altered in (claims[:-1], list(reversed(claims)), [dict(claims[0], text='fabricated')]+claims[1:]):
            with self.subTest(altered=altered[0]['text'][:15]):
                with self.assertRaises(ValueError):
                    self.reviewer([e], claims=altered).messages('What is approved?', [e])
        self.assertEqual(self.transport.calls, [])

    def test_real_engine_uses_one_receipt_and_current_history_authorization(self):
        engine, world = self.engine()
        self.dynamic()
        result = engine.query(Actor('eng_b'), 'payment-service incident runbook')
        self.assertEqual(len(self.transport.calls), 1)
        self.assertEqual(result['review_status'], 'accepted')
        self.assertEqual(result['claim_format'], 'reviewed_source_v1')
        self.assertEqual(self.transport.calls[0]['thinking'], {'type': 'disabled'})
        self.assertEqual(result['claims'][0]['text'], world.resources['C-01']['text'])
        world.revoked.add(('eng_b', 'C-01'))
        self.assertTrue(engine.safe_history(Actor('eng_b'), result['request_id'])[0]['unavailable'])

    def test_construction_and_after_review_changes_still_stop(self):
        for moment in ('construction', 'after_review'):
            for outcome in ('deny', 'unknown', 'version', 'deleted'):
                with self.subTest(moment=moment, outcome=outcome):
                    engine, world = self.engine()
                    self.dynamic()
                    self.transport.calls.clear()
                    original = engine.model.source_claims if moment == 'construction' else self.transport._send
                    def changed(*args, **kwargs):
                        value = original(*args, **kwargs)
                        self.change(world, outcome)
                        return value
                    target, name = (engine.model, 'source_claims') if moment == 'construction' else (self.transport, '_send')
                    with patch.object(target, name, side_effect=changed):
                        with self.assertRaises(PermissionError):
                            engine.query(Actor('eng_b'), 'payment-service incident runbook')
                    self.assertEqual(len(self.transport.calls), 0 if moment == 'construction' else 1)
                    self.assertEqual(engine.store.history('eng_b'), [])

    def test_existing_output_contract_rejects_missing_coverage_and_unsupported(self):
        reviewer = self.reviewer([self.evidence])
        valid = {'question_covered': True, 'filtered_answer_complete': True,
                 'verdicts': [{'index': 0, 'supported': True, 'responsive': True}]}
        self.assertEqual(reviewer.parse_output(valid, [self.evidence]), reviewer.claims)
        for output in (dict(valid, question_covered=False), dict(valid, verdicts=[]),
                       dict(valid, verdicts=[{'index': 0, 'supported': False, 'responsive': True}])):
            with self.assertRaises(ValueError):
                reviewer.parse_output(output, [self.evidence])
