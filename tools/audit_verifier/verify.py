#!/usr/bin/env python3
"""Independent CLI verifier for an exported audit v1 chain.

Usage:
  python3 tools/audit_verifier/verify.py --events export.json \
      [--checkpoint checkpoint.json --public-key pub.pem] \
      [--expected-stream-id audit-main]

The checkpoint and public key MUST be supplied from separately retained,
trusted copies; the verifier never accepts a new trust root from inside the
log being verified. Exit codes:

  0  the segment covered by the trusted signature verifies; an unanchored
     tail, if present, is reported separately and is NOT trusted
  1  verification failed: bad signature, wrong key, stream mismatch, or
     tampering detected (anchored or tail)
  2  no anchor supplied: local chain only, explicitly untrusted; a full
     chain replacement cannot be detected in this mode
"""
import argparse
import base64
import binascii
import json
import sys

from chain import canonical, verify_span, ZERO
from crypto import verify_ed25519, CryptoError, UnsupportedKeyError

SCHEMA_VERSION = 1
DEFAULT_STREAM_ID = 'audit-main'
CHECKPOINT_FIELDS = ('schema_version', 'stream_id', 'through_seq',
                     'head_hash', 'timestamp')

BOUNDARIES = [
    'Same-host, same-account signing cannot resist full compromise of that '
    'account; this is a logical demonstration, not a production independence boundary.',
    'Audit v1 events carry no stream_id; stream identity is enforced only as '
    'an external expectation parameter on the checkpoint, so cross-stream '
    'transplant prevention is checked, not proven by the event schema itself.',
    'Events after through_seq are not covered by the checkpoint signature; '
    'replacement or truncation inside the unanchored tail is undetectable by '
    'this checkpoint.',
    'Verification recomputes canonical hashes from parsed JSON; it detects '
    'content tampering, not non-canonical re-serialization of identical content.',
]


def emit(report, verdict, code):
    if verdict is not None:
        report['verdict'] = verdict
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return code


