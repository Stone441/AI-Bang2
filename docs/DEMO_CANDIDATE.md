# Demonstration candidate and remaining acceptance

2026-10-07当前固定实现64b705a（synthesis-v5，generation/review温度0）：386 clean archive回归、同48世界五fixture及两Node/语法检查通过，仅local/mock。24开发题经逐条只读复核为20核心正确返回（09/32仍有背景）＋1跨事件误导（business16把payment-service根因放入webhook答）＋2正确空答＋1有证据generation结构失败（business12第二claim的quote缺MIG-301，未进入review）；整体质量未通过。eng_b两道当前native＋真实模型正确，28精确窗口及四阶段授权allow；两题耗时含preview119.789/127.671秒，非SLA。当前core/native usage上界18016/3288microUSD，共享账本settled194985/pending0，起点含并发reservation不可用accounted差归成本。当前签名/分页副本本地验证，非独立custody或人工阅读。证据：business-validation-20261007/sampling-fixed-readonly-review、clean-sampling-fixed、sampling-comparison、audit-native-sampling-fixed及audit-core-sampling-fixed。三题各四次温度比较仅开发诊断，不是盲测或稳定质量率；旧失败及AUTH019范围保留。browser saved site denial blocked，49161停止，8094/8100未动；新失败仍open工程，Goal active，G1/G2/人工/ROI/发布not_run。

2026-10-07本地材料草稿（未提交/未获G2）：当前代码2a73bd0；模式与质量结果以STATUS及business-validation-20261007为准，旧331bd28证据继续按原版本保留。标题 **ContextLedger**；7-word blurb **Enterprise answers with permissions, citations and audit.** 16:9封面：[SVG](../assets/submission/contextledger-cover.svg) / [1600×900 PNG](../assets/submission/contextledger-cover.png)，实际本地渲染检查，不是产品浏览器截图。

English description draft: ContextLedger addresses The Internal Brain challenge: engineers and product staff must reconcile incident decisions, work status and release scope scattered across enterprise knowledge tools. This synthetic competition prototype offers independent questions, exact source citations and reauthorized answer history across Confluence, Jira, Slack and Google Drive. Its value proposition is faster, checkable decisions without turning collection credentials into employee access. Human time savings have not yet been measured.

The application uses server-verified local operator sessions, delegated read-only source adapters, bounded discovery, SQLite resource/version storage, overlapping exact-text windows and permission-filtered binary-TF BM25. It uses no embeddings, vector database or semantic reranker. Current source checks protect generation, separate review, answer commitment and subsequent citation/history access. Prompts preserve event, time and approval scope and require copied supporting quotes; structural validation and whole-answer review reject invalid output. Audit queries use restricted structured conditions. A genuinely CodeBuddy-developed offline Ed25519 verifier checks saved checkpoints, with same-machine custody limits explicitly retained.

Measured development work includes 48 core synthetic objects, 24 development questions, a separate 12-question retained evaluation, and 1000 distinct distractors. Source-owner probes recorded four-source creation and two corrections; these manual samples do not establish a freshness SLA. Selected native and paid-model runs have receipts and exact evidence records. Semantic errors, abstentions and unsupported formats remain explicit. Browser verification, complete native acceptance, human benefit, independent production custody and final team approval are incomplete.

CodeBuddy真实贡献及截图/对话继续使用既有证据索引，不能用本地材料草稿代替真实工具使用证明。录屏/视频未制作；本地源代码提交不等于远端提交或比赛交付。

2026-10-07业务增强候选实现f8ecbed：373 clean archive/五fixture/2Node/HTTP通过；binary-TF BM25、表格cell关系、资源方向审计、有界后台查询及版本反证停答已实现。四源AUTH-021新probe和两次修正native API/fake当前16断言通过，加载hash匹配候选；query约43–58秒，非SLA。12保留题冻结后一次live评测及只读语义审查已完成，具体见business-validation-20261007/heldout-review.json：有明确正确答案和safe unsupported，也有歧义/状态误答、部分答案和来源故障告知不足，不能称质量全通过；两项AUTH-019原延期不覆盖这些新失败。当前native/模型签名副本分别核验，同机测试key非独立custody；产品browser仍saved site denial blocked，49161停止、8094/8100不动；G1/G2、人类任务/ROI及发布提交not_run。Goal active，新增工程缺口仍由Codex继续负责。最新本地候选c825143非后台unknown通用修复有17定向、377 clean archive/五fixture/2Node/HTTP及只读复审通过；它尚未形成新native/live/browser结果，不能继承f8ecbed两题实际运行。

