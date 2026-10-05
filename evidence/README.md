# Evidence index

全部为合成数据，不含真实凭据/企业内容；没有上传外部证据。

- `runs/local-latest/tests.json`：unittest 实际结果、运行时间、Python 版本、被测 commit 和逐文件 SHA-256；2026-10-05 为 101 个测试方法（含 41 个 Confluence 模拟 HTTP/配置/查询/撤权runner案例、7 个预算账本案例和 seed exporter），额外权限矩阵 subtests。逐案例区分 local_synthetic / mock_http_contract，回归未调用真实 API。
- `runs/local-latest/scenarios.json`：S-01…S-05 的实际输入/输出/引用/断言与部分覆盖边界。状态 passed_local_subset 不等于完整官方场景验收通过。
- `runs/local-latest/audit.json`：五场景执行的原始合成日志链，问答正文与每次授权保留。
- `runs/first-scenario-failure.json`：首次 S-01 失败，后续增加授权关联检索修复；不是预期内容充当实际输出。
- 本轮初期：DEV-02 3 tests；DEV-04 18 tests；增量扩展后 26、30，当前数字看 tests.json。
- 环境限制：首次沙箱 HTTP bind 失败，获准 loopback 执行后通过；IAB 不可用、Chrome localhost ERR_BLOCKED_BY_CLIENT，视觉验收 blocked。
- Live API：Confluence配置探针、真实query及同会话撤权已有结果；其余三源/runtime model blocked或not_run；G1/G2：not_run。
- 首个真实配置探针结果：`runs/live-confluence/space-discovery-user-reported.json`，用户提供的 eng_b / page98564 metadata-only allow、space_id131227、无正文；不是 Codex 独立复跑，不覆盖问答或撤权。后续真实 query 证据另列，live model仍not_run。
- `runs/live-confluence/query-864b1c6c23ce43ae9b05586ab8a27b0d.json`：用户执行后 Codex 实读本地 DB，9 checks通过，C-01 v1 核心原文/定位/claim支持/模型前和返回前授权/11事件审计。真实 API + fake model，仅 operator query 子集；未独立签名、无浏览器登录或真实撤权。
- `runs/live-confluence/revocation-037bcdb06b9d4a8087b8069495a4ef7a.json`：用户执行同会话runner、Codex真实原生ACL撤权并读DB；7 runner checks及7 DB核验通过，18事件链，查询/模型/旧历史/引用拒绝且索引保留。实际撤权/恢复截图在ignored private/onboarding-20261005/，未上传。Confluence API + fake model/operator子集，非四源/前端SSO/独立签名。
- CodeBuddy：verified local。真实贡献、原生会话导出、7张截图、提交与文件哈希见 `tool-usage/README.md` / `dev09-manifest.json`。实际对话/截图只能来自真实工具，敏感原始记录放 ignored `tool-usage/private/`，未批准不上传。


2026-10-05 Jira / operator web增量：全仓库139/139tests实际通过（60 local synthetic + 79 mock HTTP），最终实际结果以runs/local-latest/tests.json为准。Jira reader/独立评论/跨源查询/版本碰撞、Jira CLI与Confluence operator身份/HTTP链路测试，没有真实Jira API或收费模型调用。五场景仍fixture_fake_model本地子集；CodeBuddy来源字段已纠正为独立已验证交付，不在新的scenario run伪称重新调用工具。

- `runs/live-jira/seed-j02-kan4.json`：真实UI创建J-02/KAN-4，正文和Done状态读回，native issue/project ID、员工API/ACL不预填通过；截图仅ignored private。
- operator UI视觉：尝试Chrome8081模拟服务被ERR_BLOCKED_BY_CLIENT阻挡，已停止临时服务；没有截图/JS点击验收成功证据。真实网页命令已交用户，待完成后查独立DB，不与之前CLI结果合并。

2026-10-05启动诊断修复：全回归142/142（60local+82mock），相关HTTP/identity 11项。8081已有operator服务；bind实际errno48复现，修复后port_in_use在隐藏输入之前报告，不请求凭据/访问平台。旧统一错误无法还原用户那次失败阶段；本轮保留现有进程、不声称真实网页问答已通过。

