# Backlog · 2026-10-05

| ID | 状态 | 已完成 / 仍需推进 / 验收 |
|---|---|---|
| DEV-00 | verified | 仓库/环境盘点，基准 68e65c8 |
| DEV-01 | in_progress | 官方 API 文档核对；真实 spike blocked，SOURCE_CAPABILITIES |
| DEV-02 | verified | 合成数据/授权 oracle/SourceAdapter，78 权限组合 |
| DEV-03/04 | verified local | HTTP/UI/持久库/fake model/身份→证据→回答→审计，Q-01/P-01/A-01 本地子集 |
| DEV-05 | verified local | 请求驱动增量/去重/重试/原子版本/删除 F组；真实 worker/scheduler 待做 |
| DEV-06 | blocked live | 四源 fixture 可运行；专用合成空间操作已批准，账号/站点及用户委托待配置；本地 seed exporter 已测试 |
| DEV-07 | verified local | stale ACL/撤权/unknown/历史/预览/导出/生成中撤权；P组部分真实机制待测 |
| DEV-08 | in_progress | 关键词+授权一跳、exact extractive support；DeepSeek 首轮 US$20 上限已批准；预算账本已测试；模型适配/真实计价与语义检索待实现 |
| DEV-09 | in_progress | 事件链/精确 scope/分页/有限 NL；生产 role/加密未实现 |
| DEV-09-CB | verified local | 真实 CodeBuddy Ed25519 检查点/独立 CLI；20 新测试+52 全回归；A-03/04 本地签名子集，A-11 缺锚点/尾部已测，密钥轮换待做；依赖 DEV-09 导出契约 |
| DEV-10 | in_progress | 英文 Workspace/History/Sources/Audit及Confluence operator入口已联通（mock HTTP验证）；真实网页/SSO待做，浏览器视觉工具阻挡 |
| DEV-11 | verified local subset | 五场景回放+安全测试；不是完整 P0/G1 通过 |
| DEV-12 | blocked | live model / 非作者人工任务测量未运行 |
| DEV-13 | in_progress | 本地候选审查包、运行指南；真实腾讯对话/7截图已本地留存；封面/视频/材料提交待做 |
| DEV-14 | in_progress | 本地小步提交及候选重建；G2/publish 未批准 |

| DEV-06-CF | verified mock contract / live configuration partial | 22 模拟 HTTP/配置测试；用户提供 eng_b / page 98564 的 metadata-only API allow，native space ID 131227 已配置；正文/双身份/撤权及 P/Q 组 live not_run |

| DEV-06-CF-QUERY | verified mock / live query partial | 14模拟查询测试；首个 eng_b C-01 v1 真实 query 的正文/引用/逐阶段授权/11事件链已实际检查 DB，9 checks通过。前端身份/live HTTP、双身份拒绝与撤权待做；非P/Q/F/A组完整通过 |

| DEV-06-CF-REVOKE | verified mock / live operator subset | 5 mock测试；真实原生C-01 eng_b撤权后7 runner检查+7独立DB检查通过，18事件链，追问/模型/旧历史/引用不泄露且保留旧索引。已恢复原Can view，Notify关闭；不等于P组四源/真实前端/真实模型完整通过 |

| DEV-08-BUDGET | verified local | SQLite micro-USD durable reservations；7 安全/故障测试；模型请求和官方计价尚未接线，live model not_run |


| DEV-06-JIRA | verified mock / blocked live | 14 reader + 10跨源 + 6CLI测试；逐用户myself、项目/工单/评论白名单、内容指纹、独立评论授权、撤权/旧历史/引用。KAN-4(J-02)已UI种植为Done，native ID/token/员工Jira访问及矩阵待落实；P-03/04/05/07/09、F-03、Q-03子集，非live通过 |
| DEV-10-OPERATOR | verified mock HTTP / live operator subset | 11测试（含3新增启动诊断/cleanup）：先验证native身份，一次性bootstrap→opaque session，API secret不入浏览器，同会话撤权保护query/history/export/citation。现有英文UI共享；JS语法通过，自动浏览器被ERR_BLOCKED_BY_CLIENT阻挡。真实 HTTP query 已持久化核验；用户确认引用/历史正常，14 事件链通过；不是OAuth/SSO完成 |

