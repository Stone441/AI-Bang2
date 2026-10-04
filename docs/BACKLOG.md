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