`runs/live-confluence/web-query-26995601e7634d2191de4a69ee7c1c2d.json`：首个真实operator HTTP query，8项持久DB核验通过，12事件未签名链。工程事故问题仅得runbook；不扩大为多源事故/真实模型/SSO或UI点击验收。

- `runs/live-jira/web-query-and-revocation.json`：真实浏览器/HTTP、持久DB核验，KAN-4问答及临时原生role restriction撤权；11 checks/21事件unsigned链。索引保留、query/model/history/citation不提供撤权内容；权限恢复原No restrictions。前端旧DOM复用发现修复及边界明确记录。private/onboarding-20261005/jira-live-query-history.jpg、jira-kan4-restricted.jpg、jira-revoked-history.jpg、jira-kan4-restored.jpg仅本地未上传。
- `node tests/frontend_operator_security.js`：4前端视图安全检查实际通过，独立于153项Python回归；不计成真实平台权限测试。

- `runs/deepseek/price-review.json`: official pricing/API read-only review, 2026-10-05 Singapore; no credentials or model call in this document check.
- `runs/deepseek/verification.json` and `runs/local-latest/tests.json`: 233 actual local tests (60 synthetic/local, 173 mock contracts), 13 new model tests. Real API/model execution is separate.
- `runs/deepseek/live-drive-query.json`: real Drive + DeepSeek evidence selection, original synthetic excerpts, browser citation/history, 14 DB/budget checks; 61-event unsigned audit snapshot. One live model request, conservative upper accounting243 micro-USD, not vendor invoice. No free-form synthesis/full matrix claim.
- `runs/deepseek/live-insufficient-evidence.json`: actual no-evidence refusal, no additional external model request/reservation/cost. UI separates NO MODEL CALL, LIVE MODEL and FAKE MODEL. Screenshots stay under ignored `tool-usage/private/onboarding-20261005/`; not uploaded.

- Drive独立reader原生问答、引用、历史及同会话撤权：[reader-query-and-revocation.json](runs/live-drive/reader-query-and-revocation.json)。fake model；恢复权限只UI，export/full ACL/unified not_run。截图留本地private。

2026-10-05 阶段收尾：local-latest当前248/248（60 local /188 mock），五场景passed_local_subset；首次sandbox loopback失败后相同测试获准重跑通过。最新真实能力及not_run以STATUS收尾段为准；本轮未调用真实API或模型，私有截图/工具对话/凭据未纳入push。

2026-10-05 AUTH-014 credential reuse: [Keychain verification](runs/keychain/verification.json), native Mac synthetic add/read/update/delete passed and test item removed; 266 local/mock regression tests. Real stored credentials, Google refresh reuse and unified live startup remain not_run. No existing password item accessed, no new live/model call.

2026-10-05 unified first live attempt: [failure checkpoint](runs/live-unified/first-query-failure.json). Four native sources/eight current objects allowed; model preflight refused inconsistent synthetic marker, no call ledger row or new model fee. Corrected compatibility mock-tested, actual successful unified answer and Keychain restart reuse still pending.

2026-10-05 unified live API + DeepSeek: [successful query](runs/live-unified/query.json). Four sources/eight objects, 18 readonly checks, native Slack reply preview and reauthorized history verified; 1030 tokens, conservative 468microUSD estimate. 53.37s latency, extractive selection only; full ACL matrix/revocation/G1/G2 separate. Screenshot remains ignored local-only.

2026-10-05 native Slack private-channel reader revocation: [same-session checkpoint](runs/live-unified/slack-revocation.json). Nine readonly checks, old mixed history hidden, later model/answer uses six objects from remaining three sources, root/reply native deny. Original member restored (Members2). Direct citation/export live not_run; screenshots ignored. New conservative cost345microUSD.

2026-10-05 [live export and stale citation checks](runs/live-unified/export-verification.json): initial JS rounding failure retained, corrected raw download9633 bytes exactly matches saved answer. Same-session native revoke rejects old export (no additional file) and old citation, clears stale views, retains valid login. No new model fee; original permission restoration separately verified.


2026-10-05 linkless source optimization: [initial failed regression](runs/linkless-optimization/first-failed-tests.json) retained; [current regression](runs/local-latest/tests.json) 270/270 passed. Mock native read counts reduced from five to four per matching linkless object; all source_refresh/before_model/model_dispatch/before_dispatch checks remain. Late-revocation injection now binds to the actual dispatch phase, retaining zero-model-call assertion. Five fixture scenarios and frontend security checks passed; no new live API/model call or measured live latency improvement.


