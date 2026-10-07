# Local contracts v1

2026-10-07有界cap跟进：a3569a1完整24题为21正确事实返回＋2空＋03复核length失败（2048个reasoning tokens，无final）。仅新增可信4096候选档，生成/复核同cap、按实际cap预留和usage上限检查；默认1024保持，未知cap8192等仍拒绝，4097超4096实测mock冻结并保留reservation。原03失败保留、不自动重试；先单题诊断，再据实际结果决定是否形成候选，不预称全通过。原生a3569a1进程仍保持启动时加载的2048配置。

2026-10-07可信operator启动增量：--reasoning-effort none|low、--output-tokens 1024|2048默认none/1024；非默认仅DeepSeek synthesis允许，fake/excerpts在listener/凭据前拒绝。两阶段继承配置。native诊断同参数及actual-cap preflight；HTTP用户不能选择。未重启运行中服务。

2026-10-07有界输出cap实验：low/1024一题全部tokens用于reasoning、finish_reason length无最终内容，原失败不升级。可信Python/runner允许1024或2048（默认1024）；instance reservation按1M context＋实际cap peak估计，preflight按同cap两次/题，genreview一致，usage越实例cap仍冻结/保留reservation，缺usage不退款。不是增加原USD20上限、换provider/账号/数据或自动retry；新增显式2048开发对比，效果待实际输出。

2026-10-07有限reasoning配置实验：可信Python/开发runner可指定reasoning_effort none/low，默认none保持非thinking；low以thinking enabled+reasoning_effort low发送且省略无效temperature，两模型阶段一致。仍DeepSeek Flash、原端点/合成范围/1024输出cap/保守peak价格/原共享USD20/reservation；仅parse最终content，不用reasoning_content作为claim或原文。错误配置在reserve前拒绝，思考tokens计入供应商completion usage；未知usage保留预留。不是新模型/客户端授权字段，是否采用待实际比较，不因选项存在标通过。

2026-10-07 synthesis-v8诊断：v7已生成有范围的未知，但review错误coverage拒绝，背景仍responsive true。v8仅澄清review coverage语句：未知前提有范围明确回应、原文记录状态及无同实体/范围正面证据可以覆盖所问项，不要求编造positive；同实体其他属性不是所问属性的回答，必要限定须改变该回答解释。supported/responsive/question_covered仍全严格true，未删除quote/权限/whole-answer断言；效果待实际验证，v7失败原件保留。

2026-10-07 synthesis-v7开发契约：内部review每claim verdict精确含index/supported/responsive；supported与responsive必须分别是布尔true，未知/缺字段/false拒绝整答，不局部删claim放行。question_covered还需明确回应未由引用资料建立的问题前提；“未建立”不等于显式否定或全源无记录。生成先按请求项分配事实，背景只因主题相近不算相关，实际请求的owner/blocker仍需覆盖。公共claim格式、原文/源context、逐阶段权限、原账本/温度0不变；当前语义效果待实际验证，v6旧结果保持原版本。

2026-10-07 synthesis-v6开发：生成/review传入同一已鉴权Evidence的原title/locator作为source_context，与text分开；不据问题推定资源事件，不将context作为指令、原文quote或权限。SyntheticProvenance原来已核title/locator一致，保留批准资源/version/原文切片和整答gate；既有100KB payload上限在reserve前执行。388/389 archive、完整24开发题和两native/model题已验证对应版本；03未知表达及32背景仍未通过，不继承旧版本结果或宣称全部质量通过。

2026-10-07 ADR-056：64b705a trusted Python/operator配置temperature默认0，允许有限数值[0,2]；None显式保留provider默认。generation/review相同值，thinking=disabled；客户端/浏览器无采样授权字段。三开发题各四次同输入比较支持可回滚选择，非确定性/语义保证。原模型、预算、原文窗口、每claim引用及whole-answer gate不变；64b705a的business16误归/business12结构失败证明精确引用＋同模型review仍非语义完备。旧原件保留，当前结果见STATUS。

2026-10-07 synthesis-v4：提案、审批、完成和撤回分别要求明确支持；非审批不推出取消/放弃。无明确问题指代时允许有范围候选事实或空claims，空claims可加通用范围澄清提示。现有结构、精确引用验证、逐阶段权限及整答review gate不变；模型review不能证明语义正确。


2026-10-07 DEV-BV-03 source fault completeness: unknown source authorization in this actor/request (including legacy preparation) stops the next synthesis/review dispatch or final commit. Unknown found before the first send means zero model calls; unknown found after generation/review does not erase prior attempts or charges. Fixture extractive diagnostics may retain allowed excerpts, but return a generic incomplete-coverage notice instead of implying verified absence. No source names, hidden objects, counts or paths are disclosed; audit still retains the original decisions. This extends completeness handling without changing ACL deny filtering or model review acceptance.

