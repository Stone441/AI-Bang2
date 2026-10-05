# Independent product reader native subset

2026-10-06 Singapore; raw UTC timestamps retained. Command: `python3 -m scripts.native_product_acceptance --live --output evidence/runs/native-product-reader`.

16 native API/fake model checks passed. Reused only AUTH-016 app-owned product_ops Confluence Keychain item; current native account verified. C-01/98564 and C-03/557057 denied (no body requests), C-02/164283 allowed. Positive evidence preserves pilot-only/not GA/no release date. Negative query has no claims/evidence or restricted title/ID/canary; denied controlled stale synthetic index remains stored and preview denied. Stale text is known synthetic owner text, not product historical ingestion. Full unsigned audit and model inputs retained.

Browser 8100: server actor product_ops, C-02 answer/preview/history actually observed; independent security query empty/refused. An initial follow-up security query supplemented the previous authorized C-02 evidence; no restricted information appeared. Added explicit New question action to clear follow-up dependency and stale views without refreshing/session reset; browser-verification.json records actual positive→New question→empty security answer checks. This is not live model quality or complete four-source persona/G1/G2 acceptance.

Local tests: 309 Python fixture/mock tests passed in 14.681s (`full-tests.log`), two harness tests passed (`harness-tests.log`), frontend security/race checks passed (`frontend-tests.log`). Initial harness test had a mock SimpleNamespace instead of dataclass Decision, so asdict failed before native decision assertion (2 tests, 1 error). Corrected mock to actual Decision contract; no assertion removed. This paragraph records the observed failure summary, not an original failure log.

Private screenshots: `evidence/tool-usage/private/product-reader-20261006/product-preview.png`, `product-denial.png`; kept ignored, no credentials or entry tickets. Evidence is tied to source hashes in verification.json; recorded base commit precedes the uncommitted new harness. No source writes, paid model calls, independent audit custody, native auditor, contractor or product Jira/Slack/Drive validation.

Post-validation cleanup removed trailing whitespace only from the harness. The recorded run hash identifies the executed pre-cleanup source; behavior unchanged.