| DEV-06-JIRA-IDS | verified mock / live metadata subset | 7 metadata-only setup 测试；native 身份+显式 KAN-4→KAN→数字 IDs；setup 禁止正文读取/DB/模型。AUTH-006 已批准凭据准备，eng_b Jira User 已于 AUTH-007 保存；用户邮箱安全验证/创建保存、KAN-4 native ID10013/project10001 已 metadata-only allow；真实正文/网页问答已verified subset，评论矩阵仍待完成 |

| DEV-10-JIRA-OPERATOR | verified mock HTTP / live subset | 4新增测试；一次启动输入凭据、重复查询逐次身份检查、同会话撤权及历史/导出/引用阻断，独立 DB；真实网页query/preview/history与同会话issue撤权11 DB checks通过，21事件unsigned链；权限已恢复，前端旧视图复用已修正；非SSO/完整矩阵 |


| DEV-06-SLACK | verified mock contract / blocked live installation | 16 reader/Engine/跨源测试；exact root/reply、native用户/team、private ACL、编辑/删除/unknown；AUTH-008 manifest最终安装被Slack创建限流，OAuth/native IDs/API尚未验证。对应P-03/04/05/07/09、F更新/删除、Q工程/产品证据子集，非完整验收 |
| DEV-10-SLACK-OPERATOR | verified mock HTTP / blocked live | 6配置/HTTP测试；一次隐藏USER token、不需邮箱、逐次native身份与权限、同会话撤权保护模型/历史/导出/引用。依赖DEV-06-SLACK真实安装和原生白名单；SSO及统一多源网页仍待做 |

2026-10-05接续优先级：P0 Slack平台创建冷却后用户最终授权→合成private root/reply种植及原生白名单→一次启动真实operator验收；P0 Drive最小只读reader与授权包（可独立本地实现）；P1多源统一operator配置及DeepSeek已批准预算接线。安装限流只阻塞Slack live，无需重复已通过的Confluence/Jira凭据诊断。最新全回归175/175，模拟与真实分列；旧表的not_run历史记录由后续条目补充。

| DEV-06-DRIVE | verified mock / blocked native approval | 16 reader/Engine测试含四源mock统一检索、单源撤权保留其他有权证据、旧混合答案阻断；personal Drive text/plain/native identity+canDownload+metadata race/version/revision。Drive OAuth/scope/账号/合成种植/live矩阵未批准配置；P-03/04/05/07/09、F更新/删除、Q子集，非完整通过 |
| DEV-10-DRIVE-OPERATOR | verified mock HTTP / blocked native setup | 6配置/HTTP测试，一次hidden access token，逐次源身份及撤权query/history/export/citation；准备--source drive入口，不是OAuth/refresh/SSO |

Slack安装状态更正：Chrome更新后已见四个同名app，选A0C6F96HFNX既有app进入Allow；user_confirmed四scope+identify+条款，等待用户保存/离开密钥页，native API仍not_run。停止新建，其他重复app保留。最新全回归197/197，60local/137mock。

Slack native setup接续：已停止app创建，A0C6F96HFNX user-confirmed grant/token保存且已离开密钥页。S-01 private频道/root/reply/native user由原生UI核对并配置0600白名单；真实API仍not_run，当前等待一次hidden token启动8084，无需邮箱。真实频道撤权需独立reader身份；不将种植/UI或mock作为通过。

2026-10-05 Slack root真实web/preview/history verified subset，reply unknown/not_used，完整线程仍blocked debugging。增加固定无敏感诊断与allowlisted parent envelope候选兼容，全199/199；接续用户重启8084一次，重复实际query并据新method诊断，不能将root通过当完整Slack/四源通过。