2026-10-05 [live native-source latency comparison](runs/linkless-optimization/live-latency.json): real approved app-owned credential reuse/native identity and Drive refresh, four sources/eight excerpts, fake model only. Baseline53.209s / optimized40.116s, one sample each; all four remaining authorization phases preserved. [Exact one-off harness text](runs/linkless-optimization/latency-harness.py.txt) records execution for review (requires existing approved private configs/Keychain; not a general startup command). Separate test DBs, original8088 untouched, no paid model request.


2026-10-05 grounded synthesis: [successful live query](runs/synthesis/live-query.json), [actual audit](runs/synthesis/live-audit.json), [exact harness](runs/synthesis/live-harness.py.txt). Four authorized input sources/eight objects, four claims citing three sources, exact quotes and separate same-model review, 10checks;58.95s. [First four-source coverage failure](runs/synthesis/first-live-query.json) preserved (valid three-source answer, did not meet probe coverage), and [first targeted audit error](runs/synthesis/first-failed-targeted-tests.txt) retained. 281local/mock regressions/Node passed; new two-query model accounting3340microUSD upper estimate, not invoice. Review is fallible; no G1/full live acceptance claim.


2026-10-05 [live-model malicious-source subset](runs/synthesis-injection/query.json), [fixture audit](runs/synthesis-injection/audit.json), [actual harness](runs/synthesis-injection/harness.py.txt): synthetic fixture business sources, real DeepSeek generation/review. Malicious authorized text actually sent; six automated boundaries and agent semantic inspection passed, privateS-01 not sent, only fixed model endpoint/no tools. One authored case, not a comprehensive injection guarantee; extra unrelated supported claim recorded. Two calls1331microUSD upper accounting; no live source writes, same existing budget.


2026-10-05 [frontend delayed-response verification](runs/ui-session-races/verification.json) and [reproduced failure](runs/ui-session-races/first-failed-node.txt): expired-session preview, overlapping queries, late history and late export; mock fetch/Node, not live UI.281Python regression remains separate.8093 native-startup succeeded but tool IPC EPERM prevented safe entry transfer; staging stopped, user8094 entry pending. No new model/API query fees.


2026-10-05 [真实综合UI验证](runs/synthesis-ui/verification.json)：四源输入/引用、展开quotes、双回执、Slack reply预览、Enter/Escape、重新鉴权历史、实际raw下载逐字段一致。初答遗漏保障措施，保留质量缺口。[v2成功重测](runs/synthesis-ui/coverage-live-query.json)及[实际审计](runs/synthesis-ui/coverage-live-audit.json)包含11checks和agent语义/覆盖对照，56.76秒。保留[首次复核拒绝](runs/synthesis-ui/first-coverage-rejected.json)和[第二次缺quote拒绝](runs/synthesis-ui/second-coverage-invalid-quotes.json)，无自动生产重试/伪造quote。282本地/mock回归通过；截图私有ignored，非作者G1/完整live仍pending。


2026-10-05 [local port-session regression](runs/port-session-isolation/verification.json), [initial reproduced failure](runs/port-session-isolation/first-failed-tests.txt): real shared CookieJar with two loopback fixture servers, no external APIs/models. Login/logout remain independent and cross-port CSRF rejected;283 regressions passed. Chrome temporary fixture navigation blocked, not browser-verified. Current8094 session-ended observation recorded without asserting cause; no Slack membership change.


2026-10-05 [v2 real browser query baseline](runs/synthesis-native-revocation/baseline.json), [actual query audit](runs/synthesis-native-revocation/baseline-audit.json): three input sources/six evidence, final cause/withdrawn hypothesis/runbook safeguards, five checks and both receipts;1296microUSD upper accounting. [Incorrect first stage-count oracle](runs/synthesis-native-revocation/first-stage-count-check.json) preserved: source_refresh covers eight configured objects while retrieval selects six; corrected check uses exact selected resource/version sets and all-allow, with refresh coverage. Specific native Remove rejected by automatic approval; no membership changed, awaiting confirmation.

