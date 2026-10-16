# Validation scope

Verification distinguishes local implementation checks, native source observations, model behavior and human review. Test counts are not answer-accuracy scores.

## Reproducible checks

The application baseline before repository preparation passed **806 Python tests** and **15 standalone frontend suites** in a clean source extraction on 16 October 2026. The full Python suite includes the frontend HTTP lifecycle wrapper. The prepared tree also passed all 806 Python tests (58.544 seconds) and all 15 standalone frontend suites after the repository dependencies were relocated. No test methods were removed.

The repository contains all existing test methods. Historical parser counterexamples needed by regression tests are kept as small hashed fixtures under `tests/fixtures/source_review/`; an old admission-gate implementation needed by two tests lives under `tests/support/`. These are test inputs, not claims that old runs certify the current release. New results are generated locally and are not committed as raw log directories.

Use the [quick-start commands](QUICKSTART.md) to rerun Python checks or the offline five-scenario rehearsal. The signature component has a separate twenty-test suite under `tests/codebuddy/`.

## What the evidence establishes

| Evidence | Scope and limits |
|---|---|
| Python tests and loopback HTTP integration | Local contracts, access failures, source/version handling, budget controls, saved-answer behavior and audit logic using synthetic data and mocks. |
| Standalone frontend tests | Rendering and interaction logic, including scoped gaps, quote controls and stale-response handling. They do not replace a browser/user study. |
| Native four-source observations | Real read-only API integrations and scoped identity/access checks against approved synthetic containers. Coverage is version and case specific. |
| Hosted browser observation | Introduction, an authenticated workspace and reauthorization when reopening a saved answer. Reopening history is not a fresh model generation. |
| Live model observations | Supported examples and documented failures exist. Full semantic acceptance has not passed, and unrun cases remain unverified. |
| Signed audit rehearsal | Hash-chain/checkpoint behavior against controlled modifications; not independent production custody. |

## Remaining limitations

A model review can miss unsupported qualifications or accept an incorrect coverage assessment. It can also reject an answer that might be useful. In an additional isolated-quotation experiment, a known positive/negative diagnostic pair behaved as expected, but the later full acceptance run stopped on the first question after a claim rejection; the other ten questions were not run. That experimental gate is off in the hosted demonstration. No general semantic pass rate is claimed.

The native employee permission matrix, independent audit custody, long-term token refresh behavior, a stable freshness/latency SLA, and broad prompt-injection resistance are not fully established. Existing SQLite `ResourceWarning` messages were observed in the baseline suite despite its successful exit; passing tests do not certify leak-free operation.

No customer adoption, measured time savings or ROI study was completed. A useful next evaluation would compare task completion time and correct decisions against manual cross-tool lookup, while counting unsupported answers, abstentions and cost. These are evaluation measures, not delivered business results.

Public operation remains dependent on the host computer, approved allowance and daily price readiness. [Security and deployment limits](SECURITY.md) apply.
