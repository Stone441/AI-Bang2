# 查询性能、答案质量与稳定性重新分析

日期：2026-10-13，Asia/Singapore。任务 DEV-PERF-REVIEW-03。基准 HEAD `1649e301959b7eea7303fdda9ba0ee58a578d19e`；独立分支 `review/query-optimization-20261013`，保留接管时全部未提交计时/契约工作。分析针对当前工作树，具体源码 SHA256 在 [offline-analysis.json](offline-analysis.json)。本轮新增离线分析脚本、报告与状态；应用、服务、预算及原始证据未修改。

用户目标为**完整答案生成并显示 ≤3 秒**，不是首字、进度响应或只返回检索结果。同学的完整答案 2–3 秒是用户转述，其权限/模型/资料规模/缓存条件未知。它是有效的体验标杆，尚非同条件架构对照。

## 1. 结论与验证边界

当前几十秒的主要原因有证据指向：多阶段原生源读取、来源内串行网络往返，以及部分模型请求的长推理。固定窗口和词法检索存在质量问题，但当前规模的 CPU 检索没有消耗几十秒。不能靠更换向量库或添加 GraphRAG 保证端到端 3 秒。

模型故障至少有三层：JSON/字段格式、证据支持、问题完整覆盖。现有服务器已严格检查格式和连续引文；这些检查仍不能证明答案覆盖用户要问的措施。更严重的已记录反例是合法输出、review accepted，但漏掉输入已有的 C01 操作。重复 prompt 调整和不断加 cap 不应作为主方案。

3 秒是新目标，**当前未达到、未证明可在现有全部外部条件下达到**。本轮没有修改运行时，也没有新 native/live model/browser 测量。当前受限 spans 已在工作树实现但尚未加载试用服务，不冒称已有最新全链路分解。

## 2. AOCI-CODE 能借鉴什么

阅读了官方 README 的工作方式、FRAS 与 RAG/CodeGraph 对比；上游 main 在本轮只读核对为 `7586820cc3bbb68e294c204ebeb978f9e70f748d`。没有运行其安装、init、scan、MCP 或索引生成指令，没有审计其全部实现，也没有取得该项目与我们任务等价的 3 秒 benchmark。

