# DEV-REVIEW-R2 · 最小发现方案（AUTH-017范围已批准 / 未实现 / 未运行）

2026-10-06。当前仍是显式对象白名单、每问刷新；用户已批准下列四个固定发现读取范围（AUTH-017）；批准不是S-02已通过。与R3A/R4独立，本地开发可以继续。以下ID仅来自本机已有非秘密配置的选定容器字段，不读Keychain/凭据；运行前仍验证tenant/native actor。

## 具体待批准范围

| 来源 | 身份与唯一容器 | 允许的最小发现读取 | 仍需确认 |
|---|---|---|---|
| Confluence | 既有eng_b，space 131227 | `GET /wiki/api/v2/spaces/131227/pages`，不请求body-format；分页元数据。仅现有批准IDs及标题以`[SYNTHETIC]`开头的新页进入内容reader；全文必须通过原合成banner再允许模型 | 从固定页面扩到该space的页元数据及明确标记新页正文，需要具体范围批准；不扩大product_ops AUTH-016 |
| Jira | 既有eng_b，KAN/project 10001 | 新版search/jql，服务端固定`project = 10001`，仅key/id/summary/updated；明确`[SYNTHETIC]`新工单才进入内容reader，逐工单原生权限继续检查 | 不跨项目，不发现评论/附件；标题标签只决定读取候选，不单独批准模型出口 |
| Slack | 既有eng_b，workspace T0C6FQ246TF / private channel C0C6R70SGG4 | 固定频道history，含正文，最早从既有root时间1791142152.858189开始；只发现明确合成根消息，以及逐条核验属于合成root的回复 | API历史列表会返回频道该窗口内正文，所以批准须覆盖该频道这个窗口；无DM/其他频道/附件。线程replies端点权限和限流另核对，不把根消息当完整线程 |
| Drive | 既有eng_b，folder 1EMYjaNhzBFQ3TXHC6ukEwN6otVIIeOEv | `files.list`固定`'<folder>' in parents and trashed=false`；direct child元数据。仅明确`[SYNTHETIC]`名称且text/plain新文件进入reader，核对parent/类型/原生读权及正文marker | 不列整个个人Drive，不递归子文件夹，不支持Google Docs/附件；共享不改变 |

复用AUTH-014已有app-owned Keychain与当前读scope，不申请token/admin/write/scope、不接个人Passwords、不新建/编辑/删除/分享源对象、不调用付费模型、不重启8094/8100。批准发现范围不等于批准新测试种植；当前AUTH-003已有种植范围按各次具体操作核对。身份/范围变化、缺scope、计费提示立即停止该源。

## 最小实现与验收

1. 新增默认关闭的固定container discovery配置，独立本地runner先mock测试分页、越容器、错误身份、429、游标/发布失败。列表结果不是权限allow；新资源仍由现有delegated reader逐阶段验证。不能从客户端/LLM更改container或JQL。
2. 初版loopback进程内轮询，正常条件目标60秒周期；每页最多15–50项（按源规则），每轮最多100新/变更对象。上限/分页未完成标backlog，不将不完整扫描当删除；只有完整成功对账才标失去访问候选，源deny直接停用。无大型worker/向量数据库。
3. 新增发现、已知更新和ACL复核分别记录：source_confirmed_at、observed_at、indexed_at、answerable_at、native_reads与各阶段耗时；同一已发布版本的content hash/精确窗口关系仍校验，不能缓存allow。
4. 更新/删除通过有界全容器对账+已知对象当前读验证，不仅用created/updated过滤，防止漏掉删除或无updated的访问变化。Slack编辑旧消息需重扫批准时间窗或精确重读已知IDs，不能只追latest游标；实际成本/限流测后再缩。
5. 多次创建/更新/删除及断连恢复按源、persona、fake/live model分列，超周期/分页上限不承诺新鲜度；对限流保留Retry-After/backoff，不能硬写SLA。当前本文件仅方案，所有native新发现/时延验收not_run。

## 官方接口依据（本轮只读核对）

- [Confluence pages in space](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-spaces-id-pages-get)：返回该用户可看的页，read:page:confluence；列表不能替代模型前当前权限复核。
- [Jira issue search](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/)：增强JQL search，Browse Projects/issue security过滤，classic read:jira-work；索引一致性不能当即时发现保证。
- [Drive files.list](https://developers.google.com/workspace/drive/api/reference/rest/v3/files/list)：q/fields/pageToken与drive.readonly；parent筛选固定，拒绝incompleteSearch作为完整扫描。
- [Slack conversations.history](https://docs.slack.dev/reference/methods/conversations.history/)：user history scopes；内部应用与商业非Marketplace的限流不同，不能凭app安装即假设50+/min。

2026-10-06 用户明确回复“批准上述四个固定范围”。授权仅下表既有eng_b身份、四个固定容器及Slack既有root时间窗，其他边界不变。实现与native发现/时延验收仍not_run。
