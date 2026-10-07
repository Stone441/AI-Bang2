# Team safety review and submission checks

2026-10-07候选0bc90ae低推理4096已有398archive、24开发模型和native2当前证据；浏览器仍saved拒绝blocked，真人3×4任务、ROI/G1/G2未运行。现有题卡只准备，当前不安排用户操作、不据开发者/Agent判断补造人类验收。

2026-10-07 BV-05仅准备的3×4任务卡，全部human not_run；不要求用户现在操作，不发送邀请。浏览器saved site denial解除并核候选服务授权后，开发者操作，团队只判断答案/交互；每人记录人工查源与候选的用时、正确/错误事实、拒答是否合理及引用是否足够，不能从Agent模拟推ROI。采用交错顺序避免全部先看答案：A先手工后候选，B相反，C交替。

| 人员 | 四项业务任务（同48对象fixture，非native/live现场） | 记录 |
|---|---|---|
| A 工程 | 事故最终原因；撤回假设；follow-up owner/status；最新版runbook | 各次开始/结束、答案/来源错误、查证能否完成 |
| B 产品 | payment-retry适用范围；Done是否批准GA；确认发布日期；提案审批与取消区别 | 各次开始/结束、范围/状态错误、是否需要澄清 |
| C 安全/使用 | 允许问题与受限问题对照；无证据问题；同会话撤权后旧引用/历史；按人/资料查看审计 | 可见内容、拒答可理解性、旧内容是否仍可见、是否能还原操作 |

这些题卡不充当盲测集；底层实现、撤权注入和日志验证由开发者负责。若以后改为native/live model，分别核具体身份/服务/模型readiness/原预算并记录模式，不能沿用fixture结果。

2026-10-07业务增强候选实现f8ecbed：373 clean archive/五fixture/2Node/HTTP通过；binary-TF BM25、表格cell关系、资源方向审计、有界后台查询及版本反证停答已实现。四源AUTH-021新probe和两次修正native API/fake当前16断言通过，加载hash匹配候选；query约43–58秒，非SLA。12保留题冻结后一次live评测及只读语义审查已完成，具体见business-validation-20261007/heldout-review.json：有明确正确答案和safe unsupported，也有歧义/状态误答、部分答案和来源故障告知不足，不能称质量全通过；两项AUTH-019原延期不覆盖这些新失败。当前native/模型签名副本分别核验，同机测试key非独立custody；产品browser仍saved site denial blocked，49161停止、8094/8100不动；G1/G2、人类任务/ROI及发布提交not_run。Goal active，新增工程缺口仍由Codex继续负责。最新本地候选c825143非后台unknown通用修复有17定向、377 clean archive/五fixture/2Node/HTTP及只读复审通过；它尚未形成新native/live/browser结果，不能继承f8ecbed两题实际运行。

2026-10-06 integrated worktree: R5 source preview links, question/time history and collapsed diagnostics have local DOM/HTTP evidence. R3 frozen variants evaluate final claims/supports/omissions separately from evidence recall; long-event review/relevance failures remain explicitly failed/partial, with user-approved deferral to this consolidated team review. Current source/commit/mode and browser permission are recorded in STATUS and ACCEPTANCE_STATUS. R3A/R4 team viewing is not a prerequisite for other local development.

G0/G1/G2 are internal team decision gates, not competition grades. This checklist does not grant approval or mark a review complete.

## 封版候选连贯观看 · 18分钟（80b9ffc，准备未执行）

由操作者展示，团队只判断问题、答案、引用及可见行为。当前无新operator实例，8094/8100未动，49161停止；browser仍为工具saved site denial blocked。先用以下真实结果回看完成连贯展示；现场页面步骤须等正式站点许可及具体实例启动/访问授权，不换入口绕过，不把回看称为新页面测试。新模型配置为v10 low/8192，原0bc90ae/v8 low4096证据仍有效但分列。当前最终回归运行中，表中预期不是预填通过。

