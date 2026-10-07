# Read-only sub-agent review · R3A/R4 local candidate

Reviewer: actual sub-agent `/root/r3a_r4_readonly_review`; primary agent records its delivered findings below. Read-only scope: repository code/documents, offline in-memory/temporary tests, existing local verifier. No credential reads, external API, source writes or operator process changes. This is agent code review, not team G1 observation or a human-independent audit.

## Initial review: dfa40c32d514bf4a1466b5af1caae8192a294334

No reproducible blocking code defect found. Actual independent execution: six `test_synthetic_provenance` methods and four offline `test_model_stages` methods passed (10 methods). HTTP method excluded from this review scope; the later primary clean archive executes it.

- `brain/synthetic_provenance.py:15–33`, `brain/retrieval.py:60–65`: approved ID, active resource, strict integer version, original full-text marker, canonical exact slice and metadata checked. Unapproved IDs, versions/text/locator tampering and illegal windows denied.
- `brain/deepseek.py:171–180`, `brain/engine.py:95–123`, `brain/synthesis.py:83–90`: no dict/client synthetic assertion accepted; trusted server provenance after authorization, review reauthorization and provenance recheck maintained.
- `brain/deepseek.py:121–167`, `brain/server.py:128–130`, `web/app.js:64–77`: prepared input, intent, attempt, validated usage, accepted/rejected output, stored answer and HTTP delivery attempt separated. Timeout retains pending budget. Effective usage is not an accepted answer; attempt does not prove vendor delivery or human receipt.
- `brain/audit.py`: event enum additions only; historical bytes unchanged. ADR-040 independent questions/history rejection maintained. Review safety assertions not removed or weakened.
- ZIP six original files independently byte-compared with extracted review files: all equal. Evidence correctly labels MOCK/native subset/real model not_run.

P2 delivery finding: new R4 lifecycle logs lacked a fixed snapshot/checkpoint/coverage/verifier binding required by the takeover prompt. Older audit-mixed logs cannot replace it. Primary disposition: accepted and closed using this directory's six new snapshots, checkpoints and actual verifier output; existing CodeBuddy tool preserved.

Nonblocking suggestion: direct observer/audit failure injection at each lifecycle stage is not newly covered. No reproduced defect; existing code appears fail closed. This optional expansion was not added to this bounded candidate task and is not claimed tested.

## Follow-up review: test isolation and new audit evidence

No new blocking finding. Reviewer actually reran the product acceptance module (two methods passed) and all 13 stored verifier commands; exit codes/verdicts matched the raw records. Six snapshot SHA256 values, events equality and runtime source hashes independently checked against current checkout.

- `tests/test_product_acceptance.py:20–43`: mock only exact `.runtime/confluence-product.json`; other file reads delegate to original. Keychain/reader/pilot mocked. Original failure/no-query/decision/no-credential assertions retained; exact account and three native mock reads additionally asserted. No weakened safety assertion.
- `capture.py`: current MOCK transport, disposable ledger/store and temporary signer only; no real source/model. Existing output refuses rerun. Private key deleted.
- Six full snapshots `anchored_valid`; body/middle/covered-tail/recomputed-chain rejected. Prefix tail explicitly unanchored. Old checkpoint + corresponding truncated snapshot accepted; truncated snapshot against separately retained newer anchor rejected. No automatic freshness or independent custody claimed.
- Initial failed archive evidence remains failed. Audit capture binds dfa40c3 runtime hashes accurately.

Primary completion after follow-up: fixed test commit `34281adfe22c839ed463a51cb3536255f47175b4` clean archive passed setup/352 regressions/five fixture scenarios/two Node checks/local HTTP smoke. `preservation.json` confirms audit runtime hashes equal that archive; test-only commit did not change runtime. Reviewer did not independently rerun full archive, native API, paid model, browser visual inspection or G1/G2.
