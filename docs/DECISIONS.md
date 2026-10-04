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


## ADR-015 · 2026-10-05 · Slack reply诊断与受限父消息响应

真实root问答通过但reply为统一unknown，尚未得到具体失败原因。增加只由固定枚举组成的unknown method，区别rate/scope/identity/argument和message selection，不存上游错误body/秘密。回复limit2且只允许exact target与预先allowlisted parent出现，父消息不替代目标、非白名单/重复/缺目标unknown；补两项边界测试，199全回归通过。此兼容只是候选修正，非实测原因结论；需重启原生API复验才能判断。代价为诊断需加载新代码/一次重新输入秘密，后续仍凭据进程内复用。四源安全要求不变。

ADR-015实测补充（2026-10-05）：用户重启后，受限父消息响应兼容实现的root/reply问答、引用与历史已native验证通过（web-thread-query.json），可保留此实现。未记录旧unknown响应内容，不把本次成功当旧失败原因的确定证明。未扩大scope或消息白名单，真实频道撤权仍待独立reader。

## ADR-016 · 2026-10-05 · 统一操作员多源入口

复用DelegatedQueryPilot与现有HTTP路由，使2–4来源在同一tenant/actor会话中检索。可信本地manifest记录身份映射已核对；该标记不是账号所有权证明，也不授予权限。所有source配置/actor映射/tenant先验证，缺少凭据才隐藏输入一次；全部native身份通过后才签发bootstrap，任一失败停止启动，查询时各源unknown/deny只隔离该源。同一历史含撤权依赖则不展示，新的独立查询仍可用其他授权源。代价是尚需人工核对跨平台persona，不能将现有eng_a和eng_b直接改名拼接；每进程独立credential/session/DB，SSO/OAuth refresh另行实现。可回滚停用multi入口，不改变单源行为。

## 2026-10-05 · AUTH-009 · Drive personal-account read-only pilot

用户明确选择“批准此只读范围，使用现有个人 Google 账号”，账号ssy44199@gmail.com；创建比赛专用Google Cloud项目，不启用Billing，仅启用Drive API，OAuth测试模式申请drive.readonly。该scope本身可读授权账号全部Drive文件，程序仅白名单合成文件；不读取个人资料，不扩scope，不付费。最终Google授权由用户点击，凭据按现有本地隐藏输入/进程内复用，不入Git/日志/浏览器。授权不证明项目/OAuth/原生ID/API/ACL完成。新条款或安全敏感持久凭据最终创建按页面另确认/交用户，不自行绕过。

AUTH-009执行补充（2026-10-05）：用户已亲自完成Google Data Policy确认/Create，UI核验OAuth配置成功；唯一drive.readonly配置保存、External Testing和单一test user已核验，尚未授权任何token。Desktop客户端在审核页准备，按UI AI-agent分类help标记agent用途，不创建standard-user第二客户端。最终Create/Download JSON交用户；不读取生成密钥页面，不新增write/profile/email scope或Publish/Billing。

## 2026-10-05 · AUTH-010 · exact Drive synthetic seed writes

用户明确“批准创建文件夹并上传这三份合成文件”，覆盖ssy44199@gmail.com个人Drive根目录AI-Bang2 Synthetic Read-only Pilot和D-01.txt/D-02.txt/D-03.txt，内容来自baseline fixture并标记SYNTHETIC，不修改已有文件/共享权限/公开分享。此前自动审批因只读scope授权未明确覆盖持久写入拒绝create_folder；这次具体确认后工具允许创建与上传。Google Drive plugin确认账号及种植读回，应用runtime仍只读。

## ADR-017 · 2026-10-05 · Drive Desktop PKCE loopback

为减少手动token复制，--oauth-client仅Drive/live入口支持，先预留operator端口并验证全配置，再读取用户下载的0600/no-symlink桌面client JSON。固定Google授权与token端点、唯一drive.readonly/S256/random state/10分钟/随机loopback端口，callback不记录URL/code，不反射秘密，拒绝错Host/Origin/state/重复/扩展参数，code单次交换。验证实际授予scope与Bearer/寿命，再about metadata-only核对me/emailAddress/permissionId，按可信配置绑定actor；login_hint不作为身份依据。秘密只进进程，忽略refresh token，不持久化、不读个人文件列表、无写权限/自动打开浏览器。代价：当前access token过期需重新Google授权，非员工SSO或后台refresh。11新模拟测试/全218通过，真实Google最终grant仍待用户，不能称live OAuth验收通过。可回滚--oauth-client分支，保留hidden token路径。