| 我操作什么 | 预期看到什么 | 检查什么 | 记录什么 |
|---|---|---|---|
| 0–2分【当前候选/配置回看】展示candidate-80b9ffc-fingerprint及当日readiness，说明没有新页面实例 | 代码80b9ffc、v10 low/8192；默认none/1024；数据/代码hash及运行模式清楚 | 团队是否知道历史证据、fixture、native和live model各证明什么 | 观看者/时间/版本/模式，页面现场not_run |
| 2–5分【当前fixture源＋live model结果回看】读known12-80b9ffc的01/02/06问题、最终claims、quote，及11的澄清/范围结果 | failover检查、Done不等于发布批准、pilot/no GA日期；未批准不等于放弃，不自动选未指定事件 | 是否回答原问题、必要限制是否清楚，空答的澄清是否可用，引用是否支持结论 | 每题业务判断pass/fail/partial；这是已知题结果回看，非盲测或native |
| 5–8分【当前native＋live model结果回看】读native-timing-80b9ffc两问、最终答案和各一个single-preview，再看分段时间 | Slack最终amber替代green；产品pilot/GA/date/Done边界；引用版本/原文与答案一致 | 答案是否可用于工作、单引用是否易核对、等待时间能否接受 | 两题判断、实际query/生成/review/单preview时间；现场native/live model not_run，不另行付费 |
| 8–10分【历史四源native＋fake回看】并排看four-source-timeline三阶段正文/版本与发布时间区间；补当前最终Slack语义结果 | 四源amber→green→amber，Slack为新reply；原metadata/发布/摘录时间分开 | 是否看懂内容何时变化；哪些缺测不能叫SLA | 观察结果；历史三阶段不是逐阶段live model或自动新鲜度通过 |
| 10–13分【新版fixture结果回看；页面许可解决后可现场补】展示five-scenes-80b9ffc的S02更新旧引用拒绝、S03受限/允许对照、S04同身份撤权后旧历史/引用 | 新版本能答，旧版本不再可读；受限资料不泄露，其他允许资料仍可答；无聊天继承/答案下载 | 业务能否理解更新与拒绝；是否仍看到旧受限内容 | 三种行为业务判断；fixture与历史native撤权分开，页面键盘/导航/历史可见交互保持not_run |
| 13–16分【当前故障＋审计回看】读known12的12来源故障与对应审计；看five-scenes的S05受限审计查询，再对照原audit-mixed四结果及配对签名记录 | 未知来源先停答，无model dispatch；可以串起身份/问题/授权/证据/最终结果或失败 | 是否清楚为什么没有答案；能否用记录还原发生了什么 | 可/不可还原项及提示可理解性；不要求团队判断数据库/密码学，独立custody未通过 |
| 16–18分【原延期＋收尾】回看AUTH019两项原问题/失败，并汇总今天实际观察 | 原延期仍为failed/partial，新回归结果和完整矩阵缺口另列 | 是否把回看当页面通过、把一次成功当稳定率、把判断当G1/G2 | 原两项延期意见与最多三项待决；G1/G2只由明确真人观看记录及具体批准产生 |

## 固定候选18分钟观看流程（准备，未执行）

固定应用/测试331bd28；6d79ed2仅状态/证据。当前浏览器blocked是工具保存站点拒绝，**不是页面验证失败**；49161已停止。现在可执行历史证据回看，表内新版fixture交互仅在正式站点许可解决、具体服务/版本/隔离模式及启动与实例访问授权确认后执行；不更换端口/工具/入口绕过。无法进入的步骤记录not_run，改看对应既有记录，不把回看计作新交互通过。团队只判断答案和可见交互，操作者负责服务准备。总计约18分钟；不预填观察结果或G1/G2。

