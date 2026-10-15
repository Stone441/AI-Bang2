"""Known synthetic retrieval regression through the real engine, no live model/API."""
import argparse
import copy
import hashlib
import json
from pathlib import Path

from brain.audit import Audit
from brain.contracts import Actor, now
from brain.engine import Engine, FakeExtractiveModel
from brain.sources import FixtureWorld
from brain.store import Store
from scripts.answer_challenges import load_cases


def build_world(data):
    world=FixtureWorld()
    templates={source:copy.deepcopy(next(r for r in world.resources.values() if r['source']==source))
        for source in ('confluence','jira','slack','drive')}
    world.resources={}
    for d in data['corpus']:
        r=copy.deepcopy(templates[d['source']]);rid=d['id'].split('@')[0]
        r.update(id=rid,native_id='synthetic-'+rid,title=d['title'],text=d['text'],
            version=1,parent='challenge',links=[],locator={'challenge_document':d['id']},
            source_updated_at=d['source_updated_at'],source_url='fixture://retrieval-challenges/'+rid)
        if r['source']=='confluence':r['policy'].update(space_groups=['staff'],page_groups=['staff'])
        elif r['source']=='jira':r['policy'].update(project_groups=['staff'],issue_groups=['staff'])
        elif r['source']=='slack':r['policy'].update(private=True,members=['eng_a'])
        else:r['policy'].update(direct_users=['eng_a'],inherited_groups=['staff'])
        world.resources[rid]=r
    return world


def run(output):
    data,digest=load_cases();output.mkdir(parents=True,exist_ok=False)
    world=build_world(data);store=Store();store.initialize(world)
    model=FakeExtractiveModel();engine=Engine(store,world,Audit(store),model)
    results=[]
    try:
        for case in data['cases']:
            questions=list(dict.fromkeys([case['question'],*case.get('retrieval_questions',[])]))
            for index,question in enumerate(questions):
                answer=engine.query(Actor('eng_a'),question)
                sent={e['evidence_id'] for e in model.calls[-1]['evidence']}
                required=set(case['rubric']['required_evidence_ids'])
                results.append({'case':case['id'],'variant':index,'question':question,
                    'required_evidence_ids':sorted(required),'model_input_evidence_ids':sorted(sent),
                    'required_missing':sorted(required-sent),'request_id':answer['request_id']})
        report={'created_at':now(),'mode':'fixture_sources_fake_extractive_model',
            'cases_sha256':digest,'retrieval_sha256':hashlib.sha256((Path(__file__).resolve().parents[1]/'brain/retrieval.py').read_bytes()).hexdigest(),
            'queries':len(results),'complete_evidence_queries':sum(not r['required_missing'] for r in results),
            'missing_evidence_queries':sum(bool(r['required_missing']) for r in results),
            'semantic_quality':'not_evaluated','native_permissions':'not_evaluated',
            'limitations':['Known synthetic development corpus, not blind or large-corpus performance.',
                'Required evidence recall is not answer correctness or retrieval precision.'],
            'results':results}
        (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(f"Required evidence complete: {report['complete_evidence_queries']}/{len(results)}; semantic quality NOT EVALUATED.")
        return report
    finally:store.db.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raise SystemExit(bool(run(args.output)['missing_evidence_queries']))
