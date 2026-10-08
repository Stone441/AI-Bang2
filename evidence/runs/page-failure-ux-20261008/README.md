# Actual page failure repair and runtime UX — 2026-10-08

Base main `23ae62b`; branch `fix/page-failure-ux-20261008`. Historical application baseline `cdbd62b`. This directory retains failures and later results; it is not a claim of full acceptance.

## Evidence and outcomes

| Layer | Record | Actual result |
|---|---|---|
| Original two failures | ../targeted-closeout-20261008/page-trial-final.json and request failure records | Both failed. Original generation finish_reason/raw response were never saved and cannot be recovered. Drive native version changed despite unchanged body hash/modifiedTime; actual cause unknown. |
| Initial current-path diagnostic batch | http-original-six/, baseline-summary.json | Six submissions retained: review rejection, stale source snapshot, four429 submissions. Not successful trial. |
| Fixed original native questions, each three times | http-fixed-six/ including fixed schedule and progress | Q1: exact quote rejection (stop), review rejection (stop), scoped incomplete response. Q2: all three grounded answers distinguish completed fix, preventive work and release approval. No selection of only successful records. |
| Startup race | http-fixed-six-startup-race/, corresponding log | Failed runner startup retained; no business/model call. |
| Actual progress | http-fixed-six/progress records | 607 samples; max read about0.00524s during running query. Server stages, no guessed progress and no four-source calls per poll. |
| Actual current citations and History | http-followup.json | Three native previews200 and History200; HTTP only, no human/browser observation. |
| Original quality cases | quality36/verification.json and case/answer/audit files | Core24:22 fact answers+2 appropriate empty. Known12 first6:3 complete/scoped,3 safe insufficient/clarification; remaining6 not_run at attempt ceiling. Source fixtures/live unchanged model, not native HTTP equivalence. |
| Semantic examination | semantic-review.json | Main-agent examination, not blind or human acceptance. Support classification retrospective over captured pre-request source publication; not a pre-frozen oracle. Wide mitigation question remains partial. |
| Full local suite | delivery-regression-2.log | 436 tests OK. Prior delivery-regression.log failed old health-lock trigger; now History still exercises and asserts original publish lock order. Earlier logs and first implementation failures retained. Terminal product_acceptance status failed is deliberate negative-test stdout, not unittest suite status. |
| Frontend | frontend-runtime.log, frontend-security.log, frontend-audit.log | All pass, including immediate elapsed time, duplicates, stale responses, logout in-flight polling, History/navigation/expiry and error preservation. VM DOM checks, not visual human acceptance. |
| Synthetic five scenarios | five-fixture/ | Five local subset passes, fake sources/model. |
| Final loaded bytes | final-startup-readonly.json | Restarted final approved49161 instance: health/static200, query_calls0. Native question batch preceded subsequent conservative guard/UX corrections; local coverage for those deltas, no silent paid rerun. |

## Implementation boundaries

ADR062 permits only one recovery for an explicit version change before any model invocation. It rereads and checks current identity, container, native mapping, download capability/deletion/body as applicable, then atomically publishes the existing object and reretrieves. It does not wait for a publisher holding its lock, reuse old allow, rewrite evidence/audit, retry denial/unknown/429/network, or regenerate after model invocation. Same-body version advance, real body change, revocation, continuous changes and model-after changes have local regression coverage. No native source writes were authorized or performed here.

Google Drive's native `version` covers server changes, including changes invisible to readers; body hash is not a substitute. `headRevisionId` and current-user `canDownload` have different meanings. Official reference: https://developers.google.com/workspace/drive/api/reference/rest/v3/files . Native version is still enforced.

Generic subject filtering and already-authorized relation expansion reduce unrelated generic-status matches. No probe object removal or question-specific hardcoding. Missing global latest approval/time remains a data/ambiguity boundary, not runtime success.

Diagnostics allowlist finish_reason, returned model, hashed bounded response identifier, usage/reasoning token counts, visible output length and validation category. No upstream response, reasoning text, keys or full one-time links in public records. Failed review's previously validated synthetic claims are controlled private0600 diagnostics in .runtime, not a product draft. Reservation on missing receipt stays unknown; known usage settles even when output is rejected.

## Authorization, budget and continuation

AUTH029: only local49161/eng_b, AUTH017 four synthetic containers read-only, unchanged DeepSeek low8192/provider, original USD20 ledger. Maximum42 questions and USD0.50 settled increment/new-unknown admission stop. Conservative count includes four429 HTTP submissions. Total42 reached; pending request to extend total to48 is not approval. Resume only known12 cases07–12 if explicitly approved, preserve original not_run record and write supplemental results. Do not rerun all charged tests for UI/docs.

Settled increment144751microUSD (USD0.144751), global settled916664/available18758932; original unknown324404 remains, no new unknown. Admission persists across restart and shares process lock with quality runner. Live instance is loaded, but new questions pause at the cap. Old8094/8100 untouched; no push/merge/deploy, browser-denial bypass, G1/G2 approval or AUTH019 expansion.

Remaining: broad mitigation question quality and/or agreed approval scope; last6 quality cases; team browser observation and actual UX perception. This goal is not complete. Read docs/STATUS.md and RUNBOOK.md current entries before continuing. Authorize no new scope by inference from old AUTH026/027/028.

## AUTH030 supplement

User approved total48 solely for remaining six. All six results saved in quality-remaining6/, model/source/config unchanged. Combined semantic examination: quality-combined-review.json. Cases07/09/11 clarify,08 limited insufficient evidence,10 partial table relevance,12 expected premodel Drive-unknown stop. No fabricated retry value, but not all task answers complete. New supplement costUSD0.021044; goal totalUSD0.165795. Old unknown324404 unchanged, no newunknown. Admission48/48 reached; no further question authorization. Historical not_run retained rather than overwritten. No product-code change or repeated paid suite.

## AUTH031 actual v11 run — 2026-10-09

2026-10-09 AUTH031实际复验完成（native6＋quality36，尚余3真人题）：v11/同provider低推理8192，四源合成只读、正常后台。Q2三次均事实完整；Q1两次覆盖不足答案（仍漏C01已批准操作）＋一次review拒绝，不称首题修复完成。原24=21事实＋2合理空＋business31一次review拒绝；known12=01/06完整＋8合理空/澄清＋02一次review拒绝＋12预期Drive unknown停答。三review拒绝均stop、额外claim responsive=false，已知usage结算，无自动重试/新增unknown，不能推断cap不足。610进度采样最长0.003752秒；三本轮引用preview与History HTTP200，非人验。今日官方峰值费率真实核查不变，PRICE_DATE改9；436完整本地回归通过。账本settled1075716/available18599880、原unknown324404保持；AUTH031增138008microUSD、Goal累计303803microUSD。额度90/93，剩余3专供真人。49161新human实例已加载v11，私有0600 token，不记录完整一次性链接；后台正常运行。v11候选质量未通过，不推广为稳定候选；G1/G2/browser工具拒绝/AUTH019不变。两次入口helper启动失败无凭据/模型调用，原件保留；8094/8100未动，未push/merge/deploy。证据v11-final-review.json、v11-native-six/、v11-quality36/、human-entry-ready.json。
