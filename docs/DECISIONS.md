# Decisions / ADR

## 2026-10-04 · AUTH-001 · approved local scope

用户本次明确授权本仓库内本地、可逆、无新增费用的完整开发、测试、独立分支和小步提交，范围不再限于 Phase 0。G0 **仅本地开发部分获批**；四源真实账号/数据/scope、运行时模型、费用及数据出口待定。G1/G2 未通过。凭据存在不代表可用。无远端推送、公开部署或业务系统写入授权。

## ADR-001 · local implementation baseline

盘点基准 `68e65c8`：只有文档，Python 3.14.7 / Node 22.23.2；未发现 Docker、uv、FastAPI、pytest 等依赖。先用 Python 标准库、SQLite 和同源原生 Web UI 构建可重现本地闭环，避免安装/云资源依赖。Python unittest 实测安全边界；SQLite 事务维护版本与日志顺序。关键词检索先建立确定性基线，语义检索/真实模型效果仍待实现与授权。

代价：stdlib HTTP 服务仅允许 loopback 合成演示，不可作为生产部署；SQLite 不具备 PostgreSQL 独立数据库写角色隔离，A-02 不能因此通过。后续公开部署前迁移受支持 Web 框架、生产身份和数据库角色。迁移保留 SourceAdapter、Evidence、Model 接口和回归测试；不得放宽安全要求。

## ADR-002 · Tencent task reservation

当前工具注册表无 CodeBuddy/WorkBuddy 调用工具，PATH 未发现 CLI；不扫描/使用凭据、不调用收费开发入口。预留 DEV-09-CB：独立签名审计检查点及验证器（`tools/audit_verifier/`、`tests/codebuddy/`），由真实 CodeBuddy 实现；Codex 完成日志契约和基础 hash-chain，持续推进同步主线。选择此任务替代原 DEV-05，是为了在人工接力前不阻塞动态更新与五场景本地开发。签名与独立信任根未交付前 A-03/A-04 仅可报告局部链检查，不能标全通过。

## ADR-003 · source-linked retrieval and durable demo authority

自然语言 S-01 回放首次遗漏 PAY-103，证据保存在 first-scenario-failure.json。保留原 oracle，增加最多一跳、逐 seed 和目标授权的链接扩展；固定候选/字符预算。没有按题目硬编码业务答案。来源权威独立持久化到 `.runtime/source.json`，每次授权检查重新读取，避免生成期间的磁盘撤权只在下一 HTTP 请求才可见。源事件处理是 request-driven demo 模式，未实现真实 webhook/后台定时同步。

## ADR-004 · honest audit scope and acceptance

审计范围先在参数化 SQL 按获准 actor 过滤，再按精确 source/resource_scope 定位请求并返回其生命周期；因此可还原问题和最终回答，而不只看到孤立资源事件。自然语言仅支持文档模板，模糊/任意 SQL 拒绝。签名检查点由真实 CodeBuddy 独占实现；在此之前 S-05 只能标 passed_local_subset，A-02/03/04 的完整验收不通过。浏览器工具 localhost 被 ERR_BLOCKED_BY_CLIENT 阻挡，视觉验收不伪造。


## 2026-10-04 · AUTH-002 · CodeBuddy execution and local evidence

用户明确授权 Codex 直接操作已安装的 VS Code CodeBuddy、必要时安装官方 CLI、协助过程截图。已验证插件 4.12.38765564 可用，因此采用真实插件入口，无需新增 CLI。允许将本项目开发任务与代码交给该工具使用现有开发额度；不将此扩展为应用 runtime 费用/真实业务数据授权，不自动充值。截图与对话证据只保存在 ignored 本地目录，不自动上传。

CodeBuddy worktree 基于已合并的 81df3ef，避免从旧基准遗漏最新任务包；v1 hash 契约不变。Codex 仅进行任务下发、命令审查、测试和后续集成，签名验证器代码由 CodeBuddy 实际生成，分别记录来源。未自动合并或推送本轮分支。

## ADR-005 · 2026-10-04 · 真实 CodeBuddy 审计签名集成

