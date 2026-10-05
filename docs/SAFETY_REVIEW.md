# Team safety review and submission checks

G0/G1/G2 are internal team decision gates, not competition grades. This checklist does not grant approval or mark a review complete.

## Safety demonstration (G1) — not_run

The developer operates the prepared application; a team member watches and records the result. No coding or repeated credential entry is required from the reviewer. Use synthetic competition data only. Keep credentials, OAuth URLs and one-time entry links out of recordings.

| Demonstration | What the reviewer should see | Current evidence and remaining work |
|---|---|---|
| Cross-source engineering and product questions | Cause, withdrawn hypothesis, open follow-up and current runbook have correct evidence; pilot approval is not confused with general availability | Local S-01 subset and live question subsets exist; native eng_b engineering/product fact subsets verified; independent personas and team quality review pending |
| Content update | New source revision becomes searchable; old revision is unavailable; no false claim of freshness during failed refresh | Four-source local lifecycle matrix and native Confluence update/restore exist; complete native update/timing matrix pending |
| Restricted material | Unprivileged user gets no restricted text, title, path or existence confirmation; an allowed question still works | Fixture identity matrix exists; full live persona matrix pending |
| Same-session revocation | After source access removal, old citation, mixed history and export are unavailable; unrelated allowed material stays usable | Native Slack synthesis subset verified, original membership restored; complete live matrix pending |
| Audit reconstruction and integrity | Authorized auditor can reconstruct question, decisions, evidence and response; covered tampering is detected and unsigned/uncovered tails are identified honestly | Local chain/signature tests and offline actual-live audit replay exist; native auditor, independent key custody and production DB role isolation remain incomplete |

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
