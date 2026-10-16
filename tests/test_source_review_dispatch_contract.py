"""Offline dispatch boundaries and immutable historical quality counterexamples.

Recorded review replay is parser evidence, never current native or model quality.
"""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from brain.contracts import Actor, Evidence
from brain.deepseek import PRICE_DATE
from brain.synthesis import DeepSeekReviewAllSourcesModel, SourcePassageReview
import test_source_review as setup_tests


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'tests/fixtures/source_review'


class DispatchContract(unittest.TestCase):
    setUp = setup_tests.SourceReview.setUp
    tearDown = setup_tests.SourceReview.tearDown
    candidate = setup_tests.SourceReview.candidate
    engine = setup_tests.SourceReview.engine
    verdicts = setup_tests.SourceReview.verdicts
    dynamic_review = setup_tests.SourceReview.dynamic_review

    @staticmethod
    def change(world, outcome):
        if outcome == 'deny':
            world.revoked.add(('eng_b', 'C-01'))
        elif outcome == 'unknown':
            world.faults.add('confluence')
        elif outcome == 'version':
            world.resources['C-01']['version'] += 1
        elif outcome == 'deleted':
            world.resources['C-01']['active'] = False

    def assert_no_answer(self, engine):
        self.assertEqual(engine.store.history('eng_b'), [])
        self.assertFalse(any(e['event_type'] == 'response_committed'
                             for e in engine.audit.export()))

    def test_change_during_quote_construction_blocks_dispatch_without_reservation(self):
        # model_dispatch has already passed; the mutation is in actual local
        # quote construction, before review_dispatch. A cached allow is unsafe.
        for outcome in ('deny', 'unknown', 'version', 'deleted'):
            with self.subTest(outcome=outcome):
                engine, world = self.engine()
                self.dynamic_review()
                self.transport.calls.clear()
                original = engine.model.source_claims

                def construct(evidence):
                    claims = original(evidence)
                    self.change(world, outcome)
                    return claims

                with patch.object(engine.model, 'source_claims',
                                  side_effect=construct):
                    with self.assertRaises(PermissionError):
                        engine.query(Actor('eng_b'), 'payment-service incident runbook')
                self.assertEqual(self.transport.calls, [])
                self.assertEqual(self.ledger.db.execute(
                    'SELECT count(*) FROM model_calls').fetchone()[0], 0)
                self.assert_no_answer(engine)

    def test_change_after_mock_review_blocks_delivery_but_preserves_usage(self):
        for outcome in ('deny', 'unknown', 'version', 'deleted'):
            with self.subTest(outcome=outcome):
                engine, world = self.engine()
                self.dynamic_review()
                self.transport.calls.clear()
                original = self.transport._send
                before = self.ledger.db.execute('SELECT count(*) FROM model_calls').fetchone()[0]

                def send(request):
                    result = original(request)
                    self.change(world, outcome)
                    return result

                with patch.object(self.transport, '_send', side_effect=send):
                    with self.assertRaises(PermissionError):
                        engine.query(Actor('eng_b'), 'payment-service incident runbook')
                self.assertEqual(len(self.transport.calls), 1)
                self.assertEqual(self.ledger.db.execute(
                    'SELECT count(*) FROM model_calls').fetchone()[0], before + 1)
                self.assertTrue(any(e['event_type'] == 'model_usage_received'
                                    for e in engine.audit.export()))
                self.assert_no_answer(engine)

    def load_record(self, case):
        manifest = json.loads((REVIEW / 'COUNTEREXAMPLES.json').read_text())
        record = next(r for r in manifest['cases'] if r['case'] == case)
        bodies = {}
        for name, item in record['files'].items():
            raw = (ROOT / item['path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), item['sha256'])
            bodies[name] = json.loads(raw)
        evidence = [Evidence(**e) for e in bodies['response']['evidence']]
        claims = self.candidate().source_claims(evidence)
        diagnostic = (bodies['result'].get('review')
                      or bodies['result']['diagnostics'][0])
        output = {'question_covered': diagnostic['review_question_covered'],
                  'filtered_answer_complete': diagnostic['review_filtered_answer_complete'],
                  'verdicts': diagnostic['review_verdicts']}
        reviewer = SourcePassageReview('synthetic-not-a-key', self.ledger,
            synthetic_only=True, transport=self.transport, today=PRICE_DATE, claims=claims)
        c01 = next(e for e in evidence if e.resource_id == record['required_resource_id'])
        indices = [i for i, c in enumerate(claims) if c['evidence_ids'] == [c01.evidence_id]]
        self.assertTrue(indices)
        self.assertEqual(''.join(claims[i]['text'] for i in indices), c01.text)
        return bodies, evidence, output, reviewer, c01

    def test_historical_v1_incomplete_coverage_is_rejected(self):
        bodies, evidence, output, reviewer, c01 = self.load_record('v1_rejected')
        with self.assertRaisesRegex(ValueError, 'Incomplete model review'):
            reviewer.parse_output(output, evidence)
        self.assertEqual(bodies['response']['answer_status'], 'evidence_only')
        self.assertFalse(output['question_covered'])
        self.assertEqual(self.transport.calls, [])

    def test_historical_v2_false_acceptance_remains_a_quality_failure(self):
        bodies, evidence, output, reviewer, c01 = self.load_record('v2_false_acceptance')
        retained = reviewer.parse_output(output, evidence)
        self.assertEqual(bodies['response']['review_status'], 'accepted')
        self.assertTrue(output['question_covered'])
        self.assertNotIn(c01.evidence_id,
                         {eid for c in retained for eid in c['evidence_ids']})
        self.assertNotIn(c01.evidence_id,
                         {eid for c in bodies['response']['claims'] for eid in c['evidence_ids']})
        self.assertEqual(self.transport.calls, [])

    def test_historical_low_preserves_action_and_same_input_not_stability(self):
        bodies, evidence, output, reviewer, c01 = self.load_record('low_single_success')
        retained = reviewer.parse_output(output, evidence)
        self.assertIn(c01.evidence_id, {eid for c in retained for eid in c['evidence_ids']})
        self.assertIn(c01.evidence_id,
                      {eid for c in bodies['response']['claims'] for eid in c['evidence_ids']})
        failed, _, _, _, _ = self.load_record('v2_false_acceptance')
        self.assertEqual(bodies['response']['evidence'], failed['response']['evidence'])
        self.assertEqual(self.transport.calls, [])


if __name__ == '__main__':
    unittest.main()
