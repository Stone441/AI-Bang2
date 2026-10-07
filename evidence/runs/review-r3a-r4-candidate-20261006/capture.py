"""One-off local candidate capture. Original evidence and runtime are untouched.

Run from repository root: python3 -B evidence/runs/review-r3a-r4-candidate-20261006/capture.py
Outputs are create-only. Mock usage is never a real vendor receipt.
"""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from brain.audit import ZERO, event_hash, verify_chain
from brain.contracts import now
from test_model_stages import ModelStages

OUT = Path(__file__).parent / 'audit'
OUT.mkdir(exist_ok=False)
COMMIT = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
def write(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
def command(args):
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result

def verify(label, events, checkpoint, expected):
    path = OUT / (label + '-events.json')
    write(path, events)
    args = [sys.executable, 'tools/audit_verifier/verify.py', '--events', str(path),
            '--checkpoint', str(checkpoint), '--public-key', str(public),
            '--expected-stream-id', 'r3a-r4-local-candidate']
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    (OUT / (label + '-verify.json')).write_text(result.stdout)
    (OUT / (label + '-verify.stderr')).write_text(result.stderr)
    actual = json.loads(result.stdout)
    assert (result.returncode == 0) == expected, (label, actual)
    return {'command': args, 'exit_code': result.returncode, 'verdict': actual['verdict'],
            'through_seq': actual.get('anchored', {}).get('through_seq'),
            'tail': actual.get('tail'), 'expected_accept': expected}

cases = {}; signature_checks = {}
with tempfile.TemporaryDirectory(prefix='aibang2-candidate-signer-') as tmp:
    private = Path(tmp) / 'disposable-private.pem'
    private.touch(mode=0o600)
    command(['openssl', 'genpkey', '-algorithm', 'ED25519', '-out', str(private)])
    public = OUT / 'test-public.pem'
    command(['openssl', 'pkey', '-in', str(private), '-pubout', '-out', str(public)])
    for case in ('success', 'guard', 'price', 'budget', 'timeout', 'review'):
        harness = ModelStages(); harness.setUp()
        try:
            result = harness.run_case(case)
        finally:
            harness.tearDown()
        assert result['transport_calls'] == {'success':1, 'guard':0, 'price':0, 'budget':0, 'timeout':1, 'review':2}[case]
        assert (result['answer'] is not None) == (case == 'success')
        assert verify_chain(result['events'])['valid']
        write(OUT / (case + '-actual.json'), result)
        events_path = OUT / (case + '-snapshot.json')
        write(events_path, result['events'])
        before = events_path.read_bytes()
        checkpoint = OUT / (case + '-checkpoint.json')
        args = [sys.executable, 'tools/audit_verifier/checkpoint.py', '--events', str(events_path),
                '--private-key', str(private), '--through-seq', str(len(result['events'])),
                '--stream-id', 'r3a-r4-local-candidate', '--out', str(checkpoint)]
        (OUT / (case + '-sign.log')).write_text(command(args).stdout)
        signature_checks[case] = verify(case, result['events'], checkpoint, True)
        assert events_path.read_bytes() == before
        cases[case] = {'snapshot': events_path.name, 'snapshot_sha256': hashlib.sha256(before).hexdigest(),
                       'checkpoint': checkpoint.name, 'through_seq': len(result['events']),
                       'transport_calls': result['transport_calls'], 'error_type': result['error_type'],
                       'mode': 'fixture_mock_model'}
        if case == 'success':
            success = result['events']; full = checkpoint
    prefix = OUT / 'success-prefix-checkpoint.json'
    args = [sys.executable, 'tools/audit_verifier/checkpoint.py', '--events', str(OUT / 'success-snapshot.json'),
            '--private-key', str(private), '--through-seq', str(len(success)-1),
            '--stream-id', 'r3a-r4-local-candidate', '--out', str(prefix)]
    (OUT / 'prefix-sign.log').write_text(command(args).stdout)
    modified = copy.deepcopy(success); modified[1]['payload']['question'] = 'tampered local copy'
    rehashed = copy.deepcopy(modified); previous = ZERO
    for event in rehashed:
        event['previous_hash'] = previous; event['hash'] = event_hash(event); previous = event['hash']
    for label, events, checkpoint, accepted in (
            ('body_modified', modified, full, False),
            ('middle_deleted', success[:2] + success[3:], full, False),
            ('covered_tail_deleted', success[:-1], full, False),
            ('whole_chain_recomputed', rehashed, full, False),
            ('uncovered_tail_present', success, prefix, True),
            ('old_checkpoint_and_truncated_snapshot', success[:-1], prefix, True)):
        signature_checks[label] = verify(label, events, checkpoint, accepted)
    # Both the old checkpoint and old snapshot verify. Only an independently
    # retained newer anchor can reject the rollback. No anti-rollback feature is claimed.
    signature_checks['truncated_snapshot_against_retained_latest'] = verify(
        'truncated_snapshot_against_retained_latest', success[:-1], full, False)
assert not private.exists()
paths = [p for folder in ('brain', 'web', 'fixtures', 'tools/audit_verifier')
         for p in sorted((ROOT / folder).rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
write(OUT / 'verification.json', {
    'finished_at': now(), 'validated_commit': COMMIT, 'mode': 'fixture_mock_model_disposable_local_signature',
    'cases': cases, 'signature_checks': signature_checks, 'private_test_key_deleted': True,
    'runtime_source_hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    'live_source_api_called': False, 'live_model_called': False, 'human_G1': 'not_run',
    'limitations': ['Mock usage is not a vendor receipt.',
                    'Disposable same-host same-account key; independent custody and production DB roles not implemented.',
                    'Prefix does not protect unsigned tail; an old checkpoint plus truncated old snapshot is accepted.',
                    'Latest separately retained checkpoint rejects covered truncation; no automatic freshness authority.',
                    'Legacy prepared event is retained verbatim in each fresh fixture stream.'],
    'status': 'verified_local_subset'})
print('Six current mock snapshots and 13 signature/rollback checks passed; disposable private key deleted.')
