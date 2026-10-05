# Mixed-outcome audit acceptance

2026-10-05, fixture sources/fake models, explicit local test auditor. Actual Engine requests generated success, partial authorization, all-authorizations-denied and a controlled model failure. The expected event IDs were captured at each request boundary, independent of inquiry filtering. 116 events matched over 17 pages. A newly executed request after page one was excluded from the fixed snapshot. Unrelated actor/scope noise was excluded, eng_a/security audit access denied, and the auditor could not expand its scope to security. The failed request has request_failed and no committed/stored answer.

The existing CodeBuddy checkpoint/verifier CLI was actually invoked with a disposable local Ed25519 key: original accepted; content modification, middle deletion and covered-tail deletion rejected. Original export unchanged, private test key deleted. The key is not independently operated; unsigned/uncovered-tail and whole-chain replacement cases remain separately documented in audit-replay. This harness is Codex work using the existing genuine CodeBuddy contribution, not a new CodeBuddy contribution.

Run with a new output directory:

```sh
make verify-audit-mixed AUDIT_OUTPUT=.runtime/audit-review-02
```

Four targeted tests passed, including an intentional omitted-failure-event inquiry that the oracle correctly rejects before signing. That test prints a failed test-run report by design while unittest passes. The first test execution instead failed because mocking subprocess.run also mocked Git revision capture; the original failure log is preserved. The test now explicitly labels revision test-only, keeping the omission and no-signing assertions. Production code was not changed to accommodate the test.

No native platform, real model, credential, existing operator or human approval was used. Team walkthrough is prepared in docs/SAFETY_REVIEW.md; human G1/G2 remains not_run. This does not close native auditor/production DB-role isolation or full-persona acceptance.
