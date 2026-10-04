# Acceptance coverage · local candidate

当前是 fixture_fake_model 的 32 个 unittest 方法（另含参数化 subtests），不是 51 个计划案例全通过。具体结果以 `evidence/runs/local-latest/tests.json` 为准。五场景 `scenarios.json` 仅为本地子集；真实平台、真实模型、人工验收均未通过。以下未覆盖部分保留，不改写 05 的 oracle。

| IDs | 当前状态与实际证据 / 缺口 |
|---|---|
| Q-01/02/04 | local subset verified：工程五事实、四源、pilot/GA；fake 摘录，不代表 LLM 综合质量 |
| Q-03 | partial：关键词实体路径已实现，尚无专门错误相似对象对照 |
| Q-05/06/07 | local subset：缺证据、伪造 ID、不支持 claim 均检查；真实模型及人工语义支持 not_run |
| Q-08 | partial：固定四源授权范围检索；没有模型路由 |
| Q-09 | local one-hop verified：authorized seed + 每目标授权；两跳未实现 |
| Q-10 | partial：候选 24、输入 16000 字符预算；长文/近重复质量未验证 |
| P-01/02 | local verified：服务端 session、body role 拒绝、同角色不同频道 |
| P-03/04 | local verified：四源撤权/unknown；真实 429/token propagation blocked |
| P-05/06/07 | local verified：历史/导出/预览复核；无答案缓存；附件下载未启用 |
| P-08 | local verified：存在/不存在可见结果一致；统计时间侧信道未证明 |
| P-09/10 | partial：fixture 原生策略和单独评论/隐藏链接；真实继承/附件 blocked |
| P-11 | local subset：恶意原文不能授予权限或调用工具；fake 可能如实引用恶意文字，真实模型 injection not_run |
| P-12/13 | local verified：拒绝非 demo tenant；旧版本引用拒绝 |
| P-14 | local only：没有第三方处理、HTTP generic errors；生产审计加密/出口 not_run |
| P-15 | local verified：内存/磁盘源生成期间撤权阻断；平台传播边界 blocked |
| P-16 | not_supported：DM 不启用 |
| F-01/02 | local verified：四源创建/更新、单对象发布；真实自动同步时延 not_run |
| F-03/04 | local verified：撤权不重建正文，删除立即由权限检查阻断，再 tombstone |
| F-05/06 | local verified：重复/乱序、失败重试、事务发布、游标不越过未完成任务 |
| F-07 | partial：已知落后证据不使用；索引 failure health，真实断连/续传 not_run |
| F-08 | not_started：真实 change-token 失效/定期对账 |
| A-01/08/09/10 | local verified：问答正文、逐对象检查、模型输入/引用/dispatch，失败关闭，60 并发追加链 |
| A-02 | blocked：SQLite connection authorizer/trigger 已测试；独立数据库角色未实现 |
| A-03/04 | partial：本地链和保存在测试内存的 trusted head 检查；独立签名留给 CodeBuddy |
| A-05/06/07 | local verified：有限 NL 模板、白名单参数、scope、带时区范围、稳定分页；任意 NL 不支持 |
| A-11 | blocked：CodeBuddy 签名/轮换/可信检查点任务 |
| U-01 | local verified：标准库可启动、显式 demo、HTTP 实际请求；独立 git archive 目录 setup/test 已通过 |
| U-02 | partial：前端分区 + server role enforcement、无 HTTP ACL 管理入口；非公开部署 |
| U-03 | not_run visual：英文 UI/labels/focus/CSP 已实现；浏览器自动化被 ERR_BLOCKED_BY_CLIENT 阻挡 |
| U-04 | not_run：无真实模型性能/成本；场景耗时只为本机 fake 调用时间 |
| U-05 | partial：五场景自动记录/架构/源码；真实腾讯对话截图、签名及 live 记录缺失 |
| U-06 | blocked：非作者人工对照尚未组织 |

失败改进记录：首次自然 S-01 未检索到 PAY-103，原失败见 `evidence/runs/first-scenario-failure.json`。保留断言，新增逐目标授权的一跳检索后回放通过。未硬编码展示答案。