| DEV-06-SLACK-THREAD-LIVE | verified live API / fake model subset | 重启后root+exact reply、引用与历史实际通过；14 DB checks/36 unsigned事件，web-thread-query.json；原先unknown原因未确定，native private channel撤权仍not_run，需独立reader |

| DEV-10-MULTI-OPERATOR | verified mock HTTP / live not_run | 2–4来源同一已验证actor/tenant；先验证完整配置再输入，全部native身份通过才bootstrap；四源网页query、Drive撤权保留其他源、旧history/export/citation保护，8新增测试；207/207完整回归。真实跨平台persona映射/Drive接入待确认 |

| DEV-06-DRIVE-LIVE-SETUP | in_progress / user action pending | AUTH-009账号/scope已批准；专用无Billing启动项目与Drive API Enabled原生UI核验；OAuth testing branding待用户接受Data Policy并Create；client/token/原生IDs/合成种植/问答/撤权仍not_run |

DEV-06-DRIVE-LIVE-SETUP增量：OAuth branding/Data Policy user_confirmed+UI verified；单一drive.readonly/External Testing/1test user均保存。Desktop client准备待用户Create/Download/关闭密钥页；PKCE loopback与原生permissionId metadata-only绑定尚待实现，源数据/API/撤权not_run。

| DEV-10-DRIVE-OAUTH | verified mock / live grant waiting user | 11 PKCE/固定scope/loopback/metadata账号绑定/配置CLI守卫测试，218完整通过；已读回Desktop client与AUTH-010三文本种植。真实Googlegrant等待用户，原生reader/撤权与ACL矩阵not_run |

| DEV-10-DRIVE-OAUTH / DEV-06-DRIVE-LIVE | verified live API / fake model subset | Google固定scope交换与原生账号绑定、三文件query/preview/history，15 DB checks/29 unsigned事件；完整220回归。Drive/Slack独立reader撤权、统一live persona、SSO及live model仍not_run；下一项DeepSeek预算/provider本地接线 |

| DEV-10-DEEPSEEK | verified mock contract / live blocked credential | 13新增预算/输出/真实本机HTTP模型mock接线及同session撤权测试；233完整通过。--model deepseek已就绪，首轮仅证据选择/非自由综合；用户8086隐藏key与Google授权后实读调用/费用上界/引用审计，语义完整性、统一四源live仍待验收 |

DEV-10-DEEPSEEK增量：真实Drive API + DeepSeek evidence selection首轮query/preview/history已verified（1514ff318e964f3e94b9080e57eef84d，14 DB checks，61unsigned事件）；USD20账本243 micro-USD保守记账。credential blocker解除；自由综合/完整语义效果/四源persona live仍not_run。后续需调用receipt与query持久关联，而非只按单一reservation现场关联。

| DEV-10-MODEL-RECEIPT | verified local/mock; live not_run | 原子预算+query ID关联、validated usage/固定失败enum、审计可join；10新增模拟测试/完整243通过；旧live不重启，新receipt真实运行待后续一次集成启动 |

| DEV-10-MULTI-OAUTH | verified mock / native reader setup in_progress | 5新增配置/CLI测试、全248通过；AUTH-011 secondary reader范围已批，真实账号/Slack membership/Drive Reader及grant尚not_run；identity_mapping_reviewed保持false |

2026-10-05 DEV-10-MULTI-OAUTH reader increment: Google test-user + synthetic-folder Viewer setup verified UI; Google reader account substitution user_confirmed. Native binding/grant/revocation and unified model receipts still pending.

2026-10-05 Slack reader invitation: native UI returned Unable to send / Couldn’t invite for 674544786@qq.com; cause not established, no membership claimed. Drive reader process started on8087 (fake model), OAuth waiting user final grant, credentials not entered or copied. Private screenshot reader-slack-invite-failed.jpg.

