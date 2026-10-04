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
