# Live onboarding · approved synthetic scope

2026-10-05：授权见 AUTH-003。此清单不是 live 集成完成证明。

## 团队先完成的注册

1. 在 Atlassian 创建比赛专用站点，加入 Jira 和 Confluence；选择可配置权限的试用方案。Free 版不能完成全部权限验收。记录试用截止日，不启用未经批准的付费续订。
2. 新建比赛专用 Slack workspace，不在 NTU 课程 workspace 安装应用或读取资料。
3. Drive 使用独立项目账号为优先方案；若沿用个人账号，仅创建并授权比赛专用测试文件。OAuth scope 另行最小化；文件夹名称不构成权限隔离。
4. 将站点 URL、workspace URL、测试 Drive 文件夹 URL 提供给开发者即可，不发送密码/token。验证码、条款接受和授权确认由团队操作。

注册入口：[Atlassian](https://www.atlassian.com/try/cloud/signup)、[Slack](https://slack.com/create)。Google 账号由团队自行登录/注册。

## 已准备的合成数据

```sh
python3 -m scripts.prepare_live_seed --out .runtime/live-seed-20261005
```

首次已实际执行，输出 13 个对象（12 顶层 + Jira 受限评论），6 个合成身份。命令只写新的本地目录，不调用网络，不覆盖既有目录。重跑请指定新目录。

`manifest.json` 包含内容校验值、父对象、关联对象、fixture policy、预期可读用户。真实 native ID/URL 留空，全部 `not_seeded` / `live_acl_verified:false`。这是待映射的种植计划，不是平台 API 请求体或已实施 ACL。

六个合成身份不得悄悄合并到同一真实账号。优先映射三位队员为 eng_a、eng_b、product_ops；contractor/security/auditor 无真实测试身份时，对应 live 案例保持 not_run。Jira 标题中的 PAY 编号为合成引用，实际创建后的 issue key 需要映射，不能假定相同。

下一开发步骤：限定站点/空间/文件白名单，先部署原生 ACL，再写资料，记录实际 ID；使用各用户委托凭据核对允许/拒绝。管理种植工具与产品只读连接器分开，不用采集服务账号的权限代替员工权限。

## DeepSeek 接入

已批准直连、合成资料、首轮等值 US$20 总上限、不自动充值。此轮没有读取或调用现有 key。

密钥不要发到聊天；待适配器与预算控制配置格式落地后，用户在本地忽略配置中填写。实现前仍使用 fake model，不创建一个当前程序不会读取的伪配置入口。

接入前必须完成：固定官方 endpoint/model；请求前预算预留及失败未知消耗处理；有限 token/超时；响应 schema、证据引用与内容支持验证。现有 Engine 只接受原文摘录，不能直接放宽为任意模型生成句子。真实生成与引用支持评测需单列，不冒充 fake 测试。

## 当前结果

- 本地 seed 导出实际运行；新增测试通过，验证受限评论/频道预期读者、内容哈希及禁止覆盖。
- 2026-10-05 浏览器实测：Slack `https://ai-bang2.slack.com` 已创建并选择 Free，用户已自行使用 Google 登录；未邀请他人。workspace ID `T0C6FQ246TF`。
- Jira `https://ssy44199.atlassian.net` 已进入可用看板；创建 `AI-Bang2 Payment Service`，实际 key `KAN`，board `2`。平台自动生成的 KAN-1/KAN-2 是示例任务，不是我们的 fixture。已退出后使用同一 Google 账户重新登录并验证可访问原站点。
- Confluence：用户明确接受 Customer Agreement 后，已在同一站点开通 Premium 30 天试用并进入编辑界面。账单详情实测 Trial ends = 2026-11-04，Payment info = None；页面提示未补付款方式将停用，不能假定自动降级 Free。下一账单估算 USD 13.19 不是实际扣款；未添加付款方式或批准续订。到期前需主动处理降级。平台自动生成的 Meeting notes 草稿不是项目种植数据。
- Drive 测试文件夹未创建。四源 API 接入、合成资料外部种植与 live ACL 验收均 not_run。
- 真实截图位于 ignored `evidence/tool-usage/private/onboarding-20261005/`：slack-created.png、jira-created.png、confluence-confirm.png、jira-google-login.png、confluence-trial-active.png；未上传。
- DeepSeek 调用：not_run；预算消耗为本任务未发起任何请求，不代表查询过平台余额。
- CodeBuddy 审计任务已合并 main，PR #2；与本接入任务独立。

### Confluence 专用空间 · 2026-10-05

已通过浏览器创建 `AI-Bang2 Synthetic Lab`，space key `AIBANG2`，主页 ID `131286`，URL https://ssy44199.atlassian.net/wiki/spaces/AIBANG2/overview 。创建表单选择 Restricted（Only you have access until you add others）；尚未用第二身份验证拒绝访问。没有邀请其他用户或开放匿名访问。平台自动生成两份 Template 页面，不算 fixture，不应纳入项目文档白名单。创建截图：`evidence/tool-usage/private/onboarding-20261005/confluence-space-created.png`（ignored，未上传）。

接续：取得队员测试邮箱及 eng_b/product_ops 映射，核验空间权限后逐文档种植本地 seed；当前账号作为管理种植身份，不当作普通员工 ACL 通过证据。真实用户委托/API 配置和文档种植仍未完成。

### 独立测试身份邀请 · 2026-10-05

用户提供两个本人控制的 QQ 邮箱，按提供顺序映射 eng_b 和 product_ops。已通过 Confluence 邀请界面发送两封邀请，页面明确显示 Users added / 邮件已发送；后台两位用户均 Invited。真实邮箱/native account ID 仅保存在 ignored `.runtime/live-identities.json`，不入 Git。当前仅开通 Confluence User，未授予管理员、未开通 Jira，未将邀请视为已注册/已登录或空间 ACL 验证。截图：ignored `evidence/tool-usage/private/onboarding-20261005/test-users-invited.png`。

用户接续：分别在两个 QQ 邮箱打开 Atlassian 邀请，用对应邮箱注册/登录；建议使用独立浏览器配置，避免已登录的 Google 管理员账号误接受。新密码、验证码和法律协议由用户完成，不发送密码到聊天。之后核验 account ID、普通用户空间允许/拒绝，并配置文档级权限。

### 首个原生页面权限配置 · 2026-10-05

用户报告两个账号已注册；空间成员管理实际显示 Kyle6745 / Kyle29183，均设为 Viewer（查看和评论），管理员仍为 Kyle SHI。后台注册标记/last seen 不当作用户访问证明；本轮仍未取得各普通用户实际会话。平台自动附带 Chat Notifications / Microsoft Teams App Admin 成员已观察到，非本轮主动安装；应用身份应与员工身份区分，需后续审计其来源和能力。

C-01 已实际发布，native page ID `98564`，URL https://ssy44199.atlassian.net/wiki/spaces/AIBANG2/pages/98564/C-01+Payment-service+runbook 。发布前设 Restricted，具体名单只有管理种植者和工程师 Kyle6745，工程师 Can view，产品运营未加入。核心 runbook 原文发布后读取核对一致，添加合成警示和 fixture ID 元数据；manifest 已本地映射。真实端点授权/搜索隐藏/撤权验收仍 `not_run`，不可将界面配置当允许/拒绝测试通过。证据：ignored `confluence-viewers.png` 和 `confluence-c01-restricted.png`。

精确接续：用独立普通用户会话先验证 eng_b 可读 C-01、product_ops 被拒绝，再用管理员撤回 eng_b 页面访问，原会话重读应拒绝；之后恢复测试基线。未取得普通用户会话时继续 C-02/C-03 种植及只读连接器实现，权限合同测试保持 not_run。

2026-10-05 继续种植 C-02：真实页面 `164283`，URL https://ssy44199.atlassian.net/wiki/spaces/AIBANG2/pages/164283/C-02+Payment-retry+capability 。在 AIBANG2 受限空间内继承访问，两个 Viewer 可读的原生配置已保存；未开启公网匿名访问。正文与本地 seed 核对一致，包含合成警示与 fixture ID。截图 ignored `confluence-c02-published.png`。fixture 中 contractor/security 等身份仍未映射；不宣称完整权限矩阵。C-03 及其安全身份未种植/未映射。
