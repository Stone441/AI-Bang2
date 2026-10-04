"""DEV-09-CB: signed checkpoints and the independent verifier CLI.

Covers the signature-related assertions of A-03 (content edit / middle
deletion inside checkpoint coverage fails), A-04 (signed-tail deletion and
whole-chain recomputation cannot pass; trusted signature and sequence are
checked), and A-11 (missing checkpoint and unanchored tail are reported
explicitly, never as a blanket "all trusted").

All openssl calls (genpkey / pkey / pkeyutl -rawin) are executed for real via
subprocess; keys live only in TemporaryDirectory.
"""
import base64
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

from brain.audit import Audit, event_hash as brain_event_hash
from brain.store import Store

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS_DIR = os.path.join(REPO_ROOT, 'tools', 'audit_verifier')
CHECKPOINT_CLI = os.path.join(TOOLS_DIR, 'checkpoint.py')
VERIFY_CLI = os.path.join(TOOLS_DIR, 'verify.py')
EVENTS_COUNT = 10


def load_tool_module(name):
    spec = importlib.util.spec_from_file_location(
        'dev09_' + name, os.path.join(TOOLS_DIR, name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


chain = load_tool_module('chain')


def openssl(*args):
    result = subprocess.run(['openssl', *args], capture_output=True)
    if result.returncode != 0:
        raise AssertionError('openssl %s failed: %s' % (
            ' '.join(args), result.stderr.decode('utf-8', 'replace')))
    return result


def rebuild_chain(events, mutate=None):
    """Recompute a fully consistent chain after optional mutation, mimicking
    an attacker who rewrites the whole chain."""
    rebuilt = copy.deepcopy(events)
    if mutate is not None:
        mutate(rebuilt)
    for i, event in enumerate(rebuilt):
        if i:
            event['previous_hash'] = rebuilt[i - 1]['hash']
        event['hash'] = chain.event_hash(event)
    return rebuilt


class VerifierTestBase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        self.priv = os.path.join(self.tmp, 'signing-key.pem')
        self.pub = os.path.join(self.tmp, 'public-key.pem')
        openssl('genpkey', '-algorithm', 'ed25519', '-out', self.priv)
        openssl('pkey', '-in', self.priv, '-pubout', '-out', self.pub)
        store = Store()
        self.addCleanup(store.db.close)
        audit = Audit(store)
        for i in range(EVENTS_COUNT):
            audit.append('request_started', 'eng_a', 'req-%d' % i,
                         {'query': 'question %d' % i})
        self.events = audit.export()
        self._counter = 0
        self.events_path = self.write_events(self.events)

    def write_events(self, events):
        self._counter += 1
        path = os.path.join(self.tmp, 'events-%d.json' % self._counter)
        with open(path, 'w', encoding='utf-8') as handle:
            json.dump(events, handle, ensure_ascii=False)
        return path

    def make_checkpoint(self, events_path=None, through_seq=None,
                        stream_id='audit-main', private_key=None,
                        out=None, expect_success=True):
        out = out or os.path.join(self.tmp, 'checkpoint.json')
        args = [sys.executable, CHECKPOINT_CLI,
                '--events', events_path or self.events_path,
                '--private-key', private_key or self.priv,
                '--out', out]
        if through_seq is not None:
            args += ['--through-seq', str(through_seq)]
        if stream_id is not None:
            args += ['--stream-id', stream_id]
        result = subprocess.run(args, capture_output=True, text=True)
        if expect_success and result.returncode != 0:
            self.fail('checkpoint generation failed: %s %s'
                      % (result.stdout, result.stderr))
        return result, out

    def verify(self, events_path=None, checkpoint_path=None, public_key=None,
               expected_stream_id='audit-main'):
        args = [sys.executable, VERIFY_CLI,
                '--events', events_path or self.events_path,
                '--public-key', public_key or self.pub,
                '--expected-stream-id', expected_stream_id]
        if checkpoint_path is not None:
            args += ['--checkpoint', checkpoint_path]
        result = subprocess.run(args, capture_output=True, text=True)
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail('verifier printed non-JSON output: stdout=%r stderr=%r'
                      % (result.stdout, result.stderr))
        return result.returncode, report


class HashContractCompatibility(unittest.TestCase):
    """The verifier's independent recomputation must match brain v1 exactly."""

    def test_independent_recomputation_matches_brain_v1(self):
        store = Store()
        self.addCleanup(store.db.close)
        audit = Audit(store)
        audit.append('request_started', 'eng_a', 'r1', {'query': 'q'})
        audit.append('evidence_used', 'eng_a', 'r1', {'evidence_ids': ['E-01@1']})
        audit.append('response_committed', 'eng_a', 'r1', {'answer': 'a'})
        events = audit.export()
        previous = '0' * 64
        for seq, event in enumerate(events, 1):
            self.assertEqual(event['seq'], seq)
            self.assertEqual(event['previous_hash'], previous)
            self.assertEqual(chain.event_hash(event), brain_event_hash(event))
            body = {k: v for k, v in event.items() if k != 'hash'}
            self.assertEqual(
                chain.canonical(body),
                json.dumps(body, sort_keys=True, ensure_ascii=False,
                           separators=(',', ':')))
            previous = event['hash']
        self.assertTrue(chain.verify_span(events, 1, len(events), '0' * 64)['chain_valid'])


class CheckpointGeneration(VerifierTestBase):
    def test_signs_full_chain_and_reports_coverage(self):
        result, path = self.make_checkpoint()
        self.assertEqual(result.returncode, 0)
        with open(path, encoding='utf-8') as handle:
            wrapper = json.load(handle)
        self.assertEqual(wrapper['algorithm'], 'ed25519')
        cp = wrapper['checkpoint']
        self.assertEqual(cp['through_seq'], EVENTS_COUNT)
        self.assertEqual(cp['head_hash'], self.events[-1]['hash'])
        self.assertEqual(cp['stream_id'], 'audit-main')

    def test_refuses_to_sign_broken_chain(self):
        corrupted = copy.deepcopy(self.events)
        corrupted[3]['payload']['query'] = 'tampered'
        path = self.write_events(corrupted)
        result, out = self.make_checkpoint(events_path=path, expect_success=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(os.path.exists(out))


class VerificationOutcomes(VerifierTestBase):
    def test_original_chain_with_trusted_signature_passes(self):
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT)
        code, report = self.verify(checkpoint_path=path)
        self.assertEqual(code, 0)
        self.assertEqual(report['verdict'], 'anchored_valid')
        self.assertTrue(report['signature']['verified'])
        self.assertEqual(report['anchored']['through_seq'], EVENTS_COUNT)
        self.assertFalse(report['tail']['present'])

    def test_a03_body_modification_inside_coverage_fails(self):
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT)
        edited = copy.deepcopy(self.events)
        edited[3]['payload']['query'] = 'tampered'
        code, report = self.verify(events_path=self.write_events(edited),
                                   checkpoint_path=path)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'anchored_chain_invalid')
        self.assertEqual(report['anchored']['reason'], 'chain_mismatch')
        self.assertTrue(report['signature']['verified'])

    def test_a03_middle_deletion_inside_coverage_fails(self):
        # full-coverage checkpoint: deletion shrinks the export below the
        # signed through_seq and is reported as missing covered events
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT)
        spliced = self.events[:4] + self.events[5:]
        code, report = self.verify(events_path=self.write_events(spliced),
                                   checkpoint_path=path)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'covered_events_missing')

    def test_a03_middle_deletion_partial_coverage_breaks_chain(self):
        # partial-coverage checkpoint: export stays longer than through_seq,
        # so detection happens via the recomputed seq/previous_hash chain
        _, path = self.make_checkpoint(through_seq=6)
        spliced = self.events[:2] + self.events[3:]
        code, report = self.verify(events_path=self.write_events(spliced),
                                   checkpoint_path=path)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'anchored_chain_invalid')
        self.assertEqual(report['anchored']['reason'], 'chain_mismatch')
        self.assertEqual(report['anchored']['sequence'], 3)

    def test_a04_signed_tail_deletion_fails(self):
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT)
        truncated = self.events[:7]
        code, report = self.verify(events_path=self.write_events(truncated),
                                   checkpoint_path=path)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'covered_events_missing')
        self.assertTrue(report['signature']['verified'])
        self.assertEqual(report['anchored']['through_seq'], EVENTS_COUNT)
        self.assertEqual(report['anchored']['exported_events'], 7)

    def test_a04_whole_chain_recomputation_fails(self):
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT)
        replaced = rebuild_chain(
            self.events,
            lambda events: events[0]['payload'].__setitem__('query', 'replacement'))
        # sanity: the rebuilt chain is internally consistent
        self.assertTrue(chain.verify_span(replaced, 1, len(replaced), '0' * 64)['chain_valid'])
        code, report = self.verify(events_path=self.write_events(replaced),
                                   checkpoint_path=path)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'anchored_head_mismatch')
        self.assertTrue(report['signature']['verified'])

    def test_wrong_public_key_rejected(self):
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT)
        other_pub = os.path.join(self.tmp, 'other-public-key.pem')
        other_priv = os.path.join(self.tmp, 'other-private-key.pem')
        openssl('genpkey', '-algorithm', 'ed25519', '-out', other_priv)
        openssl('pkey', '-in', other_priv, '-pubout', '-out', other_pub)
        code, report = self.verify(checkpoint_path=path, public_key=other_pub)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'signature_invalid')
        self.assertFalse(report['signature']['verified'])

    def test_corrupted_signature_rejected(self):
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT)
        with open(path, encoding='utf-8') as handle:
            wrapper = json.load(handle)
        raw = bytearray(base64.b64decode(wrapper['signature']))
        raw[0] ^= 0xFF
        wrapper['signature'] = base64.b64encode(bytes(raw)).decode('ascii')
        bad_path = os.path.join(self.tmp, 'corrupted-checkpoint.json')
        with open(bad_path, 'w', encoding='utf-8') as handle:
            json.dump(wrapper, handle)
        code, report = self.verify(checkpoint_path=bad_path)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'signature_invalid')
        self.assertFalse(report['signature']['verified'])

    def test_missing_checkpoint_reports_untrusted(self):
        code, report = self.verify(checkpoint_path=None)
        self.assertEqual(code, 2)
        self.assertEqual(report['verdict'], 'untrusted_no_anchor')
        self.assertFalse(report['signature']['verified'])
        self.assertIn('undetectable', report['tail']['note'])

    def test_a11_unanchored_tail_reported_separately(self):
        _, path = self.make_checkpoint(through_seq=6)
        code, report = self.verify(checkpoint_path=path)
        self.assertEqual(code, 0)
        self.assertEqual(report['verdict'], 'anchored_valid_tail_unanchored')
        self.assertEqual(report['anchored']['through_seq'], 6)
        tail = report['tail']
        self.assertTrue(tail['present'])
        self.assertFalse(tail['anchored'])
        self.assertEqual((tail['from_seq'], tail['to_seq'], tail['count']), (7, 10, 4))
        self.assertTrue(tail['chain_valid'])
        self.assertIn('undetectable', tail['note'])
        # the report must not describe the tail as trusted
        self.assertNotIn('trusted', json.dumps(tail['note']))

    def test_a11_tampering_inside_unanchored_tail_reported(self):
        _, path = self.make_checkpoint(through_seq=6)
        edited = copy.deepcopy(self.events)
        edited[7]['payload']['query'] = 'tail tamper'
        code, report = self.verify(events_path=self.write_events(edited),
                                   checkpoint_path=path)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'tail_chain_invalid')
        self.assertTrue(report['anchored']['chain_valid'])
        self.assertFalse(report['tail']['chain_valid'])
        self.assertEqual(report['tail']['sequence'], 8)

    def test_stream_id_checked_as_external_expectation(self):
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT,
                                       stream_id='other-stream')
        code, report = self.verify(checkpoint_path=path)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'stream_id_mismatch')
        self.assertFalse(report['stream_id']['match'])
        self.assertTrue(report['signature']['verified'])
        # the same checkpoint passes when the external expectation matches:
        # identity is an expectation parameter, not intrinsic to v1 events
        code, report = self.verify(checkpoint_path=path,
                                   expected_stream_id='other-stream')
        self.assertEqual(code, 0)
        self.assertEqual(report['verdict'], 'anchored_valid')


