# Evidence and audit contracts

## Evidence and authorization

`brain/contracts.py` defines immutable actor, decision and evidence records. An actor contains the server-resolved user ID and tenant. An authorization decision is `allow`, `deny` or `unknown`, with check time, method and policy version. Unknown is never permission.

Evidence retains `evidence_id`, `resource_id`, `version`, `source`, `title`, `locator`, original `text`, `source_updated_at`, `indexed_at` and a backend-mapped `source_url`. A versioned locator identifies the source window; it is not a model-created citation. Current source access and content consistency must still be checked when the evidence is used.

Source adapters expose capability, listing, fetching, read-check and source-link operations. A collector's ability to fetch content is distinct from the requesting actor's permission. Saved answers and previews preserve this distinction.

## Audit v1 event

The audit chain uses these event fields:

```text
schema_version, seq, previous_hash, event_type, actor,
request_id, timestamp, payload, hash
```

`schema_version` is integer 1. `seq` starts at 1 and is contiguous; booleans are not valid integer substitutes. The first `previous_hash` is 64 zero characters, and subsequent values match the preceding event hash.

Canonical JSON is produced with `sort_keys=True`, `ensure_ascii=False`, and `separators=(',', ':')`. The hash is:

```text
SHA256(b"ContextLedger.audit.v1\0" + canonical(event_without_hash).encode("utf-8"))
```

The `\0` denotes a NUL byte in the domain separator. Producer: `brain/audit.py`; independent verifier: `tools/audit_verifier/chain.py`.

## Signed checkpoint

The checkpoint includes `schema_version`, `stream_id`, `through_seq`, `head_hash` and `timestamp`. The Ed25519 signature covers the canonical UTF-8 checkpoint. The wrapper identifies the algorithm and contains the checkpoint and base64 signature.

The verifier accepts a checkpoint and public key from separately trusted inputs. Its expected stream ID is an external parameter; audit v1 events themselves contain no stream ID. Covered event hashes must reproduce the signed head. A suffix after `through_seq` is reported as an unanchored tail.

| CLI exit code | Meaning |
|---|---|
| 0 | Signature-covered segment verifies; any unanchored tail is reported separately. |
| 1 | Verification fails, including invalid signature, key, schema, chain or covered data. |
| 2 | No checkpoint supplied: local chain only, explicitly untrusted. |

Unanchored-tail truncation, a stale or rolled-back trust anchor, and full compromise of the signing account require external operational controls. Canonical-content verification does not detect a different serialization of identical parsed JSON.
