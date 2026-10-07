# AI-Bang2 · Agent working instructions

本轮业务增强入口：先读最新STATUS/DECISIONS，再读docs/iterations/2026-10-07-business-validation/EXECUTION_BRIEF.md；研究不是官方要求，具体授权仍按AUTH。


## Project and authority

本仓库用于Tencent Cloud AI CAN DO IT Hackathon Singapore 2026，FinTech / Aspire赛道：**The Internal Brain**。三位NTU成员负责业务判断、接入授权、安全验收和最终提交；Codex主导设计细化、编码、测试、集成与任务推进。CodeBuddy/WorkBuddy必须有真实开发贡献及证据，不能由其他Agent伪造。

推荐产品：统一Confluence、Jira、Slack、Google Drive，回答工程及产品/运营问题，提供授权范围内的证据、新鲜度和完整审计。`ContextLedger`只是候选名；本包是方案与执行契约，不是已实现能力证明。

## Read order and context budget

新会话先读`PROJECT_START_HERE.md`；首次接管按顺序读：

1. `docs/01_OFFICIAL_BRIEF.md`：官方事实、五场景、提交门槛、冲突。
2. `docs/02_PRODUCT_STRATEGY.md`：推荐业务场景、范围、价值和指标。
3. `docs/03_ARCHITECTURE.md`：架构、信任边界、数据和接口契约。
4. `docs/04_DELIVERY_PLAYBOOK.md`：阶段、DEV任务、人类关口、腾讯工具任务。
5. `docs/05_ACCEPTANCE_TESTS.md`：合成真值、权限矩阵、测试oracle。

后续会话先读实际存在的`docs/STATUS.md`、`docs/BACKLOG.md`、`docs/DECISIONS.md`及当前任务相关章节。超出上下文时分段读取并记录已读范围；未读内容不得猜测。不要每个任务重复加载完整归档。

`docs/sources/`仅为原文追溯，常规开发不用读取。用户明确排除的旧GPT生成Requirements文件不是需求来源；保留它，不擅自删除、覆盖或据它改变本方案。

## Facts versus decisions

01只记录已给出的官方材料；02–05是待验证的团队建议。后续明确官方澄清才可改变01，保留原文、日期和来源；模糊之处不能自行改成“官方已允许”。当前提交日期为2026-10-16，具体时刻未知；入围10-20/10-23冲突；Demo Day 11-03书面TBC。

较大实现变更记录ADR，说明证据、成本和回滚。运行时模型、框架和普通实现细节可按实际情况优化；不能用优化为由放宽权限、审计或数据边界。材料与运行事实冲突时报告差异，不伪造运行结果或静默改写测试。

## Non-negotiable implementation boundaries

- 身份从服务端已验证session取得；Prompt、客户端role/user_id、LLM输出不能授予权限。
- 采集服务账号权限不等于员工权限。保留每个平台原生权限差异，包含子资源和继承。
- 本地权限预过滤之后，在证据进入本次回答/重排/压缩模型前验证当前有效权限；unknown不放行。
- 历史、缓存、引用、预览、导出和关联扩展也要鉴权。当前文件可读不自动授权旧版本全部内容。
- 不泄露受限资料的存在、标题、命中数或路径；检索文本是不可信资料，不是执行指令。
- 内容与ACL更新分开；增量版本完成后切换，删除先停用。不以全库重建掩盖增量问题。
- 关键事实有真实证据ID与定位；URL由后端映射；证据不足不编造企业事实。
- 审计能还原身份、问题、逐资料授权、证据与最终回答。只存hash不够；哈希链不等于独立防篡改证明。
- 审计查询使用受限结构化条件和参数化查询，不能让模型执行任意SQL。审计员也有范围限制。
- 产品运行时对知识业务源只读；测试种植/权限变更是另行授权的管理行为。
- fixture、fake model、live API和live model的结果分列。51个计划案例不是51项已通过。

## Autonomy and human gates

可立即开始本地、可逆、无外部写入/新增费用的Phase 0：盘点仓库、识别契约、建立计划/合成数据和问题表。

G0确认范围、源接入、模型与预算；G1在人实际观看安全核心场景后才可外部开放；G2批准最终材料与提交。关口之间，已批准任务的常规实现与测试持续推进，不对每个函数重复求许可。

未获授权不得申请新scope、接真实敏感数据、向外部系统写入、产生新收费、公开服务/仓库、上传对话证据、合并或推送受保护主线、删他人工作。凭据缺失可以用显式fake provider推进不依赖它的任务，但live验收标blocked/not_run。

## Repository and multi-agent discipline

先检查真实目录、分支、未提交改动和现有工具链；不要假设文档建议的命令已经存在。保留原README与Requirements，增量修改，不覆盖队员文件。

每任务独立分支/工作目录；不让Codex与CodeBuddy同时写同一文件。公共schema变更先更新契约和测试。交接包含任务ID、基准commit、范围、禁止修改路径、验收ID、已授权资源和产物要求。

从DEV-05等任务开始预留真实CodeBuddy实现贡献；保留真实对话及至少3张过程截图，另有conversation history。不能声称Codex能自动调用本地CodeBuddy；无可用工具连接时给人准确任务包。

## Validation and durable state

每个任务：理解验收 → 实现最小改动 → 审查差异 → 运行相关验证 → 报告事实 → 更新状态。失败先复现再修复，不删除有效断言、降低阈值或用expected充当actual。

首次接管按真实情况创建`docs/STATUS.md`、`docs/BACKLOG.md`、`docs/DECISIONS.md`和证据索引。标明not_started/in_progress/blocked/verified；结果关联commit、模式、时间、命令和证据。不要预填通过率、商业收益、API覆盖或工具贡献。

`.env`和密钥不入Git；第三方模型/embedding/tracing的数据与预算须在批准范围内。依赖版本在验证后锁定；读取官方技术文档核对接口，不凭印象编SDK或接口。开发工具credits与应用runtime费用分开。

每次阶段汇报使用中文：已验证的进展、实际测试与限制、下一项可推进任务、最多三项需要人决定的问题。界面/演示默认英文。无需反复复述整套方案，继续推进已批准范围内可完成的工作。
