"""Reproduce the frozen candidate's fixture recall and local timing; no external API/model."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import time
from brain.contracts import Actor
from brain.server import App
from brain.timing import install, request_scope


def run(oracle_path, output):
    raw=oracle_path.read_bytes();oracle=json.loads(raw)
    if oracle.get('synthetic') is not True:raise ValueError('Synthetic oracle required')
    baseline=Path(__file__).resolve().parents[1]/'fixtures/baseline.json'
    if hashlib.sha256(baseline.read_bytes()).hexdigest()!=oracle['baseline_sha256']:
        raise ValueError('Baseline differs from frozen oracle')
    output.mkdir(parents=True,exist_ok=False)
    rows=[]
    relevance={'release-readiness':{'J-02','C-02','D-02','D-03','S-02'},
        'delivery-planning':{'J-02','J-03','C-02','D-02','D-03','S-02'},'customer-impact':set()}
    for role in ('eng_b','product_ops','contractor'):
        app=App()
        with tempfile.TemporaryDirectory() as directory:
            recorder=install(app,Path(directory).resolve())
            try:
                for case in oracle['cases']:
                    for variant,question in enumerate([case['question'],*case['paraphrases']]):
                        before=set(Path(directory).glob('*.json'));started=time.perf_counter()
                        with request_scope(app,'query'):
                            answer=app.engine.query(Actor(role),question)
                        wall=time.perf_counter()-started
                        paths=set(Path(directory).glob('*.json'))-before
                        if len(paths)!=1:raise RuntimeError('Missing timing record')
                        timing=json.loads(paths.pop().read_text())
                        ids=sorted({item['evidence_id'].split('@')[0] for item in answer['evidence']})
                        required=set(case['required']) if role!='contractor' else set()
                        rows.append({'role':role,'case':case['id'],'variant':variant,'question':question,
                            'evidence_ids':ids,'missing_required':sorted(required-set(ids)),
                            'non_supporting_for_requested_fact':sorted(set(ids)-relevance[case['id']]),
                            'required_oracle_applies':role!='contractor',
                            'wall_seconds':wall,'spans':timing['spans'],
                            'semantic_quality':'not_evaluated_fake_model','native_source_latency':'not_run',
                            'live_generation_review_frontend_wait':'not_run'})
            finally:recorder.close();app.store.db.close()
    report={'mode':'baseline_fixture_fake_model','oracle_sha256':hashlib.sha256(raw).hexdigest(),
        'blind':False,'rows':rows,'limitations':['Author-defined evidence relevance; not blind or general retrieval quality.',
        'Nested spans overlap; do not sum authorization and retrieval as independent wall stages.',
        'No embeddings, live sources, live model, model-review quality or browser timing measured.']}
    (output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Queries:',len(rows),'staff necessary-evidence misses:',sum(bool(r['missing_required']) for r in rows))
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--oracle',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.oracle,args.output)
