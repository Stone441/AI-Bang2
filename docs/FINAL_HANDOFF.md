# ContextLedger · 当前发布与提交入口 · 2026-10-16

应用已通过 [PR #13](https://github.com/Stone441/AI-Bang2/pull/13) 合并，发布commit **869f407**。现有网页 **https://contextledger.hellokyleshi.com** 已切换到该commit的代码/UI。后续文档提交仅补发布证据，不更换应用字节。

完整结果：[发布与部署报告](reviews/2026-10-16-release/REPORT.md)；此前资料归档：[本地收口报告](reviews/2026-10-16-final-check/REPORT.md)。

## 提交材料

- [英文文案](SUBMISSION_CANDIDATE.md)、[架构图](../assets/submission/contextledger-architecture.svg)、[封面](../assets/submission/contextledger-cover.png)、[CodeBuddy实际贡献](CODEBUDDY_CONTRIBUTION.md)。
- 私有CodeBuddy原始对话、7张过程截图及补丁仍单独保管，不在Git；尚未上传赛事。
- 四源真实验收和历史fixture证据已归档，保留各自原版本和失败，不能用历史测试给新版本背书。
- 原本地收口85d22ea资料包保留为历史快照；当前源码以GitHub main及发布报告为准，发布后的新包在本检查工作区artifacts/published-20261016。

## 使用与边界

公网使用已有密码账号，source-review模式，账户/权限/预算不变。完整语义验收仍未通过，隔离引文实验未默认上线；fa88f2f本机人工试用仍为独立实例。浏览器公网新版登录页已实际检查；三账号API安全检查通过本机反向代理上游，不冒称公网全流程或真人G1/G2。

无凭据复现：`python3 -m scripts.reviewer_demo`，仅fixture/fake模式。原main目录“打开试用页面.command”仍指向私有人工试用；远程组员请使用上面的公网链接。

下一步是团队核对最终文案与私有证明上传范围，完成赛事签核及提交。推送合并和网页升级已完成，不需要重复批准；比赛提交尚未执行。
