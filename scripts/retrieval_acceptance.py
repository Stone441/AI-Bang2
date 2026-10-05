"""Reproducible authored lexical/window cases; not a semantic benchmark."""
import hashlib
import json
from pathlib import Path
from brain.audit import Audit, verify_chain
from brain.contracts import Actor, now
from brain.engine import Engine, FakeExtractiveModel
from brain.sources import FixtureWorld
from brain.store import Store
from scripts.build_metadata import revision


def run():
    world = FixtureWorld()
    r = world.resources['C-01']
    r.update(title='Synthetic operations manual', links=[], text=(
        '[SYNTHETIC]\n' + 'Routine housekeeping.\n' * 1000
        + 'Orion incident: retry budget exhausted; early cache explanation withdrawn.\n'
        + 'Appendix.\n' * 600))
    store = Store(); store.initialize(world)
    model = FakeExtractiveModel(); audit = Audit(store)
    engine = Engine(store, world, audit, model)
    cases = []
    try:
        for label, question, expected in (
            ('late_exact', 'Orion incident retry budget', True),
            ('lexical_alias', 'Orion outage retracted explanation', True),
            ('unsupported_vocabulary', 'interruption annulled hypothesis', False),
            ('entity_fallback', 'Orion interruption annulled hypothesis', True),
            ('unrelated', 'unfindablezebra', False)):
            answer = engine.query(Actor('eng_a'), question)
            found = any('retry budget exhausted' in e['text'] for e in answer['evidence'])
            # The entity-fallback case matches Orion alone. It does not
            # demonstrate understanding of interruption/annulled/hypothesis.
            if found != expected: raise RuntimeError('Retrieval case failed: ' + label)
            cases.append({'case': label, 'question': question, 'request_id': answer['request_id'],
                          'expected_target_found': expected, 'actual_target_found': found,
                          'evidence': answer['evidence'], 'status': 'passed_local_subset'})
        report = {'time': now(), 'commit': revision(), 'mode': 'fixture_fake_model',
                  'live_api_called': False, 'live_model_called': False,
                  'cases': cases, 'audit_chain': verify_chain(audit.export()),
                  'limitations': ['Authored examples, not held-out quality or semantic accuracy.',
                                  'Small English lexical alias map; no embeddings or reranker.',
                                  'Fixed overlapping character windows can split sentences; maximum three per resource.',
                                  'DeepSeek synthetic guard unchanged: windows without a valid marker are rejected.',
                                  'No performance or whole-corpus completeness guarantee.'],
                  'source_hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in [Path('brain/retrieval.py'), Path('brain/engine.py'), Path(__file__)]}}
        target = Path('evidence/runs/retrieval-local'); target.mkdir(parents=True, exist_ok=True)
        (target/'results.json').write_text(json.dumps(report, indent=2) + '\n')
        print('5 authored retrieval cases passed_local_subset; fixture/fake only')
    finally:
        store.db.close()


if __name__ == '__main__': run()
