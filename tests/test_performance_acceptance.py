"""Actual local allowance/model integration of the frozen runner; no network."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from brain.budget import BudgetLedger
from scripts import performance_acceptance as runner


class FixtureAdmission(unittest.TestCase):
    def run_candidate(self, usage_unknown=False, structured=False):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);private=root/'private';(private/'.runtime').mkdir(parents=True)
            (root/'.runtime').mkdir()
            (root/'.runtime/operator-bundle.json').write_text(json.dumps({'approved_synthetic_only':True,
                'identity_mapping_reviewed':True,'sources':{'jira':'jira.json'}}))
            (root/'.runtime/jira.json').write_text(json.dumps({'tenant':'synthetic-test'}))
            budget=root/'.runtime/deepseek-budget.sqlite';ledger=BudgetLedger(str(budget));ledger.close()
            manifest_path=root/'candidate.json';manifest_path.write_text('{}')
            world,cases=runner.inputs();cases=cases[:2]
            manifest={'fixture_cases':cases,'plan_sha256':'a'*64}
            calls=[]
            class Transport:
                def _send(self,request):
                    body=json.loads(request.data);calls.append(body)
                    data=json.loads(body['messages'][1]['content'])
                    output={'selected':[p['alias'] for p in data['passages']],
                            'selection_safe':True,'question_covered':True}
                    result={'model':'deepseek-flash','choices':[{'finish_reason':'stop',
                        'message':{'role':'assistant','content':json.dumps(output)}}]}
                    if not usage_unknown:result['usage']={'prompt_tokens':100,'completion_tokens':20,'total_tokens':120}
                    return 200,result
            candidate='structured-v2' if structured else 'whole-v1'
            model=runner.DeepSeekStructuredSourceReviewModel if structured else runner.DeepSeekWholeSourceReviewModel
            expected=dict(runner.EXPECTED,window_strategy='structured' if structured else 'fixed')
            with patch.object(runner,'ROOT',root),patch.object(runner,'PRIVATE',private), \
                 patch.object(runner,'CANDIDATE',candidate),patch.object(runner,'MODEL',model), \
                 patch.object(runner,'EXPECTED',expected), \
                 patch.object(runner,'MANIFEST',manifest_path),patch.object(runner,'validate_frozen',return_value=manifest), \
                 patch.object(runner,'inputs',return_value=(world,cases)),patch.object(runner,'check_price_review'), \
                 patch('brain.deepseek.check_price_review'),patch('brain.deepseek.ModelTransport',return_value=Transport()), \
                 patch.object(runner.MacKeychain,'get',return_value='synthetic-not-a-key'):
                result=runner.fixture()
            report=json.loads((private/('final-fixture-'+candidate)/'report.json').read_text())
            return result,report,calls

    def test_model_calls_settle_in_original_ledger_with_goal_count(self):
        result,report,calls=self.run_candidate()
        self.assertEqual(result,0)
        self.assertEqual(len(calls),2)
        self.assertEqual(report['after']['model_calls_used'],2)
        self.assertEqual(report['budget_after']['pending_requests'],0)
        self.assertTrue(report['audit_chain']['valid'])
        self.assertTrue(all(r['mechanical_oracle_pass'] for r in report['results']))

    def test_unknown_usage_stops_before_next_case_and_retains_reservation(self):
        result,report,calls=self.run_candidate(usage_unknown=True)
        self.assertEqual(result,2)
        self.assertEqual(len(calls),1)
        self.assertEqual(report['status'],'stopped_admission')
        self.assertEqual(report['after']['model_calls_used'],1)
        self.assertEqual(report['budget_after']['pending_requests'],1)
        self.assertGreater(report['budget_after']['accounted_micro_usd'],0)

    def test_structured_candidate_has_separate_artifact_and_original_ledger(self):
        result,report,calls=self.run_candidate(structured=True)
        self.assertEqual(result,0)
        self.assertEqual(len(calls),2)
        self.assertEqual(report['after']['model_calls_used'],2)
        self.assertTrue(report['audit_chain']['valid'])

    def test_structured_unknown_also_stops_without_retry(self):
        result,report,calls=self.run_candidate(usage_unknown=True,structured=True)
        self.assertEqual(result,2)
        self.assertEqual(len(calls),1)
        self.assertEqual(report['after']['model_calls_used'],1)
        self.assertEqual(report['budget_after']['pending_requests'],1)