## 精简验收准备 · 2026-10-06

候选保持不变。本次只核对/整理文档，不启动服务、不调用源API或付费模型。`331bd28`→`6d79ed2`的155个变更路径全部属于docs（8个）或本轮evidence（147个），实现、测试、fixture、配置与构建文件无差异。357项/17.406s、五fixture场景、两Node及HTTP结果明确对应[331bd28干净归档](../evidence/runs/review-integrated-20261006/rebuild-scope-current/verification.json)。6d79ed2是状态/证据提交，不需要因该提交补实现回归；不能把这等同于新浏览器或完整native/live model验收。模型/native各轮仍按原记录的基准commit和实际工作树hash解释，不改写成331bd28新执行。

### 两项已批准延期（仍failed/partial）

| 项目 | 原问题、身份/模式 | 期望 / 实际 / 失败证据 | 场景影响与批准边界 |
|---|---|---|---|
| 指定事件长文无最终回答 | “In the Orion incident, which early explanation was withdrawn and what caused the duplicate requests?”；fixture_eng_a，合成源＋真实DeepSeek（fixture_source_live_model_synthesis），不是native员工权限 | 应只回答Orion撤回cache解释、retry budget mismatch造成重复请求，不混入Vega DNS或无关事故。最新[scope recheck原记录](../evidence/runs/review-integrated-20261006/quality-long-scope-recheck/verification.json)，request `6bf6313898ed42a080944661b6e1ea0d`：draft有正确Orion句，但又附payment-service RCA及cache历史；review verdict true/false/true，整答ModelUnavailable、claims_only为空、answer文件null。原v2成功和后续各失败均保留，不能称全部是review误拒 | S-01工程问答、Q-10长文/相似事件：证据送达不等于可得到最终答案。这是明确指定事件的问题，不以多事件歧义解释失败 |
| 自然题附非必答背景 | 工程原题：“For the payment-service follow-up work, separate the completed repair from safeguards still being worked on, and name the safeguard owner.”；fixture_eng_a。产品原题：“Does PAY-102 being done authorize a general customer rollout?”；fixture_product_ops。均合成源＋真实DeepSeek | 工程应给PAY-102 Done、PAY-103 In Progress、Maya；实际满足这些事实，但又给pilot/GA/no GA date背景。产品应说明Done不等于发布批准；实际正确，但重复pilot限制及日期/扩展范围背景。见[工程最终claims及quotes](../evidence/runs/review-integrated-20261006/quality-final-live/followup_status-answer.json)，request `a2f7afb45d3d4788bc2018f3d0d1946e`；[产品最终claims及quotes](../evidence/runs/review-integrated-20261006/quality-final-live/code_not_release-answer.json)，request `292602be834b4149a5d8eeb818ffc804`。支持事实/原子覆盖通过不代表相关性与简洁度通过。这轮v3早于最后review-scope澄清，保留原hash，不冒作最终版本重跑六题 | S-01工程及产品/运营答案：增加阅读负担，重点容易被背景淹没。不能把所有六题都说成失败，也不能把部分事实正确说成质量全通过 |

仅沿用AUTH-019及[原批准记录](../evidence/runs/review-integrated-20261006/quality-deferral-approval.json)：用户“批准明确延期并交团队验收”，允许固定候选带这两项已知缺口交团队语义观看；不是修复通过，不是降低review gate、清预算、新scope、G1/G2、发布或提交批准。本次没有重新申请或重新批准。

### R2原生8项检查究竟证明什么

[verification](../evidence/runs/review-integrated-20261006/native-discovery-current/verification.json)与[实际cycle](../evidence/runs/review-integrated-20261006/native-discovery-current/discovery-cycle.json)：AUTH-014/017、eng_b、四源live API＋fake model，无源写入/模型网络调用。2026-10-06新加坡时间14:34:49–14:35:26；cycle约20.351s是一次运行耗时，不是源变更至可回答时延。

