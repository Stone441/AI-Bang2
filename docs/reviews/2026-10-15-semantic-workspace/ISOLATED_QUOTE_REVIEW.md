# Isolated quote entailment candidate

## Evidence and decision

The latest real negative gate (quote-scope-gate-live-results.json) accepted a provenance claim whose selected quote contained only the two follow-up identifiers. Explicit prompt instructions did not prevent using uncited full-source context. This candidate changes what each review call can see, not merely the wording of that instruction.

`DeepSeekIsolatedSectionedModel` is an explicit opt-in backend (`--answer-style isolated-sectioned-synthesis`, `--source-review-dispatch legacy`). Existing default paths and the running human trial remain unchanged. No new live/model call or grant was created for this implementation.

## Input and acceptance contract

1. Generate the same compact sectioned answer; keep existing strict parsing, exact quote and identifier checks.
2. For **each factual claim independently**, recheck current authorization, then send only its claim text and selected quote strings to `IsolatedQuoteReview`. Do not serialize the question, resource IDs, titles, locators, full source, other claims or their quotations. The union of that claim's quotations may support genuine cross-source synthesis. No keyword-based entailment substitute is used.
3. Require the exact boolean JSON object `{"quote_supported":true}`. False, missing/unknown fields, strings, duplicate fields, transport failure or unknown usage stop the draft. No claim is dropped and no retry occurs.
4. Recheck authorization again and run the existing full-source `SectionedAnswerReview`, retaining all original evidence, parts, gap claims, premise, conflict, completeness and responsiveness checks. Quote-only acceptance cannot hide an omitted pilot limitation or replace whole-source review.
5. The engine requires one distinct settled/accepted same-request receipt for every quote review, separate from generation and full-source review. Preserve those receipts in audit, response/history and the usage UI. No reviewed draft is released until every stage and the final native authorization check passes.

Passing `evidence` to the shared transport wrapper is necessary for the existing synthetic/current-provenance validation; the quote review's `messages()` serializes only claim+quotes. Tests inspect the actual message body, not merely a claimed mode. Each REST request is independent; no previous generation or review conversation is included.

## Cost and latency tradeoff

For N factual claims (0–4), the candidate uses **N+2 sequential calls**: generation, N quote reviews, whole-source review. Empty factual claims still need full-source coverage review. Thus each question uses2–6 calls;11 questions may require22–66 calls, before any calibration probes. More current-permission checks also add latency. No empirical latency estimate is asserted.

The earlier24-call scope cannot guarantee a complete11-question run for this architecture. Do not silently reuse, expand or restart a closed grant. A future live plan must separately bound calibration and the full suite using this actual call structure. The running user preview is not switched to a higher-call implementation.

Rollback is selecting the existing `sectioned-synthesis` backend and its immutable release. Retain added audit and ledger events; do not erase records or claim that rollback removes the known old review weakness. Existing UI ignores extra receipt fields when absent.

## Verification and limits

Eight focused fixture/mock tests cover input isolation; exact typed verdicts; per-review authorization; all receipts distinct; rejection of missing/reused receipts; immediate stop and no draft after negative quote review; full-source rejection even when all isolated quotes pass; and the zero-claim path. The UI test verifies all review costs remain visible. Initial focused tests exposed the engine's exact model-class allowlist; the new class was explicitly added without broadening it to arbitrary subclasses, then tests passed.

Full regression:798 Python tests passed in55.804s; node tests/frontend_operator_security.js passed, including all extra receipt display. Results are recorded in isolated-quote-full-regression.log. These checks prove payload boundaries and orchestration, **not real model entailment accuracy**. An isolated model may still approve an unsupported claim from learned associations; the next decisive experiment must test the known short quote, a sufficiently quoted positive, then broader unseen counterexamples before declaring improvement. Same-model agreement is not independent human acceptance.

The original11-question truth, current-source checks and goal scope remain unchanged. Current goal is incomplete; no claim of real quality improvement, latest human delivery or complete acceptance is made.
