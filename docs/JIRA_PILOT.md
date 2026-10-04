# Jira delegated read pilot

2026-10-05：只读reader/CLI及Confluence+Jira共享Engine已mock验证；Jira真实API仍not_run。J-02实际UI种植为KAN-4、Done，证据 `evidence/runs/live-jira/seed-j02-kan4.json`。不能把工单标题中的PAY-102当原生key，也不能猜测原生issue/project ID。

## 读取与权限

每次按当前操作员独立凭据GET `/rest/api/3/myself`，要求匹配已核验accountId、active与atlassian accountType；管理员替换、过期、unknown均不放行。固定HTTPS站点/cloud UUID；issue ID→key、project ID和comment ID→parent ID白名单，移动/复用或返回其他项目不能扩大读取范围。API scope、员工Jira应用访问与原生权限配置仍需具体批准/落实；现有Confluence token不用于Jira。

工单仅取summary/description/status/assignee/project/updated，不取评论/附件/任意JQL。受限评论是单独证据：先读取父issue，再以同一员工凭据GET该comment；父正文可见不代表评论可见。源API负责project/issue security/评论group或role限制；本地group模拟不代替它。403/404为deny，其余失败/身份不匹配/缺字段/不支持ADF为unknown，不返回正文或上游错误。无正向ACL缓存，不跟重定向。

普通文本ADF支持paragraph/list/table/code等；嵌入媒体、卡片、mention/未知节点拒绝，不后台抓关联资源。Jira正文revision用完整内容SHA-256记录在locator，索引version是兼容整数指纹，非原生单调revision/ACL版本。当前读取还比对完整payload，碰撞停止发布；内容、状态、负责人或updated变化后旧引用/历史不可用。

## 配置与命令

复制 `config/jira-pilot.example.json` 到ignored `.runtime/jira-pilot.json`，在平台种植和原生ID核验后替换占位符，填已核验员工accountId。`comment_ids`将comment ID映射到父issue ID；未种植的评论不能填猜测ID。只包含比赛合成对象，排除KAN-1/KAN-2等平台示例和个人资料。

credential references只接受 `AIBANG2_JIRA_*`；secret值不入JSON。可选择在真实TTY `--prompt-credential`隐藏输入，内存组装Basic，不保存/导出环境，不回退echo；没有具体Jira token授权时不执行带live命令。

默认不联网的配置检查路径：

```sh
python3 -m scripts.jira_query --config .runtime/jira-pilot.json --actor eng_b --resource NATIVE_ISSUE_ID
```

预期not_run、退出2，不读凭据/配置/DB。实际Jira凭据和scope获准后才使用：

```sh
python3 -m scripts.jira_query --config .runtime/jira-pilot.json --actor eng_b --resource NATIVE_ISSUE_ID --prompt-credential --live
python3 -m scripts.jira_query --config .runtime/jira-pilot.json --actor eng_b --question "Show the payment-service fix status" --prompt-credential --live
```

resource诊断stdout仅decision/指纹version/是否有内容，不打印标题、正文或secret；query输出此次允许的合成摘录与证据，DB/完整审计在`.runtime/jira-query.sqlite`。history-id重查旧依赖。CLI actor为本机操作员选择，不是员工登录。shared `DelegatedQueryPilot({'confluence': ..., 'jira': ...}, store)`支持同一tenant跨源，逐源audit标mock/live，fake model不产生收费。

## 验证与未完成

14 reader、10跨源、6CLI测试，mock包括父/子权限、源撤权、401/429、搬迁/错误项目、内容更改（timestamp不变也能检测）、旧历史/引用、最终模型前撤权、短指纹碰撞和默认无联网。全仓库结果见local-latest/tests.json。首个评论检索测试用含下划线的标记误命中父工单中的synthetic词；改为独立单词sentinel以隔离评论场景，保留独立资源、模型输入和撤权断言。

仍缺：真实ID发现、Jira普通账号访问/委托token、真实评论/issue-security与权限矩阵、附件、分页/后台同步、跨源关联链接、真实模型、SSO。Free计划实际能力需核验；不能用mock冒充Free支持完整issue security。J-01/J-03及安全评论尚未种植；不虚构Maya原生负责人账号。

核对官方文档（2026-10-05）：[Get current user](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-myself/#api-rest-api-3-myself-get)、[Get issue](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get)、[Get comment](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-id-get)、[ADF structure](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)。完整granular scope列表尚未核齐/批准，不按印象申请scope。
