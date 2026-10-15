"""Prepare a frozen synthetic answer worksheet or check saved drafts, without APIs.

Quote/shape checks are mechanical only; reference answers are author-written.
This development set is known to the implementation and is not blind evaluation.
"""
import argparse
import hashlib
import json
from pathlib import Path

from brain.contracts import Evidence, now
from brain.sectioned_answer import validate_answer_parts
from brain.synthesis import validate_claim

CASES_PATH = Path(__file__).resolve().parents[1]/'fixtures/answer_challenges.json'


def case_evidence(case, corpus):
    return [Evidence(d['id'],d['id'].split('@')[0],1,d['source'],d['title'],
        {'challenge_document':d['id']},d['text'],d['source_updated_at'],
        '2026-10-14T00:00:00+00:00','fixture://answer-challenges/'+d['id'])
        for d in (corpus[i] for i in case['evidence_ids'])]


def check_draft(draft, question, evidence):
    if (not isinstance(draft,dict) or set(draft)!={'claims','answer_parts'}
            or not isinstance(draft['claims'],list) or len(draft['claims'])>4):
        raise ValueError('Invalid challenge draft')
    for claim in draft['claims']:validate_claim(claim,evidence)
    validate_answer_parts(draft['answer_parts'],draft['claims'],question)


def load_cases():
    raw=CASES_PATH.read_bytes();data=json.loads(raw)
    if data.get('synthetic') is not True or data.get('schema_version')!=1:
        raise ValueError('Synthetic challenge set required')
    corpus={d['id']:d for d in data['corpus']}
    if len(corpus)!=len(data['corpus']) or any(not d['text'].startswith('[SYNTHETIC]') for d in corpus.values()):
        raise ValueError('Invalid synthetic corpus')
    ids=[c['id'] for c in data['cases']]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate challenge ID')
    for case in data['cases']:
        evidence=case_evidence(case,corpus)
        check_draft(case['reference_draft'],case['question'],evidence)
        if (not case['rubric']['must_explain'] or not case['rubric']['must_not_conclude']
                or not set(case['rubric']['required_evidence_ids'])<=set(case['evidence_ids'])):
            raise ValueError('Invalid challenge rubric')
    return data,hashlib.sha256(raw).hexdigest()


def run(output, answers_path=None):
    data,digest=load_cases();answers=json.loads(answers_path.read_text()) if answers_path else {}
    known={c['id'] for c in data['cases']}
    if not isinstance(answers,dict) or set(answers)-known:
        raise ValueError('Answers must map known challenge IDs to saved drafts')
    output.mkdir(parents=True,exist_ok=False)
    corpus={d['id']:d for d in data['corpus']};results=[]
    for case in data['cases']:
        evidence=case_evidence(case,corpus);draft=answers.get(case['id'])
        status='not_run'
        if case['id'] in answers:
            try:check_draft(draft,case['question'],evidence);status='valid_shape_and_quotes'
            except (ValueError,KeyError,TypeError):status='invalid_shape_or_quotes'
        results.append({'id':case['id'],'question':case['question'],'tags':case['tags'],
            'evidence':[e.to_dict() for e in evidence],
            'rubric':case['rubric'],'author_reference_not_model_result':case['reference_draft'],
            'actual_answer':draft,'mechanical_status':status,'semantic_review':'not_run',
            'human_review':{'facts_and_scope':None,'premise_correction':None,
                'conflict_handling':None,'missing_evidence_handling':None,'notes':''}})
    source_files=[Path(__file__),Path(__file__).resolve().parents[1]/'brain/sectioned_answer.py']
    report={'created_at':now(),'mode':'offline_worksheet_no_model_calls','cases_sha256':digest,
        'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
        'live_model':'not_run','native_sources':'not_run','semantic_quality':'not_evaluated',
        'mechanical_failures':sum(r['mechanical_status']=='invalid_shape_or_quotes' for r in results),
        'limitations':['Known development set, not a blind or held-out evaluation.',
            'Exact quotes do not establish entailment, conflict resolution or correct premises.',
            'Reference drafts are examples; alternative correct answers require semantic review.'],
        'cases':results}
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(f"Prepared {len(results)} challenges; mechanical failures {report['mechanical_failures']}; semantic quality NOT EVALUATED.")
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True,help='New directory; existing results are preserved')
    parser.add_argument('--answers',type=Path,help='Optional local JSON: challenge ID -> claims/answer_parts draft')
    args=parser.parse_args()
    raise SystemExit(bool(run(args.output,args.answers)['mechanical_failures']))


if __name__=='__main__':main()
