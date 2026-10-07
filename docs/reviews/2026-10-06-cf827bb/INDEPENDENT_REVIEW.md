# AI-Bang2 独立产品、架构与交付审查

审查基准：`cf827bb12c022e63f8e1b498c565d79d20ed25e6`  
审查日期：2026-10-06  
范围：固定版本的入口、docs/01–05、状态/决定/验收/运行材料，核心问答/权限/检索/模型/HTTP/存储/审计代码，四源reader相关逻辑、前端代码、选取的测试与公开执行证据。不是全仓逐行安全认证。

本次使用GitHub连接器读取固定版本，没有修改远端仓库，没有访问用户本机服务、凭据、付费模型或私密截图；没有独立重跑全部311项测试。另做了离线函数探针：retrieval模块按Git blob SHA验证与原文件逐字节一致；价格/合成标记函数为源文件摘录。探针不等于完整应用或native验证。

## 结论

保留现有实现，进入收敛与交付验证，不恢复原来的大架构。真正的优先项是：当前日期下真实模型可用性、S-02新增对象发现与新鲜度、业务问题的召回和最终回答质量、审计语义及固定候选证据。不是补向量数据库、连续聊天或导出。

已确认ADR-040落实在Engine、HTTP和前端；8100的公开验证记录是Confluence native API/fake model，正问后负问没有继承证据，下载404仅由fixture/mock HTTP验证。8094未重启属于运行状态风险，不能由代码合并推断已更新。

311项测试日志确实写有OK，但属于fixture/mock；部分测试在验证限制/拒绝行为。原生四源和DeepSeek综合证据确实存在，例如live-s01的eng_b单题、8项证据、4个claims和两次已结算模型回执，但不是当前完整身份/模式矩阵、人类G1或最终候选通过。

## R1 · P0：真实模型复核日期已失效

**事实：** `brain/deepseek.py` 的PRICE_DATE为2026-10-05，check_price_review要求当前日期与其相等。`brain/operator_web.py::main`启动检查；非空模型请求再次检查。`tests/test_deepseek.py::test_price_date_and_approval_guard`明确期待2026-10-06拒绝。

**离线复现：** 10月5日允许；10月6日和16日拒绝。完整应用未在本次联网运行，但默认启动/请求的阻断路径由代码和现有测试共同支持。

**建议：** 保留fail-closed，核对官方模型/价格并记录新复核依据；增加跨日运行准备检查及用户可行动的错误。不能改系统日期、传旧today、关闭guard或清预算。保留US$20总账本。给候选进程加入最小版本识别，避免旧后台配新静态页面。

## R2 · P0：S-02尚缺新增发现，不只是缺一个worker

**事实：** `DelegatedAuthority.prepare`每问遍历固定native_ids，读白名单对象并更新索引。没有自动将新建页面、工单、消息或文件纳入；native资源的links还统一为空。已知对象的请求时刷新可以有价值，不能因为没有webhook就否定它。

**官方缺口：** 创建和更新应在有界可预测窗口内进入答案。手工新增ID或重启后的成功不能证明自动发现与完整新鲜度。当前原生更新/删除证据仅覆盖子集。

**建议：** 在具体批准的比赛专用容器范围内实现最小新增/更新发现，按源记录可查询延迟及故障行为。超出显式对象白名单的发现范围先申请，不扫描个人Drive/无关Slack。先保留简化实现，不要求Kafka、复杂worker或向量索引。

**性能：** 每次全量读取已知对象，再在多个阶段重复读取正文；长文每个window可能重复检查同一资源。HTTP整个请求持有store.lock。已有40–60秒以上的单样本记录说明值得优先剖析；不构成稳定SLA。先测源调用次数、分阶段时间和同资源重复量，再优化；不得缓存过时allow或移除模型阶段检查。

## R3 · P1：检索边界测试通过，不代表业务问题答对

**事实与反例：**
- `scripts/retrieval_acceptance.py`把“interruption annulled hypothesis”检索不到目标设为expected=False，仍标passed_local_subset。它诚实说明边界，但不是质量成绩。
- 本次同一合成文档的离线探针中，“Which hypothesis was abandoned?”没有窗口命中；含Orion/incident或现有别名的表达可以命中。这是单文档反例，不是全业务准确率。
- `tests/test_retrieval.py::test_marker_is_not_invented_for_real_model_windows`明确验证：正确晚段切片不含合成标记。本次C-01@1#20000:22400包含相关事实，marked_synthetic仍为false；按provider代码会在预留和网络前拒绝。
- `DelegatedAuthority.resource`为native资源写入links=[]；fixture授权一跳测试不证明native关联扩展。
- `test_engine.py::test_cross_source_claims_and_audit`等断言在整个JSON中查事实，事实只在evidence里也可能满足，不足以证明最终claims覆盖。

**建议：** 将批准原资源/版本和精确切片的可验证来源关系接入合成出口检查，不补造原文banner。建立少量未参与调参的自然表达、相似实体、限制/反证、长文和无答案案例，分别测召回、claims、引用和遗漏。先试通用词法、排序/去重与预算分配；只有业务改善证据支持才引入更重组件。模型复核只见已提供证据，不能发现完全没召回的关键反证。