| 来源与固定范围 | 本次实际行为 | 新资料发现范围 |
|---|---|---|
| Confluence space 131227 | 1页list、2次exact read、发布2对象 | 本轮没有新增ID |
| Jira KAN / 10001 | 1页list、3次exact read、发布3对象 | 既有但不在原白名单的KAN-6 / 10015进入新索引；不是本轮新建工单 |
| Slack C0C6R70SGG4，自既有合成root起 | 2页list、4次exact read、发布2对象（含thread读取） | 本轮没有新增ID |
| Drive固定文件夹1EMYjaNhzBFQ3TXHC6ukEwN6otVIIeOEv | 1页list、3次exact read、发布3对象 | 本轮没有新增ID |

8个actual断言逐项：①四native身份核验；②四源周期complete；③发现原白名单外既有10015；④它确实进入本次fake答案（Revision2 green）；⑤发现对象preview精确匹配；⑥原reader白名单未改；⑦product_ops未获发现权限；⑧本地审计链有效。它们不是8个四源生命周期案例。尚未证明四源各自新增/更新/删除完整native矩阵、源变更到答案的时限/p95、持续多周期新鲜度、完整persona/ACL矩阵或此候选的native＋live model＋browser端到端。历史Confluence/Jira更新及其他撤权/删除子集继续按原版本有效，不重做或升级其含义。

