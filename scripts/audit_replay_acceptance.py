"""Offline audit inquiry/signature validation over captured synthetic live events.

The caller is a local test auditor, not a native/SSO authenticated auditor. Signing
uses a disposable local Ed25519 key; this proves mechanics, not independent custody.
Never changes the original audit export or queries a business platform/model.
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
from brain.audit import Audit, event_hash, verify_chain, ZERO
from brain.audit_query import parse_inquiry
from brain.contracts import Actor, now
from brain.store import Store, canonical
from scripts.build_metadata import revision


def write(path, value): path.write_text(json.dumps(value, indent=2) + '\n')


def command(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if result.returncode: raise RuntimeError('Local signer command failed')
    return result


def run(events_path, output):
    original_bytes = events_path.read_bytes()
    events = json.loads(original_bytes)
    if not events or not verify_chain(events)['valid']: raise ValueError('Valid nonempty audit export required')
    output.mkdir(parents=True, exist_ok=True)
    # Import a COPY into memory; inquiry append events never touch original live DB.
    store = Store()
    try:
        with store.transaction() as db:
            for event in events:
                db.execute('INSERT INTO audit(seq,body) VALUES(?,?)', (event['seq'], canonical(event)))
        audit = Audit(store)
        end = datetime.fromisoformat(events[-1]['timestamp']) + timedelta(seconds=1)
        filters = parse_inquiry('Show everything eng_b accessed related to payment-service in the last 30 days.', as_of=end)
        filters['page_size'] = 7
        # The input stream is this eng_b two-query pilot; record a concrete oracle.
        expected = [e['seq'] for e in events if e['actor'] == 'eng_b']
        page = audit.inquire(Actor('auditor'), filters)
        actual = list(page['events']); pages = 1
        while page['next_after']:
            page = audit.inquire(Actor('auditor'), dict(page['filters'], after=page['next_after']))
            actual.extend(page['events']); pages += 1
        if [e['seq'] for e in actual] != expected: raise RuntimeError('Inquiry oracle mismatch')
        try: audit.inquire(Actor('eng_b'), filters)
        except PermissionError: nonauditor_denied = True
        else: raise RuntimeError('Unauthenticated audit role grant')
        if not any(e['event_type'] == 'response_committed' for e in actual): raise RuntimeError('Response not reconstructed')
        write(output / 'inquiry.json', {'filters': page['filters'], 'expected_event_ids': expected,
              'actual_event_ids': [e['seq'] for e in actual], 'pages': pages, 'events': actual,
              'caller_mode': 'explicit_local_test_auditor', 'nonauditor_denied': nonauditor_denied})
        stream = 'ai-bang2-local-replay-demo'
        Path('.runtime').mkdir(exist_ok=True)
        results = {}
        with tempfile.TemporaryDirectory(prefix='audit-replay-', dir='.runtime') as directory:
            temp = Path(directory)
            private = temp / 'test-private.pem'
            private.touch(mode=0o600)
            command(['openssl', 'genpkey', '-algorithm', 'ED25519', '-out', str(private)])
            public = output / 'test-public.pem'
            command(['openssl', 'pkey', '-in', str(private), '-pubout', '-out', str(public)])
            def sign(through, path):
                command([sys.executable, 'tools/audit_verifier/checkpoint.py', '--events', str(events_path),
                         '--private-key', str(private), '--through-seq', str(through),
                         '--stream-id', stream, '--out', str(path)])
            full = output / 'checkpoint-full.json'; prefix = output / 'checkpoint-prefix.json'
            sign(len(events), full); sign(len(events)-1, prefix)
            modified = copy.deepcopy(events); modified[0]['payload']['query'] = 'Modified local copy'
            rehashed = copy.deepcopy(modified)
            previous = ZERO
            for e in rehashed:
                e['previous_hash'] = previous; e['hash'] = event_hash(e); previous = e['hash']
            variants = [('original', events, full, True), ('body_modified', modified, full, False),
                        ('middle_deleted', events[:2] + events[3:], full, False),
                        ('covered_tail_deleted', events[:-1], full, False),
                        ('whole_chain_recomputed', rehashed, full, False),
                        ('uncovered_tail_present', events, prefix, True),
                        ('uncovered_tail_removed', events[:-1], prefix, True)]
            for label, value, checkpoint, expected_ok in variants:
                path = temp / (label + '.json'); write(path, value)
                result = subprocess.run([sys.executable, 'tools/audit_verifier/verify.py', '--events', str(path),
                         '--checkpoint', str(checkpoint), '--public-key', str(public),
                         '--expected-stream-id', stream], capture_output=True, text=True, timeout=30)
                verification = json.loads(result.stdout)
                if (result.returncode == 0) != expected_ok: raise RuntimeError('Signature case failed: ' + label)
                results[label] = {'exit_code': result.returncode, 'actual': verification,
                                  'expected_accept': expected_ok, 'status': 'passed_local_subset'}
        if events_path.read_bytes() != original_bytes: raise RuntimeError('Original export modified')
        report = {'finished_at': now(), 'commit': revision(), 'mode': 'offline_replay_of_live_synthetic_audit',
                  'input': str(events_path), 'input_sha256': hashlib.sha256(original_bytes).hexdigest(),
                  'source_hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                    [Path(__file__), Path('brain/audit.py'), Path('brain/audit_query.py'),
                                     Path('tools/audit_verifier/verify.py'), Path('tools/audit_verifier/checkpoint.py')]},
                  'pagination_oracle_matches': True, 'nonauditor_denied': nonauditor_denied,
                  'original_unchanged': True, 'signature_cases': results,
                  'private_test_key_deleted': True, 'human_G1': 'not_run', 'status': 'verified_local_subset',
                  'limitations': ['Local test auditor; not native auditor authentication or production role isolation.',
                                   'Disposable same-machine test key, not independently operated key custody.',
                                   'Captured stream contains successful and no-evidence queries; not the full S-05 mixed-outcome oracle.',
                                   'Uncovered tail can be removed without detection by the prefix checkpoint.',
                                   'Queries reconstruct application activity, not proof a human read the material.']}
        write(output / 'verification.json', report)
        print('Audit pagination oracle and 7 signature boundary cases passed_local_subset')
    finally:
        store.db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', type=Path, default=Path('evidence/runs/live-product/audit.json'))
    parser.add_argument('--output', type=Path, default=Path('evidence/runs/audit-replay'))
    args = parser.parse_args()
    run(args.events, args.output)
