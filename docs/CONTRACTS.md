# Local contracts v1

状态：实现基线，模式固定 fixture_fake_model。`brain/contracts.py` 是类型入口。

- 身份：仅服务端 opaque session → Actor；仅显式 loopback demo 登录允许从六个固定合成用户选取。业务 API 拒绝额外 user_id/role/tenant 字段。
- 稳定资源 ID 为 demo 内逻辑 ID；tenant/workspace/native_id 单独保存。真实模式未启用，fixture 链接用 `fixture://`，绝不冒充平台 URL。
- 每资源有 current version、active 和 source policy；local ACL snapshot 只负责候选过滤，current source policy 决定模型输入。J-01 的受限评论为独立子资源。
- SourceAdapter 的 list_initial/list_changes 返回 items 与 next_cursor；source revision 单调递增，事件以 event_id 幂等。源状态与索引状态独立保存，便于测试 stale ACL / interrupted indexing。
- Evidence 按 `resource_id@version` 定位，所有引用访问重查当前权利和版本。旧版默认不提供正文。历史/导出必须重查依赖，缓存关闭。
- Model 输出 claims[{text,evidence_ids}]、uncertainties；当前 fake provider 返回动态检索到的原文摘录，不硬编码题目答案。fake 的引用支持验证采用 exact extractive contract；不能推断真实 LLM 语义质量。
- 审计事件 v1：seq, previous_hash, event_type, actor, request_id, timestamp, payload, hash。规范化 JSON 为 ensure_ascii=False, sort_keys=True, separators=(',', ':')；hash = SHA256(b'ContextLedger.audit.v1\0' + canonical event excluding hash)。起始 previous_hash 为 64 个 0。
- 审计 payload 保存问题、逐资源授权、实际模型输入证据 ID、最终回答和 dispatch 阶段；受限审计员只有 eng_a/eng_b/product_ops 范围。端点无任意 SQL。应用 SQL authorizer 是逻辑防护，不宣称独立 DB role。
- CodeBuddy 独立签名验证器以导出的 JSON 数组为输入，签名 trusted checkpoint 的 schema/编码须与此契约一致；其路径由任务包独占。
