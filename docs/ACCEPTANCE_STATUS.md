# Acceptance coverage · local candidate

2026-10-05 S-01工程事实single eng_b live subset：新增J-03/KAN-5实际In Progress，正文scenario owner Maya fictional、native assignee Unassigned分别表达；四源8证据/4claims覆盖原因、撤回猜测、J-02 Done与J-03仍open、当前CF native3/runbook v1。7fact checks+agent全原文语义对照/quotes/native四阶段/双回执账本独立核验通过；不是原eng_a及product_ops矩阵或人G1。283回归方法数量不变，新增J-03正/负subtests；evidence/runs/live-s01。

当前283个unittest方法（61 local synthetic + 222 mock HTTP/model/credential contracts，另含参数化subtests），不是51个计划案例全通过。具体结果以 `evidence/runs/local-latest/tests.json` 为准。五场景 `scenarios.json` 仅为本地子集；四源真实查询/各源撤权子集与DeepSeek原文选择及opt-in综合另列。综合已有一次成功四源测试与agent语义对照，完整live矩阵、SSO、人工G1/G2仍未通过。以下未覆盖部分保留，不改写05的oracle。

| IDs | 当前状态与实际证据 / 缺口 |
|---|---|
| Q-01/02/04 | local subset verified；Q-02 live synthesis subset：pilot/GA、Done/发布及未确认日期已agent对照；Q-04首题保留Slack撤回时间线。完整S-01五事实及非作者人工综合质量仍pending |
| Q-03 | partial：关键词实体路径已实现，尚无专门错误相似对象对照 |
| Q-05/06/07 | local/mock subset：缺证据、伪造ID、quote不匹配、负面/未知review拒绝；live synthesis 4claims精确quote和agent语义支持subset。模型review非准确性证明，人工语义支持not_run |
| Q-08 | partial：固定四源授权范围检索；没有模型路由 |
| Q-09 | local one-hop verified：authorized seed + 每目标授权；两跳未实现 |
| Q-10 | partial：候选 24、输入 16000 字符预算；长文/近重复质量未验证 |
| P-01/02 | local verified：服务端 session、body role 拒绝、同角色不同频道 |
| P-03/04 | local verified：四源撤权/unknown；真实 429/token propagation blocked |
| P-05/06/07 | local/mock verified；原文及综合模式旧历史/引用/导出native Slack撤权live subset（synthesis-native-revocation）；恢复后合法导出精确匹配。完整平台/ACL矩阵仍pending；无答案缓存，附件未启用 |
| P-08 | local verified：存在/不存在可见结果一致；统计时间侧信道未证明 |
| P-09/10 | partial：fixture 原生策略和单独评论/隐藏链接；真实继承/附件 blocked |
| P-11 | local subset：恶意原文不能授予权限或调用工具；fixture业务源+真实DeepSeek单个恶意文档样本已验证（synthesis-injection），无工具执行/私有资料模型输入；完整攻击族及非作者质量验收not_run |
| P-12/13 | local verified：拒绝非 demo tenant；旧版本引用拒绝 |
| P-14 | partial：已批准合成证据发送DeepSeek，当前权限检查及受控错误/预算有local/mock和live子集；未发送真实敏感数据。生产审计加密/出口治理not_run |
| P-15 | local verified：内存/磁盘源生成期间撤权阻断；平台传播边界 blocked |
| P-16 | not_supported：DM 不启用 |
| F-01/02 | local verified：四源创建/更新、单对象发布；lifecycle-local额外四源更新矩阵记录旧索引拒绝/新版本发布；真实自动同步时延 not_run |
| F-03/04 | local verified：lifecycle-local四源各撤权/删除，旧索引模型输入、旧历史/导出projection/引用全部保护，不重建正文，再 tombstone；真实更新/删除完整矩阵not_run |
| F-05/06 | local verified：重复/乱序、失败重试、事务发布、游标不越过未完成任务 |
| F-07 | partial：已知落后证据不使用；索引 failure health，真实断连/续传 not_run |
| F-08 | not_started：真实 change-token 失效/定期对账 |
| A-01/08/09/10 | local verified：问答正文、逐对象检查、模型输入/引用/dispatch，失败关闭，60 并发追加链 |
| A-02 | blocked：SQLite connection authorizer/trigger 已测试；独立数据库角色未实现 |
| A-03/04 | local signature subset verified：CodeBuddy 离线 Ed25519 检查点/独立 CLI；正文、中间/已覆盖尾部删除、整链重算、错误公钥/签名拒绝。独立保管运营边界尚未建立 |
| A-05/06/07 | local verified：有限 NL 模板、白名单参数、scope、带时区范围、稳定分页；任意 NL 不支持 |
| A-11 | partial：缺检查点显式不可信、未覆盖尾部单列、非 Ed25519 密钥拒绝已测试；当前单公钥，密钥轮换未实现 |
| U-01 | local verified：标准库可启动、显式 demo、HTTP 实际请求；独立 git archive 目录 setup/test 已通过 |
| U-02 | partial：前端分区 + server role enforcement、无 HTTP ACL 管理入口；非公开部署 |
| U-03 | partial：英文原文答案/引用/历史/导出已有真实浏览器subset；综合quotes/双回执/引用/history/raw下载真实浏览器验证，Enter展开/Escape关闭partial；完整键盘/对比度及非作者G1pending |
| U-04 | live measured subset：同题live API/fake model53.21→40.12秒（单样本）；真实综合双调用58.95秒、双回执和共享USD20账本实查。供应商实扣/并发性能未测，不作SLA承诺 |
| U-05 | partial：五场景自动记录/架构/源码；真实腾讯对话/7截图及离线签名已完成；live记录已分模式保存，完整矩阵和最终材料未提交 |
| U-06 | blocked：非作者人工对照尚未组织 |

