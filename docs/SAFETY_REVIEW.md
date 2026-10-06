# Team safety review and submission checks

2026-10-06 integrated worktree: R5 source preview links, question/time history and collapsed diagnostics have local DOM/HTTP evidence. R3 frozen variants evaluate final claims/supports/omissions separately from evidence recall; long-event review/relevance failures remain explicitly unresolved until actual recheck. Current source/commit/mode and browser permission are recorded in STATUS and ACCEPTANCE_STATUS. R3A/R4 team viewing is not a prerequisite for other local development.

G0/G1/G2 are internal team decision gates, not competition grades. This checklist does not grant approval or mark a review complete.

## Safety demonstration (G1) — not_run

The developer operates the prepared application; a team member watches and records the result. No coding or repeated credential entry is required from the reviewer. Use synthetic competition data only. Keep credentials, OAuth URLs and one-time entry links out of recordings.

| Demonstration | What the reviewer should see | Current evidence and remaining work |
|---|---|---|
| Cross-source engineering and product questions | Cause, withdrawn hypothesis, open follow-up and current runbook have correct evidence; pilot approval is not confused with general availability | Local S-01 subset and live question subsets exist; native eng_b engineering/product fact subsets verified; independent personas and team quality review pending |
| Content update | New source revision becomes searchable; old revision is unavailable; no false claim of freshness during failed refresh | Four-source local lifecycle matrix, native Confluence update/restore and Jira KAN-6 text update exist; native Slack/Drive updates and timing matrix pending |
| Restricted material | Unprivileged user gets no restricted text, title, path or existence confirmation; an allowed question still works | Native owner-only C-03 denied to eng_b and C-02 allowed, stale synthetic index/query/model evidence/preview checks passed; full live persona/timing matrix pending |
| Same-session revocation | After source access removal, old citation and dependent history are unavailable; ordinary answer export remains absent (ADR-040); unrelated allowed material stays usable | Native Slack synthesis subset verified, original membership restored; complete live matrix pending |
| Audit reconstruction and integrity | Authorized auditor can reconstruct question, decisions, evidence and response; covered tampering is detected and unsigned/uncovered tails are identified honestly | Mixed fixture success/partial/denied/failed requests: 116 expected events across 17 pages, late request excluded, role/scope denied, signed-copy tampering detected. Actual-live replay is separate; native auditor, independent custody and production DB role isolation remain incomplete |

Before external access, additionally confirm the entry point exposes no source administration, secrets are absent from Git/recordings, access is limited to the approved audience, and limitations are stated accurately. The current service is loopback-only; this checklist does not authorize deployment.

Record reviewer, date, exact commit, mode, evidence paths, observed pass/fail/not_run and unresolved issues in a new evidence record. Never infer human approval from automated test results or general trust.

## Final submission confirmation (G2) — not_run

The team reviews the finished candidate, playable video, actual measured results, remaining limitations, real CodeBuddy/WorkBuddy contribution records, and evaluator access instructions. Publishing materials or submitting the competition entry requires explicit final approval. No submission has been performed by this checklist.

## Reproduce local checks

```sh
make setup
make verify
make verify-lifecycle
node tests/frontend_operator_security.js
```

`verify` covers five local worked examples. `verify-lifecycle` records twelve isolated cases: content update, ACL revocation and deletion for each of four fixture sources. It leaves the index deliberately stale first and checks answer evidence, model evidence input, old history/export projection and citation access before applying an object-scoped event. It then checks new revision availability or removal, event replay, unchanged unrelated data and audit-chain integrity.

These commands use fake sources and a fake model. They do not validate native platform ACL propagation, background webhooks, real model quality, or a human review. Lifecycle history checks exercise the shared backend export projection; HTTP/browser export behavior has separate evidence. The first lifecycle probe incorrectly searched the user question as well as evidence for a test marker; that diagnostic failure is preserved, and the corrected check inspects model evidence only.

Current five-scene candidate and precise remaining prerequisites: `DEMO_CANDIDATE.md`. Native product questions and offline audit reconstruction are preparation evidence, not completed team observation.

## One consolidated team walkthrough — prepared, not_run

Use a single short review session. The developer presents the application and evidence; the reviewer records only observed results. The fixture identity switcher is a labeled simulation, not production identity or native SSO. Keep the existing 8094 service running; no credential re-entry is needed to review stored evidence.

| Order | Developer presents | Reviewer checks | Evidence to compare |
|---|---|---|---|
| 1 | Existing engineering and product answers, their quoted support and source versions | Incident cause/withdrawn hypothesis/open follow-up; pilot approval must not become GA or an invented date | `evidence/runs/live-s01` and `live-product`; exact native eng_b identity, not the product_ops ACL persona |
| 2 | Recorded native update/restore and disposable-file deletion, then fixture lifecycle results | Updated evidence is current; old versions/deleted content are unavailable; no background-sync SLA claim | `live-lifecycle` and `lifecycle-local` |
| 3 | Native restricted seed and the negative/positive query pair | No C-03 title/path/canary in the negative answer/model evidence; C-02 still works; stale index stays present | `native-restricted-fixed`; owner screenshot is private and must not be uploaded automatically |
| 4 | Recorded same-session native Slack revocation, denied old preview/history/export and restored member | Revoked mixed answers unavailable; unrelated answers remain usable; legitimate earlier downloads cannot be withdrawn | `synthesis-native-revocation` |
| 5 | Mixed audit oracle, paginated inquiry and verifier output | All four outcomes reconstructed; 116 event IDs match; failed query has no committed answer; audit roles/scopes restricted; unsigned-tail boundary stated | `audit-mixed` plus `audit-replay` for uncovered-tail/whole-chain cases |

Replay the mixed audit without API credentials, native writes or model costs:

```sh
make verify-audit-mixed AUDIT_OUTPUT=.runtime/team-review-01
```

Choose a new directory for every run; existing evidence is deliberately refused. `oracle.json` contains the four actual request IDs and the developer-captured expected event IDs. `inquiry.json` is the actual inquiry result. `verification.json` describes real execution, signatures and limitations. These files do not record team approval.

Create a separate observation record only when the team actually watches. Record reviewer/date/candidate commit and, for each scene, observed pass/fail/not_run, demonstration mode and open issue. A historical log review does not become a newly witnessed native revocation. G1 external opening requires the approved audience and unresolved safety risks to be assessed separately; no public deployment is included here.