ADR-017修正（2026-10-05）：Google官方discovery声明authorization_response_iss_parameter_supported=true/issuer=https://accounts.google.com；旧callback未知参数过滤会将含标准iss的合成合法响应拒绝400，已复现。新增iss且必须精确Google issuer，缺失/错误/重复仍拒绝；不放宽state/PKCE/scope/账号。固定枚举诊断仅记录reason，不记录请求URL/code/上游body。旧真实callback未记录原因，因此此项是确定兼容缺陷，不是旧现场根因的已证实结论。参考https://accounts.google.com/.well-known/openid-configuration 与RFC9207。

## ADR-018 · 2026-10-05 · DeepSeek evidence selection and conservative accounting

AUTH-003批准的DeepSeek直连/合成-only/总USD20保持不变。实读官方pricing与chat-completions页面（evidence/runs/deepseek/price-review.json），采用deepseek-flash/非thinking/JSON/1024输出tokens；固定HTTPS端点，无redirect、tools、stream或自动retry。价格按peak/cache-miss输入USD0.30/百万和输出USD1.20/百万保守记账，不冒充发票实际费用；每请求预留整个1M上下文上限+输出上限，不将字节误当token。未知usage/timeout保持全额预留，使用既有持久USD20账本；所有operator共用.runtime/deepseek-budget.sqlite，不能换目录/删账本重置预算。账本只限制本程序，不控制账号其他客户端。

