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
            except AcceptanceStop:
                break
        self.assertEqual(calls, ['a', 'b'])
        with self.assertRaises(AcceptanceStop):run.begin('c')

    def test_no_retry_and_new_unknown_stop_even_with_accepted_answer(self):
        run = AcceptanceRun(['a', 'b'])
        run.begin('a')
        run.finish('a', 200, {'review_status':'accepted'}, {'unknown':[]})
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
        run.begin('c')
        with self.assertRaises(AcceptanceStop):
            run.finish('c', 200, {'answer_status':'evidence_only'}, {'unknown':[]})