2026-10-07 DEV-BV-03 bounded publication: published candidate snapshot never grants current permission. Current native unknown or explicit content/version-changed denial stops the question before sending or committing an answer. ACL denial filters inaccessible candidates. Preview/history retain unavailable semantics; only a fresh complete publication makes the new content eligible. Same-request same-stage resource/version windows share one check; separate model/review/answer stages always reauthorize. No client flags or old checkpoint authorize this path.

2026-10-07 DEV-BV-04: auditor resource-direction inquiry accepts exact resource_id with payment-service scope, optional actor; omitted actor searches only existing AUDIT_ACTORS. Structured parameterized conditions only, stable as_of pagination and inquiry audit retained. Return matching resource decisions plus surrounding request lifecycle, not unrelated resource decisions; events indicate candidate/allow/prepared/attempt/answer separately, never human reading. No new native auditor or payload scope.

2026-10-06 synthesis-v3: explicit structured identifiers (alphabetic prefix plus hyphen and numeric suffix) in final claims must occur in their copied supporting quotes, case-insensitively; an identifier in unrelated/uncited evidence is insufficient. This guards identifier provenance, not full semantic entailment. Minimum necessary claims and requested-event attribution are prompt/review requirements; same-model review remains fallible.

2026-10-06 R5 additive response fields: new committed answers carry server-recorded `question` and UTC ISO `answered_at`; history returns these only after all dependency authorization/version checks. Old records lacking either remain missing, never inferred or rewritten. Unavailable history placeholders expose neither question nor time. Reauthorized evidence preview adds `source`; UI original-platform URLs come only from that successful current preview, require HTTPS, no userinfo/non-default port and source-specific Atlassian/Slack/Google host checks. Fixture URIs have no external link. Long IDs/locator/model-accounting details are collapsed diagnostics. ADR-040 independent queries and late-response invalidation remain unchanged.

AUTH-017 opt-in发现契约见[R2_DISCOVERY_CONTRACT](R2_DISCOVERY_CONTRACT.md)：服务端固定容器与eng_b身份，列表不授予权限，新增对象仍逐阶段当前原生鉴权；无新增浏览器API/客户端synthetic字段。

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


Slack delegated reader：固定 workspace team ID/site、channel ID/public-private 类型、message ts→thread parent 白名单；每读 auth.test 核对 user_id/team_id 且拒 bot/app credential。private channel 要当前 is_member=true，public 权利由原生 API 决定（退群不是撤权）。conversations.info 禁止 DM/跨workspace共享，随后 history/replies 只取指定 ts，子回复独立证据，禁止附件/隐藏 rich content 进入模型。消息删改/受限/unknown不出正文，指纹 version/full payload保护旧历史/引用；限流不默认放行。


Drive delegated reader：固定file ID→parent ID、tenant、原生permissionId身份映射；about(user.permissionId,me)逐读验证，不使用email/Prompt授予权限。personal Drive text/plain UTF-8，原生文件GET和canDownload当前读取权威；alt=media固定HTTPS源、无redirect，metadata前后相同/字节size与checksum一致才返回。locator存file/headRevision/native version/SHA256，不推断旧revision授权。trash/403/404/下载禁止deny；未知/unsupported类型、共享盘、shortcut、父目录变动、竞态unknown；其他同Engine边界不变。

2026-10-05 Model receipt response increment: successful query responses and stored history may include `model_call`. Engine validates server request correlation, accepted/settled state, strict integer token counts and conservative cost bounds; it projects fixed public fields and supplies its own accounting notice, dropping unrelated provider fields. Explicit no-call is allowed only for empty authorized evidence. Historical records without a receipt remain unknown, never inferred from evidence count. Existing citation/history/export authorization applies to the entire response, including its receipt. No new provider request or budget scope is introduced.


## Opt-in local credential persistence · AUTH-014

The reviewed multi-source operator may use --credential-store macos-keychain; memory remains default. App-owned Generic Password items are namespaced by source/tenant/actor/native account, and Drive by client/email. Existing Passwords entries are not accessed. Saving syntactically valid delegation does not validate platform rights: mandatory native identity checks still precede bootstrap and current rights gate every evidence path. Google offline refresh retains exact drive.readonly scope and rechecks the native account; unknown errors fail closed. --replace-credential bypasses only the named saved source for one launch. OS Keychain protection does not isolate malicious same-user code. No token enters browser, SQLite or plaintext files.

DEV-BV-03 2026-10-07：可信operator --discovery-auth017运行时采用bounded_queries。仅活跃、当前完整、无backlog、进程内120秒有效发布的同actor映射用于CPU候选预过滤；不复用allow。失效/unknown为请求暂不可用，不解释为无证据。所有既有native阶段及精确原文/版本边界保留。HTTP与worker统一pilot.lock→store.lock顺序；原library默认旧刷新路径保持。