观看采用[18分钟四列流程](SAFETY_REVIEW.md#固定候选18分钟观看流程准备未执行)。浏览器仍blocked（工具报告saved site denial），页面交互not_run；49161已停止，不用新端口/工具/入口绕过。启动前须由操作者确认具体服务、331bd28版本、fixture模式、隔离数据与已有启动/实例访问授权；未满足就只回看历史记录。8094/8100不动，native/live model现场测试不纳入这次无费用准备。

2026-10-06 integrated candidate now supersedes the earlier R3A/R4-only handoff: fixed application/test **331bd28**, clean archive **357 regressions**, five fixture scenes, two Node checks and local HTTP passed. R2 current native read-only discovery subset, R3 fixture-source true model failures/fixes and R5 existing UX are [bound by mode and source hash here](../evidence/runs/review-integrated-20261006/README.md). **Fixed candidate prepared**: long/relevance quality explicitly approved deferred to team review, still not passed; browser tool site permission remains blocked and actual browser check not_run; G1/G2 not_run. Earlier historical native/model/browser records remain valid within their original modes, not proof of this new runtime.

2026-10-06 current R3A/R4 local candidate: fixed application/test commit `34281adfe22c839ed463a51cb3536255f47175b4`, branch `fix/r3a-r4-team-candidate`. Clean archive: 352 regressions, five fixture scenes, both Node checks and local HTTP smoke passed; six current mock lifecycle audit snapshots and 13 signature/rollback checks bound to exact runtime hashes, actual read-only sub-agent review closed. [Candidate handoff and limits](../evidence/runs/review-r3a-r4-candidate-20261006/README.md). New-build native/browser visual/live model and G1/G2 remain **not_run**. Historical evidence below keeps its original versions/modes; old 8100 independent-question evidence remains valid. Do not treat prior feature/download descriptions as current ADR-040 behavior.

2026-10-05. Local-only candidate; this document is not G1/G2 approval, a production claim or a submission.

## Five-scene coverage

| Scene | Prepared evidence | What can currently be claimed | Remaining before complete acceptance |
|---|---|---|---|
| S-01 Cross-source answer | `evidence/runs/live-s01`, `evidence/runs/live-product`, local five-scene replay | Native eng_b engineering and product questions use four source inputs, live DeepSeek and exact quotes; product answer distinguishes pilot/GA, Done/release and unconfirmed date | Original eng_a/product_ops independent ACL personas and team semantic review. Current eng_b can access incident data; do not present it as product_ops isolation |
| S-02 Updated content | `evidence/runs/live-lifecycle`, `evidence/runs/native-jira-update`, `evidence/runs/lifecycle-local` | Native Confluence update/restore and dedicated Jira KAN-6 text update protect old references/history and refresh new evidence with readonly eng_b/fake model; four fixture sources update without whole-store rebuild | Native Slack/Drive content updates, representative timing samples, live model/browser updated answer, enough samples for any p95 claim. Source refresh is query-triggered, not background webhooks |
| S-03 Restricted information | `evidence/runs/native-restricted-fixed`, fixture permission/security regression | Native owner-only C-03 is denied to existing eng_b; C-02 is allowed. A controlled stale synthetic index is retained while negative query/model evidence and preview exclude C-03; 13 checks pass | Original contractor/full native persona matrix, browser/live-model observation and statistical timing side channels remain not_run. Local stale text is synthetic setup, not historical ingestion proof |
| S-04 Revocation | `evidence/runs/synthesis-native-revocation`, source revocation records, `evidence/runs/live-lifecycle` | Native private Slack removal protects same-session synthesis citation/history/export, member restored; CF/Jira/Drive reader revocation subsets and disposable Drive trash protection exist | Exact original persona/full per-platform ACL and child-resource matrix, in-flight propagation boundaries and team observation. Legitimate past downloads cannot be withdrawn |
| S-05 Audit | `evidence/runs/audit-mixed`, `evidence/runs/audit-replay`, CodeBuddy verifier records | Four fixture outcomes match 116 event IDs over 17 stable pages; failed answers are not committed and audit roles/scopes are denied. Actual-live replay and signature boundary proof are separate | Native auditor authentication, independent key custody/DB role isolation and team observation. Mixed-outcome oracle is developer fixture evidence; offline test auditor is explicitly a test identity |

The live product harness had a stale `fake_model` response-mode suffix despite actual DeepSeek calls; original records are unchanged and the discrepancy is documented beside them. Current runner fixes future labels. Do not silently relabel old signed/hashed audit records.

## Rebuild evidence

Application/test commit `e9a55e6` passed a clean git-archive run: setup, 295 tests, five fixture scenarios, Node security checks and a newly started HTTP demo through login/query/exact citation preview. Evidence: `evidence/runs/rebuild-fixed`. The earlier archive failure is preserved; one test had depended on a leftover database and now uses an independent real temporary DB. Browser visual review remains separate.

Latest audit UI application/test commit `0278bab` also passed clean archive setup, 295 Python tests, fixture scenarios, both frontend Node scripts and HTTP smoke (`evidence/runs/rebuild-audit-ui`). Audit UI now separates process stages and rejects stale inquiry/page responses. Chrome visual inspection was blocked; it remains not_run.

## Review preparation

For the local deterministic walkthrough:

```sh
make setup
make test
make verify
make verify-lifecycle
make demo
```

Use only the explicitly labeled fixture demo for switching test identities. The approved native operator uses the existing Keychain mapping and `make live-synthesis LIVE_PORT=8094`; an existing process need not be restarted for document review. If loading a new candidate, restart it normally and open its new one-time entry link privately; never record credentials or entry tickets.

The live product runner requires `--live`, uses the original approved budget DB, and refuses to overwrite existing evidence. Running it makes real paid model calls within the existing ceiling, so it is not part of `make test` or demo startup. Audit replay uses copies and disposable local signing keys, without platform/model calls.

Team review: follow `SAFETY_REVIEW.md`, record exact commit/mode, observe outputs and mark each limitation. G1 concerns approved external access after safety observation; G2 concerns final material/submission approval. Neither has been completed by this evidence preparation.

## Next dependency order

1. Close candidate reproducibility and the remaining automatic safety/quality failures; keep the five-scene matrix current.
2. Prepare native independent-persona acceptance only with existing reviewed accounts/grants, or obtain the specific missing authorization. Do not fabricate product_ops from an engineering identity.
3. Run remaining authorized native update/negative-permission cases and organize one consolidated team review.
4. Assemble the validated demo recording and final material candidate; publishing/submission awaits G2.

Retrieval improvements remain DEV-08, evaluated against these delivery requirements. Adding vectors/reranking is conditional on a demonstrated gap and approved resources, not a prerequisite to every next task.

Latest restricted-acceptance candidate `b541c02` passed clean archive setup, 297 Python tests, five fixture scenarios, both Node checks and HTTP smoke (`evidence/runs/rebuild-native-restricted-approved`). The earlier sandbox run denied loopback bind; its failed logs remain separate. No platform/model access or operator restart was involved.
