# Demonstration candidate and remaining acceptance

2026-10-06 integrated candidate now supersedes the earlier R3A/R4-only handoff: fixed application/test **331bd28**, clean archive **357 regressions**, five fixture scenes, two Node checks and local HTTP passed. R2 current native read-only discovery subset, R3 fixture-source true model failures/fixes and R5 existing UX are [bound by mode and source hash here](../evidence/runs/review-integrated-20261006/README.md). **Overall in_progress**: long/relevance quality disposition and browser tool site permission remain unresolved; G1/G2 not_run. Earlier historical native/model/browser records remain valid within their original modes, not proof of this new runtime.

2026-10-06 current R3A/R4 local candidate: fixed application/test commit `34281adfe22c839ed463a51cb3536255f47175b4`, branch `fix/r3a-r4-team-candidate`. Clean archive: 352 regressions, five fixture scenes, both Node checks and local HTTP smoke passed; six current mock lifecycle audit snapshots and 13 signature/rollback checks bound to exact runtime hashes, actual read-only sub-agent review closed. [Candidate handoff and limits](../evidence/runs/review-r3a-r4-candidate-20261006/README.md). New-build native/browser visual/live model and G1/G2 remain **not_run**. Historical evidence below keeps its original versions/modes; old 8100 independent-question evidence remains valid. Do not treat prior feature/download descriptions as current ADR-040 behavior.

2026-10-05. Local-only candidate; this document is not G1/G2 approval, a production claim or a submission.

## Five-scene coverage

| Scene | Prepared evidence | What can currently be claimed | Remaining before complete acceptance |
|---|---|---|---|
| S-01 Cross-source answer | `evidence/runs/live-s01`, `evidence/runs/live-product`, local five-scene replay | Native eng_b engineering and product questions use four source inputs, live DeepSeek and exact quotes; product answer distinguishes pilot/GA, Done/release and unconfirmed date | Original eng_a/product_ops independent ACL personas and team semantic review. Current eng_b can access incident data; do not present it as product_ops isolation |
| S-02 Updated content | `evidence/runs/live-lifecycle`, `evidence/runs/native-jira-update`, `evidence/runs/lifecycle-local` | Native Confluence update/restore and dedicated Jira KAN-6 text update protect old references/history and refresh new evidence with readonly eng_b/fake model; four fixture sources update without whole-store rebuild | Native Slack/Drive content updates, representative timing samples, live model/browser updated answer, enough samples for any p95 claim. Source refresh is query-triggered, not background webhooks |
| S-03 Restricted information | `evidence/runs/native-restricted-fixed`, fixture permission/security regression | Native owner-only C-03 is denied to existing eng_b; C-02 is allowed. A controlled stale synthetic index is retained while negative query/model evidence and preview exclude C-03; 13 checks pass | Original contractor/full native persona matrix, browser/live-model observation and statistical timing side channels remain not_run. Local stale text is synthetic setup, not historical ingestion proof |
| S-04 Revocation | `evidence/runs/synthesis-native-revocation`, source revocation records, `evidence/runs/live-lifecycle` | Native private Slack removal protects same-session synthesis citation/history/export, member restored; CF/Jira/Drive reader revocation subsets and disposable Drive trash protection exist | Exact original persona/full per-platform ACL and child-resource matrix, in-flight propagation boundaries and team observation. Legitimate past downloads cannot be withdrawn |
| S-05 Audit | `evidence/runs/audit-mixed`, `evidence/runs/audit-replay`, CodeBuddy verifier records | Four fixture outcomes match 116 event IDs over 17 stable pages; failed answers are not committed and audit roles/scopes are denied. Actual-live replay and signature boundary proof are separate | Native auditor authentication, independent key custody/DB role isolation and team observation. Mixed-outcome oracle is developer fixture evidence; offline test auditor is explicitly a test identity |

The live product harness had a stale `fake_model` response-mode suffix despite actual DeepSeek calls; original records are unchanged and the discrepancy is documented beside them. Current runner fixes future labels. Do not silently relabel old signed/hashed audit records.

## Rebuild evidence

Application/test commit `e9a55e6` passed a clean git-archive run: setup, 295 tests, five fixture scenarios, Node security checks and a newly started HTTP demo through login/query/exact citation preview. Evidence: `evidence/runs/rebuild-fixed`. The earlier archive failure is preserved; one test had depended on a leftover database and now uses an independent real temporary DB. Browser visual review remains separate.

Latest audit UI application/test commit `0278bab` also passed clean archive setup, 295 Python tests, fixture scenarios, both frontend Node scripts and HTTP smoke (`evidence/runs/rebuild-audit-ui`). Audit UI now separates process stages and rejects stale inquiry/page responses. Chrome visual inspection was blocked; it remains not_run.

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

Latest restricted-acceptance candidate `b541c02` passed clean archive setup, 297 Python tests, five fixture scenarios, both Node checks and HTTP smoke (`evidence/runs/rebuild-native-restricted-approved`). The earlier sandbox run denied loopback bind; its failed logs remain separate. No platform/model access or operator restart was involved.
