# Source capability ledger

2026-10-07 Google Docs可行性核对（非实现/新格式授权）：现有drive.readonly在官方[files.export](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/export)允许导出，Docs可输出[text/plain](https://developers.google.com/workspace/drive/api/guides/ref-export-formats)，导出上限10MB。当前reader只支持已批准UTF-8 text/plain blob，未实现Docs导出、格式规范化、导出前后version一致性或旧版本证据定位；scope可调用不等于任意文件/格式已获业务授权。本轮无Docs创建/读取或新增API启用，现有native probe仍text/plain；Docs标unsupported，后续按具体格式/资源范围决定。

2026-10-04：仅核对官方文档，没有使用任何凭据，没有真实平台 API 调用。四源均 `fixture_only`，live 验收 `blocked`（账号、数据/scope 授权待定）。fixture 策略用于测试原生差异，不是平台 ACL 的完整复制。

| Source | 本地策略覆盖 | 真实权限方案 / 待实测 |
|---|---|---|
| Confluence | 空间成员 + 页面读限制交集 | 官方 content permission check 检查 site/space/content；查他人需要管理员权限。优先用户委托检查自身，不申请管理员 scope |
| Jira | 项目成员 + issue security + 单独 comment restriction | 目标用户委托 GET；父 issue 与受限 comment 分开读取/验证；附件范围待核对 |
| Slack | workspace + public/private/外部频道成员 | token 类型决定可读范围，bot 能读不等于员工能读；私有成员、线程、删除事件、分页及限流待测；DM 不支持 |
| Drive | 文件直接分享 + 继承目录组关系 | 用户委托读取当前文件；shared drive/组/域/继承变化、changes 游标及权限传播待测 |

共同未验证：真实 pagination、429/backoff、token 过期、撤权传播延迟、事件漏投、真实源链接定位。未获批准不得植入外部资料。fake source 分页/错误只能证明本地分支。

核对资料（2026-10-04）：
- [Confluence permission check](https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content-permissions/)
- [Jira issue comments / visibility](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/)
- [Slack conversations.history / token access](https://docs.slack.dev/reference/methods/conversations.history/)
- [Drive changes](https://developers.google.com/workspace/drive/api/guides/manage-changes)
- [Python HTTP server security considerations](https://docs.python.org/3/library/http.server.html#security-considerations)：本地演示用途，非生产服务器。

2026-10-05 增量：Confluence reader/probe 已实现并通过 16 个 mock HTTP/配置合同测试，见 CONFLUENCE_PILOT。注册和 C-01 种植已完成，不再称账号全未创建；四源 runtime 仍 fixture_only，真实 API/委托/模型未运行。

2026-10-05 最新增量：Confluence mock 合同共36项（包括14 query），全回归96。用户提供 metadata-only live configuration probe：eng_b/page98564 allow、space_id131227、未返回正文；证据 provenance 为 user_supplied_cli_output。普通凭据 current-user 比对及白名单页面 metadata 此次成功不代表正文/问答/撤权通过。独立 operator query pilot 已接共享 Engine；前端仍 fixture，live model not_run。

2026-10-05 query 增量：首个 live operator query 已实际检查本地持久DB，eng_b 的 C-01 v1 核心原文/引用及逐阶段授权通过，C-02亦获准刷新；11事件本地链有效，无独立签名锚点。5新增撤权runner mock测试，全回归101；真实同会话撤权正在测试，不能提前标通过。Jira/Slack/Drive runtime仍fixture，前端仍fake身份，live model未运行。

2026-10-05 撤权结果：Confluence同一operator pilot/Actor/逻辑会话，原生移除eng_b Can view后，query/历史/引用均明确native deny（C-02仍allow），没有重建/删除本地C-01索引。7 runner checks + 7 DB核验通过，18事件链有效。已在UI恢复原有Can view；不声称传播延迟/HTTP登录/真实模型/四源撤权/独立签名已验收。


2026-10-05 Jira增量：reader每次GET myself→白名单issue字段，评论另GET并先确认父issue访问；指定源端permissions为权威，不使用本地模拟group名单授予native权限。14 reader+10跨源+6CLI mock验证，真实Jira API not_run。KAN-4为已种植J-02，UI原生Done读回；native issue/project ID、普通员工Jira访问和token、评论ACL及权限矩阵待落实。Jira Free的issue-security/角色能力不能由mock补成live；需要具体账户实测。未申请新的scope。Confluence网页入口新增8 mock/HTTP验证，不扩大既有真实CLI结果到浏览器/SSO。


## Current incremental capability status — 2026-10-05

Earlier fixture-only/not_run entries are historical; current evidence is split below. Operator sessions are native-verified local sessions, not employee SSO. Models remain fake-extractive. Fixed-whitelist request refresh is not a background changes worker.

| Source | Implemented and actually checked | Still not_run / blocked |
|---|---|---|
| Confluence | eng_b native API query, local web/history/citation user confirmation, actual C-01 native revoke + retained index/old history/preview protection, restored permission; precise evidence under live-confluence | Full identity/space/page inheritance matrix, attachments/macros, SSO |
| Jira | KAN-4 exact native ID/project discovery, live local web query/preview/history, Administrator-only restriction followed by same-session native deny/no model evidence; restored original restriction; evidence under live-jira | Restricted comments and full multi-identity/security matrix, attachments, SSO |
| Slack | 22 mock tests; existing app A0C6F96HFNX four user scopes, no bot; user-confirmed Allow including identity/terms and secret save; actual private synthetic root/reply and native IDs seeded | Native API/query/reply result and same-session channel revoke still not_run; one-member channel needs separate reader identity for removal; full rich content/Connect/DM unsupported |
| Drive | 22 mock tests; fixed personal Drive UTF-8 text/plain native-user/file/canDownload/body+metadata-race boundary; shared four-source Engine query and Drive revoke retaining other authorized sources | OAuth scope/account/real IDs/seed/API not approved/configured, Docs/PDF/shared drives/changes and full inheritance matrix unsupported |

All four readers use exact resource native IDs and current delegated reads before model use; failures/unknown supply no evidence. No permissions-list reconstruction or collector/admin authority is substituted for current user access. Complete four-source live integration remains unverified; current unified four-source evidence is mock HTTP only. Latest Python full regression197/197 (60local/137mock), no live source/model calls during tests.

2026-10-05 Slack native increment: root + exact thread reply now verified through the local operator, including reply preview, reauthorized history and 14 persisted checks (web-thread-query.json). Fake model only; native channel revocation not_run. Latest unchanged-code full regression is 199/199 (60 local/139 mock HTTP). Earlier Slack not_run and 197-test rows describe preceding checkpoints.

2026-10-05 current increment: Drive fixed-scope PKCE OAuth/native account binding and three allowlisted text/plain files now verified through actual query, D-02 preview and reauthorized history (live-drive/web-query.json; 15 checks/29 unsigned events). Earlier Drive not-approved/not_run rows are historical. All four sources now have individual live API/fake-model query subsets; unified four-source live, employee SSO, full ACL matrices and live LLM remain unverified. Latest local regression220/220 (60local/160mock HTTP). Drive owner-only and Slack single-member channel require separate reader identities for meaningful native revocation.

2026-10-05 model increment: Drive operator8086 now verified with native API + real DeepSeek evidence selection (deepseek/live-drive-query.json). Three original synthetic texts, native locators, preview and history checked; model only selects IDs, server derives text. Free-form synthesis and comprehensive model semantics remain unverified. Conservative shared ledger accounted243 micro-USD for one observed live call; this is not a vendor invoice. Other source operators remain fake models; unified four-source live still not_run.
