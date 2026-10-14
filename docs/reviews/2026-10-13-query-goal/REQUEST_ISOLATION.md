# Request isolation candidate · ADR096 · 2026-10-13

Status: local validated, live not_run. Default remains serial; explicit trial launcher option `--query-concurrency isolated3` enables the candidate. Existing running structured-v2 was not restarted or replaced. Frozen manifests and PLAN.json are unchanged.

## Behavior and boundaries

Each admitted query builds a fresh Engine and request-local delegated authority, catalog, reader mappings and eligibility snapshot. It never inherits native allow decisions. The same original store, audit and durable budget remain authoritative. Three request scopes may overlap native/model I/O; the scope includes HTTP delivery, with server session identity, CSRF and same-session 409 preserved.

Root publication epochs reject disable/restore ABA. Current source coverage, stored content and version are revalidated around native reads. Model dispatch retains the publication/store fence through persisted dispatch audit and releases it at the transport boundary. Final authorization retains this fence through response delivery. Existing single pre-model version recovery remains; no paid automatic retry is added. Discovery raw SQLite reads now respect the store lock, with authority-before-store lock order.

The short-lock AUTH036 admission gate is wired only for isolated3. An owning-process lease, per-request reservation ownership, original budget transactions and unknown handling remain intact. This does not imply that three actual model calls fit the current allowance.

## Important integration finding

Initial three-session HTTP test returned 503 for all requests: the first mock call waited at a barrier while other reservations correctly failed the goal cap. DeepSeek currently reserves the entire 1,048,576-token context plus output for each call, more than USD0.30. Multiple simultaneous reservations therefore cannot fit AUTH036 USD0.50. The initial failure is preserved in isolated-http-initial.log.

Tests now separately prove HTTP overlap with the original USD20 mock ledger and AUTH036 rejection of a second full-context reservation while the first completes. No allowance, conservative reservation, or valid assertion was weakened. This is an unresolved constraint for actual concurrent trial use. Before live enablement, implement safe model-stage scheduling or prove a smaller enforceable reservation bound; do not increase authorization silently.

## Evidence

- isolated-integration.log: 12 local mock/loopback tests, 2.223s, pass.
- isolated-full-regression.log: 630 tests, 29.109s, pass. Existing ResourceWarnings and a mock runner's printed failed JSON are retained; unittest result is OK.
- isolated-version-recovery.log: 10 request-isolation tests, including two added after the full suite, 0.132s, pass. Native version recovery before the sole mock call and unhealthy coverage after the call verified; no new runtime edits after full suite.
- Covered: three independent HTTP sessions, per-session result/progress, duplicate 409, client identity override, budget rejection, final publication fence, ABA, new candidates, native revocation, construction-time changes, legacy review stages, empty evidence, source failure and recovery.
- All sources and model I/O in these tests are mocks. No browser evidence, native API performance evidence, provider billing, or G1/G2 acceptance is claimed.

AUTH036 remains 43 actual calls / USD0.056704 incremental settlement / new unknown 0, with original two unknown reservations retained. This turn made no paid/native calls. Earlier native structured-v2 results remain 0/12 at full-answer 3 seconds; this candidate has no native speed claim.

## Rollback and next work

Use default serial and do not attach IsolatedQueries; the running v2 is already unchanged. No schema migration or data reset is needed. Code publication epochs are process-local concurrency guards, not external permission proofs. History and preview retain original fresh authorization paths.

Next resolve budget-aware model scheduling without waiting while holding publication locks, then inspect source-stage latency for further proven-equivalent reductions. Freeze a new candidate and a bounded remaining-call allocation before any paid validation. The original final native allocation is exhausted; do not reuse its manifest or relabel prior evidence. Browser tool's earlier ERR_BLOCKED_BY_CLIENT remains unresolved and must not be bypassed.