CodeBuddy 插件在隔离 worktree 实现 DEV-09-CB；原提交 `4165ee6`，Codex 审查后 cherry-pick 为 `8cd5088`。使用系统 OpenSSL Ed25519，无新增 Python 依赖或应用运行时费用。Codex 指出初版密钥算法与 bool/int 验证问题，由 CodeBuddy 修正并增加测试；Codex 独立复跑 20 新测试、全仓库 52 测试通过。签名只证明 trusted checkpoint 覆盖的规范化事件，未覆盖尾部、检查点回滚/新鲜度、v1 跨流身份、同账号全面失陷和密钥轮换未被此实现解决。回滚可单独 revert 集成提交，不改变问答链路。真实截图/对话留本地 ignored evidence；未上传/提交比赛。

## 2026-10-05 · AUTH-003 · synthetic live sources and DeepSeek pilot

用户“可以，按你说的来”批准上一轮明确提案：建立比赛专用 Confluence/Jira/Slack/Drive 测试空间，仅写入合成资料，允许在这些空间调整测试身份权限；不接入 NTU 课程 Slack 或既有个人资料。站点/文件白名单和真实账号映射仍需落实。注册验证码、条款接受和授权确认由用户完成。平台采用可用免费/试用方案，不授权收费续订。

DeepSeek 直连首轮总预算上限等值 US$20，仅处理合成资料，不自动充值；OpenRouter 仅备用，未批准额外调用。密钥通过本地忽略配置提供，不能发到聊天或提交 Git。配置存在不等于 live 验收完成；预算控制与输出校验完成后才开启调用。G0 部分授权扩大，不标整体通过；G1/G2 仍待人工验收。

## 2026-10-05 · AUTH-004 · Confluence trial agreement

用户在展示具体 Customer Agreement、隐私政策与 30 天 Premium 试用后明确回复“同意接受”，已点击 Try now 并验证开通。仅授权免费试用，不授权付费续订。账单显示 2026-11-04 到期、Payment info None，且提示未补付款方式将停用；不能把通用自动降级说明当成本账户保证。到期前人工检查并选择 Free，避免演示中断。截图仅本地 ignored 保存，API/ACL live 验收仍 not_run。

## ADR-006 · 2026-10-05 · 委托读取与集中端到端验收

根据用户明确反馈，停止逐页人工平台权限点验，保留一次接通问答链路后的真实撤权/同会话/引用历史验收。实现首个只读 Confluence pilot：凭据身份用 current user accountId 实测比对，不回退到管理员；页面与空间 ID 白名单，metadata/body 双读取一致性，无允许缓存。平台不提供 ACL revision 时 policy_version=0，不能替代真实 ACL 版本。仅支持普通合成 storage 文本；宏/附件拒绝使用，避免忽略子资源权限。暂不接入原 FixtureWorld/Engine，以免假身份及 fixture 模式掩盖真实模型/权限差异；下一步显式 live authority 与服务端 session 接线。配置只保存 env reference，CLI actor 是操作员诊断参数，非产品身份。真实 scope/token 创建仍未执行。回滚可单独移除 reader/probe，不影响 fixture 应用。

## ADR-007 · 2026-10-05 · 未知模型消耗保留预算

预算使用 integer micro-USD（总上限 20,000,000），SQLite BEGIN IMMEDIATE 串行预留。网络发送前持久化 dispatched；超时/进程崩溃不自动退款，未知用量继续占用全部预留。只可取消未发送请求。真实费用结算超过预留时先记录实际值，再冻结后续发送并报错，不能把超支隐藏为成功。账本不控制供应商账户其他调用；需固定模型价格/token 上界与官方计价后接入 provider，未接入时不声称预算保证。

## ADR-008 · 2026-10-05 · 共享问答引擎的操作员 pilot

保留 fixture 应用默认身份和模式；为 Engine 增加显式 tenant/mode 与 authority prepare/prefilter 接口，Confluence 每次查询重新委托读取白名单页面，用本次获准快照过滤持久索引。model_dispatch 增加整组证据重查；历史无证据时也验证 actor/tenant。操作员 CLI 没有前端登录路由，不能将 --actor 当员工认证。native 读取/索引/审计使用同一问答引擎，避免另写一套绕开安全测试的展示逻辑。