失败改进记录：首次自然 S-01 未检索到 PAY-103，原失败见 `evidence/runs/first-scenario-failure.json`。保留断言，新增逐目标授权的一跳检索后回放通过。未硬编码展示答案。

2026-10-05 live增量：Confluence C-01 v1 query 的原文/定位/引用/逐阶段授权已查DB，9checks通过；实际撤权后同一pilot/Actor/逻辑会话追问、模型输入、旧历史和引用均保护，7runnerchecks+7DB核验通过。映射Q-03/06/07、P-03/04/05/07、F-03、A-01的Confluence操作员子集，不将上述整体ID标live passed。无跨用户答案缓存、附件或真实前端登录，不能扩大P-07/01；18事件链无独立检查点，不能扩大A-03/04。实际结果见 evidence/runs/live-confluence/；已恢复原生Can view，仅UI读回，未追加API复验。


2026-10-05新增mock覆盖：Jira当前字段、父工单/受限评论独立授权、跨Confluence/Jira答案、更新/撤权/unknown/旧历史/引用及碰撞停止；operator网页登录含native identity匹配、ticket单次/过期、CSRF/Host/伪role、同HTTP session撤权后的query/history/export/preview。对应Q-03/06/07/08、P-01/03/04/05/07/09、F-03本地或mock子集，未将完整ID升级passed。网页入口不是SSO，真实网页和JiraAPI仍not_run。J-02/KAN-4 UI种植证据仅原生Done/正文，不能等同源权限通过。前一增量中的Q-04（Slack撤回猜测）映射已纠正，不用Confluence runbook验收替代Slack线程场景。


2026-10-05 synthesis增量：281回归、前端Node、五场景local subset。10项live检查、4结论精确quote及agent语义对照见 `evidence/runs/synthesis/live-query.json`，同模型独立prompt/call复核、当前权限`review_dispatch`和返回前检查分别记录。Q-02/06/07、P-01/03/05/07/15、A-01/10、U-04仅按各实际local/mock/live子集覆盖，不将整体ID标passed。首次四源覆盖探针failed记录保留（三源7证据），第二个明确Jira code fix问题四源8证据通过；关键词检索并不保证全语义召回。两题3340microUSD保守费用，不是vendor invoice。G1非作者观看、综合live撤权、完整五场景矩阵仍pending。


2026-10-05 P-11补充：真实DeepSeek、fixture-only业务源的单个恶意授权文档样本已执行；6自动边界检查及agent逐结论核对通过。含GA谎报/admin/private channel/other-user audit/external URL指令的资料实际进入模型，未采纳；仅固定模型endpoint无tools，私有S-01不发送。来源evidence/runs/synthesis-injection/，1331microUSD保守账。输出有额外无关但受证据支持的事故claim，相关性单列。完整攻击族、源平台传播和非作者G1仍未验收，不将P-11整体标passed。


2026-10-05 8094综合真实UI子集：eng_b身份、8对象四源输入/五阶段各8allow、4结论支持片段展开、双回执、Slack reply精确预览、Recent answers与raw实际下载一致已核验（synthesis-ui/verification.json）。这次4结论引用四源，但问题保障措施漏答，Q-07完整性failed；费用1591microUSD上界。v2增加模型question_covered严格判断和生成覆盖提示，282回归含missing/false/unknown拒绝；两次真实拒绝诊断分列，不能据拒答称修复后回答质量通过。现有用户8094 Python进程仍是v1，刷新前端不会加载新model。完整live场景/综合原生撤权/非作者G1不变。

修复后单题live结果：synthesis-ui/coverage-live-query.json，四源8对象、11checks及保障措施精确quote通过；agent覆盖/语义检查通过，前三claim冗余保留。首轮review拒绝原因unknown、次轮缺quote拒绝分列；不是完整Q-07人工质量通过，综合原生撤权及非作者G1仍pending。

2026-10-05 会话修复：共享CookieJar/双loopback端口的登录、退出、CSRF隔离local verified，283回归。实际8094新页面的query后session-ended、旧信息清空已观察，原因unknown；不是新问答/撤权通过。Chrome双端口临时fixture自动导航blocked，浏览器完整验收不补写。

2026-10-05 综合v2原生撤权：真实8094 eng_b在private Slack member2→1后旧reply citation拒绝并清空旧内容；含Slack的旧综合history/supports/双回执整条隐藏，不含Slack的旧记录可用。单独批准第二轮后旧export拒绝、无文件0→0；两轮都恢复同一UID/Members2，合法导出8146字节精确一致。P-05/07/09与S-04按该合成private子集verified，非全ACL/真实SSO/人G1；初始事故问答三源6input/3claim，不称四源coverage或完整S-01，源码283回归沿用。证据synthesis-native-revocation/。

2026-10-05 F/P lifecycle live subset补充：Confluence真实内容更新1→2及恢复3，新增内容问答、旧版本引用/history保护；Drive临时文件native trash后旧引用/history/export projection拒绝、query/model无旧证据而索引保留，原三文件UI保留。见live-lifecycle。仅独立trusted operator/fake model，无本次HTTP/browser下载或后台同步测量；完整四源矩阵/G1不升级。
