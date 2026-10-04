# Source capability ledger

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
