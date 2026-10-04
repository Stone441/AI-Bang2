#!/usr/bin/env python3
"""Generate a signed checkpoint over an Audit.export() JSON array.

Usage:
  python3 tools/audit_verifier/checkpoint.py --events export.json \
      --private-key priv.pem [--through-seq N] [--stream-id audit-main] \
      --out checkpoint.json

Signs canonical(checkpoint) with Ed25519 via the system OpenSSL CLI
(pkeyutl -rawin). The signed checkpoint must be retained separately from the
audit log by the integrator; keeping it next to the log under the same
account is only a logical demonstration, not a production boundary.

The private key is read by openssl directly from the given path; its content
is never displayed, copied, or embedded in the output file.
"""
import argparse
import base64
import json
import sys
from datetime import datetime, timezone

from chain import canonical, verify_span, ZERO
from crypto import sign_ed25519, CryptoError

SCHEMA_VERSION = 1
DEFAULT_STREAM_ID = 'audit-main'
CHECKPOINT_FIELDS = ('schema_version', 'stream_id', 'through_seq',
                     'head_hash', 'timestamp')


def build_checkpoint(events, through_seq, stream_id):
    return {
        'schema_version': SCHEMA_VERSION,
        'stream_id': stream_id,
        'through_seq': through_seq,
        'head_hash': events[through_seq - 1]['hash'],
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Sign an audit v1 checkpoint (Ed25519 via system OpenSSL).')
    parser.add_argument('--events', required=True,
                        help='path to Audit.export() JSON array')
    parser.add_argument('--private-key', required=True,
                        help='path to Ed25519 private key (read by openssl only)')
    parser.add_argument('--through-seq', type=int, default=None,
                        help='checkpoint coverage (default: all exported events)')
    parser.add_argument('--stream-id', default=DEFAULT_STREAM_ID)
    parser.add_argument('--out', required=True, help='output checkpoint path')
    args = parser.parse_args(argv)

    try:
        with open(args.events, 'r', encoding='utf-8') as handle:
            events = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print('error: cannot read events: %s' % exc, file=sys.stderr)
        return 1
    if not isinstance(events, list) or not all(isinstance(e, dict) for e in events):
        print('error: events must be a JSON array of objects', file=sys.stderr)
        return 1

    through = args.through_seq if args.through_seq is not None else len(events)
    if not 1 <= through <= len(events):
        print('error: --through-seq must be within 1..%d' % len(events),
              file=sys.stderr)
        return 1

    prefix = verify_span(events, 1, through, ZERO)
    if not prefix['chain_valid']:
        print('error: refusing to sign: chain invalid at seq %s (%s)'
              % (prefix.get('sequence'), prefix.get('reason')), file=sys.stderr)
        return 1
    if prefix['head_hash'] != events[through - 1]['hash']:
        print('error: internal consistency check failed', file=sys.stderr)
        return 1

    checkpoint = build_checkpoint(events, through, args.stream_id)
    message = canonical(checkpoint).encode('utf-8')
    try:
        signature = sign_ed25519(args.private_key, message)
    except CryptoError as exc:
        print('error: %s' % exc, file=sys.stderr)
        return 1

    wrapper = {
        'schema_version': SCHEMA_VERSION,
        'algorithm': 'ed25519',
        'signing_backend': 'openssl pkeyutl -rawin (Ed25519, one-shot)',
        'checkpoint': checkpoint,
        'signature': base64.b64encode(signature).decode('ascii'),
    }
    with open(args.out, 'w', encoding='utf-8') as handle:
        handle.write(canonical(wrapper))
    print('checkpoint written: stream_id=%s through_seq=%d head_hash=%s'
          % (checkpoint['stream_id'], through, checkpoint['head_hash']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