依据官方 scoped token 文档，API base 固定到 api.atlassian.com/ex/confluence/{cloudId}，而引用仍由后端构造站点 URL；UUID 与站点分别严格校验。代价：小范围每次读取并非后台同步，多轮 HTTP 无原子撤权保证，真实身份/前端及传播延迟仍待测。14 新 mock query 测试与全回归 91 测试通过；无真实 API 调用。回滚可移除 query pilot/CLI，恢复 Engine 的默认 fixture 路径，保留新增租户校验。

## 2026-10-05 · AUTH-005 · eng_b scoped token 配置

用户在具体行动时选择“批准此范围”：eng_b 的 `AI-Bang2 eng_b read-only pilot` token，2026-10-20 到期，拟选 `read:page:confluence` 与 `read:content-details:confluence`，程序只读白名单合成页面；最终创建和密钥保存由用户亲自完成。此批准不覆盖 product_ops token、写入/admin scope、既有个人资料或新增收费。先前自动审批拒绝配置动作；得到这次具体批准后方继续，不绕过拒绝。


## ADR-009 · 2026-10-05 · 多源委托与Jira内容版本

证据：官方Jira Get issue/current user/Get comment约束、现有Engine整数version契约、Jira字段/评论无可依赖整数正文revision。采用固定native ID/key/project白名单、每次myself验证员工、评论单独GET，不将父权限推广到子资源。Jira locator保存完整SHA-256；兼容version为前15hex整数，非原生revision/非单调序号。事务中碰撞检测，最终当前读取还比较完整payload，不能因短hash相同复用旧正文。共同DelegatedAuthority保留Confluence接口/CLI兼容；不足：白名单按请求刷新、无后台worker/原子ACL事务/附件。可回滚Jira/general pilot改动，保留原Confluence基线。

## ADR-010 · 2026-10-05 · 本机操作员网页会话

为尽早联通真实reader与现有产品UI，提供单一已映射操作员的loopback入口：TTY隐藏输入→服务端验证native账户→随机一次性10分钟ticket→HttpOnly/SameSite/CSRF session。浏览器不接API token、user/role选择；每次业务读取仍验证源身份/权限。ticket是本机入口凭证，不入Git或截图，消费后不可复用；退出/重启需新入口。此方式只满足本机操作员试点，不能宣称员工OAuth/SSO或多用户生产鉴权；网页真实验收仍需实际执行。保持fixture demo独立路径，避免bootstrap入口让fixture身份转入真实API。无新增平台scope、费用或公开监听。


2026-10-05 ADR-010修正：8081实际已有operator服务，复现启动端口冲突；将监听socket预留移到隐藏输入前，避免重复输入token后才发现端口不可用。使用同一reserved listener，identity通过后才挂接application和serve，避免预检查释放端口的竞争窗口。固定阶段错误码代替统一失败，禁止异常原文/上游响应日志；不终止未知归属的已有服务，不改变身份/ACL验证。新增失败路径与资源释放验证；无新增外部调用。


## 2026-10-05 · AUTH-006 · eng_b Jira read-only pilot

用户明确“批准此范围”：必要时仅在免费额度内启用 eng_b 普通 Jira User；token `AI-Bang2 eng_b Jira read-only pilot`，2026-10-20 到期，拟用 `read:jira-user` 与 `read:jira-work`，无 write/admin scope。scope 覆盖账号可读 Jira 内容，程序另限 KAN 合成工单白名单。最终创建、密钥保存由用户完成；收费、条款或不同 scope 需要另外确认。授权不等于凭据已创建、API 已验证或 G1/G2 通过。

AUTH-006 执行限制：只读账单核验显示 Jira 已为 Premium 免费试用而非 Free；2026-11-04 到期，付款方式 None、未来估价 USD18.30/1 user。自动审批拒绝保存新增 Jira User，要求具体试用范围确认；配置仍未提交，不将拟选 User 当已授权访问，不自行购买或接受新条款。


## 2026-10-05 · AUTH-007 · existing Jira free trial User access