class NonEd25519KeyRejection(VerifierTestBase):
    """pkeyutl picks the algorithm from the key, so non-Ed25519 keys must be
    rejected explicitly by checking the SPKI OID (1.3.101.112) exported by
    openssl as DER."""

    def _make_non_ed25519_keypair(self, algorithm, extra):
        priv = os.path.join(self.tmp, '%s-private-key.pem' % algorithm)
        pub = os.path.join(self.tmp, '%s-public-key.pem' % algorithm)
        openssl('genpkey', '-algorithm', algorithm, *extra, '-out', priv)
        openssl('pkey', '-in', priv, '-pubout', '-out', pub)
        return priv, pub

    def test_generator_rejects_rsa_and_ec_signing_keys(self):
        cases = (('rsa', ['-pkeyopt', 'rsa_keygen_bits:2048']),
                 ('ec', ['-pkeyopt', 'ec_paramgen_curve:prime256v1']))
        for algorithm, extra in cases:
            with self.subTest(algorithm=algorithm):
                priv, _ = self._make_non_ed25519_keypair(algorithm, extra)
                result, out = self.make_checkpoint(private_key=priv,
                                                   expect_success=False)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('not an Ed25519 key', result.stderr)
                self.assertFalse(os.path.exists(out))

    def test_verifier_rejects_rsa_public_key(self):
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT)
        _, rsa_pub = self._make_non_ed25519_keypair(
            'rsa', ['-pkeyopt', 'rsa_keygen_bits:2048'])
        code, report = self.verify(checkpoint_path=path, public_key=rsa_pub)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'non_ed25519_key')
        self.assertFalse(report['signature']['verified'])
        self.assertIn('not an Ed25519 key', report['signature']['detail'])

    def test_verifier_rejects_ec_public_key(self):
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT)
        _, ec_pub = self._make_non_ed25519_keypair(
            'ec', ['-pkeyopt', 'ec_paramgen_curve:prime256v1'])
        code, report = self.verify(checkpoint_path=path, public_key=ec_pub)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'non_ed25519_key')


