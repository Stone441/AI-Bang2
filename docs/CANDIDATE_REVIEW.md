# 本地候选版本审查包（非最终提交）

选题：The Internal Brain。工作名 ContextLedger（尚未正式确认）。

英文 short blurb（8 words）：**Trusted answers across tools, backed by verifiable evidence.**

当前候选提供英文 workspace、动态来源证据卡、六个合成用户、四源 fixture、权限复核、增量事件、撤权/历史/引用保护、审计查询和本地日志链检查。没有接入 Aspire/NTU/个人真实资料，没有调用外部模型或新增云资源，不包含虚构 ROI。

实际源代码与信任边界：`docs/IMPLEMENTED_ARCHITECTURE.md`。复现步骤：`docs/RUNBOOK.md`。五场景实际输入、输出、引用和日志：`evidence/runs/local-latest/scenarios.json` / `audit.json`。验收缺口：`docs/ACCEPTANCE_STATUS.md`。

## G1 人工核验（全部 not_run）

- 工程场景逐项核对事实与引用，产品场景不把 Done 当 GA。
- contractor 请求安全报告不确认存在，且普通获准查询可用。
- 同一 eng_a 会话撤权后追问、旧引用和 Recent answers 不再提供受限信息。
- runbook v2 只更新一个对象，旧版本引用不可继续读取。
- 审计 scope / 精确分页正确；日志副本篡改检测；签名检查点完成后重做完整审计验收。
- 核对当前模式与覆盖声明；生产身份、真实 source scope、真实模型和公开部署另行批准。

## 最多三组团队接力

1. **真实接入与数据边界**：推荐只使用团队控制、仅合成数据的四个测试空间，为实际提问用户配置委托读取；由团队提供允许的 workspace/site/drive 和身份映射。先核对必要 scope，再审批，不能用全库 service token 代替员工权限。
2. **运行时模型与费用**：推荐先批准单一 provider、仅合成证据、明确总费用和单次上限；当前保持零外部调用。开发 credits 不计作 runtime 预算。
3. **腾讯工具与赛事规则**：立即转交 `docs/CODEBUDDY_TASK.md`，保留真实 conversation history + 至少三张截图；同时请规则负责人确认 mock 接受范围、Codex 混用和 10/16 截止时刻。01 中的 OQ 不因开发进展自动解决。

## G2 / 提交项

| 项 | 当前状态 |
|---|---|
| 标题、短介绍 | candidate |
| 项目描述、实际架构、五场景记录 | local candidate；需补 live 状态 |
| 完整源代码 | 本地独立分支；未推送/公开 |
| CodeBuddy/WorkBuddy conversation history | blocked：尚未实际执行 |
| 至少3张真实工具截图 | blocked：尚未实际执行 |
| 封面、5–8分钟演示视频 | not_started：产品验收与真实工具贡献后制作 |
| 公共 demo URL | not_deployed；G1 未通过 |
| 人工质量/ROI/真实模型成本 | not_run |
| G2 发布和最终提交 | not_approved |

不得将这份候选文件直接包装为完整四源 live 产品或最终交付完成。
