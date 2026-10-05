"""Reproducible four-source lifecycle checks. Synthetic sources and fake model only."""
import hashlib
import json
from pathlib import Path

from brain.audit import Audit, verify_chain
from brain.contracts import Actor, now
from brain.engine import Engine
from brain.ingestion import Ingestion
from brain.sources import FixtureWorld
from brain.store import Store
from scripts.build_metadata import dirty, revision


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def run_case(resource_id, operation):
    world = FixtureWorld()
    store = Store()
    store.initialize(world)
    audit = Audit(store)
    engine = Engine(store, world, audit)
    ingestion = Ingestion(store, world)
    actor = Actor('eng_a')
    marker = 'lifecyclecanary' + resource_id.replace('-', '').lower()
    try:
        seed = world.mutate(resource_id, 'content', version=2,
                            text=f'SYNTHETIC payment-service {marker} initial revision',
                            source_updated_at=now())
        ingestion.process(seed)
        prior = engine.query(actor, marker)
        check(resource_id in {e['resource_id'] for e in prior['evidence']}, 'baseline missing')
        published = ingestion.processed_objects
        changes = ({'version': 3, 'text': f'SYNTHETIC payment-service {marker} replacement revision',
                    'source_updated_at': now()} if operation == 'content' else
                   {'user_id': 'eng_a'} if operation == 'revoke' else {})
        event = world.mutate(resource_id, operation, **changes)
        # Deliberately leave the index stale: current authority must protect all reads.
        before_sync = engine.query(actor, marker, prior['request_id'])
        before_model_input = engine.model.calls[-1]
        check(resource_id not in {e['resource_id'] for e in before_sync['evidence']}, 'stale evidence returned')
        check(marker not in json.dumps(before_model_input['evidence']), 'stale text sent to model')
        history = engine.safe_history(actor, prior['request_id'])
        check(history[0].get('unavailable') is True, 'old history/export projection exposed')
        check('claims' not in history[0] and 'evidence' not in history[0], 'old payload exposed')
        try:
            engine.evidence(actor, f'{resource_id}@2')
        except PermissionError:
            preview = 'denied'
        else:
            raise AssertionError('old citation allowed')
        sync = ingestion.process(event)
        after_sync = engine.query(actor, marker)
        target = [e for e in after_sync['evidence'] if e['resource_id'] == resource_id]
        if operation == 'content':
            check(len(target) == 1 and target[0]['version'] == 3, 'new revision missing')
            check('replacement revision' in target[0]['text'], 'new text missing')
            check(sync['processed_objects'] == 1, 'update was not object scoped')
        else:
            check(not target and marker not in json.dumps(engine.model.calls[-1]['evidence']), 'removed evidence used')
            check(ingestion.processed_objects == published, 'ACL/delete rebuilt content')
        check(store.get('C-02')['version'] == 1, 'unrelated object changed')
        check(ingestion.process(event)['state'] == 'duplicate', 'event replay not idempotent')
        chain = audit.export()
        check(verify_chain(chain)['valid'], 'audit chain invalid')
        return {'status': 'passed_local_subset', 'source': world.resources[resource_id]['source'],
                'resource_id': resource_id, 'operation': operation,
                'prior_answer': prior, 'before_sync_answer': before_sync,
                'before_sync_model_input': before_model_input,
                'old_history_export_projection': history, 'old_preview': preview,
                'sync': sync, 'after_sync_answer': after_sync, 'audit': chain}
    finally:
        store.db.close()


def run(output):
    report = {'started_at': now(), 'commit': revision(), 'worktree_dirty': dirty(),
              'mode': 'fixture_source_fake_model', 'live_api': 'not_run',
              'live_model': 'not_run', 'human_G1': 'not_run', 'cases': []}
    for resource_id in ('C-01', 'J-01', 'S-01', 'D-01'):
        for operation in ('content', 'revoke', 'delete'):
            try:
                case = run_case(resource_id, operation)
            except Exception as error:
                case = {'resource_id': resource_id, 'operation': operation,
                        'status': 'failed', 'error': str(error)}
            report['cases'].append(case)
    report['finished_at'] = now()
    report['source_hashes'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                               for root in ('brain', 'scripts', 'fixtures')
                               for p in sorted(Path(root).rglob('*'))
                               if p.is_file() and '__pycache__' not in str(p)}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'results.json').write_text(json.dumps(report, indent=2) + '\n')
    success = all(c['status'] == 'passed_local_subset' for c in report['cases'])
    print(json.dumps({'successful': success, 'cases': len(report['cases']),
                      'mode': report['mode'], 'report': str(output / 'results.json')}))
    return success


if __name__ == '__main__':
    raise SystemExit(not run(Path('evidence/runs/lifecycle-local')))
