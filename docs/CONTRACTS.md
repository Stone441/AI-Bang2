# Local contracts v1

状态：实现基线，默认演示模式 fixture_fake_model；委托operator模式另列。`brain/contracts.py` 是类型入口。

- 身份：仅服务端 opaque session → Actor；仅显式 loopback demo 登录允许从六个固定合成用户选取。业务 API 拒绝额外 user_id/role/tenant 字段。
- 稳定资源 ID 为 demo 内逻辑 ID；tenant/workspace/native_id 单独保存。真实模式未启用，fixture 链接用 `fixture://`，绝不冒充平台 URL。
- 每资源有 current version、active 和 source policy；local ACL snapshot 只负责候选过滤，current source policy 决定模型输入。J-01 的受限评论为独立子资源。
- SourceAdapter 的 list_initial/list_changes 返回 items 与 next_cursor；source revision 单调递增，事件以 event_id 幂等。源状态与索引状态独立保存，便于测试 stale ACL / interrupted indexing。
- Evidence 按 `resource_id@version` 定位，所有引用访问重查当前权利和版本。旧版默认不提供正文。历史/导出必须重查依赖，缓存关闭。
- Model 输出 claims[{text,evidence_ids}]、uncertainties；当前 fake provider 返回动态检索到的原文摘录，不硬编码题目答案。fake 的引用支持验证采用 exact extractive contract；不能推断真实 LLM 语义质量。
- 审计事件 v1：seq, previous_hash, event_type, actor, request_id, timestamp, payload, hash。规范化 JSON 为 ensure_ascii=False, sort_keys=True, separators=(',', ':')；hash = SHA256(b'ContextLedger.audit.v1\0' + canonical event excluding hash)。起始 previous_hash 为 64 个 0。
- 审计 payload 保存问题、逐资源授权、实际模型输入证据 ID、最终回答和 dispatch 阶段；受限审计员只有 eng_a/eng_b/product_ops 范围。端点无任意 SQL。应用 SQL authorizer 是逻辑防护，不宣称独立 DB role。
- CodeBuddy 独立签名验证器以导出的 JSON 数组为输入，签名 trusted checkpoint 的 schema/编码须与此契约一致；其路径由任务包独占。

## Delegated operator reader contract · 2026-10-05

新增多源操作员 pilot 的 reader 返回 `(Decision, content | None)`，每次读均验证凭据的原生员工身份；tenant、源与 native ID 白名单不可由问答扩大。content沿用Evidence字段；评论为单独资源，不并入父工单。Jira固定issue ID→key、project ID及comment ID→parent ID，只请求选定字段与单条评论，不请求附件/列表/任意JQL。unknown不出正文。

Jira没有可依赖的工单整数正文版本：locator保存完整SHA-256（正文/标题/状态/负责人/updated/原生ID），兼容索引的version为其前15个hex转整数，**非原生revision/非单调版本**。最终授权另外比较完整content payload，短ID碰撞不得继续放行；旧内容不凭当前可读而恢复。按对象事务切换，权限更新不改变正文版本。固定白名单请求刷新不是后台增量worker。模式逐源注明mock/live且model明确fake，禁止真实传输被标mock。

默认前端仍fixture；另有服务端核对native身份/一次性bootstrap的operator网页，不是员工SSO。此合同不授权新token/scope或外部调用。

## Signed checkpoint v1（DEV-09-CB 实现）

离线 CLI 位于 `tools/audit_verifier/`。JSON wrapper 包含 `schema_version:1`、`algorithm:"ed25519"`、`checkpoint`、base64 `signature`；`signing_backend` 仅为说明。签名消息为上述 canonical 编码的 checkpoint UTF-8 字节。checkpoint 包含 `schema_version:1, stream_id, through_seq, head_hash, timestamp`。序号/版本必须是整数，bool 不被接受。

验证器显式接收外部可信 checkpoint、公钥和 expected stream ID，使用 OpenSSL 校验 Ed25519 密钥类型与签名，独立重算导出链。退出码 0 仅表示已覆盖段通过，未覆盖尾部始终单列；1 失败；2 无检查点、不可信。签名不保护 wrapper 的说明文本。

v1 事件不含 stream_id；该字段只绑定检查点的外部期望，不能据此宣称事件原生跨流隔离。选择最新可信检查点、独立保管、密钥轮换仍由后续机制保证；同机同账号的测试不提供这些生产边界。


Jira ID setup discovery 独立于正文读取：显式 discovery_only reader 只接受预先批准 issue key→project key，验证 native 身份后 GET 单工单 `?fields=project`，仅返回 issue/project ID 与 key。该 reader 不允许 read/模型/索引；正常 reader 仍要求不可变数字 ID 白名单。错误身份、移动项目、非法 key 和未知结果均不出元数据。

Operator web 支持显式 --source jira（默认仍 confluence），独立 .runtime/{source}-web.sqlite。每个服务进程隐藏输入一次，内存复用 Delegation，每个业务请求仍重验 native identity/当前源权限；不持久化 token，不从密码管理器自动提取，不提供浏览器角色授权。Jira discovery_only reader 不允许绑定网页。
