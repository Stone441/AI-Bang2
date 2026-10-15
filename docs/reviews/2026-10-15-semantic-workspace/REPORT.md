# Semantic workspace candidate · 2026-10-15

状态：**in_progress / live quality acceptance failed**。可运行本地候选，尚未达到 Goal 全部交付标准。

候选运行代码 `a2be0fd7057bac91f2be7e4c12a7b76162c092aa`，分支 `feat/semantic-workspace-20261015`，基准 `0d5be3096cfcbf09b267fe6b54853b1fac2e67af`。本报告为该候选的后续证据。没有 push、merge、生产重启或切换。生产仍是独立旧版本；部署与回退见 DEPLOYMENT_AND_DEMO.md。

## 实现与本地验证

顶部 Workspace / Recent answers、用户菜单、输入优先、三张业务卡、可展开四源摘要、桌面引用抽屉/手机全屏、默认折叠原文、真实阶段等待、历史重新鉴权和失败状态已实现。建议题仅填入，不提交。复用 sectioned-synthesis，仅加强直接回答及跨源整合提示，未放宽 JSON、精确引用、独立复审或权限检查。

- 763 Python 回归通过，55.443 秒；日志保留既有 SQLite ResourceWarning。
- 最新 14 个前端 DOM 套件全部通过；sectioned 17 项、HTTP lifecycle Python 包装 1 项通过。
- Chrome 实际观察：登录、题卡填入、明确提交、顶部导航、完整 mock 分题答案、默认折叠原文、桌面引用、Escape 恢复焦点、390×844 手机布局/全屏引用、历史重新打开。截图来自明确 fixture/mock 模式，不代表真实模型质量。
- 最后补测：来源故障显示无法完成/来源完整性未确认；mock 生成失败不展示草稿。本地 fixture 在回答后撤销 J-02，点击引用后清除旧答案并提示不可用；历史仅显示自己的提问摘要，打开显示 Unavailable。见 source-failure-mock.png、history-revoked-mock.png。没有修改原生平台权限。
- 27 次 fixture/fake Engine 检索覆盖 9 问法 × 3 身份。工程/产品必要证据无缺失，外协不要求其无权工单。具体来源相关性不等于结论支持。

## 本轮真实验收

用户批准 AUTH-SEMANTIC-WORKSPACE-20261015-24-USD1：新独立自动 grant 最多 24 次 DeepSeek 调用、USD1，仍受原 USD20 账本约束，现有四源合成资料只读、无付费重试。原 2 笔 unknown 保留。执行前 SQLite backup、新 grant 迁移和候选 archive 固定；工程角色精确应用策略核对；当前原文版本/文本冻结并在每题前比对；每题等待四源 complete/current。

2026-10-15 重新读取 [DeepSeek 官方定价](https://api-docs.deepseek.com/quick_start/pricing/)，现有峰值/cache-miss 保守费率符合当日价格。12 次实际调用，保守记账 **USD0.016174**，不是供应商账单；新增 unknown 0，人工 grant 记账未变，原 unknown 2 笔保留。私有原始账本、原文、回执、审计留在 .runtime/semantic-live-20261015/；不进入 Git。

实际有 7 题提交结果，5 题生成＋复审接受、2 题安全回退。**这不是 5/7 业务验收通过**：其中一题仍有类别问题。逐题非秘密摘要见 live-results.json。

| 用例 | 结果与人工对照原文判断 |
|---|---|
| 发布准备原题 | accepted；明确 PAY-102 Done 不等于发布获批，受控试点/GA 未批准/无日期，引用支持；略有重复 |
| 发布准备英文改写 | 仅原文回退；JSON 在结尾缺少分隔/闭合，finish_reason=stop、325 output tokens，不是已证明的 token 上限截断 |
| 发布准备中文改写 | accepted；保留范围与限制，引用支持；略有重复 |
| 交付计划原题 | 仅原文回退；严格 citation_ids 校验拒绝；原始失败草稿未保存，不能进一步断言是错误 ID 还是重复 ID |
| 交付计划英文改写 | accepted；PAY-102 Done、PAY-103 In Progress，发布日期单独 insufficient；符合部分证据目标 |
| 交付计划中文改写 | accepted，事实/引用正确，但将“无确认日期”标 supported，界面成为完整回答；不符合预定部分证据类别，记录为失败而非改写 oracle |
| 赔偿金额原题 | accepted，整题 insufficient、无金额/无零赔偿断言；从审计恢复的已提交结果，非完成 HTTP 计时样本 |

成功草稿所有精确引文逐项核对存在于返回 evidence；再对当前原文核对事实、限定与作用域。付款服务基线与 SG-GATE 冲突探针保持区分。模型自己的 accepted 不能替代该业务核验。剩余赔偿两改写、错误前提与冲突题未执行。

### 停止与执行器缺陷

计划要求重复生成失败停止。私有执行器误检查 answer_mode 而非 answer_status，导致第二次失败后又运行后续题。发现后人工停止新调度；检查无未结付费请求后发出中断，HTTP 服务关闭期间已开始的赔偿题完成并结算，因此 6 个客户端完成记录、7 个审计提交结果。所有 12 次调用均在批准的原用例/24次/USD1内，无题目重试，无新增 unknown。不能将延迟停止描述成自动停止规则成功。

执行器字段已更正，加 CLOSED.json 硬停止，当前 grant 不自动复用。原始历史保留。重复失败需要诊断，不因余额尚有剩余继续消费。

## 安全与测量边界

本地完整回归覆盖权限、撤权、版本、历史、引用；浏览器撤权是 fixture。真实运行保留原四阶段权限检查，审计链 702 事件 valid，但未有外部签名锚定。因提前停止，计划中的真实 same/cross-session history、preview、audit HTTP 检查未执行；不能用旧结果冒充此次结果。

前六题 HTTP 总耗时 9.67–18.16 秒，包含源检查/模型/复审；样本少、不代表 p95/SLA。真实阶段 recorder 装在内层 OperatorApp，外层 ReviewerApp 未传播，因此 **真实分阶段 spans 未记录**，不从总耗时推算生成/审查时长。本地 fixture 检索 spans 0.200–1.414 ms 见 measured-retrieval-v2/report.json。浏览器 mock 等待与这些 HTTP 数据不同，不能混为一项。

## 下一步与运行

优先本地诊断：日期缺失的 supported/insufficient 语义契约、严格 citation_ids 的安全诊断粒度、私有执行器的停止条件和外层 timing 安装。不要自动修复非法 JSON、降低审查门槛或显示失败草稿。修复后的新候选需要独立、具体的剩余真实验证计划；本次无付费重试授权。上述质量与安全/阶段测量缺口完成前，Goal 不算完成。

`python3 -m scripts.reviewer_demo` 可启动无凭据 fixture/fake 预览；它不代表真实模型质量。用户已有 51686 预览保持原快照，本轮没有替换。Embedding 不纳入：当前小样本无必要证据漏召回且无已授权/已安装真实 embedding 条件，详见 EMBEDDING.md。
