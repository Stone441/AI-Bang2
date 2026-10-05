"""Opt-in readonly Jira update check; synthetic UI seeding/editing is separate.

Uses existing eng_b app-owned Keychain authorization, two exact synthetic issues,
fake model and an isolated memory store. Never edits the running operator config.
"""
import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from brain.audit import verify_chain
from brain.confluence import Delegation
from brain.contracts import Actor, now
from brain.delegated_query import DelegatedQueryPilot
from brain.jira import JiraReader
from brain.keychain import MacKeychain
from brain.store import Store
from scripts.build_metadata import revision


def run(output):
    if output.exists():
        raise FileExistsError('Preserve evidence; choose a new directory')
    output.mkdir(parents=True)
    report = {'started_at': now(), 'commit': revision(), 'mode': 'jira_live_api_fake_model',
              'actor': 'eng_b', 'source_writes_by_runner': False, 'model_network_calls': 0,
              'human_G1': 'not_run', 'source_hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in (Path(__file__), Path('brain/jira.py'), Path('brain/delegated_query.py'), Path('brain/engine.py'))}}
    store = pilot = None
    def write(name, value):
        (output / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n')
    try:
        config = json.loads(Path('.runtime/jira-pilot.json').read_text())
        if config['approved_synthetic_only'] is not True:
            raise ValueError('Reviewed synthetic source required')
        mapping = config['delegations']['eng_b']
        value = MacKeychain().get('jira', config['tenant'], 'eng_b', mapping['account_id'])
        if not value:
            raise ValueError('Existing saved authorization unavailable')
        delegations = {'eng_b': Delegation(mapping['account_id'], value)}
        actor = Actor('eng_b', config['tenant'])
        discovery = JiraReader(config['site'], config['tenant'], {}, [], delegations,
                               cloud_id=config['cloud_id'], discovery_only=True,
                               discovery_keys={'KAN-6': 'KAN'})
        decision, ids = discovery.discover_ids(actor, 'KAN-6')
        report['discovery'] = {'decision': asdict(decision), 'ids': ids}
        if decision.result != 'allow' or not ids or ids['project_id'] not in config['project_ids']:
            raise ValueError('Native synthetic mapping unavailable')
        native_id = ids['issue_id']
        reader = JiraReader(config['site'], config['tenant'], {native_id: 'KAN-6', '10013': 'KAN-4'},
                            config['project_ids'], delegations, cloud_id=config['cloud_id'])
        store = Store()
        pilot = DelegatedQueryPilot({'jira': reader}, store, live=True)
        first = pilot.query(actor, 'What is the update-check queue revision?')
        initial = next(e for e in first['evidence'] if e['resource_id'] == 'jira:' + native_id)
        if 'CANARY_JIRA_UPDATE_V1' not in initial['text']:
            raise ValueError('Initial revision not observed')
        control = store.get('jira:10013')
        write('before-answer', first)
        write('checkpoint-before-update', {'native_id': native_id, 'version': initial['version'],
                                          'control_version': control['version']})
        print('awaiting_source_update: KAN-6 Revision 1 observed; runner is readonly.', flush=True)
        input()
        old_index_preserved = store.get('jira:' + native_id)['version'] == initial['version']
        preview_denied = False
        try:
            pilot.evidence(actor, initial['evidence_id'])
        except PermissionError:
            preview_denied = True
        history = pilot.history(actor, first['request_id'])
        old_decision, old_content = reader.read(actor, native_id, initial['version'])
        fresh = pilot.query(actor, 'What is the update-check queue revision?')
        current = next(e for e in fresh['evidence'] if e['resource_id'] == 'jira:' + native_id)
        preview = pilot.evidence(actor, current['evidence_id'])
        control_after = store.get('jira:10013')
        chain = pilot.audit.export()
        checks = {
            'baseline_revision_1_observed': 'CANARY_JIRA_UPDATE_V1' in initial['text'],
            'old_index_present_before_refresh': old_index_preserved,
            'native_old_version_denied': old_decision.result == 'deny' and old_content is None,
            'old_preview_denied_before_index_refresh': preview_denied,
            'old_history_export_projection_denied': history[0].get('unavailable') is True,
            'fresh_version_changed': current['version'] != initial['version'],
            'fresh_revision_2_observed': 'CANARY_JIRA_UPDATE_V2' in current['text'] and 'green' in current['text'],
            'fresh_has_no_revision_1': 'CANARY_JIRA_UPDATE_V1' not in current['text'],
            'new_preview_matches_exact_text': preview['text'] == current['text'],
            'unrelated_control_unchanged': control_after['version'] == control['version'] and control_after['text'] == control['text'],
            'new_model_evidence_has_revision_2': any('CANARY_JIRA_UPDATE_V2' in e['text'] for e in pilot.engine.model.calls[-1]['evidence']),
            'new_model_evidence_has_no_revision_1': all('CANARY_JIRA_UPDATE_V1' not in e['text'] for e in pilot.engine.model.calls[-1]['evidence']),
            'audit_chain_valid': verify_chain(chain)['valid'],
        }
        report.update(checks=checks, native_id=native_id, before_version=initial['version'],
                      after_version=current['version'], before_request_id=first['request_id'],
                      after_request_id=fresh['request_id'], audit_events=len(chain),
                      status='verified_native_subset' if all(checks.values()) else 'failed',
                      limitations=['New synthetic KAN-6 only, existing eng_b readonly operator and fake model.',
                                   'Native version is a content fingerprint, not a sequential Jira revision number.',
                                   'Query-triggered source refresh, not webhook/scheduler or propagation SLA.',
                                   'History uses shared export projection; no browser HTTP download tested here.',
                                   'Unsigned audit chain, not independent signature custody or human G1.'])
        write('after-answer', fresh)
        write('old-history', history)
        write('new-preview', preview)
        write('model-inputs', pilot.engine.model.calls)
    except Exception as error:
        report.update(status='failed', reason=type(error).__name__)
    finally:
        if pilot:
            write('audit', pilot.audit.export())
        report['finished_at'] = now()
        write('verification', report)
        if store:
            store.db.close()
    print(json.dumps({'status': report['status'], 'checks': report.get('checks', {})}), flush=True)
    return report['status'] == 'verified_native_subset'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not args.live:
        parser.error('--live required within the approved synthetic scope')
    raise SystemExit(0 if run(args.output) else 1)
