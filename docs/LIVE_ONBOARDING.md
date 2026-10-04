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
- 四源账号注册、API 接入、外部种植：not_run。
- DeepSeek 调用：not_run；预算消耗为本任务未发起任何请求，不代表查询过平台余额。
- CodeBuddy 审计任务已合并 main，PR #2；与本接入任务独立。
