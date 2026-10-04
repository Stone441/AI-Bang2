"""Independent recomputation of the audit v1 hash chain contract.

This module deliberately does NOT import brain.*: the verifier must check an
export against the documented contract (docs/CONTRACTS.md v1), not by reusing
the producer's code. Any divergence from brain/store.py canonical() or
brain/audit.py event_hash() is a compatibility bug in this module.

Contract (must stay byte-compatible with v1):
- canonical JSON: json.dumps(value, sort_keys=True, ensure_ascii=False,
  separators=(',', ':'))
- event hash: SHA256(b'ContextLedger.audit.v1\\0' + canonical(event without
  the 'hash' key).encode('utf-8'))
- genesis previous_hash is 64 '0' characters; seq starts at 1 and is
  contiguous; each event's previous_hash equals the prior event's hash.
"""
import hashlib
import json

DOMAIN = b'ContextLedger.audit.v1\0'
ZERO = '0' * 64
REQUIRED_FIELDS = ('schema_version', 'seq', 'previous_hash', 'event_type',
                   'actor', 'request_id', 'timestamp', 'payload', 'hash')


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'))


def event_hash(event):
    body = {k: v for k, v in event.items() if k != 'hash'}
    return hashlib.sha256(DOMAIN + canonical(body).encode('utf-8')).hexdigest()


def verify_span(events, start_seq, end_seq, previous_hash):
    """Recompute the chain over events[start_seq-1:end_seq].

    Returns {'chain_valid': bool, 'head_hash': recomputed head} on success or
    {'chain_valid': False, 'reason': ..., 'sequence': seq} on the first
    mismatch. An empty span is valid with head_hash == previous_hash.
    """
    previous = previous_hash
    for seq in range(start_seq, end_seq + 1):
        event = events[seq - 1]
        if not isinstance(event, dict):
            return {'chain_valid': False, 'reason': 'schema_mismatch',
                    'sequence': seq}
        missing = [f for f in REQUIRED_FIELDS if f not in event]
        if (missing or type(event['schema_version']) is not int
                or event['schema_version'] != 1):
            return {'chain_valid': False, 'reason': 'schema_mismatch',
                    'sequence': seq, 'detail': {'missing_fields': missing}}
        # bool is rejected even though bool subclasses int (True == 1):
        # sequence numbers and schema versions must be real integers.
        if (type(event['seq']) is not int or event['seq'] != seq
                or event['previous_hash'] != previous
                or event['hash'] != event_hash(event)):
            return {'chain_valid': False, 'reason': 'chain_mismatch',
                    'sequence': seq}
        previous = event['hash']
    return {'chain_valid': True, 'head_hash': previous}