def load_json(path, label):
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            return json.load(handle), None
    except (OSError, json.JSONDecodeError) as exc:
        return None, 'cannot read %s: %s' % (label, exc)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Verify an audit v1 export against an independent signed checkpoint.')
    parser.add_argument('--events', required=True, help='path to Audit.export() JSON array')
    parser.add_argument('--checkpoint', default=None,
                        help='path to separately retained signed checkpoint')
    parser.add_argument('--public-key', default=None,
                        help='path to trusted Ed25519 public key')
    parser.add_argument('--expected-stream-id', default=DEFAULT_STREAM_ID)
    args = parser.parse_args(argv)

    report = {'boundaries': BOUNDARIES}

    events, error = load_json(args.events, 'events')
    if error:
        return emit(report, 'invalid_events: ' + error, 1)
    if not isinstance(events, list) or not all(isinstance(e, dict) for e in events):
        return emit(report, 'invalid_events: must be a JSON array of objects', 1)
    report['exported_events'] = len(events)

    if args.checkpoint is None:
        local = verify_span(events, 1, len(events), ZERO)
        report['signature'] = {'verified': False,
                               'detail': 'no checkpoint supplied'}
        report['anchored'] = {'through_seq': 0, 'chain_valid': local['chain_valid'],
                              'reason': local.get('reason')}
        report['tail'] = {'present': bool(events), 'from_seq': 1,
                          'to_seq': len(events), 'count': len(events),
                          'anchored': False, 'chain_valid': local['chain_valid'],
                          'note': 'No anchor: local chain only; whole-chain '
                                  'replacement or truncation is undetectable.'}
        return emit(report, 'untrusted_no_anchor', 2)

    if args.public_key is None:
        report['signature'] = {'verified': False, 'detail': 'missing public key'}
        return emit(report, 'missing_public_key', 1)

    wrapper, error = load_json(args.checkpoint, 'checkpoint')
    if error:
        return emit(report, 'invalid_checkpoint: ' + error, 1)
    if (not isinstance(wrapper, dict)
            or type(wrapper.get('schema_version')) is not int
            or wrapper.get('schema_version') != SCHEMA_VERSION):
        return emit(report, 'invalid_checkpoint: unsupported schema', 1)
    if wrapper.get('algorithm') != 'ed25519':
        return emit(report, 'invalid_checkpoint: unsupported algorithm', 1)
    cp = wrapper.get('checkpoint')
    if not isinstance(cp, dict) or any(f not in cp for f in CHECKPOINT_FIELDS):
        return emit(report, 'invalid_checkpoint: missing fields', 1)
    if (type(cp.get('schema_version')) is not int
            or cp.get('schema_version') != SCHEMA_VERSION):
        return emit(report, 'invalid_checkpoint: unsupported checkpoint schema', 1)
    # bool is rejected even though bool subclasses int (True == 1)
    through = cp.get('through_seq')
    if type(through) is not int or through < 0:
        report['anchored'] = {'through_seq': through, 'chain_valid': False,
                              'reason': 'invalid through_seq'}
        return emit(report, 'invalid_checkpoint_through_seq', 1)
    try:
        signature = base64.b64decode(wrapper.get('signature', ''),
                                      validate=True)
    except (binascii.Error, TypeError, ValueError):
        report['signature'] = {'verified': False, 'detail': 'malformed signature encoding'}
        return emit(report, 'invalid_signature', 1)

    message = canonical(cp).encode('utf-8')
    try:
        verified, detail = verify_ed25519(args.public_key, message, signature)
    except UnsupportedKeyError as exc:
        report['signature'] = {'algorithm': 'ed25519', 'verified': False,
                               'detail': str(exc)}
        return emit(report, 'non_ed25519_key', 1)
    except CryptoError as exc:
        report['signature'] = {'algorithm': 'ed25519', 'verified': False,
                               'detail': str(exc)}
        return emit(report, 'openssl_error', 1)
    report['signature'] = {'algorithm': 'ed25519', 'verified': verified,
                           'detail': 'ok' if verified else detail}
    if not verified:
        return emit(report, 'signature_invalid', 1)

    report['stream_id'] = {'checkpoint': cp.get('stream_id'),
                           'expected': args.expected_stream_id,
                           'match': cp.get('stream_id') == args.expected_stream_id}
    if not report['stream_id']['match']:
        return emit(report, 'stream_id_mismatch', 1)

    if through > len(events):
        report['anchored'] = {'through_seq': through,
                              'exported_events': len(events), 'chain_valid': False,
                              'reason': 'covered_events_missing',
                              'note': 'checkpoint covers more events than exported; '
                                      'consistent with deletion of the signed tail'}
        return emit(report, 'covered_events_missing', 1)

    prefix = verify_span(events, 1, through, ZERO)
    if not prefix['chain_valid']:
        report['anchored'] = {'through_seq': through, 'chain_valid': False,
                              'reason': prefix.get('reason'),
                              'sequence': prefix.get('sequence')}
        return emit(report, 'anchored_chain_invalid', 1)
    if prefix['head_hash'] != cp.get('head_hash'):
        report['anchored'] = {'through_seq': through, 'chain_valid': False,
                              'reason': 'head_hash_mismatch',
                              'note': 'chain is internally consistent but does not '
                                      'match the signed checkpoint; consistent with '
                                      'whole-chain recomputation/replacement'}
        return emit(report, 'anchored_head_mismatch', 1)

    report['anchored'] = {'through_seq': through, 'head_hash': cp.get('head_hash'),
                          'chain_valid': True, 'events': through}

    tail_count = len(events) - through
    if tail_count > 0:
        anchor_head = events[through - 1]['hash'] if through >= 1 else ZERO
        suffix = verify_span(events, through + 1, len(events), anchor_head)
        report['tail'] = {'present': True, 'from_seq': through + 1,
                          'to_seq': len(events), 'count': tail_count,
                          'anchored': False,
                          'chain_valid': suffix['chain_valid'],
                          'reason': suffix.get('reason'),
                          'sequence': suffix.get('sequence'),
                          'note': 'Not covered by the checkpoint signature; '
                                  'replacement or truncation inside this tail is '
                                  'undetectable by this checkpoint.'}
        if not suffix['chain_valid']:
            return emit(report, 'tail_chain_invalid', 1)
        return emit(report, 'anchored_valid_tail_unanchored', 0)

    report['tail'] = {'present': False, 'count': 0}
    return emit(report, 'anchored_valid', 0)


if __name__ == '__main__':
    sys.exit(main())
