# Demonstration candidate and remaining acceptance

2026-10-05. Local-only candidate; this document is not G1/G2 approval, a production claim or a submission.

## Five-scene coverage

| Scene | Prepared evidence | What can currently be claimed | Remaining before complete acceptance |
|---|---|---|---|
| S-01 Cross-source answer | `evidence/runs/live-s01`, `evidence/runs/live-product`, local five-scene replay | Native eng_b engineering and product questions use four source inputs, live DeepSeek and exact quotes; product answer distinguishes pilot/GA, Done/release and unconfirmed date | Original eng_a/product_ops independent ACL personas and team semantic review. Current eng_b can access incident data; do not present it as product_ops isolation |
| S-02 Updated content | `evidence/runs/live-lifecycle`, `evidence/runs/lifecycle-local` | Native Confluence version 1→2→3 update/restore verified with readonly operator/fake model; four fixture sources independently update without whole-store rebuild | Native Jira/Slack/Drive content-update timing, live model/browser updated answer, enough samples for any p95 claim. Source refresh is query-triggered, not background webhooks |
| S-03 Restricted information | `evidence/runs/local-latest/scenarios.json`, permission/security regression | Fixture contractor denial preserves existence boundary and an allowed query works; unknown/native source checks have separate mock/native subsets | Native restricted seed plus independent restricted reader and allowed control. A nonsense no-evidence query does not substitute for this scenario |
| S-04 Revocation | `evidence/runs/synthesis-native-revocation`, source revocation records, `evidence/runs/live-lifecycle` | Native private Slack removal protects same-session synthesis citation/history/export, member restored; CF/Jira/Drive reader revocation subsets and disposable Drive trash protection exist | Exact original persona/full per-platform ACL and child-resource matrix, in-flight propagation boundaries and team observation. Legitimate past downloads cannot be withdrawn |
| S-05 Audit | `evidence/runs/audit-replay`, CodeBuddy verifier records, local five-scene replay | Offline reconstruction of actual synthetic live queries has exact pagination and normal-reader denial; local signatures detect covered tampering, unsigned-tail deletion remains outside protection | Native auditor authentication, independent key custody/DB role isolation, full mixed-outcome oracle and team observation. Offline test auditor is explicitly a test identity |

The live product harness had a stale `fake_model` response-mode suffix despite actual DeepSeek calls; original records are unchanged and the discrepancy is documented beside them. Current runner fixes future labels. Do not silently relabel old signed/hashed audit records.

## Review preparation

For the local deterministic walkthrough:

```sh
make setup
make test
make verify
make verify-lifecycle
make demo
```

Use only the explicitly labeled fixture demo for switching test identities. The approved native operator uses the existing Keychain mapping and `make live-synthesis LIVE_PORT=8094`; an existing process need not be restarted for document review. If loading a new candidate, restart it normally and open its new one-time entry link privately; never record credentials or entry tickets.

The live product runner requires `--live`, uses the original approved budget DB, and refuses to overwrite existing evidence. Running it makes real paid model calls within the existing ceiling, so it is not part of `make test` or demo startup. Audit replay uses copies and disposable local signing keys, without platform/model calls.

Team review: follow `SAFETY_REVIEW.md`, record exact commit/mode, observe outputs and mark each limitation. G1 concerns approved external access after safety observation; G2 concerns final material/submission approval. Neither has been completed by this evidence preparation.

## Next dependency order

1. Close candidate reproducibility and the remaining automatic safety/quality failures; keep the five-scene matrix current.
2. Prepare native independent-persona acceptance only with existing reviewed accounts/grants, or obtain the specific missing authorization. Do not fabricate product_ops from an engineering identity.
3. Run remaining authorized native update/negative-permission cases and organize one consolidated team review.
4. Assemble the validated demo recording and final material candidate; publishing/submission awaits G2.

Retrieval improvements remain DEV-08, evaluated against these delivery requirements. Adding vectors/reranking is conditional on a demonstrated gap and approved resources, not a prerequisite to every next task.
