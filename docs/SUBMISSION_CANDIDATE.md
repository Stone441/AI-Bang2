# ContextLedger · submission candidate

2026-10-15 主线集成说明：本轮收尾修复将作为下一轮开发基线合并main，后续继续完善前端、项目亮点、候选题问答与开发细节，不作正式封版。当前业务代码与10cc970一致；冲突题和四源题分别已有真实通过记录，JSON故障根因仍开放，线上仍独立运行f2f0633。[主线合并验证](reviews/2026-10-15-main-closeout-merge/REPORT.md)及[最新真实记录](reviews/2026-10-15-sectioned-live/json-investigation/REPORT.md)优先于下方历史说明。

2026-10-15 当前运行已切换到本地修复代码 `f2f0633`，同一公网入口；最新[真实验收与剩余缺陷](reviews/2026-10-15-closeout-live/REPORT.md)优先于下方历史状态。自动复验10次/USD0.011808，人工额度未占用、旧unknown保留。两项可选分题生成仍失败，不能宣称全部通过；未push/main合并或比赛提交。



Updated 15 October 2026 for the local closeout candidate based on GitHub main `5727300`. This is an unsubmitted candidate. See [current closeout status](reviews/2026-10-15-closeout/REPORT.md). Earlier hosted/native measurements describe older builds; no new-build native acceptance is asserted. [Previous text](reviews/2026-10-14-pd/prior-round8-submission.md) is retained.

## Copy-ready fields

**Project title:** ContextLedger — The Internal Brain

**Short blurb (8 words):** Permission-aware enterprise answers with evidence and audit trails.

**Project description:**

An engineer investigating an incident and a product colleague checking release readiness need answers spread across Confluence, Jira, Slack and Google Drive. ContextLedger brings these sources into one question workspace while preserving evidence, current access checks and an inspectable audit trail. Our prototype uses fictional payment-service material, not Aspire internal data.

The engineering question connects a confirmed incident cause, a withdrawn hypothesis, follow-up work and a runbook. The product question distinguishes completed code from release approval, a controlled pilot from general availability, and an unknown date from a cancelled release. Users can inspect exact source passages and versions. Each question is independent; an earlier answer cannot grant access to later questions.

Python source adapters, a SQLite versioned index and a browser interface form the implementation. Local BM25 and lexical matching retrieve exact source windows, with a bounded bilingual business glossary and authorized source relationships. Server-verified identity and application resource policies narrow candidates; current native access/content checks govern model input and final delivery. Unknown access cannot pass. Saved answers and citation previews are checked again. Shared collection credentials do not represent every employee’s permissions.

The older deployed configuration uses one DeepSeek Flash evidence review and server-reconstructed source passages. The local pd candidate additionally implements an opt-in two-call mode: a draft groups conclusions by subquestion with exact supporting quotations, then a separate review checks support, coverage, insufficiency, material premises and conflicting evidence. Missing or negative review decisions reject the draft. The model cannot invent source URLs or grant permission. These are fallible model checks; the new mode has known live failures in the 15 October baseline trial; the repaired candidate still requires separate live semantic acceptance and it has not replaced the hosted configuration.

Incremental updates and authorization changes remain separate. An isolated, credential-free operator lab makes the sequence visible: read version 1, publish version 2, block old-version access, revoke access, then check a new answer, employee History and citation previews. Only temporary in-memory fixtures change. The lab transcript retains earlier operator observations and is explicitly separate from employee History; these local steps do not establish native update latency.

Audit records retain identity, question, per-resource decisions, prepared evidence, model activity and the stored answer or stop reason. A scoped explorer groups a request and shows its observed sequence, retaining mixed authorization outcomes and raw events. Preparation, sending, usage, storage and reading are distinguished. CodeBuddy previously contributed an independent hash-chain and Ed25519 checkpoint verifier; local chain validity and local checkpoint custody are not independent production protection.

Local validation of this pd candidate passed 714 Python tests, 13 standalone frontend suites and 19 offline check groups. On a known synthetic development set, the same 18 query variants improved from 11 to 18 queries containing every required evidence item after the bounded retrieval fix. Eight fixture security challenges passed. These measurements test implementation behavior, not blind answer accuracy, live-model prompt-injection resistance, native permission coverage, customer ROI or a production SLA. Failures and mode boundaries are retained.

The prototype demonstrates inspectable, permission-aware enterprise knowledge access. Remaining validation includes the new model mode, real-platform update/revocation behavior, independent employee identity mappings and team viewing. Production SSO, independently managed audit custody, all attachments/direct messages and arbitrary document formats are outside demonstrated scope. No customer adoption or quantified business return is claimed.

## Submission readiness

| Requirement | Artifact | Current boundary |
|---|---|---|
| Title / short blurb | Above | Final team wording review pending |
| Project description | Above | Describes pd code; local candidate, not the older deployed instance |
| Real CodeBuddy/WorkBuddy conversation history | [DEV09 manifest](../evidence/tool-usage/dev09-manifest.json) | All 15 declared private originals are absent from this clone; obtain originals from the team |
| At least three genuine development screenshots | Same manifest | Required originals are absent locally; this lab’s screenshots are not substitutes |
| Cover image | [PNG](../assets/submission/contextledger-cover.png), 1600×900 | Exact 16:9; existing cover retained |
| Architecture with trust boundaries | [SVG](../assets/submission/contextledger-architecture.svg), [implementation](IMPLEMENTED_ARCHITECTURE.md) | Includes optional two-call mode and isolated lab; not a native acceptance certificate |
| GitHub complete source | Repository with local closeout working changes | Source baseline is main 5727300; fixes are on local fix/systematic-closeout-20261015, pending an approved handoff. Deployment and competition submission remain separate actions |
| Aspire live demonstration | [Seven-minute script](DEMO_CANDIDATE.md), [lab guide](SCENARIO_LAB.md) | Local lab has browser evidence; latest native/model demo remains pending access |
| Optional video | Script available | No finished video claimed |
| Optional public link | Earlier hosted deployment is documented historically | Availability and version not checked this round; do not submit an unverified link |

Official requirements remain [01 section 8](01_OFFICIAL_BRIEF.md). G1/G2 are internal team review gates, not additional handbook clauses. This candidate does not authorize external uploads or final submission.
