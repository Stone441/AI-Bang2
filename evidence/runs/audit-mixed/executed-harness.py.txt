"""Actual fixture mixed-outcome audit walkthrough; no native identity or model API.

The expected event IDs are captured around four independently executed requests,
not computed with the audit inquiry's filtering logic. Human review stays not_run.
"""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from brain.audit import Audit, verify_chain
from brain.audit_query import parse_inquiry
from brain.contracts import Actor, now
from brain.engine import Engine, FakeExtractiveModel
from brain.sources import FixtureWorld
from brain.store import Store
from scripts.build_metadata import revision


class FailedModel:
    name = 'explicit-failed-fixture-model'

    def generate(self, question, evidence):
        raise RuntimeError('synthetic_model_failure')


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def run(output):
    if output.exists():
        raise FileExistsError('Preserve evidence; choose a new output directory')
    output.mkdir(parents=True)
    world = FixtureWorld()
    store = Store()
    store.initialize(world)
    audit = Audit(store)
    engine = Engine(store, world, audit)
    actor = Actor('eng_a')
    report = {'started_at': now(), 'commit': revision(), 'mode': 'fixture_fake_model',
              'native_api': 'not_run', 'native_auditor': 'not_run', 'human_G1': 'not_run',
              'source_hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                (Path(__file__), Path('brain/audit.py'), Path('brain/audit_query.py'),
                                 Path('brain/engine.py'), Path('tools/audit_verifier/verify.py'))}}
    cases = []
    try:
        def execute(label, question, expected_failure=False):
            start = len(audit.export())
            answer = None
            try:
                answer = engine.query(actor, question)
            except RuntimeError as error:
                if not expected_failure or str(error) != 'synthetic_model_failure':
                    raise
            events = audit.export()[start:]
            request_ids = {e['request_id'] for e in events}
            if len(request_ids) != 1 or any(e['actor'] != actor.user_id for e in events):
                raise AssertionError('Unexpected request boundary')
            record = {'case': label, 'request_id': next(iter(request_ids)),
                      'event_ids': [e['seq'] for e in events], 'answer': answer,
                      'failure_observed': answer is None}
            cases.append(record)
            return answer, events

        question = 'What caused the payment-service incident and what is the latest runbook?'
        success, events = execute('success', question)
        assert success['evidence'] and any(e['event_type'] == 'response_committed' for e in events)
        world.mutate('S-01', 'revoke', user_id='eng_a')
        partial, events = execute('partial_authorization', question)
        assert partial['evidence'] and all(e['resource_id'] != 'S-01' for e in partial['evidence'])
        assert any(e['event_type'] == 'authorization_decided' and e['payload']['result'] == 'deny' for e in events)
        for resource_id in world.resources:
            world.revoked.add(('eng_a', resource_id))
        denied, events = execute('authorization_denied', question)
        assert not denied['evidence'] and not denied['claims']
        assert any(e['event_type'] == 'authorization_decided' and e['payload']['result'] == 'deny' for e in events)
        world.revoked.clear()
        engine.model = FailedModel()
        failed, events = execute('question_failed', question, expected_failure=True)
        assert failed is None and any(e['event_type'] == 'request_failed' for e in events)
        assert not any(e['event_type'] == 'response_committed' for e in events)
        assert store.run(cases[-1]['request_id'], 'eng_a') is None

        # Controlled unrelated noise: scope exclusion and actor exclusion.
        audit.append('authorization_decided', 'eng_a', 'outside-scope',
                     {'resource_scope': 'unapproved-other-scope', 'result': 'allow'})
        audit.append('authorization_decided', 'security', 'outside-actor',
                     {'resource_scope': 'payment-service', 'result': 'allow'})
        before = audit.export()
        expected = [seq for case in cases for seq in case['event_ids']]
        end = datetime.fromisoformat(before[-1]['timestamp']) + timedelta(seconds=1)
        question = 'Show everything jdoe accessed related to payment-service in the last 30 days.'
        filters = parse_inquiry(question, as_of=end)
        filters['page_size'] = 7
        page = audit.inquire(Actor('auditor'), filters)
        snapshot = page['as_of']
        actual = list(page['events'])
        pages = 1
        # A real new request after page one must not leak into its fixed snapshot.
        engine.model = FakeExtractiveModel()
        late = engine.query(actor, 'What is the current payment-service runbook?')
        while page['next_after']:
            page = audit.inquire(Actor('auditor'), dict(page['filters'], after=page['next_after']))
            assert page['as_of'] == snapshot
            actual.extend(page['events'])
            pages += 1
        assert [e['seq'] for e in actual] == expected
        assert not any(e['request_id'] == late['request_id'] for e in actual)
        role_denials = []
        for uid in ('eng_a', 'security'):
            try:
                audit.inquire(Actor(uid), filters)
            except PermissionError:
                role_denials.append(uid)
            else:
                raise AssertionError('Unauthorized audit access')
        try:
            audit.inquire(Actor('auditor'), dict(filters, actor='security'))
        except PermissionError:
            scope_denied = True
        else:
            raise AssertionError('Auditor scope expanded')
        original = audit.export()
        events_path = output / 'audit.json'
        write(events_path, original)
        original_hash = hashlib.sha256(events_path.read_bytes()).hexdigest()
        signatures = {}
        with tempfile.TemporaryDirectory(prefix='aibang2-mixed-signing-') as directory:
            temp = Path(directory)
            key = temp / 'disposable.pem'
            key.touch(mode=0o600)
            def command(args):
                result = subprocess.run(args, capture_output=True, text=True, timeout=30)
                if result.returncode:
                    raise RuntimeError('Local signature command failed')
                return result
            command(['openssl', 'genpkey', '-algorithm', 'ED25519', '-out', str(key)])
            public = output / 'test-public.pem'
            command(['openssl', 'pkey', '-in', str(key), '-pubout', '-out', str(public)])
            checkpoint = output / 'checkpoint.json'
            stream = 'ai-bang2-fixture-mixed-outcomes'
            command([sys.executable, 'tools/audit_verifier/checkpoint.py', '--events', str(events_path),
                     '--private-key', str(key), '--through-seq', str(len(original)),
                     '--stream-id', stream, '--out', str(checkpoint)])
            modified = copy.deepcopy(original)
            modified[0]['payload']['query'] = 'modified test copy'
            for label, value, expected_ok in (
                    ('original', original, True), ('modified', modified, False),
                    ('middle_deleted', original[:2] + original[3:], False),
                    ('covered_tail_deleted', original[:-1], False)):
                variant = temp / (label + '.json')
                write(variant, value)
                result = subprocess.run([sys.executable, 'tools/audit_verifier/verify.py', '--events', str(variant),
                                         '--checkpoint', str(checkpoint), '--public-key', str(public),
                                         '--expected-stream-id', stream], capture_output=True, text=True, timeout=30)
                assert (result.returncode == 0) == expected_ok
                signatures[label] = json.loads(result.stdout)
        assert hashlib.sha256(events_path.read_bytes()).hexdigest() == original_hash
        write(output / 'oracle.json', {'mode': 'developer_fixture_oracle_not_human_review',
                                      'requests': cases, 'expected_event_ids': expected})
        write(output / 'inquiry.json', {'question': question, 'filters': page['filters'], 'pages': pages,
                                       'events': actual, 'actual_event_ids': [e['seq'] for e in actual]})
        report.update(status='verified_local_subset', outcome_cases=[c['case'] for c in cases],
                      oracle_event_count=len(expected), pagination_pages=pages,
                      stable_snapshot=snapshot, pagination_oracle_matches=True,
                      role_denials=role_denials, auditor_scope_denied=scope_denied,
                      failed_request_not_stored=True, signature_cases=signatures,
                      private_test_key_deleted=True, original_unchanged=True,
                      audit_chain=verify_chain(original),
                      limitations=['Fixture identities and sources; not native auditor authentication.',
                                   'Developer oracle is not independent human acceptance.',
                                   'Same-machine disposable signing key is not independent key custody.',
                                   'Unsigned/uncovered tail deletion boundary remains as demonstrated in audit-replay.',
                                   'Audit reconstructs application operations, not human reading.'])
    except Exception as error:
        report.update(status='failed', reason=type(error).__name__)
        write(output / 'audit.json', audit.export())
        write(output / 'partial-cases.json', cases)
    finally:
        report['finished_at'] = now()
        write(output / 'verification.json', report)
        store.db.close()
    print(json.dumps({k: report[k] for k in ('status', 'outcome_cases', 'oracle_event_count', 'pagination_pages') if k in report}))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.output)['status'] == 'verified_local_subset' else 1)
