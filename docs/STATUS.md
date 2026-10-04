# Current status

更新：2026-10-04（Asia/Singapore）。起始基准 `68e65c8` / main，仅文档。原未跟踪 `.DS_Store` / `Analysis&Planning/` 保留，Requirements 未改；README 仅追加运行说明。已完整阅读 AGENTS、PROJECT_START_HERE、docs/01–05，未采用旧 GPT Requirements。

**G0 仅本地完整开发已批准**；外部数据、账号/scope、运行时模型/预算仍待定。G1/G2 未通过。未推送远端、未部署、未调用真实平台/模型。

## 已实现与验证

- 12 顶层对象 + 独立 Jira 安全评论，6 用户、78 权限组合；Confluence/Jira/Slack/Drive 各自 fixture policy。
- loopback 服务、opaque session/CSRF、英文 UI、四源关键词 + 授权一跳检索、fake extractive model、逐结论引用。
- 当前源授权在模型前和返回前检查；未知拒绝；四源撤权、旧历史/导出/引用保护。模型、HTTP 均有实际回归。
- 持久 fake source 与 SQLite 索引分离；对象级事务发布、创建/更新/删除、去重/乱序/重试、失败任务不被游标越过、重启恢复。请求触发处理，不宣称真实自动同步。
- 完整问答审计、逐资料决策、sent_to_model/cited/dispatch 区分、scope 查询与稳定分页；60 并发追加链测试。本地 hash-chain 不等于独立签名完整性。
- `make test-report` 32/32 tests passed；另有 78 权限组合。`make verify` 五场景均 `passed_local_subset`，非完整 live 验收。首次 S-01 检索遗漏已复现、保留失败记录并修复。

已通过从提交导出的独立临时目录 `make setup` / `make test` / JS 语法检查。

证据：`evidence/runs/local-latest/tests.json`、`scenarios.json`、`audit.json`；包含运行时间、模式、基准 commit 与精确源码 SHA-256。验收映射见 ACCEPTANCE_STATUS。

## 能力边界与阻塞

| 项目 | 状态 |
|---|---|
| 四源 | fixture_only；live blocked（真实测试空间与委托用户授权未获批准） |
| 模型 | fake-extractive-v1；live not_run，无 embedding/reranker/compressor |
| 审计完整性 | partial；独立 DB role / 加密 / 签名根未实现 |
| 腾讯工具 | not_started；无 callable tool/CLI；DEV-09-CB 任务包已准备 |
| 浏览器视觉 | blocked：IAB 不可用，Chrome localhost ERR_BLOCKED_BY_CLIENT；HTTP 集成通过不替代视觉检查 |
| 部署与人工 | local only；G1/G2 / 非作者质量与 ROI not_run |

## 精确接续点

1. 团队转交 `docs/CODEBUDDY_TASK.md`，CodeBuddy 基准 `889773c`，独占签名验证器路径；完成后 Codex 审查集成。不要在等待时冒领它的实现。
2. DEV-06：按 SOURCE_CAPABILITIES 核对获批四源测试空间/用户/scope，实施真实委托读取、分页/变更流/撤权合同测试；授权前不得碰现有凭据。
3. DEV-08/09：批准 runtime 后接入真实模型与语义支持评测；生产 DB/身份/HTTP 栈和独立审计边界仍需工程实现及运行验证。
4. 浏览器可访问后按 RUNBOOK 完成 UI/键盘/移动布局检查，并组织 G1 人工核验；完善候选材料，最后 G2。

本轮只交付本地候选，不宣称完整项目完成；没有承诺会话结束后继续运行。