[固定上游 README](https://github.com/aoci-spec/aoci-code/blob/7586820cc3bbb68e294c204ebeb978f9e70f748d/README.md)将它定义为给编程 Agent 使用的持久代码认知索引：记录文件责任、关系、接口和约束，并随代码增量维护。其对象是代码和数据库结构；它不直接实现本项目的四源员工权限问答。

可借鉴的设计是把工作提前到后台：维护有来源的对象描述、实体/关系、适用范围和版本绑定，查询只取必要上下文。这里的借鉴是我们的设计推论，不能写成 AOCI 已验证企业 RAG。

企业资料不能直接效仿“整库 Whole-Index 送模型”。索引描述、关系、标题、摘要同样可能透露受限事实；必须分别绑定原始 resource/version/security scope，模型前当前鉴权。机器摘要不能当原始引文，跨源关系不能继承种子权限。AOCI 可辅助开发上下文，不能替代产品的运行时权限与审计。

## 3. 慢在哪里：已经有的真实证据

复算原归档 [performance-comparison.json](../../../evidence/runs/lock-contention-20261008/performance-comparison.json)。这些是当时固定候选的真实源 API＋真实模型 CLI 样本，不是本轮实时测量，也不是最新 source-review v2 的阶段统计。

| 历史问题 | 完整 query wall | 授权 wall | generation | review | 查询原生 HTTP 次数 |
|---|---:|---:|---:|---:|---:|
| slack_latest | 41.873s | 33.329s | 6.407s | 2.100s | 192 |
| product_scope | 51.226s | 37.107s | 9.879s | 4.191s | 208 |

四个授权阶段分别重复 48/52 个 HTTP 请求。192 次中：Slack 84、Drive 64、Confluence 36、Jira 8；208 次中 Jira 为24，其余相同。单个问题中 Drive 正文下载16次、metadata32次；Slack auth.test28次、channel info28次。所有阶段/endpoint详细统计在离线JSON。

原生 HTTP 累计工作秒为70.786/80.479，四源并行，**不能加到授权 wall 或总时间上**。Drive 累计工作33.289/37.046s，与授权 wall量级相同，是这两个样本的重要关键路径线索，不等于最新服务仍有同样占比。

早期53.209→40.116s是 native API＋fake model、单样本，不能作为当前真实模型时间。较新 source-review 原Q1 66.140s、Q2 40.371s、scope44.174s是各一次，不能当稳定率。Q1 low一次的6915 completion tokens中6785是reasoning，最终可见输出496字符；因此“只输出很短JSON”仍可能很慢。

## 4. 本轮无费用本地测量

运行 [analyze.py](analyze.py)，复用48对象作者合成世界及现有1000干扰对象构造；内存SQLite、fixture权限、FakeExtractiveModel。每题各5次，不是独立题或p95；无网络、钥匙串、真实账本或模型访问。完整结果及源码指纹在 [offline-analysis.json](offline-analysis.json)。

| 对象量；明确payment-service题 | 读取快照＋权限预过滤＋主题过滤＋BM25 中位 | 完整fixture/fake query 中位 | 后者最大 |
|---|---:|---:|---:|
| 48 | 0.424ms | 3.416ms | 4.361ms |
| 1048 | 23.083ms | 189.598ms | 198.858ms |

“完整fixture/fake query”包含本地关系扩展、假权限、假模型、审计和保存，不包含native网络/真实模型/浏览器。两组本地审计链valid，只是本地链，未独立签名。

注意这些世界与当前native资料不等价。宽泛mitigation题在两组均0证据，不能把它的快速空答算成功。1048组明确题1008对象有词匹配，最终18条证据，说明通用词会污染召回；本地速度不证明答案质量或完整关键证据召回。规模提升后关系扩展反复分词仍值得优化，但不是40秒的主要解释。

## 5. 各环节诊断和建议

| 环节 | 当前代码事实 | 建议；预期影响与限制 |
|---|---|---|
| 后台采集/新鲜度 | discovery在锁外原生读取、短临界区发布；bounded_queries已有四源就绪/时效检查 | 保留后台增量及删除先停用。后台准备结构块、词项、明确实体/链接和version快照；不要每问全库同步。这里已有优化，不重做worker |
| 解析/切块 | <=4000字符整篇；长文2400/400重叠、每资源最多3窗；Confluence保留表格列分隔 | 增加章节/段落/表格/消息结构切块候选，保留连续offset及父上下文；表头、范围、否定/撤回不能与事实分离。非连续片段用多个真实supports，不能拼成伪连续quote |
| 本地检索 | SQLite全量读取，binary-TF BM25、少量aliases、主题过滤、精确ID及有限关系扩展；无embedding/语义reranker | 第一轮离线预计算词项/结构，建版本绑定倒排或FTS候选，并比较相同业务oracle。匹配“mitigation→措施”等语义缺口后，再评估获批encoder的混合召回/RRF；不默认新收费/provider |
| 关联/上下文 | source_identifiers反复扫描；native资源links初始化为空，另按显式编号关联 | 缓存请求内词项/编号、后台发布可追溯关系；命名事件/时间/适用范围引导证据包，保留反证。每个目标独立鉴权；native正文链接解析仍有缺口，不称知识图谱已实现 |
| 身份/源读取 | 每资源read重复验证credential身份；权限检查同时读正文/版本；Slack动态reply还检查父root | 考察一次阶段内共享身份核验及同channel/root读取，但对象/消息/评论仍独立判断；不能把channel allow推成所有消息可读。actor/tenant/credential/phase绑定，未知终止；跨阶段禁止沿用allow。须先证明等价 |
| HTTP transport | JsonTransport使用urllib build_opener；本机Python3.14.7源码明确Connection: close | 优先候选：有界持久连接池，按来源/凭据边界隔离，保留TLS、禁止redirect、响应大小、超时、限流冷却和unknown；不自动重试模型POST。不减少检查即可实验，但实际收益尚未知 |
| 来源并发 | 已有最多四source lane，同一source内串行 | 先优化连接及请求依赖，再评估受控来源内并发/批量；429共用冷却，稳定audit顺序，线程只操作局部快照。平台quota决定上限，不设无界fanout |
| 模型衔接 | json_object＋严格parser；旧双调用保留；当前source-review在代码构造原文后只做一次review | 把可确定的事实/ID/引文构造交服务器；模型只做有界语义任务。进一步精简“证据＋claims/supports重复原文”的输入，按claim→evidence映射解引用。字段类型/唯一index/支持/coverage严格验证不变；新契约先离线验证，不拍脑袋json_schema |
| 业务覆盖 | 仅question_covered/filtered_complete布尔值可能误判 | 增加可审查的子问题→具体证据→状态/范围映射；无证据/歧义分开。模型自报coverage仍不可信，既有Q1/Q2/GA等独立事实oracle是发布判据。不硬编码C01或问题文本 |
| 模型性能 | 当前low单review可产生几千reasoning tokens；disabled曾误接受遗漏措施 | 先用更完整、结构化证据包降低推理负担，再受控比较同provider轻量模式。不能直接改none并称质量不降。若单调用本身持续>预算，就须更快模型/部署或明确3秒不可达，而非删校验 |
| 输出/恢复 | evidence_only明确非答案成功；UI等待、view/session迟到保护、History重新鉴权已实现 | 保留这些正确边界。完整已验证答案直接响应的路径不能被1.5s runtime轮询替代；流式未验证草稿不作为企业事实展示。前端显示时间也计入3秒 |
| 锁/审计/预算 | foreground查询持有共享锁；账本reserve/dispatch/settle，unknown保留；审计完整原文和最终答案 | 锁争用在旧优化后单请求较小，三并发仍须查。若缩锁改成版本快照/短提交，需重新验竞态与锁顺序；不以异步丢日志/取消已派发模型保留来加速 |

## 6. 安全检查能否减少

当前`Engine`执行before_model、model_dispatch、review_dispatch、before_dispatch；单review路径虽然无generation网络，前三阶段仍发生。它们存在减少重复工作的空间，但检查名称相邻不代表等价。现有契约测试证明：原文构造期间撤权/unknown/version/delete必须在review出口被阻断；模型返回后变更必须在最终交付被阻断。

设计候选：先完成本地选择、原文构造和完整模型payload，**在最后一个不可信数据出口前执行权威鉴权与版本核对**；一次review后在返回/保存前重新检查。关联展开如需权威检查，仍保留其种子边界；History/preview单独当前检查。此候选必须覆盖旧双调用路径，每次模型出口仍独立验证，不能因新单review修改旧生成/审查的安全。

本轮没有采纳或实现这个阶段合并。证明需包含actor/credential绑定、deny/unknown、内容/版本/删除、构造/序列化/ledger前变化、异常/预算、模型调用真实次数、模型前无秘密、审计与最终commit。授权不是跨平台原子事务，不宣称绝对实时；检查后的并发变更与原生API传播边界仍需明确。

正文缓存只存不可变版本，绝不缓存正向权限。某平台若能由当前delegated API确认员工访问和**完整可信revision/content绑定**，可用本地该版本正文；不能只凭modifiedTime或角色跳过读。Drive MD5/revision与metadata前后race保护、Slack消息编辑/删除、Jira受限comment、Confluence子页要逐源证明。缺证明的源保持完整read，不能为3秒放宽。

## 7. 3 秒目标怎样落地

采用受控正常网络/指定模型/固定代表题集上的**完整正确答案目标**。以下是设计预算，不是实测性能或承诺：

| 串行路径 | 预算 |
|---|---:|
| session、检索、证据构造、排队 | 0.15s |
| 并行原生权限/版本与模型出口核对 | 0.65s |
| 单次有界模型处理 | 1.40s |
| 最终原生复查 | 0.65s |
| 审计/保存、响应及页面渲染 | 0.15s |
| 总计 | 3.00s |

必须同时压低source请求和模型时间。即使把CPU检索变成0，历史两样本也只剩原生授权33/37秒及模型8.5/14秒；只优化切块无法达到3秒。只删除一轮约8秒权限检查同样不够。

连接复用、合并一次API响应中的版本和正文、阶段内去重、受控并发是减网络候选。例如Confluence官方[Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)支持body-format且响应有version，可探索单响应核验；但它不能自动证明旧metadata/body两步保护可删除，须比较真实字段、权限、竞态和oracle。

狭窄事实类任务可探索确定性原文证据答案；跨源解释类保留模型判断。两者必须有明确语义及完整覆盖，不能把复杂问题强制降为检索列表。在当前固定原题上不得以重新命名“答案”、提前展示未经审查草稿、快速空答、3秒timeout错误或热缓存单样本代替达标。

第三方API/模型超时或429时不能保证每次都成功≤3秒。目标验收需记录超时与失败率，并明确网络条件；如果关键路径实测仍超预算，就报告未达标并调整实现/模型，不能虚构保证。

## 8. 验收同时看速度、效果、稳定性

1. **完整时间**：前端submit→完整可用答案渲染；服务端admission/queue→audit/store完成并返回分别记录，cold/warm、后台轮询、1/3并发分列。首字/检索/HTTP200不是目标。
2. **正常代表题质量**：原Q1含实际批准操作且明确未知顺序；Q2同时含Done/In Progress/pilot而非GA；命名事件/歧义/反证/表格/旧新规则另按真值核对。正确且完整才算成功；evidence_only、误接受、review拒绝单列。
3. **稳定性分层**：transport/429、usage未知、length、空JSON、格式/index/quote、review支持、覆盖误判、源变化/unknown、UI恢复分别计数。不把安全阻断都叫parser bug，也不把可回答题被弃答算质量通过。
4. **安全**：模型各出口/返回/History/preview的撤权、版本、删除与unknown；同role不同权限、子资源/线程；模型输入/响应/普通UI无受限内容和元信息。映射原P/F/A/U及五场景S01–S05，不降低有效断言。
5. **复现**：同数据/问题/oracle、源码指纹、模型/prompt/config、后台/网络条件、全部失败及预算；样本少报告逐次和最大。后续样本量应在收费批准范围内一次冻结，不任意恢复旧42题循环，不以小样本宣称p95/SLA。

## 9. 推进顺序与具体下一项

| 顺序 / 任务 | 具体交付及停止条件 | 授权状态 |
|---|---|---|
| P0 DEV-PERF-REVIEW-03 | 当前报告、历史调用复算、CPU测量、三历史失败/成功原件hash、契约重放 | 本轮离线诊断已完成 |
| P1 DEV-PERF-TRANSPORT-04 | 本地opt-in有界连接池候选；loopback验证连接复用、no redirect/TLS边界、credential隔离、超时/429/断连、无模型重试；默认旧transport回退 | 可在现有本地可逆范围推进，无新安装费用；尚未实现 |
| P1 DEV-PERF-NATIVE-05 | 逐源列每API调用的身份/权限/内容/版本oracle；证明single response、phase内去重及有界并发；当前阶段先保留 | 本地mock可推进；native验证/实例更新需具体范围 |
| P2 DEV-PERF-CONTEXT-06 | 章节/表格/消息证据包、请求内词项复用；同48/1048世界关键事实与权限差异对比，不只测快 | 可做本地可逆实验；embedding/provider/新增依赖另核授权 |
| P2 DEV-PERF-CONTRACT-07 | 模型紧凑输入、需求覆盖映射/确定性边界，固定Q1/GA反例、旧双调用兼容 | 本地候选可推进；阶段合并须完整等价证明及ADR，未批准上线 |
| P3 DEV-PERF-LIVE-08 | 把最新私有spans加载明确自有实例，先少量固定题定向测量，再冻结候选做代表质量/并发验收 | 未执行。AUTH034为真人问答，不自动授权新付费测试；重启/自动调用需具体批准 |

具体下一项选**连接复用的本地候选**，理由是它不靠删除安全检查，可先证明网络行为等价和连接数下降，再决定是否做native A/B。无需先安装AOCI、向量库或新框架。若其本地验证失败，保留原transport；若实际收益不足，接着审查API读路径，不重复同类付费prompt试验。

需要团队后续集中决定的仅两组：自有试用实例加载计时＋固定少量native/live调用与累计成本边界；如果当前provider单调用无法满足预算，是否允许更快模型/本地encoder的具体数据出口、依赖与费用。已有开发授权不因这些未定项而失效。

## 10. 本轮实际执行

```sh
python3 docs/reviews/2026-10-13-query-optimization/analyze.py --output docs/reviews/2026-10-13-query-optimization/offline-analysis.json
python3 -m unittest discover -s tests -p test_source_review_dispatch_contract.py -v
```

分析脚本完成20次fixture/fake查询（两种规模、两题各5次），另20次本地快照/过滤/BM25计时，两个本地审计链valid。三历史反例9原件SHA256均吻合。既有契约专项5项0.039s通过：构造期4类变化阻断、模型后4类变化阻断并保留usage、历史v1拒绝/v2误接受/low单次成功保留。没有改业务runtime，未重复全502回归或旧收费题集。

检查实际本机Python3.14.7的`urllib.request.AbstractHTTPHandler.do_open`，包含`headers["Connection"] = "close"`及关闭socket路径；与[Python官方文档](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen)一致。这证明当前实现缺连接复用，不证明具体握手耗时或新transport收益。

DeepSeek官方[JSON Output](https://api-docs.deepseek.com/guides/json_mode/)说明json_object/JSON示例和max_tokens，并注明可能空内容；因此合法JSON不等于业务schema或语义正确。官方[Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)只核对能力，未在本轮改变配置或运行模型。

新增方案均标候选；原3秒目标、全部失败、unknown预算、G1/G2及私密工具证明边界保持。没有来源写入、服务重启、安装、推送、合并、发布或提交。
