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