2026-10-05 Drive独立reader：用户已完成Google只读授权，程序完成token交换及kyle000909@gmail.com原生about身份绑定，并启动8087 live API/fake model服务。Chrome自动导航ERR_BLOCKED_BY_CLIENT，已交用户地址栏Enter；问答/撤权尚not_run，未新增模型调用或费用。

2026-10-05 Drive独立reader真实subset verified：eng_b问答30376d91652d4f7ab7ba32bfe64f3fca，三份原生文件版本4（共享后版本变化，正文hash未变），引用/历史可用。移除folder Reader后同会话70bcbe2030c34427a990eae47862e246引用原history_id，三source_refresh deny，claims/evidence空、无evidence_used；旧preview deny、history unavailable、三资料索引保留。6项前置+8项后置DB检查，unsigned chain有效；evidence/runs/live-drive/reader-query-and-revocation.json。fake model，无收费调用；真实export/全继承ACL/统一四源仍not_run。权限恢复保存已成功，角色readback另记录。Slack邀请失败仍需处理。

2026-10-05 Slack独立reader：获批改用kyle000909@gmail.com后native邀请成功（colleague，30days expiry），等待用户邮件接受/Google登录/条款；native user ID、私有channel membership、reader OAuth/live撤权仍not_run。不得复用eng_a token或提前identity_mapping_reviewed=true。下一步用户加入后核对实际身份和频道成员，再交用户最终OAuth。

2026-10-05 Slack browser blocker解除；native own profile邮箱kyle000909@gmail.com/avatar公开URL memberID U0C66B76TE3已核对，本地ignored slack-reader.json按eng_b配置。该读者当前频道列表无合成private频道，尚未用token auth.test验证；正在切换主账号管理membership，reader OAuth/live测试pending。

2026-10-05 Slack独立reader合成private成员已添加：切换已授权主账号后，选择已在工作区的Kyle（邮箱此前核对），频道原生事件1791147372.136469确认added by Kyle SHI；未使用Slack Connect/付费功能。existing app分发页要求HTTPS Redirect URL，未发布/新增redirect；继续检查原生Install App流程，OAuth/token/API撤权仍not_run。

2026-10-05 Slack reader在用户点击Allow后出现“Contact a member of your team who is a Collaborator of this app and they can add you.”应用开发后台权限提示。既有工作区/合成private频道成员核验仍有效；不能据此认定OAuth失败，grant outcome unknown，reader token取得/API auth.test/撤权仍blocked/not_run。未添加app Collaborator，未扩大scope、读取token或改变公共分发；拟请求用户明确批准仅现有app A0C6F96HFNX的临时开发协作者权限，保存读者自己的token后移除。已有248项本地/mock回归沿用，本轮无代码或模型调用。

2026-10-05 AUTH-012临时Slack app Collaborator已native UI添加并核对reader U0C66B76TE3；读者Google重新登录后可进入Install App。原四项user读scope+identify展开审核一致，等待用户最终Allow与保存eng_b-slack-token；之后移除临时Collaborator。无secret读取/API问答/模型调用，新reader auth.test和撤权仍not_run。证据private/slack-reader-collaborator-added.jpg；原有248回归未重复运行（仅文档/平台setup）。

2026-10-05 用户报告eng_b Slack token保存并离开密钥页；agent未读取秘密。按AUTH-012从已核对U0C66B76TE3自己的Collaborators页面Leave，native确认移除后Your Apps不再列出该app；未退出工作区/频道、未卸载业务OAuth grant。截图private/slack-reader-collaborator-removed.jpg。四源public配置均加载校验同tenant/actor，Drive映射kyle000909@gmail.com、SlackU0C66B76TE3与既有QQ Atlassian对应用户已确认persona；创建ignored0600 operator-bundle.json（mapping reviewed仅表示账号映射审查，非API验收）。下一步一次启动8088 multi+Drive PKCE+DeepSeek并逐source native identity强制核对。reader Slack API/统一live问答/撤权仍not_run；没有新模型调用。

