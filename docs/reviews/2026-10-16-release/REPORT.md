# GitHub发布与现有网页升级 · 2026-10-16

用户明确授权推送、合并和更新现有网页链接。本次已完成，未提交比赛、上传私有对话原件或新增模型调用。

## 发布与部署

- PR #13：https://github.com/Stone441/AI-Bang2/pull/13 ，已合并。
- 应用发布commit：869f40741f89b7327f442114af8bfdf9e8aea859。其brain/scripts/web/tests与此前800项离线通过的2b79036相同；本轮文案整理不改变运行代码。
- 现有链接：https://contextledger.hellokyleshi.com ，Chrome实际打开新版登录页；截图hosted-login.jpg。
- LaunchAgent现从不可变869f407源码目录启动。启动指纹2ae1f11b731edb67d6a5686cbac99d0096868d52978a0089718b0bde7c99a3ad；加载时间2026-10-16T07:10:18.953950Z（新加坡15:10）。
- 保留source-review/structured/single/none8192配置、原三账号与审计范围、原state-root及人工grant；未默认开启分题或隔离引文实验。私有fa88f2f人工试用仍独立保留，不冒充与公网模型模式相同。

## 实际验收及限制

- 本机反向代理上游：health指纹匹配；HTML/app.js/style.css与不可变release逐字节一致。
- 三个现有普通账号登录/session/runtime/logout均通过；Secure/HttpOnly/SameSite=Strict cookie齐全；匿名session、普通账号审计查询、跨Origin登录均403。
- 四源最近同步均complete，快照current；模型及问答readiness为ready。它是检查时的快照，不是长期SLA或已重新生成答案的证据。
- Chrome公网实际看到新UI及密码登录页。命令行公网请求被Cloudflare 403/1010拒绝；未修改WAF、伪装客户端或绕过。API认证检查经同一服务的本机上游和现有反向代理Host/HTTPS头完成，不冒称完整公网登录验收。
- 原账号注册表SHA256不变；预算、grant、model_calls计数和既有unknown状态不变，新增模型调用0。没有重置费用、搬迁身份或恢复旧数据库。
- 首次bootstrap在旧服务卸载时返回5；验证plist且确认旧服务已移除后再bootstrap成功。保留此操作失败，不称零中断。上线前私有数据库/配置备份已保留，未回滚数据库。

证据：[DEPLOYMENT_CHECK.json](DEPLOYMENT_CHECK.json)、[READINESS.json](READINESS.json)。完整语义验收仍有历史失败，G1真人观看及G2赛事签核不因此完成。

## Git工作区

原main曾因8个同名未跟踪fixture文件拒绝快进。逐个确认与远端文件字节完全一致后，将原件移至原main/.runtime/release-sync-20261016私有备份，再快进；8文件现为已跟踪且字节不变。原三份历史运行JSON和本机启动器修改仍保留。其他工作区没有被reset、删除或改写。

本报告及入口文档作为后续文档提交发布；它们不改变已部署应用字节，所以无需为记录发布结果再重启服务。

## CodeBuddy文案整理

README与当前任务入口改为实际交付说明；修正技术交付文档的“未提交、待集成”旧状态。新增CODEBUDDY_CONTRIBUTION.md，说明独立审计校验器、签名检查点、20项组件测试、真实提交和证据。初始执行计划明确标为历史并折叠，原提交/对话/截图不改写。仓库继续如实说明多工具开发及Codex/团队的审查、集成与其他开发工作。