[First native synthesis revocation cycle](runs/synthesis-native-revocation/first-cycle-verification.json), [actual endpoint audit](runs/synthesis-native-revocation/first-cycle-audit.json): member2→1→2, same-session stale citation deny clears answer/preview, mixed synthesis history/quotes/dual receipts withheld, unrelated answer remains usable. Original same member/UID restored;7checks, zero new model calls. Extra export cycle not_run after approval review rejected it; original access remains restored.

[Second native synthesis export cycle](runs/synthesis-native-revocation/second-cycle-verification.json), [endpoint audit](runs/synthesis-native-revocation/second-cycle-audit.json): separately approved, stale export unavailable and files0→0; same native UID finally restored, Members2. Legitimate restored export8146 bytes matches the entire stored answer including quotes/dual receipts; zero extra model calls.
# Latest local lifecycle acceptance

2026-10-05 [real S-01 engineering fact verification](runs/live-s01/verification.json), [actual answer](runs/live-s01/answer.json), [audit](runs/live-s01/audit.json), [new synthetic J-03 native read](runs/live-s01/j03-native-read.json): four sources,8selected/9refresh,4claims covering root cause/withdrawn cache hypothesis/Done code fix/open protective follow-up/fictional Maya/current runbook;7checks and independent quote/stage/ledger validation. Single eng_b operator, not complete personas/G1. Two settled actual receipts1856microUSD conservative estimate. Actual harnesses saved; ignored private screenshot j03-in-progress.png. [Initial sandbox bind error](runs/live-s01/first-sandbox-test-block.json) retained; unchanged full283 tests passed in authorized loopback environment. No newscope/membership and no user8094 restart.

2026-10-05 AUTH-015 [Confluence real update/restore verification](runs/live-lifecycle/confluence-verification.json), [original answer](runs/live-lifecycle/confluence-baseline.json), [new revision](runs/live-lifecycle/confluence-updated.json), [restored answer](runs/live-lifecycle/confluence-restored.json), [old access denial](runs/live-lifecycle/confluence-old-access.json), [actual audit](runs/live-lifecycle/confluence-audit.json). Native versions1→2→3, original text exactly restored; first diagnostic Evidence.native_id KeyError preserved separately. [Drive disposable deletion verification](runs/live-lifecycle/drive-verification.json), [baseline](runs/live-lifecycle/drive-baseline.json), [audit](runs/live-lifecycle/drive-audit.json): native allow→trash→deny, old preview/history withheld, query/model empty while old index retained. Original three files unchanged in native UI. Both actual harnesses included as text; screenshots ignored/private. User performed upload after Chrome file URL permission blocked; no permission bypass. Live API / fake model / operator logical session, no new model fees, no HTTP export or human G1 claim.

2026-10-05 [twelve-source-operation matrix](runs/lifecycle-local/results.json), executed with `make verify-lifecycle`: four fixture sources × content/revoke/delete; stale-index model evidence exclusion, history/export projection withholding, citation denial, new revision publication/removal, unrelated revision retention, duplicate event handling and actual audit chains. Fake model / no live API / no human G1. [First probe failure](runs/lifecycle-local/first-probe-failure.json) preserved: the question intentionally contained the marker, so evidence-only leakage checking replaced the overbroad question+evidence check. Five existing local worked examples and six ingestion tests also rerun successfully; Node frontend guard checks passed. No real source writes or model costs.

2026-10-05 native-restricted-fixed：S-03 Confluence真实只读+fake model+明确controlled stale synthetic index，13checks/16events；native-restricted保留首次计数探针失败。管理员合成seed/权限截图仅ignored private（native-seed.json存路径/hash），非CodeBuddy/人工G1或完整persona矩阵。

2026-10-05 rebuild-native-restricted-approved：b541c02 clean archive297tests/五fixture场景/两Node/HTTP smoke通过；rebuild-native-restricted保留先前沙箱bind EPERM失败，未降低断言。

2026-10-05 audit-mixed：四类fixture请求/116event oracle/17页稳定snapshot/role及scope拒绝/4实际签名CLI结果，原测试失败日志保留；team walkthrough prepared，非live审计员/人G1。

2026-10-06 native-jira-update：真实Jira专用合成KAN-6 UI正文更新/eng_b只读API/fake model，13checks/23events；ignored screenshots与hash在native-seed.json。既有runtime服务/配置/原工单不改。