2026-10-05 阶段收尾：248/248回归与五场景local subset重跑通过；统一8088真实验收/Slack reader API和撤权not_run，用户休息前不再要求凭据。下一P0统一reader启动与native identity→跨源问答→Slack/混合历史撤权；P1有证据模型综合及完整live矩阵。

2026-10-05 DEV-11-RECEIPT-UI verified local/mock：新增3个Python案例（251=60local+191mock）、13项receipt针对性测试与Node前端状态/usage测试通过；回答/历史/导出回执一致且撤权时隐藏。对应A-10/P-05/P-07子集、模型费用可核验。统一four-source live仍等待用户完成8088启动，不把listener存在当服务ready。下一P0 native四源问答/Slack撤权；P1 grounded综合回答与完整live矩阵。

2026-10-05 DEV-10-INPUT verified local/mock：5新增测试覆盖格式失败分类、field-only bounded retry、安全TTY及listener cleanup；全256通过。P0统一live启动仍待用户重试并提供固定code，不申请新scope/token或读取密码管理器。


2026-10-05 DEV-10-KEYCHAIN verified local/mock + native synthetic smoke：AUTH-014下实现 app-owned 系统钥匙串、逐项保存、单项更新、Google refresh exact scope/原生身份校验；266回归和五场景local subset通过。依赖 reviewed bundle/native映射不变；真实持久化及统一live启动/refresh复用 not_run，Slack读者撤权仍P0待验收。用户接续命令 make live，无新scope/预算。


2026-10-05 DEV-10-UNIFIED in_progress：真实startup/四源8对象当前读取allow已现场验证，首轮问答在DeepSeek bracket-only合成guard停止且无费用。DEV-10-MARKER verified local/mock（268测试）：兼容已批准CF C-01/C-02与Jira J-02完整banner，不允许标题/错source/错fixture放行。P0用户make live重启验证Keychain复用→成功联合问答/引用/历史→Slack及混合历史撤权；完整live矩阵仍pending。


2026-10-05 DEV-10-UNIFIED verified live query subset：四源8对象/DeepSeek原文选择，web answer/Slack reply preview/reauthorized history/usage receipt，18readonly checks通过；新模型保守账468microUSD。Slack reader API已验证，private撤权/混合历史/导出仍in_progress；53.37秒延迟需改善。Keychain restart user_reported、Google refresh具体路径未独立检查。


2026-10-05 DEV-10-SLACK-REVOKE verified live subset：原生private成员移除→同会话旧混合历史隐藏→新query只有三源六证据（Slack root/reply native deny）→恢复Members2；9readonly checks。直接旧引用/导出live not_run（Chrome自动本机导航blocked），完整权限矩阵仍pending。真实模型新345microUSD上界；G1/G2未批准。


2026-10-05 DEV-11-EXPORT verified local/live subset：按原端点新增导出入口及expired session提示；实测下载逐字段一致（raw保留大整数）、撤权旧导出不创建文件、旧引用GET拒绝且清除视图。268Python+Node回归通过，未新调用模型。剩余P1性能/grounded综合/五场景完整live和人工G1，现有ACL完整矩阵仍partial。


2026-10-05 DEV-10-LINKLESS verified local/mock：省去无links对象的空关联源读取，命中对象mock读取5→4，保留所有模型/响应边界检查；270回归与五场景local subset通过。真实延迟/Keychain refresh复用仍not_run，旧8088无需本轮重启。下一P1受控真实性能对比及grounded综合；完整live矩阵/G1仍pending。


