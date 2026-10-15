# ContextLedger · 最终交接说明

2026-10-15 当前运行已切换到本地修复代码 `f2f0633`，同一公网入口；最新[真实验收与剩余缺陷](reviews/2026-10-15-closeout-live/REPORT.md)优先于下方历史状态。自动复验10次/USD0.011808，人工额度未占用、旧unknown保留。两项可选分题生成仍失败，不能宣称全部通过；未push/main合并或比赛提交。



2026-10-15 收尾候选：基准 GitHub main `5727300`，修复位于本地 `fix/systematic-closeout-20261015`。当前入口与状态以[收尾报告](reviews/2026-10-15-closeout/REPORT.md)为准。新候选未替换 49161 的旧运行后端，不能把旧公网问答成绩当作本次验收。原生三角色演示边界保持；原账本、账号和两笔旧 unknown 保留。

下列 10 月 13–14 日数据、包和部署记录均为历史，当前候选的验证模式及待办另见收尾报告。

14 October pd local update: the remaining authorized local improvements are complete: isolated fixture lab, eight security probes, scoped audit timeline, bilingual retrieval and optional per-part model mode. See [local guide](SCENARIO_LAB.md) and [current submission candidate](SUBMISSION_CANDIDATE.md). This branch has not replaced the earlier hosted build. The new model mode/native behavior remain unverified; all 15 declared private tool-proof originals are missing locally. Dated deployment/account statements below describe earlier builds, not a fresh availability check.

演示账号代表具体虚构人物：Blair（工程）、Morgan（产品与运营）、Jordan（外部协作方）。权限按账号配置，岗位标签不表示所有同岗位人员拥有相同权限。此次只改登录名和显示名，原密码、内部身份、历史与权限保持不变。

2026 年 10 月 13 日。**本机已提供三个应用角色账号，接入真实四源和原有真实模型。** 在线入口已部署；用户授权代理代验已完成，未宣称 G1 真人观看或 G2 最终提交通过。

共用知识库连接统一显示为 **Team Knowledge Connection（团队知识库连接，`team_knowledge`）**，与 Blair、Morgan、Jordan 三个演示人物区分。已有原生授权和审计内部标识保留兼容，不表示新建平台服务账号。

## 在线试用（当前入口）

https://contextledger.hellokyleshi.com

组员无需克隆或配置四个平台，使用下方三个演示账号及本机私密卡片中的原密码登录。真实四源与真实模型，内容仍为已批准合成演示资料。账号通常在创建七天后到期；共用同一账号的人共用该账号历史。

本机托管已配置用户级后台进程与运行期间防空闲休眠。保持电脑开机、联网、用户已登录，避免合盖。可双击根目录 `停止在线试用.command` 停止应用和隧道，`启动在线试用.command` 重新启动。密码不随Git传播。

最终公网问答8.855秒、四源证据齐全；Jordan一次退回授权原文，综合回答未成功。验收为用户委托代理的HTTP/API验证，浏览器工具被拦截，未宣称真人验收。详见 [部署验收](reviews/2026-10-13-hosted-demo/README.md)。

## 打开并试用

双击仓库根目录的 [打开试用页面.command](../打开试用页面.command)，在登录页输入账号和密码。三个账号的密码见本机私密文件 `.runtime/query-goal-20261013/reviewer-login-cards.txt`；工程账号原密码保留，密码不会进入 GitHub。

| 账号 | 角色 | 当前真实环境的资料范围 |
|---|---|---|
| engineer_blair (Blair) | 工程 | 团队连接当前允许的获批合成工程资料 |
| product_morgan (Morgan) | 产品与运营 | 能力、工作项、发布审批和运营说明，五个明确资源 |
| partner_jordan (Jordan) | 外部协作方 | 明确共享的能力页，一个资源 |

这些是**应用演示身份**，共用团队获批原生连接；有效权限是应用角色白名单与当前原生权限的交集。用户已明确接受此方式。它们读取真实四源中的合成演示资料，但不能据此声称三名员工在四个平台分别拥有原生独立身份。受限角色不一定能引用每一个来源。

推荐先用工程账号问事故问题，再分别用产品和外部协作方账号问 `Can we offer payment-retry to all customers today?`，比较证据范围。切换账号前退出登录。各账号历史独立；多人共用同一账号时，历史与审计归属该账号。

组员克隆源码后，不配置平台账号也可以执行 `python3 -m scripts.reviewer_demo --accounts --open`。这条备用路径使用合成数据和模拟模型，不能冒充真实模型体验。完整操作见[中文接入说明](REVIEWER_ACCESS.md)和[英文评委指南](REVIEWER_QUICKSTART.md)。

## 已验证的结果

上一问答封版通过 642 项本地测试；最终五次原生 API＋真实模型问答均保留核心事实。Q1/Q2 单独提交分别为 13.26/9.60 秒，三个同时提交、串行处理的请求分别在 9.14/22.11/28.64 秒后返回。History 为 1.89 秒，引用预览为 0.75 秒。这些是历史 HTTP 实测，不是新角色版重新测得的浏览器耗时，也不构成 SLA。

角色版的本地测试覆盖：受限资料不会进入模型、角色不能覆盖原生拒绝、角色撤销影响 History/预览、模型发送前及最终返回前的策略变更会停止交付、角色配置缺失不会变成全权限。四源各一项实际原生读取已通过；三个真实服务账号登录与源状态已检查。没有用人工额度自动重复真实模型问答；新角色的真人问答和页面观看仍待实际操作。

当前源码包独立解压后 **661 项测试通过（39.447 秒）**，七个前端 DOM 套件通过。精确源码指纹及检查模式见[应用角色验证记录](reviews/2026-10-13-application-roles/VALIDATION.json)。源码、运行配置和恢复说明见[运行手册](FINAL_RUNBOOK.md)。[当前三角色源码包](../artifacts/contextledger-application-roles-source-20261013.zip)已生成，排除密码、凭据和运行数据库。旧冻结源码包保留作为历史快照，不将旧耗时或验收结果改写为本轮测量。

## 已接受限制与预算

回答可能引用正确原文，却不主动指出问题中的错误前提。用户已接受这一比赛原型限制；两版失败的自动解释实验未启用。部分答案仍有多余背景，主要呈现经校验的原文段落。

审计具备本地哈希链与账号/角色/源身份关联；不声称独立防篡改保管或企业 SSO。此前 28,602 个事件的本地审计链检查是历史证据，不是当前事件数量。

人工试用已取消提问次数限制，从启用起新增结算上限 **USD 1**；仍受费用预留和未知结算保护。原 Goal 的 55 次模型调用、USD 0.062807 新增结算及原两笔未知预留全部保留。本轮角色实现与检查不新增真实模型调用。自动付费测试不能占用人工额度。

## 团队最后的事项

1. 集中观看三个账号的问答、引用、History、退出重登和刷新恢复，再观看源更新、撤权与审计证据，记录真人结果并作出 G1 决定。
2. 审阅[提交文案](SUBMISSION_CANDIDATE.md)、[演示讲解稿](DEMO_CANDIDATE.md)、[封面](../assets/submission/contextledger-cover.png)、[架构图](../assets/submission/contextledger-architecture.svg)与真实 CodeBuddy 贡献材料，完成 G2。提交描述须区分应用角色和原生连接身份。
3. 确定托管服务器、域名、费用和开放期限，再批准公网发布、必要凭据迁移、源码推送及最终提交。已准备[部署说明](REVIEWER_DEPLOYMENT.md)；该条为上线前历史事项；10 月 13 日部署记录在本页上方，当前可用性与版本须以收尾报告核验，不据此宣称新候选已上线。