| 我操作什么 | 预期看到什么 | 检查什么 | 记录什么 |
|---|---|---|---|
| 0–1分【历史证据回看】打开DEMO_CANDIDATE顶部及331bd28归档记录；说明今日未启动服务 | 固定版本、357本地回归、各模式边界、browser blocked | 大家是否知道fixture身份/摘录答案与真实模型/native的差别 | 观看者、时间、331bd28代码/6d79ed2记录版本，观看方式 |
| 1–4分【新版fixture，条件满足才现场】eng_a问“Which fault actually produced duplicate payment requests, and what earlier explanation was ruled out?”；product_ops问“Does PAY-102 being done authorize a general customer rollout?”；展开引用/Recent answers/折叠诊断，用Tab导航。当前未解锁时回看rebuild-scope-current与原答案 | FAKE MODEL摘录标识；原因和撤回解释、Done不等于GA批准；历史问题/时间；引用与诊断可识别 | 答案是否回答问题、证据是否能读懂，等待/失败提示是否清楚，键盘是否能到达控件；fixture引用不伪造原平台链接 | 两问实际答案与身份/模式，引用是否支持；交互各pass/fail/not_run；历史回看不填浏览器通过 |
| 4–7分【历史真实模型证据回看】并排读DEMO_CANDIDATE两项延期中的原问题、final claims/quotes与long scope recheck结果 | 工程/产品题有事实但多余背景；Orion有draft而最终claims为空 | 背景是否必要；Orion问题是否明确、无最终答案怎样影响使用；draft不能算用户收到答案 | 两项failed/partial及业务影响，团队意见；沿用AUTH-019延期，不填新模型运行/质量通过 |
| 7–10分【新版fixture，条件满足才现场】在隔离演示目录问runbook、更新为runbook-v2后再问，打开旧引用/旧历史；当前未解锁时回看已有S-02记录及R2 native verification/cycle | 新版内容；旧引用/历史不可用。R2记录中四源cycle与KAN-6 Revision2 green | 新旧是否清楚，失败时是否误称最新；KAN-6是既有资源发现，cycle耗时不是新鲜度SLA | fixture观察pass/fail/not_run；R2仅历史native只读＋fake回看，缺失四源生命周期/时限仍未完成 |
| 10–12分【新版fixture，条件满足才现场】contractor问security，再问允许的pilot；当前未解锁时回看S-03及历史native restricted正负对照 | 禁止问题无受限内容/标题/路径/存在提示，允许问题仍可答 | 是否泄露信息，拒绝提示是否清楚 | 身份、两问结果、泄露与否；历史native与当前fixture分开记录 |
| 12–14分【新版fixture，条件满足才现场】同一eng_a会话先读S-01，隔离fixture撤权后重新问并打开旧引用/历史；当前未解锁时回看S-04与原Slack撤权记录 | 旧引用和依赖历史不可用；无聊天继承或答案下载 | 撤权后是否还看到旧内容，是否还能独立问其他允许问题 | 会话/身份、前后可见结果、pass/fail/not_run；回看不称新native撤权 |
| 14–17分【历史证据回看；新版fixture只在已解锁时补可见界面】看audit-mixed四种结果及当前签名检查输出；操作者展示受限auditor查询 | 能把问题、允许/拒绝、证据和最终结果串起来；失败无成功答案；fake无vendor回执 | 团队能否读懂发生了什么；局部签名不等于独立保管或生产防篡改 | 能/不能还原的结果、界面not_run与限制；不要求团队判断签名或数据库实现 |
| 17–18分【收尾；native/live model现场测试均not_run】汇总本次实际观察；不运行API/模型、不重启8094/8100 | 观察结果、两项延期、工具浏览器阻塞、未完成native/新鲜度矩阵分列 | 是否有任何回看/mock被错写成现场通过，是否把团队意见当G1/G2授权 | 本次各步骤的pass/fail/not_run与少量待办；未来native须核固定资源/身份及服务授权，live model另核当日readiness/原预算与具体费用许可，本次不执行 |

## Safety demonstration (G1) — not_run

The developer operates the prepared application; a team member watches and records the result. No coding or repeated credential entry is required from the reviewer. Use synthetic competition data only. Keep credentials, OAuth URLs and one-time entry links out of recordings.