2026-10-05 DEV-10-LATENCY verified live API/fake model subset：双隔离进程验证已保存CF/Jira/Slack Keychain+真实Drive refresh复用，统一8证据源读取53.209→40.116秒（每版本单样本）；模型/返回边界保持，旧8088未重启。性能及refresh试点阻塞解除，长期过期处理/完整矩阵仍partial。下一P1 grounded模型综合；G1/G2仍pending。


2026-10-05 DEV-08-SYNTHESIS verified local/mock + live subset：opt-in双调用/精确quote/逐结论review/二次原生授权与双回执实现；281回归、Node及五场景local subset通过。实际四源8input证据→4综合claim（引用三源），10live checks通过；首题仅三源命中的四源探针失败记录保留。新模型保守费用3340microUSD，同一USD20ledger。综合模式HTTP/同会话撤权已verified mock；下一P0人工UI验收、官方五场景live矩阵与未知/撤权完整覆盖；当前模型复核非准确性保证，G1/G2未通过。


2026-10-05 P-11-SYNTHESIS verified single authored adversarial subset：fixture业务源/live DeepSeek，同模型复核；GA错误指令不被采纳、S-01不入模型、无业务工具/外部任意请求。新保守账1331microUSD，同一USD20账本。答案存在额外相关性不足claim，完整prompt-injection/人工语义及真人UI验收仍pending。源码未改、281回归沿用。


2026-10-05 DEV-11-VIEW-RACE verified local：4延迟响应安全断言+281回归通过，session/view guard和综合状态文字修正；make LIVE_PORT可选。综合UI live blocked新入口：8093启动成功但工具内存IPC EPERM，已安全停止；用户已获准确8094命令，无需凭据重输。等待用户新页，同时现有原文8088保留；非作者G1/完整live矩阵仍pending。


2026-10-05 DEV-08/11-SYNTHESIS-UI verified live subset：真实综合UI支持片段/双回执/引用/history/raw下载与键盘Enter/Escape通过；初答漏问到的保障，保留质量失败。v2 question_covered明确boolean判定及更严格生成提示，282回归通过；真实首轮review拒绝、次轮缺quote拒绝、最终四源同题11checks通过且补齐timeout budget/failover。前三claim重复仍待优化，不据单样本/G1泛化。用户8094旧v1保留，backend更新需终端重启一次，无凭据重输；下一P0综合原生撤权/增量更新与完整live矩阵，P1质量/性能。


2026-10-05 DEV-11-PORT-SESSION verified local HTTP：原共享CookieJar双端口互相覆盖已复现、修复并验证login/logout/CSRF独立；283回归通过。真实8094本轮会话失败归因unknown，Chrome双端口fixture被blocked；综合撤权in_progress等待修复版有效入口，不修改原生权限、不再要求token。


2026-10-05 综合v2真实8094三源6证据/3结论/5检查已verified query subset，费用1296microUSD；与单题四源模型测试分开，S-01仍缺两事实。P0原生Slack综合撤权blocked具体动作审批：用户已关闭扩展，Remove未执行，待明确U0C66B76TE3/C0C6R70SGG4本次移除及恢复；不重新索要凭据。

综合撤权当前verified citation/history subset：原生2→1→2，同一v2混合答案/quotes/双回执隐藏、无关答案可用、preview deny与session保留；同一UID恢复确认。Export旧按钮依赖第二轮，自动审批拒绝/新具体批准pending，未再次移除成员，无新模型费用。

第二轮旧综合export已获独立批准并verified live subset：deny不下载、正文清除、session保留；同一原读者最终恢复Members2，合法raw实际下载精确一致。综合撤权P0本子集解除阻塞，完整S-04及更新/删除矩阵/G1仍partial，283源码回归沿用，无新模型调用。
# 2026-10-05 lifecycle acceptance increment

