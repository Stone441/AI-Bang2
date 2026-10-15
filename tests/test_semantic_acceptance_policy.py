import unittest
from scripts.semantic_acceptance_policy import AcceptanceRun, AcceptanceStop


class AcceptancePolicy(unittest.TestCase):
    def test_real_response_shape_stops_second_failure_before_third_dispatch(self):
        run = AcceptanceRun(['a', 'b', 'c'])
        response = {'answer_kind':'sectioned_synthesis', 'answer_status':'evidence_only',
                    'synthesis_failure':'model_output_unavailable', 'claims':[]}
        calls = []
        for case_id in ['a', 'b', 'c']:
            try:
                run.begin(case_id)
                calls.append(case_id)
                run.finish(case_id, 200, response, {'unknown':[]})
                run.assess(case_id, passed=True, evidence='structural-policy-test-only')
            except AcceptanceStop:
                break
        self.assertEqual(calls, ['a', 'b'])
        with self.assertRaises(AcceptanceStop):run.begin('c')

    def test_no_retry_and_new_unknown_stop_even_with_accepted_answer(self):
        run = AcceptanceRun(['a', 'b'])
        run.begin('a')
        run.finish('a', 200, {'review_status':'accepted'}, {'unknown':[]})
        run.assess('a', passed=True, evidence='test oracle checked')
        with self.assertRaises(AcceptanceStop):run.begin('a')
        run.begin('b')
        with self.assertRaises(AcceptanceStop):
            run.finish('b', 200, {'review_status':'accepted'}, {'unknown':['reservation']})
        self.assertTrue(run.stopped)

    def test_failure_count_is_not_reset_by_success(self):
        run = AcceptanceRun(['a', 'b', 'c'])
        for case_id, status in [('a','evidence_only'), ('b','accepted')]:
            run.begin(case_id)
            run.finish(case_id, 200, {'answer_status':status,'review_status':status}, {'unknown':[]})
            run.assess(case_id, passed=True, evidence='structural-policy-test-only')
        run.begin('c')
        with self.assertRaises(AcceptanceStop):
            run.finish('c', 200, {'answer_status':'evidence_only'}, {'unknown':[]})

    def test_accepted_review_cannot_dispatch_before_business_assessment(self):
        run = AcceptanceRun(['partial', 'conflict'])
        run.begin('partial')
        run.finish('partial', 200, {'review_status': 'accepted'}, {'unknown': []})
        with self.assertRaises(AcceptanceStop):
            run.begin('conflict')
        with self.assertRaises(AcceptanceStop):
            run.assess('partial', passed=False, evidence='Date absent but marked supported')
        with self.assertRaises(AcceptanceStop):
            run.begin('conflict')

    def test_independent_pass_unlocks_exactly_next_case(self):
        run = AcceptanceRun(['a', 'b'])
        run.begin('a')
        run.finish('a', 200, {'review_status': 'accepted'}, {'unknown': []})
        run.assess('a', passed=True, evidence='report.json#case-a')
        run.begin('b')
        self.assertEqual(run.pending, 'b')

    def test_missing_or_wrong_assessment_fails_closed(self):
        for case_id, passed, evidence in [('b', True, 'report'), ('a', True, ''), ('a', 'true', 'report')]:
            with self.subTest(case_id=case_id, passed=passed, evidence=evidence):
                run = AcceptanceRun(['a', 'b'])
                run.begin('a')
                run.finish('a', 200, {'review_status': 'accepted'}, {'unknown': []})
                with self.assertRaises(AcceptanceStop):
                    run.assess(case_id, passed=passed, evidence=evidence)
                with self.assertRaises(AcceptanceStop):
                    run.begin('b')
