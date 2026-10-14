"""Offline pipeline diagnosis: recorded native timings plus fixture CPU timings.

No credentials, network, runtime databases, or real model construction. Creates
a new output file; never replaces historical evidence. Run from repository root.
"""
import argparse
import collections
import copy
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from brain.audit import Audit, verify_chain
from brain.contracts import Actor
from brain.engine import Engine, FakeExtractiveModel
from brain.retrieval import tokens, subject_related, bm25_windows
from brain.store import Store
from scripts.business_validation import build_world


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def timing(values):
    return {'samples': len(values), 'min_seconds': min(values),
            'median_seconds': statistics.median(values), 'max_seconds': max(values)}


def historical():
    path = ROOT / 'evidence/runs/lock-contention-20261008/performance-comparison.json'
    data = json.loads(path.read_text())
    results = []
    for record in data['results']:
        rows = [r for r in data['calls_by_source_phase_endpoint']
                if r['case'] == record['case'] and r['operation'] == 'query']
        breakdown = {}
        for dimension in ('source', 'phase', 'endpoint'):
            counts, work = collections.Counter(), collections.Counter()
            for row in rows:
                counts[row[dimension]] += row['calls']
                work[row[dimension]] += row['cumulative_seconds']
            breakdown[dimension] = {
                k: {'calls': counts[k], 'worker_seconds': work[k]} for k in counts}
        results.append({'recorded_measurement': record,
                        'query_native_http_calls': sum(r['calls'] for r in rows),
                        'breakdown': breakdown})
    return {'source_file': str(path.relative_to(ROOT)), 'sha256': digest(path),
            'mode': 'offline_reanalysis_of_historical_native_live_model_run',
            'cases': results,
            'limit': 'Worker totals overlap concurrent authorization wall. Not a current run or SLA.'}


def benchmark(noise):
    world, _ = build_world()
    for i in range(noise):
        r = copy.deepcopy(world.resources['BV-01'])
        rid = f'NOISE-{i:04}'
        r.update(id=rid, native_id='synthetic-'+rid,
                 title=f'Synthetic unrelated catalog {i}',
                 text=f'SYNTHETIC catalog entry {i}: warehouse rack {i%37}, inspection interval {i%19+1} days, '
                      f'owner catalog-worker-{i%43}. Token rotation migration payment scope status and approval '
                      f'are catalog column labels, not business decisions. Inventory code SKU-{10000+i}.',
                 links=[], source_url='fixture://synthetic-demo/confluence/'+rid)
        world.resources[rid] = r
    store = Store()
    try:
        store.initialize(world)
        audit = Audit(store)
        model = FakeExtractiveModel()
        engine = Engine(store, world, audit, model)
        actor = Actor('eng_b')
        cases = []
        for question in ('What is the latest approved mitigation?',
                         'What is payment-service code fix status and release scope?'):
            cpu, full, footprints = [], [], []
            for _ in range(5):
                started = time.perf_counter()
                qt = tokens(question)
                visible = [r for r in store.resources() if r['tenant'] == actor.tenant
                           and engine.prefilter(actor, r)]
                visible = subject_related(visible, qt)
                ranks = bm25_windows(visible, qt)
                cpu.append(time.perf_counter()-started)
                started = time.perf_counter()
                answer = engine.query(actor, question)
                full.append(time.perf_counter()-started)
                footprints.append({'evidence_count': len(answer['evidence']),
                                   'evidence_characters': sum(len(e['text']) for e in answer['evidence']),
                                   'ranked_resource_count': sum(bool(x) for x in ranks.values())})
            cases.append({'question': question,
                          'local_snapshot_topic_bm25': timing(cpu),
                          'full_fixture_fake_query': timing(full),
                          'footprints': footprints})
        assert len(model.calls) == 10
        chain = verify_chain(audit.export())
        return {'objects': len(world.resources), 'noise_objects': noise,
                'mode': 'fixture_fake_model_in_memory_sqlite', 'cases': cases,
                'audit_chain': chain,
                'limit': 'Authored repeated questions, small local sample. No native latency or model quality evidence; no p95 claim.'}
    finally:
        store.db.close()


def counterexamples():
    path = ROOT / 'docs/reviews/2026-10-13-source-review-dispatch/COUNTEREXAMPLES.json'
    manifest = json.loads(path.read_text())
    result = []
    for case in manifest['cases']:
        bodies = {}
        for name, file in case['files'].items():
            source = ROOT / file['path']
            if digest(source) != file['sha256']:
                raise ValueError('Historical evidence hash changed')
            bodies[name] = json.loads(source.read_text())
        response = bodies['response']
        supplied = {e['evidence_id'] for e in response['evidence']
                    if e['resource_id'] == case['required_resource_id']}
        retained = {eid for claim in response['claims'] for eid in claim['evidence_ids']}
        result.append({'case': case['case'], 'meaning': case['meaning'],
                       'elapsed_seconds': bodies['result']['elapsed_seconds'],
                       'required_source_supplied': bool(supplied),
                       'required_source_cited': bool(supplied & retained),
                       'answer_status': response.get('answer_status'),
                       'review_status': response.get('review_status'),
                       'original_hashes_verified': True})
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Choose a new output; preserve original analysis.')
    paths = [Path(__file__), *sorted((ROOT / 'brain').glob('*.py')),
             ROOT / 'scripts/business_validation.py', ROOT / 'fixtures/baseline.json']
    report = {'schema_version': 1, 'date': '2026-10-13 Asia/Singapore',
              'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'source_hashes': {str(p.relative_to(ROOT)): digest(p) for p in paths},
              'native_api_called': False, 'live_model_called': False,
              'historical': historical(), 'counterexamples': counterexamples(),
              'local_cpu': [benchmark(n) for n in (0, 1000)]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print('Offline analysis saved; native_api_called=false, live_model_called=false')
