# Backlog · 2026-10-04

| ID | 状态 | 已完成 / 仍需推进 / 验收 |
|---|---|---|
| DEV-00 | verified | 仓库/环境盘点，基准 68e65c8 |
| DEV-01 | in_progress | 官方 API 文档核对；真实 spike blocked，SOURCE_CAPABILITIES |
| DEV-02 | verified | 合成数据/授权 oracle/SourceAdapter，78 权限组合 |
| DEV-03/04 | verified local | HTTP/UI/持久库/fake model/身份→证据→回答→审计，Q-01/P-01/A-01 本地子集 |
| DEV-05 | verified local | 请求驱动增量/去重/重试/原子版本/删除 F组；真实 worker/scheduler 待做 |
| DEV-06 | blocked live | 四源 fixture 可运行；专用合成空间操作已批准，账号/站点及用户委托待配置；本地 seed exporter 已测试 |
| DEV-07 | verified local | stale ACL/撤权/unknown/历史/预览/导出/生成中撤权；P组部分真实机制待测 |
| DEV-08 | in_progress | 关键词+授权一跳、exact extractive support；DeepSeek 首轮 US$20 上限已批准；预算控制/模型适配与语义检索未实现 |
| DEV-09 | in_progress | 事件链/精确 scope/分页/有限 NL；生产 role/加密未实现 |
| DEV-09-CB | verified local | 真实 CodeBuddy Ed25519 检查点/独立 CLI；20 新测试+52 全回归；A-03/04 本地签名子集，A-11 缺锚点/尾部已测，密钥轮换待做；依赖 DEV-09 导出契约 |
| DEV-10 | in_progress | 英文 Workspace/History/Sources/Audit 已联通；浏览器视觉工具阻挡 |
| DEV-11 | verified local subset | 五场景回放+安全测试；不是完整 P0/G1 通过 |
| DEV-12 | blocked | live model / 非作者人工任务测量未运行 |
| DEV-13 | in_progress | 本地候选审查包、运行指南；真实腾讯对话/7截图已本地留存；封面/视频/材料提交待做 |
| DEV-14 | in_progress | 本地小步提交及候选重建；G2/publish 未批准 |

| DEV-06-CF | verified mock contract / blocked live | 白名单站点/page/space、逐读取验证凭据身份、403/404 deny、未知拒绝、版本保护、scoped gateway 与受限诊断 CLI；22 模拟 HTTP/配置测试含 TTY 不保存凭据与 metadata-only discovery；真实凭据与 native space ID 待做；P/Q 组 live not_run |

| DEV-06-CF-QUERY | verified mock contract / blocked live | 独立 operator pilot 复用 Engine/索引/审计；14 模拟查询测试覆盖跨身份索引、同会话撤权、旧引用/历史、更新/删除/unknown、dispatch 撤权、空证据历史租户和错误模式。无前端身份/live HTTP 路由，需真实凭据后集中验收；P/Q/F/A 组 live not_run |

| DEV-08-BUDGET | verified local | SQLite micro-USD durable reservations；7 安全/故障测试；模型请求和官方计价尚未接线，live model not_run |