Engine原生鉴权链保持，模型只输出已提供evidence IDs，后端从当前授权证据组装完整原文，不允许模型输出新事实/URL/自授权限；重复/未知ID、额外字段、工具调用、截断/错模型均失败，已知usage仍结算。这个阶段是live model evidence selection接口，不是自由综合回答或效果已验收；遗漏相反/限制证据的语义完整性仍需真实效果验收，不能用引用校验代替。仅显式标记[SYNTHETIC的源正文可发送，不将该标记当身份/源ACL。价格复核限定SGT2026-10-05，启动与每次非空调用均校验；以后先复核官方价格再更新，不静默沿用。key一次hidden TTY进内存，不写文件/浏览器/日志，默认fake不变；旧服务不热注入或读取其进程秘密。独立新8086 Drive OAuth进程用于真实模型验收。

预算SQLite新增进程内RLock/check_same_thread=False以支持Web worker；跨进程仍BEGIN IMMEDIATE保证预算预留。回滚provider/--model入口不影响四源reader，必须保留既有账本用于核销。G1/G2仍待批准。

## ADR-019 · 2026-10-05 · Model budget receipt linked to server request

为解决首轮live只能按单一reservation现场关联的证据缺口，增量model_calls表与reservation/query_id关联在同一预留事务落库；Engine传服务端UUID，provider不从Prompt取identity/request ID。validated usage与保守成本结算原子提交，失败状态固定enum，无原始vendor body/key/问题/资料正文。成功generation_completed审计事件保存同一receipt；失败通过query_id连接request_failed。dispatched只代表持久化发送意图：called=None，不冒充已收到供应商回复；settled/validated usage才called=True，空证据called=False且不建reservation。旧reservation保持unlinked，不能事后猜测添加query_id。本地账本不是独立签名或供应商发票。新增getpass warning-as-error，不能降级为终端明文输入。迁移不修改已有预算/额度，回滚Engine/provider接线仍保留table/既有支出。

## AUTH-011 · 2026-10-05 · unified eng_b reader preparation

用户明确“批准按推荐范围准备独立读者”，账号674544786@qq.com，保留CF/Jira既有eng_b；准备该邮箱Google免费注册/登录、仅比赛AI-Bang2 Slack普通reader成员、现有三合成Drive文件folder Reader共享。后续Drive drive.readonly（该新reader账号全Drive平台范围但程序三文件白名单）、Slack channels:read/channels:history/groups:read/groups:history+identify同试点scope；不接NTU/DM/bot/write/Billing/公开sharing或增模型预算。最终password/OTP/terms/OAuth由用户亲自操作，新收费或不同权限另确认。授权范围已获批，不代表reader账户、membership、native权限/API或完整四源验收已完成。具体候选与接口见UNIFIED_LIVE_PILOT.md。

## ADR-020 · 2026-10-05 · multi-source Drive PKCE

统一入口--source multi允许--oauth-client；先读public OAuth mapping构造无credential reader，再全部source actor/tenant验证，才读取private desktop client并按需hidden其他source；Drive不手工复制access token。客户端无效先于人工输入，Google拒绝不能返回partial bundle，全部native身份通过才bootstrap。load_oauth_reader单源接口保持，拆分prepare/complete共享实现，无扩scope/自动persona合并。example默认identity_mapping_reviewed=false；AUTH-011未完成native身份确认前不改为true。5新mock配置/CLI测试通过；此前新增测试缺续行SyntaxError已复现修复，单独OAuth HTTP测试在沙箱bind拒绝，完整许可本机回归248/248通过（60local/188mock）。本轮未调用真实平台/模型、不重启旧服务。

2026-10-05 AUTH-011 amendment: user confirmed kyle000909@gmail.com as eng_b Google/Drive identity, replacing QQ Google registration; existing Atlassian identity retained. Cloud test user saved and exact synthetic folder Viewer sharing read back; general access remains Restricted, notification unchecked. This does not establish API identity or grant. Slack still uses the specifically approved QQ email pending membership.

2026-10-05 Slack reader invitation: native UI returned Unable to send / Couldn’t invite for 674544786@qq.com; cause not established, no membership claimed. Drive reader process started on8087 (fake model), OAuth waiting user final grant, credentials not entered or copied. Private screenshot reader-slack-invite-failed.jpg.

2026-10-05 AUTH-003权限测试执行：仅在已批准合成folder移除eng_b Reader以验证同会话撤权，再恢复相同Viewer/Restricted范围，无公开share、正文编辑或新scope。原生Drive版本因权限分享从3至4变化但正文hash相同，按保守原生版本校验处理，不把权限引起的version变化记为新企业事实。

2026-10-05 AUTH-011 Slack amendment：用户明确批准eng_b Slack也用kyle000909@gmail.com，限AI-Bang2工作区和合成私有频道，原四项user只读scope+identify，不接NTU、不新增付款或写scope，最终terms/OAuth用户点击。QQ邀请失败原因未知，新Google邮箱邀请UI显示You’ve invited 1 person/Invited as a colleague/Expires in30days；仅邀请成功，尚未入组或授权。

2026-10-05 Slack reader OAuth准备：保留既有私有app原生install_redirect流程，未启用public distribution、未新增redirect或读取client/signing secret。用户既有Google登录用于主账号添加已批准的内部reader成员，随后仅Sign out切回reader，明确未选择leave workspace。只有最终Allow授予读权限，由用户操作；固定eng_b原生ID映射将在启动auth.test再次校验。参考Slack官方OAuth说明：https://docs.slack.dev/authentication/installing-with-oauth/。

2026-10-05 AUTH-011边界补充：普通Slack reader成员与只读OAuth批准不包括app Collaborator开发后台权限。平台在Allow后要求Collaborator，采用grant未知/token后台blocked记录，不默认新增权限。临时协作者候选仅kyle000909@gmail.com与app A0C6F96HFNX；其可管理app设置，因此另行征求明确授权，未批准前不执行。

2026-10-05 AUTH-012：用户对上一项明确候选回复“好的，可以”，批准kyle000909@gmail.com临时成为existing app A0C6F96HFNX Collaborator，token保存后移除。native UI候选及名单均确认U0C66B76TE3。平台明确可edit/submit/delete app、full member可管理collaborators；本次未修改scope/public distribution/付费/工作区admin。移除尚pending，不把临时developer访问视为业务资料可读证明。

2026-10-05 用户报告eng_b Slack token保存并离开密钥页；agent未读取秘密。按AUTH-012从已核对U0C66B76TE3自己的Collaborators页面Leave，native确认移除后Your Apps不再列出该app；未退出工作区/频道、未卸载业务OAuth grant。截图private/slack-reader-collaborator-removed.jpg。四源public配置均加载校验同tenant/actor，Drive映射kyle000909@gmail.com、SlackU0C66B76TE3与既有QQ Atlassian对应用户已确认persona；创建ignored0600 operator-bundle.json（mapping reviewed仅表示账号映射审查，非API验收）。下一步一次启动8088 multi+Drive PKCE+DeepSeek并逐source native identity强制核对。reader Slack API/统一live问答/撤权仍not_run；没有新模型调用。
