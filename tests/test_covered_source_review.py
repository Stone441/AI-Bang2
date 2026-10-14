"""Independent omission rejection; no claim of complete semantic validation."""
import json
import unittest
from dataclasses import replace
from brain.coverage import required_action_sources
from brain.synthesis import CoveredSourcePassageReview, DeepSeekCoveredSourceReviewModel
from brain.deepseek import PRICE_DATE
import test_compact_source_review as compact_tests
import test_source_review_dispatch_contract as dispatch_tests


class CoveredReview(compact_tests.CompactReview):
    load_record = dispatch_tests.DispatchContract.load_record

    def candidate(self):
        return DeepSeekCoveredSourceReviewModel('synthetic-not-a-key', self.ledger,
            synthetic_only=True, transport=self.transport, today=PRICE_DATE,
            reasoning_effort='none', output_tokens=8192)

    def covered(self, evidence, question):
        reviewer = CoveredSourcePassageReview('synthetic-not-a-key', self.ledger,
            synthetic_only=True, today=PRICE_DATE, claims=self.candidate().source_claims(evidence))
        reviewer.messages(question, evidence)
        return reviewer

    def test_historical_false_acceptance_now_rejected_positive_retained(self):
        for case, reject in [('v2_false_acceptance', True), ('low_single_success', False)]:
            bodies, evidence, output, original, required = self.load_record(case)
            reviewer = self.covered(evidence, bodies['response']['question'])
            self.assertIn(required.evidence_id, reviewer.required_action_ids)
            if reject:
                with self.assertRaisesRegex(ValueError, 'operational evidence omitted'):
                    reviewer.parse_output(output, evidence)
            else:
                claims = reviewer.parse_output(output, evidence)
                self.assertEqual(claims, original.parse_output(output, evidence))
        self.assertEqual(self.transport.calls, [])

    def test_new_subject_and_ids_require_full_qualified_passage(self):
        text = '[SYNTHETIC] Proposed archive remediation: inspect the export queue. '+('Retain limited trial scope. '*70)+'Approval withdrawn; do not execute.'
        e = replace(self.evidence, evidence_id='fresh-archive@7', title='Archive runbook', text=text)
        reviewer = self.covered([e], 'What is the approved archive remediation?')
        self.assertEqual(reviewer.required_action_ids, {e.evidence_id})
        verdicts = [{'index': i, 'supported': True, 'responsive': True} for i in range(len(reviewer.claims))]
        self.assertGreater(len(verdicts), 1)
        output = {'question_covered': True, 'filtered_answer_complete': True, 'verdicts': verdicts}
        self.assertEqual(''.join(c['text'] for c in reviewer.parse_output(output, [e])), text)
        # Keeping the source ID but omitting the final withdrawal must not pass.
        verdicts[-1]['responsive'] = False
        with self.assertRaisesRegex(ValueError, 'operational evidence omitted'):
            reviewer.parse_output(output, [e])

    def test_narrow_guard_does_not_guess_ambiguous_or_other_subject(self):
        e = replace(self.evidence, title='Archive runbook', text='[SYNTHETIC] Inspect the archive export queue.')
        for question in ['Who owns the archive runbook?', 'When was the archive mitigation approved?',
                         'What is the archive runbook owner?', 'What is the approved mitigation?',
                         'What is the payroll mitigation?', 'What is the archive status?']:
            with self.subTest(question=question):
                self.assertEqual(required_action_sources(question, [e]), set())
        status = replace(e, text='[SYNTHETIC] Archive runbook: pilot approved, GA not approved.')
        self.assertEqual(required_action_sources('What is the archive mitigation?', [status]), set())

    def test_guard_cannot_override_model_rejection(self):
        e = replace(self.evidence, title='Archive runbook', text='[SYNTHETIC] Inspect the archive queue.')
        reviewer = self.covered([e], 'What is the archive mitigation?')
        output = {'question_covered': True, 'filtered_answer_complete': True,
                  'verdicts': [{'index': 0, 'supported': True, 'responsive': True}]}
        for bad in [dict(output, question_covered=False), dict(output, filtered_answer_complete=False),
                    dict(output, verdicts=[{'index': 0, 'supported': False, 'responsive': True}])]:
            with self.assertRaises(ValueError):
                reviewer.parse_output(bad, [e])