用户明确选择“批准仅现有免费试用期内添加 User”，覆盖当前 Jira Premium 免费试用内 eng_b 普通 User，至 2026-11-04；不添加付款方式、不购买、不授权付费续订，到期前人工降级或停用。解决 AUTH-006 执行时的自动审批范围拒绝后已保存，页面核验 Jira User。随后平台显示 Teamwork Collection upgrade 推广，关闭且未下单；不据此扩大资源/收费授权。Jira token 仍按 AUTH-006：用户最终创建/保存。


## ADR-011 · 2026-10-05 · 复用操作员进程中的 Jira 凭据

用户指出独立诊断命令反复要求邮箱/token 造成操作负担。每次权限重查不要求重复人工输入凭据，因此扩展现有 operator web 到 Jira，并保留默认 Confluence 兼容。token 只驻留服务进程，固定 source/actor、独立数据库、一用 ticket/opaque session，查询仍 native identity/current access 检查；不缓存允许决定、不读取密码应用、不持久化秘密。代价：进程停止后再次输入，当前每进程单源/单操作员，SSO/多源同入口后续实施。可单独回滚 --source Jira 分支。


## ADR-012 · 2026-10-05 · 导航时清除旧答案视图

真实Jira撤权后，后端query/citation/history正确deny，但Workspace导航复用之前渲染DOM，违反新访问不恢复旧内容的产品要求。选择导航清除答案/隐藏历史、query开始清除旧答案、preview失败清除相关视图；继续保存historyId以便服务端重查追问依赖。代价是返回Workspace需新问答或Recent answers获取重新鉴权的历史，不能保留不经检查的旧视图便利。不声称能消除用户已看到/截图保存的内容，也不承诺平台ACL变更瞬时推送。node frontend安全验证及真实会话重载后UI验证通过，无服务器重启/凭据重输。


## 2026-10-05 · AUTH-008 · Slack user read-only pilot

用户明确“批准此只读试点范围”：AI-Bang2 workspace T0C6FQ246TF 准备/安装 AI-Bang2 Read-only Pilot app，user scopes channels:read/channels:history/groups:read/groups:history；无 Bot/write/DM/files scope。首轮使用个人Google登录身份，程序另限合成频道/消息白名单，不接NTU Slack。10月20日前人工撤销试点 token；最终授权/密钥保存由用户完成，新条款/费用另确认。批准不证明实际安装或API/ACL验证完成。


## ADR-013 · 2026-10-05 · Slack 原生用户读权限与精确消息试点

采用固定 workspace、user delegation、channel type 与 exact message/root mapping；每读先 auth.test/info，再正文，无 bot/admin fallback。公开频道不以 is_member=false 伪造撤权，真实撤权使用 private channel；不支持的共享频道/附件/富文本 unknown，不静默剥离后声称完整覆盖。成本是首轮对象覆盖有限且重复原生检查可能遇限流，后续仍须 native root/reply/API 验证；可单独停用 Slack reader，不改变其他源。错配 source/reader 在构造时明确拒绝。用户最终安装遇应用创建限流，未创建成功/取得 token；保留审核页面，相关 live 任务 blocked，其他本地工作继续。


AUTH-008 补充（2026-10-05）：原生OAuth审核另显示基础identify与应用隐私/条款，已明确交用户审核；用户回复“授权完成”。授权/接受为user_confirmed，agent未点击Allow或读取token。Chrome更新后的列表实际已有四个同名app，选择A0C6F96HFNX继续，其他保留；早先“未观察创建成功”不代表未创建，停止重复新建。等待用户保存并离开token页。

## ADR-014 · 2026-10-05 · Drive 最小委托文本文件边界

先支持固定file→parent白名单的personal Drive text/plain UTF-8文件；about.user.permissionId/me验证当前用户，文件原生GET与canDownload而非本地permission列表授予权利，正文前后重复metadata排除读写竞态。验证size/MD5传输一致性，另保存SHA256证据指纹和headRevisionId/native version，不编造页码。缺点为暂不支持Google Docs/PDF/shortcut/shared drive、后台changes与完整继承传播矩阵；这是覆盖范围限制，不能当四源live通过。移出白名单目录unknown、删除/原生deny停止，网络/过期未知不放行。尚未申请Drive scope或使用凭据；真实OAuth/平台种植需具体授权。本地可回滚停用drive reader。