## R4 · P1：审计“准备输入”被界面称为“已经发送”

**事实：** Engine在provider输入审查、预算及网络前记录sent_to_model；前端将其呈现为Sent to answer model。`live-unified/first-query-failure.json`明确存在同类记录但网络未发送、账本无该请求，并注明它只表示assembly。

**建议：** 新事件/读取投影区分输入准备、发送意图/尝试、有效回执和回答返回；不要改写旧日志。对price、synthetic guard、预算和review失败加测试；无网络发送时不能显示发送成功，超时也不能说确定没发送。

**保留与限制：** CodeBuddy离线Ed25519验证器真实存在，audit-mixed记录混合结果116条预期事件、17页和签名篡改案例。它能验证受可信检查点覆盖的段落，不证明同机全面失陷防护或未覆盖尾部安全。最终应绑定同一候选日志快照、可信检查点和验签结果，明确保管方式；不为此恢复普通用户下载。完整生产DB角色/WORM/企业密钥服务可延期，不能把它们自动当官方实现方式。

## R5 · P1：独立问答正确，证据和历史体验仍未闭合

**事实：** 040移除的按钮/路由不应恢复；独立问题提交和迟到响应防护已存在。当前preview中source_url是纯文本，而非原平台链接；普通用户看到原始evidence ID/locator JSON；Recent answers保存/渲染的response缺原始问题和生成时间，只能看整条答案及request ID。失败/等待提示较笼统。

**建议：** 保留现有页面，补重新鉴权后安全的原文入口；让历史能够识别问题和时间，旧记录缺失则明示；将诊断细节折叠。长等待、来源暂时无法验证和资料不足要有不泄露受限对象存在性的提示。不得为处理这些问题重建聊天、下载、管理操作或反馈训练功能。本次未现场观看用户浏览器，视觉判断依据HTML/JS和执行记录，不声称完成真人UX验收。

## R6 · P1：交付事实分散，旧入口容易诱发重做与误判

**事实：** PROJECT_START_HERE仍是“只有文档、Phase0”的初始交接；03前部仍以原候选栈为主要图示；BACKLOG主表及RUNBOOK部分段落残留live未配置、重复输入、导出等旧状态。后续决定和证据已覆盖其中许多内容。它们不是当前pending，也不能删除历史来掩盖过程。

**建议：** 在现有文件顶部维护唯一当前总表：需求性质、实现、fixture/mock、native、live model、浏览器、人工、commit/运行版本与证据。旧记录标superseded或归档。311日志不等于当前commit的干净归档重建；历史297等重建成绩不能替代新候选。G1/G2及非作者任务评估仍须人实际完成。

## 范围取舍

保留：本地只读试点、独立问答、重新鉴权历史、精确引用/版本保护、原生委托身份、fail-closed、预算及审计、现有真实CodeBuddy贡献。

修正：R1–R6。核心是官方五场景、实际用户效果和可重建交付，不是把测试数字做大。

删除/延期：不恢复New question/答案导出；不新增DM、附件大扩展、复杂GraphRAG、多Agent、自动反馈学习、无业务依据的管理功能；不为旧候选图强制迁移整套数据库/框架。六persona完整矩阵与部分生产标准是团队设计，调整必须有明确决定，不能把未做项涂绿。保留关键角色权限对照，原生product_ops不能由eng_b替代。线上URL是可选项，不为加分仓促公开当前loopback服务。

## 建议下一阶段顺序

- 10月6–7日：当前状态/进程版本统一；复核并修复日期阻断；长文出口和质量反例固定为回归。
- 10月7–10日：S-02最小发现/新鲜度；业务质量与重复原生读取优化；审计阶段语义修正。
- 10月10–12日：现有界面收敛；在明确模式和关键角色对照下演示五场景；组织一次非作者任务/安全观看。
- 10月13日：固定候选，干净重建并重跑所承诺模式。
- 10月14–15日：录像、封面、描述、使用证明、证据/访问方式和G2审阅，保留提交缓冲。

日期为审查建议，不是官方阶段安排。时间不足先删非核心增强，不删官方场景或伪造验收。

## 主要证据定位（均在审查固定commit）

官方及当前决定：docs/01_OFFICIAL_BRIEF.md；docs/DECISIONS.md，AUTH-014/016、ADR-040。  
实现：brain/engine.py、retrieval.py、delegated_query.py、deepseek.py、synthesis.py、operator_web.py、server.py、store.py、audit.py；四源reader；web/app.js、index.html；tools/audit_verifier/verify.py。  
断言：tests/test_deepseek.py、test_retrieval.py、test_engine.py、test_http.py；scripts/retrieval_acceptance.py。  
执行记录：evidence/runs/independent-query/{README.md,full-tests-final.log,live-verification.json}；live-s01/verification.json；retrieval-local/results.json；live-unified/first-query-failure.json；audit-mixed/verification.json。

本次离线探针：independent_probes.json；执行脚本reproduce_review.py；按blob校验的retrieval_snapshot.py。接管指令：CODEX_TAKEOVER_PROMPT.md。