| Demonstration | What the reviewer should see | Current evidence and remaining work |
|---|---|---|
| Cross-source engineering and product questions | Cause, withdrawn hypothesis, open follow-up and current runbook have correct evidence; pilot approval is not confused with general availability | Local S-01 subset and live question subsets exist; native eng_b engineering/product fact subsets verified; independent personas and team quality review pending |
| Content update | New source revision becomes searchable; old revision is unavailable; no false claim of freshness during failed refresh | Four-source local lifecycle matrix, native Confluence update/restore and Jira KAN-6 text update exist; native Slack/Drive updates and timing matrix pending |
| Restricted material | Unprivileged user gets no restricted text, title, path or existence confirmation; an allowed question still works | Native owner-only C-03 denied to eng_b and C-02 allowed, stale synthetic index/query/model evidence/preview checks passed; full live persona/timing matrix pending |
| Same-session revocation | After source access removal, old citation and dependent history are unavailable; ordinary answer export remains absent (ADR-040); unrelated allowed material stays usable | Native Slack synthesis subset verified, original membership restored; complete live matrix pending |
| Audit reconstruction and integrity | Authorized auditor can reconstruct question, decisions, evidence and response; covered tampering is detected and unsigned/uncovered tails are identified honestly | Mixed fixture success/partial/denied/failed requests: 116 expected events across 17 pages, late request excluded, role/scope denied, signed-copy tampering detected. Actual-live replay is separate; native auditor, independent custody and production DB role isolation remain incomplete |

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

## 历史观看提纲（由上方18分钟流程覆盖）

Use a single short review session. The developer presents the application and evidence; the reviewer records only observed results. The fixture identity switcher is a labeled simulation, not production identity or native SSO. Keep the existing 8094 service running; no credential re-entry is needed to review stored evidence.

| Order | Developer presents | Reviewer checks | Evidence to compare |
|---|---|---|---|
| 1 | Existing engineering and product answers, their quoted support and source versions | Incident cause/withdrawn hypothesis/open follow-up; pilot approval must not become GA or an invented date | `evidence/runs/live-s01` and `live-product`; exact native eng_b identity, not the product_ops ACL persona |
| 2 | Recorded native update/restore and disposable-file deletion, then fixture lifecycle results | Updated evidence is current; old versions/deleted content are unavailable; no background-sync SLA claim | `live-lifecycle` and `lifecycle-local` |
| 3 | Native restricted seed and the negative/positive query pair | No C-03 title/path/canary in the negative answer/model evidence; C-02 still works; stale index stays present | `native-restricted-fixed`; owner screenshot is private and must not be uploaded automatically |
| 4 | Recorded same-session native Slack revocation, denied old preview/history/export and restored member | Revoked mixed answers unavailable; unrelated answers remain usable; legitimate earlier downloads cannot be withdrawn | `synthesis-native-revocation` |
| 5 | Mixed audit oracle, paginated inquiry and verifier output | All four outcomes reconstructed; 116 event IDs match; failed query has no committed answer; audit roles/scopes restricted; unsigned-tail boundary stated | `audit-mixed` plus `audit-replay` for uncovered-tail/whole-chain cases |

Replay the mixed audit without API credentials, native writes or model costs:

```sh
make verify-audit-mixed AUDIT_OUTPUT=.runtime/team-review-01
```

Choose a new directory for every run; existing evidence is deliberately refused. `oracle.json` contains the four actual request IDs and the developer-captured expected event IDs. `inquiry.json` is the actual inquiry result. `verification.json` describes real execution, signatures and limitations. These files do not record team approval.

Create a separate observation record only when the team actually watches. Record reviewer/date/candidate commit and, for each scene, observed pass/fail/not_run, demonstration mode and open issue. A historical log review does not become a newly witnessed native revocation. G1 external opening requires the approved audience and unresolved safety risks to be assessed separately; no public deployment is included here.