| Task | Priority / dependencies | Status / acceptance |
|---|---|---|
| DEV-12-LIFECYCLE | P0；existing Engine/current ACL/Ingestion | verified local subset：四源各更新/撤权/删除12组；旧索引阶段不入模型，旧history/export projection与引用阻断，单对象发布/事件幂等/审计链；对应S-02/S-04、F-01/03/04/05、P-05/07/12部分，不计作native通过 |
| DEV-12-SAFETY-REVIEW | P0；完整live五场景后组织 | checklist prepared / human not_run；团队观看内容及局限已整理，未预填通过 |

DEV-12-LIFECYCLE live increment：AUTH-015完成CF content revision1→2→3恢复原文与旧访问拒绝，Drive disposable native trash/旧访问/模型保护verified operator subset。真实四源更新/删除矩阵仍partial；不是完整S-02/S-04。原runtime whitelist未扩展，独立临时reader测试已结束。下一S-01缺J-03真实合成资料，种植/原生访问及白名单尚pending；核对AUTH-003已有授权范围，界面/审计候选工作可继续。

2026-10-05 S-01工程facts解除前置：AUTH-003合成J-03/KAN-5种植、In Progress及API白名单完成；真实四源/DeepSeek single eng_b question覆盖五工程要求及虚构owner说明、7checks+独立quote/auth/ledger审查，费用1856microUSD。完整eng_a/product_ops、真实权限负面矩阵/G1仍pending。DEV-08检索质量继续P0：先本地长文/同义/相似资料评测、切块/全文排序；embedding provider未选，不新增付费服务。

2026-10-05 DEV-08-window verified local subset：精确原文长窗口/字符定位、规范引用ID、少量英文alias、旧历史与权限保护；10新test/293回归，5 authored检索cases（含未知词汇miss边界）、5场景与12生命周期。下一P0：语义质量的独立问题集/检索召回评测；长片段合成边界在真实模型前仍blocked（不为通过伪造marker），embedding及reranker未实现，未新增费用或公开部署。

2026-10-05 验收优先级按用户确认恢复到交付依赖：DEV-12五场景/独立persona/候选安全演示优先，DEV-08质量以实际评测缺口驱动，不因提问新增向量服务。DEV-12-PRODUCT verified eng_b native/model subset（非product_ops ACL）：四结论、1529microUSD、缺证据不调用；DEV-12-AUDIT-REPLAY verified offline captured-live subset：NL分页/普通reader拒绝/7签名边界，独立custody与live审计员仍blocked。DEMO_CANDIDATE集中各场景实际证据与缺口，G1/G2 pending。新runner显式--live/防覆盖，mode标签失配保留原record、修复未来执行。

2026-10-05 DEV-12-REBUILD verified local committed candidate e9a55e6：无本机.runtime/.env的git archive，setup/295tests/5fixture场景/Node/启动HTTP资产+login+four-source-query+preview全部通过。首次26dc4a9 archive仅1测试依赖本机残留DB导致失败，保留rebuild-candidate，修正测试真实独立DB而非削弱安全断言；成功rebuild-fixed。浏览器视觉/原生persona/G1仍pending，本次没有source/model调用，不重启8094。

2026-10-05 DEV-10/12-AUDIT-UI verified local Node subset：原same-view查询竞态已复现、修复；stable snapshot分页捕获result.filters、旧请求/重复点击/导航丢弃、source HTML纯文本、unsafe整数明确提示。审计timeline与raw event并存，原server scope/role及SQL契约未改。Chrome visual blocked/not_run；临时fixture停止，8094保留。下一候选archive加入独立audit frontend check，独立persona/G1/G2仍pending。

2026-10-05 DEV-12-AUDIT-CANDIDATE verified clean local subset：0278bab archive setup/295Python/5fixture/2Node脚本/实际fixture HTTP smoke通过，rebuild-audit-ui。下一P0 native S-03优先existing eng_b+owner的受限C-03合成seed/真实deny与允许C-02控制，在已有AUTH-003范围核对管理员UI；原product_ops/contractor全矩阵不冒称完成，新增身份grants另批。Chrome视觉blocked，不扩安全权限，不重启8094。
