# Semantic workspace candidate · 2026-10-15

状态：in_progress。基准 `0d5be3096cfcbf09b267fe6b54853b1fac2e67af`，独立 `feat/semantic-workspace-20261015`。未经 push/merge/生产切换。

## 已实施与验证

- 顶部 Workspace / Recent answers，原服务端审计入口权限保持；输入优先、三张英文业务卡、靛蓝视觉、折叠运行模式说明、四源可展开摘要、桌面右侧引用抽屉和移动端全屏 CSS。
- 复用 sectioned-synthesis，提示强调先回答、跨源整合、事实/推断/原文建议区分；不改变严格 JSON、引用、分题/复审或权限边界。真实模型质量未验证。
- Chrome 实际 fixture 登录、卡片填入但不提交、手动问答、引用抽屉准确显示 PAY-102 原文、Escape 关闭并回到原引用按钮已观察。截图 drawer-desktop.png。浏览器 fake extractive 输出不是语义综合成功；移动端和全部错误态尚未完成。
- 14 个现有前端 DOM 套件通过；17 个 sectioned 单测通过；Python HTTP lifecycle 包装 1 项通过。未宣称全量回归或 native/live model 验收。
- 浏览器复现未登录 fixture 被误报服务断开；新增 boot 断言先红后绿，修正为选择演示身份，无自动 query。
- 实际 Engine + fake model 对三个题目、三种 baseline 身份运行九次，必要证据及耗时见 default-question-baseline.json。员工前两题必要资料被召回；外协不能获取内部工单，不能沿用员工 oracle。第三题相关资料召回不代表金额可回答。

## 真值与后续

question-oracle.json 冻结三个业务 oracle 及六条新改写，不声称盲测，不进入模型输入，不按问题字符串硬编码答案。原生角色精确资料映射仍须核实。

下一步：新改写召回/阶段时间测量、完整分题 mock 浏览器与移动布局/错误态、安全回归、固定候选的有界真实模型计划及实际授权核对、embedding 条件评估、部署回退计划。既有一次性 live grant 已结束，人工额度不可用于自动测试；本轮未调用真实源或模型、未下载模型/安装依赖。

## 运行

在此独立 worktree 运行 `python3 -m scripts.reviewer_demo` 可启动无凭据 fixture/fake 预览。它不模拟真实模型质量。静态资产按启动时快照固定，修改后重启自己的隔离实例；不重启生产。

## 后续实测增量

Chrome 390×844 视口已实际核对单列题卡、历史列表/原回答打开及全屏引用，保存 drawer-mobile.png；视口已恢复。27次原题/六改写 × 三身份检索见 paraphrase-retrieval.json。此为小型已知合成集、作者改写，非盲测；fake结果不计语义质量。

## 当前回归结果

763项Python回归/55.443秒通过（存在既有测试连接未关闭的ResourceWarning，日志保留）；14个DOM套件在最后的状态栏节点稳定修复后重新通过。状态轮询保留展开节点与键盘焦点身份，新增对应断言。此前HTTP包装1项通过。桌面/移动截图来自修复前的UI快照，未冒称最终提示词的真实模型验证。Embedding暂不接入，条件与理由见 EMBEDDING.md。
