"""Opt-in native Confluence denial/control, with a labeled stale synthetic index.

Uses only the existing reviewed eng_b app-owned Keychain item. No source writes,
credential prompts, model network calls or changes to the running operator.
"""
import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from brain.audit import verify_chain
from brain.confluence import ConfluenceReader, Delegation, JsonTransport
from brain.contracts import Actor, now
from brain.delegated_query import DelegatedAuthority, DelegatedQueryPilot
from brain.keychain import MacKeychain
from brain.store import Store
from scripts.build_metadata import revision

RESTRICTED_ID = '557057'
CONTROL_ID = '164283'
TITLE = 'C-03 · Restricted security investigation [SYNTHETIC]'
TEXT = ('[SYNTHETIC COMPETITION TEST DATA — NOT AN ACTUAL COMPANY RECORD]\n'
        'Fixture ID: C-03\nRestricted security investigation. CANARY_SEC_7Q9.')


class StatusTransport(JsonTransport):
    """Retain bounded status facts, never headers, credentials or error bodies."""
    def __init__(self):
        super().__init__()
        self.statuses = []

    def get(self, url, authorization):
        status, data = super().get(url, authorization)
        suffix = url.split('/wiki/', 1)[1]
        target = ('identity' if suffix == 'rest/api/user/current' else
                  'restricted' if suffix.startswith('api/v2/pages/' + RESTRICTED_ID) else
                  'control' if suffix.startswith('api/v2/pages/' + CONTROL_ID) else 'other')
        self.statuses.append({'target': target, 'body_request': '?body-format=' in suffix,
                              'status': status})
        return status, data