class StrictIntegerTypes(VerifierTestBase):
    """bool subclasses int and True == 1 in Python, so isinstance checks
    would accept JSON true where an integer is required."""

    def test_bool_seq_and_schema_version_rejected_in_chain(self):
        forged = copy.deepcopy(self.events)
        forged[0]['schema_version'] = True
        forged[0]['hash'] = chain.event_hash(forged[0])
        result = chain.verify_span(forged, 1, len(forged), '0' * 64)
        self.assertFalse(result['chain_valid'])
        self.assertEqual(result['reason'], 'schema_mismatch')

        only_seq = copy.deepcopy(self.events)
        only_seq[0]['seq'] = True
        only_seq[0]['hash'] = chain.event_hash(only_seq[0])
        result = chain.verify_span(only_seq, 1, len(only_seq), '0' * 64)
        self.assertFalse(result['chain_valid'])
        self.assertEqual(result['reason'], 'chain_mismatch')

    def test_bool_through_seq_rejected_by_verifier(self):
        _, path = self.make_checkpoint(through_seq=EVENTS_COUNT)
        with open(path, encoding='utf-8') as handle:
            wrapper = json.load(handle)
        wrapper['checkpoint']['through_seq'] = True
        tampered = os.path.join(self.tmp, 'bool-through-seq-checkpoint.json')
        with open(tampered, 'w', encoding='utf-8') as handle:
            json.dump(wrapper, handle)
        code, report = self.verify(checkpoint_path=tampered)
        self.assertEqual(code, 1)
        self.assertEqual(report['verdict'], 'invalid_checkpoint_through_seq')


if __name__ == '__main__':
    unittest.main()
