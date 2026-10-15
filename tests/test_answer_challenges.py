import copy
import json
from pathlib import Path
import tempfile
import unittest

from brain.sectioned_answer import DeepSeekSectionedSynthesisModel, REASONING_CHECKS
from scripts.answer_challenges import case_evidence, check_draft, load_cases, run
import test_sectioned_answer
from test_synthesis import SequentialTransport


class AnswerChallenges(unittest.TestCase):
    def test_fixed_set_references_have_valid_quotes_and_scoped_rubrics(self):
        data,digest=load_cases()
        self.assertEqual(len(data['cases']),12);self.assertEqual(len(digest),64)
        tags={t for c in data['cases'] for t in c['tags']}
        self.assertTrue({'false_premise','unresolved_conflict','chinese','supersession','recency',
            'unestablished_premise','chronology','ambiguity','prompt_injection','multipart'}<=tags)
        corpus={d['id']:d for d in data['corpus']}
        for case in data['cases']:
            with self.subTest(case=case['id']):
                check_draft(case['reference_draft'],case['question'],case_evidence(case,corpus))
                cited={i for c in case['reference_draft']['claims'] for i in c['evidence_ids']}
                self.assertTrue(set(case['rubric']['required_evidence_ids'])<=cited)

    def test_all_challenges_reach_independent_review_with_all_evidence(self):
        setup=test_sectioned_answer.SectionedAnswer();setup.setUp();self.addCleanup(setup.doCleanups)
        data,_=load_cases();corpus={d['id']:d for d in data['corpus']}
        for case in data['cases']:
            with self.subTest(case=case['id']):
                draft=case['reference_draft'];evidence=case_evidence(case,corpus)
                transport=SequentialTransport(draft,[{'index':i,'supported':True,'responsive':True}
                    for i in range(len(draft['claims']))])
                transport.outputs[1].update({k:True for k in REASONING_CHECKS})
                model=DeepSeekSectionedSynthesisModel('synthetic-not-a-key',setup.ledger,
                    synthetic_only=True,transport=transport,today=setup.model._today())
                result=model.generate_with_authorization(case['question'],evidence,'a'*32,lambda _:None)
                self.assertEqual(result['claims'],draft['claims'])
                body=json.loads(transport.calls[1]['messages'][1]['content'])
                self.assertEqual([e['evidence_id'] for e in body['evidence']],case['evidence_ids'])
                self.assertNotIn('rubric',body);self.assertNotIn('reference_draft',body)
                prompt=transport.calls[1]['messages'][0]['content']
                self.assertIn('premise_handled',prompt);self.assertIn('conflicts_handled',prompt)
                generation=transport.calls[0]['messages'][0]['content']
                self.assertIn('BOTH',generation);self.assertIn('newer edit timestamp',generation)

    def test_preparation_has_no_actual_answers_or_semantic_pass_rate(self):
        with tempfile.TemporaryDirectory() as directory:
            report=run(Path(directory)/'new')
            self.assertEqual(report['semantic_quality'],'not_evaluated')
            self.assertTrue(all(c['actual_answer'] is None and c['mechanical_status']=='not_run' for c in report['cases']))
            self.assertNotIn('pass_rate',report)

    def test_bad_saved_quote_is_retained_as_failure_without_overwriting_results(self):
        data,_=load_cases();case=data['cases'][0];draft=copy.deepcopy(case['reference_draft'])
        draft['claims'][0]['supports'][0]['quote']='fabricated and absent'
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);answers=root/'answers.json'
            answers.write_text(json.dumps({case['id']:draft}));output=root/'run'
            report=run(output,answers)
            self.assertEqual(report['mechanical_failures'],1)
            self.assertEqual(report['cases'][0]['actual_answer'],draft)
            original=(output/'report.json').read_bytes()
            with self.assertRaises(FileExistsError):run(output,answers)
            self.assertEqual((output/'report.json').read_bytes(),original)

    def test_structurally_valid_but_false_conclusion_is_not_semantically_approved(self):
        data,_=load_cases();case=data['cases'][0];draft=copy.deepcopy(case['reference_draft'])
        draft['claims'][0]['text']='General availability is approved.'
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);answers=root/'answers.json'
            answers.write_text(json.dumps({case['id']:draft}))
            report=run(root/'run',answers);result=report['cases'][0]
            self.assertEqual(result['mechanical_status'],'valid_shape_and_quotes')
            self.assertEqual(result['semantic_review'],'not_run')
            self.assertIsNone(result['human_review']['facts_and_scope'])

    def test_unknown_case_is_rejected_before_creating_evidence_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);answers=root/'answers.json';answers.write_text('{"unknown":{}}')
            with self.assertRaises(ValueError):run(root/'run',answers)
            self.assertFalse((root/'run').exists())