def run(output):
    # Refuse before Keychain/API access; existing evidence must remain unchanged.
    if output.exists():
        raise FileExistsError('Choose a new evidence directory')
    output.mkdir(parents=True)
    report = {'started_at': now(), 'commit': revision(), 'actor': 'eng_b',
              'mode': 'confluence_live_api_fake_model_controlled_stale_index',
              'source_writes': False, 'model_network_calls': 0,
              'human_G1': 'not_run', 'contractor_permission_persona': 'not_run',
              'stale_index_origin': 'Known synthetic owner UI text; not fetched as eng_b',
              'source_hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (Path(__file__), Path('brain/confluence.py'),
                                          Path('brain/delegated_query.py'), Path('brain/engine.py'))}}
    store = pilot = transport = None
    try:
        config = json.loads(Path('.runtime/confluence-pilot.json').read_text())
        if config['approved_synthetic_only'] is not True or CONTROL_ID not in config['page_ids']:
            raise ValueError('Reviewed synthetic configuration required')
        mapping = config['delegations']['eng_b']
        saved = MacKeychain().get('confluence', config['tenant'], 'eng_b', mapping['account_id'])
        if not saved:
            raise ValueError('Existing approved saved credential unavailable')
        transport = StatusTransport()
        # This isolated instance adds only the newly seeded synthetic page.
        reader = ConfluenceReader(config['site'], config['tenant'], [RESTRICTED_ID, CONTROL_ID],
                                  config['space_ids'], {'eng_b': Delegation(mapping['account_id'], saved)},
                                  transport=transport, cloud_id=config.get('cloud_id'))
        actor = Actor('eng_b', reader.tenant)
        denied, restricted_content = reader.read(actor, RESTRICTED_ID)
        allowed, control = reader.read(actor, CONTROL_ID)
        report['native_decisions'] = {'restricted': asdict(denied), 'control': asdict(allowed)}
        if denied.result != 'deny' or restricted_content is not None or allowed.result != 'allow' or not control:
            raise ValueError('Native denial/control precondition failed')
        store = Store(':memory:')
        stale = DelegatedAuthority.resource(
            {'source': 'confluence', 'native_id': RESTRICTED_ID, 'version': 1,
             'title': TITLE, 'text': TEXT, 'locator': {'page_id': RESTRICTED_ID, 'version': 1},
             'source_updated_at': now(),
             'source_url': config['site'] + '/wiki/pages/viewpage.action?pageId=' + RESTRICTED_ID},
            reader.tenant)
        store.initialize(SimpleNamespace(resources={stale['id']: stale}))
        pilot = DelegatedQueryPilot({'confluence': reader}, store, live=True)
        negative = pilot.query(actor, 'What does the security investigation conclude?')
        positive = pilot.query(actor, 'What is the payment retry capability and supported rollout scope?')
        preview_denied = False
        try:
            pilot.evidence(actor, stale['id'] + '@1')
        except PermissionError as error:
            preview_denied = str(error) == 'Unavailable'
        chain = pilot.audit.export()
        public = json.dumps(negative, ensure_ascii=False)
        model_inputs = json.dumps(pilot.engine.model.calls, ensure_ascii=False)
        refresh_denials = {e['request_id'] for e in chain
                          if e['event_type'] == 'authorization_decided'
                          and e['payload']['resource_id'] == stale['id']
                          and e['payload']['phase'] == 'source_refresh'
                          and e['payload']['result'] == 'deny'}
        checks = {
            'native_restricted_denied_without_content': denied.result == 'deny' and restricted_content is None,
            'native_control_allowed': allowed.result == 'allow',
            'negative_has_no_claims_or_evidence': not negative['claims'] and not negative['evidence'],
            'negative_does_not_reveal_title_id_or_canary': all(s not in public for s in (TITLE, RESTRICTED_ID, 'CANARY_SEC_7Q9')),
            'restricted_never_in_model_inputs': all(s not in model_inputs for s in (TITLE, RESTRICTED_ID, 'CANARY_SEC_7Q9')),
            'positive_control_in_answer': any(e['resource_id'] == 'confluence:' + CONTROL_ID for e in positive['evidence']),
            'both_queries_have_native_refresh_denial': {negative['request_id'], positive['request_id']} <= refresh_denials,
            'stale_index_not_deleted_to_hide_problem': store.get(stale['id'])['text'] == TEXT,
            'stale_preview_denied': preview_denied,
            'preview_has_native_denial': any(e['event_type'] == 'authorization_decided'
                                            and e['payload']['phase'] == 'preview'
                                            and e['payload']['result'] == 'deny' for e in chain),
            'negative_fake_model_receives_empty_evidence': len(pilot.engine.model.calls) == 2 and not pilot.engine.model.calls[0]['evidence'],
            'only_positive_query_sends_evidence_to_fake_model': len(pilot.engine.model.calls) == 2 and bool(pilot.engine.model.calls[1]['evidence']),
            'audit_chain_valid': verify_chain(chain)['valid'],
        }
        report.update(checks=checks, negative_request_id=negative['request_id'],
                      positive_request_id=positive['request_id'],
                      status='verified_native_subset' if all(checks.values()) else 'failed',
                      limitations=['One existing eng_b identity, not the original contractor/full ACL matrix.',
                                   'The stale index is controlled synthetic test setup, not historical ingestion proof.',
                                   'No timing side-channel, browser denial, live-model or human acceptance claim.',
                                   'The audit chain is unsigned; no independent tamper-proof custody.'])
        for name, value in (('negative-answer', negative), ('positive-answer', positive),
                            ('model-inputs', pilot.engine.model.calls)):
            (output / (name + '.json')).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    except Exception as error:
        report.update(status='failed', reason=type(error).__name__)
    finally:
        if pilot:
            (output / 'audit.json').write_text(json.dumps(pilot.audit.export(), indent=2) + '\n')
        if transport:
            report['native_statuses'] = transport.statuses
        report['finished_at'] = now()
        (output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        if store:
            store.db.close()
    print(json.dumps({'status': report['status'], 'checks': report.get('checks', {})}))
    return report['status'] == 'verified_native_subset'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not args.live:
        parser.error('--live required within the approved synthetic pilot')
    raise SystemExit(0 if run(args.output) else 1)
