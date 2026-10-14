# AUTH036 查询优化 Goal 执行记录

Latest local candidate: [ADR096 request isolation](REQUEST_ISOLATION.md). HTTP integration verified locally; full-context budget reservations currently prevent simultaneous AUTH036 model calls. Live v2 unchanged; no speed claim.

新增本地并发预算门控：原子预留、在途/unknown与真实进程退出恢复验证通过，618完整本地；未接运行实例，无新调用/费用。[实现边界与接续](CONCURRENT_ADMISSION.md)。

后续本地增量：迟到原生响应的发布竞态保护已实现，611项本地通过；尚未加载，不改下方冻结v2的实测结论。[并发安全前置与准确接续](CONCURRENCY_SAFETY.md)。无新增模型调用/费用。

## 当前候选 structured-v2（3秒未达）

结构切块已消除已见business_16的长归档混入和断词，旧引用/History兼容。607完整本地、运行器更新后4专项、6前端DOM及fixture HTTP生命周期通过；这些不替代浏览器。固定12开发案例使用10次live model，均保留预期事实；前提纠正的表达仍有限。

| HTTP完整答案 | Q1 | Q2 | SCOPE |
|---|---:|---:|---:|
| 每题新进程首次查询 | 9.900s | 8.094s | 6.477s |
| 同进程热组 | 8.499s | 6.841s | 8.873s |
| 三并发第1组 | 18.025s | 26.922s | 8.353s |
| 三并发第2组 | 15.021s | 24.905s | 6.938s |

12/12固定关键事实通过、每题一次模型及一次usage receipt、无新增unknown；**0/12在3秒内**。模型0.535–1.015s，原生授权wall 5.820–8.911s；并发锁等待最高18.024s。检索与link_seed授权嵌套，不能把分类时长直接相加。冷组仍有正常后台同步，平台/模型缓存未控制，不能声称所有HTTP连接冷。小样本不报告可靠p95/SLA。

History1.863s与C01preview0.839s通过当前鉴权、正文相同，0模型/费用。完整本地审计链27823事件有效，无独立签名证明。浏览器工具ERR_BLOCKED_BY_CLIENT未绕过，因此提交到渲染时间及真人G1/G2仍未验收。

Goal累计43实际模型、新增结算USD0.056704，旧2unknown保留；最终fixture原配额余4、native12已用完。不追加相同候选的付费重复。下一步先在本地审查全局锁、请求状态隔离及授权阶段等价性；不删除安全检查或跨阶段缓存allow。代码和原始证据未推送/合并。

[结构契约及回退](STRUCTURED_WINDOWS_CONTRACT.md) · [冻结清单](CANDIDATE_STRUCTURED_V2.json) · [逐次机器结果及边界](VALIDATION_STRUCTURED_V2.json)

2026-10-13（Asia/Singapore）。基准 `1649e301959b7eea7303fdda9ba0ee58a578d19e`，独立分支 `perf/query-goal-20261013`。保留接管时全部 dirty 工作、历史失败、原账本和队友资料。目标仍为提交到完整正确答案渲染 ≤3 秒，当前未达到、未验证。

## 当前冻结候选 whole-v1

原生三道题在同一候选下完成并通过固定事实核对：**Q1 8.84秒、Q2 7.55秒、范围题6.39秒**。模型耗时分别1.08 / 0.96 / 0.72秒；当前主要剩余延迟是原生授权阶段。完整3秒仍未达，以上为HTTP、非浏览器，也不是稳定p95。原Q1六段正文与此前54.73秒的low候选完全一致；Q2保留Done/In Progress/pilot-GA且少一段冗余背景。

whole契约仅让模型选择完整段落别名，并判断selection_safe/question_covered；原文、精确引文、证据映射与必要措施由程序校验，模型不能写事实或URL。旧解析器和单审查前后权限检查保留。详见[契约与结果](WHOLE_SOURCE_CONTRACT.md)。

[冻结候选清单](CANDIDATE_WHOLE_V1.json)确定配置pooled/4/whole/none8192/single/history batch与代码/题目hash；当前自有49161 runtime9d26fabd2fa7，备份后加载，正常后台保留。12个已知作者开发案例机械事实探针全部通过，10次live model、两次无证据/受限0模型；主Agent逐条语义复核发现**business_16冗长无关archive及断句窗口**，另business_03没有自然语言纠正rejected前提。因此整体质量验收仍未完成，不能称12/12全面合格。冻结v1原件保留，下一步结构切块改进必须作为新候选。

583完整本地通过（25.842s）；冻结运行器另经13相关测试（0.191s），覆盖真实GoalLedger类集成及unknown停止。Goal累计 **21次模型 / USD0.046237新增账本结算 / 新unknown0**；旧2unknown不变。最终fixture已用10实际调用、该子额度余14；最终native12仍未用。详情[机器结果](VALIDATION_WHOLE_V1.json)，私有原始答案/审计/逐条复核在`.runtime/query-goal-20261013/final-fixture-whole-v1`。

浏览器工具本轮访问本地服务返回`net::ERR_BLOCKED_BY_CLIENT`，未绕过；真实前端渲染验收blocked。native最终冷/热/三并发及G1/G2仍未完成。下一步由当前反例改进章节/行/表格窗口，不再同样提示词反复收费；保持固定事实要求，不把质量或3秒目标改窄。

## 前一阶段 · 原生并发与 History

**完整新答案3秒仍未达成；本轮没有模型调用。** 自有49161当前运行 `4b63a5a7f7c5`（pooled / 每源最多4个完整读取 / covered / low8192 / single / History batch）。运行前已检查归属和空闲、备份原持久状态；正常后台同步保留。Goal累计仍为9提交、8模型、USD0.040951、新unknown0，原2unknown和最终36调用额度保留。

| 真实只读比较 | 原实现 | 新候选 | 保持的检查 |
|---|---:|---:|---|
| Drive三个文件、热连接、一次完整读取组 | 并发2：3.643545s | 并发4：1.994013s | 两者均12次HTTP，身份/元数据/正文/读后版本完整，全部内容一致 |
| 重新打开同一Q2历史答案 | serial：9.392120s | batch：1.968095s | 两者均25次HTTP，全部证据本次鉴权，完整record逐字一致 |

并发4在这组Drive数据中实际最多同时3个完整read；冷连接样本5.788908/1.969055秒，顺序/网络影响不能排除。每批join后才进入下一批，unknown不接纳新批，连接池最多4，来源cooldown/no retry不变；无身份/ACL/正文缓存。History只在本次访问内将同一资源同一版本的窗口合并读取；权限、版本、删除、窗口或引文不符合仍整条不可用，每次打开都重新鉴权。没有把History的1.97秒当成新问题完整答案达标。

578项完整本地25.844s通过，53项相关1.107s通过；不是合计631项。包含四路在途上限、第五个不提前接纳、unknown停止、ContextVar/有序审计、TLS连接第五个超时不发出、review/final晚撤权、History重复访问与错误引文/版本等。详情及回退见 [FOUR_READS_HISTORY.md](FOUR_READS_HISTORY.md)，机器结果 [VALIDATION_FOUR_HISTORY.json](VALIDATION_FOUR_HISTORY.json)。本轮未新增provider/依赖/scope/源码推送或业务写入。

接续：当前单轮完整证据授权约1.96秒，但新问题仍需多阶段检查，模型低推理仍曾耗时27–41秒。下一项处理模型的职责和覆盖契约，避免仅重复布尔审查提示词；保留原事实oracle和安全要求。完整query冷/热/三并发、浏览器提交到完整显示、最终质量矩阵及G1/G2仍未验收。

## 前一阶段 · compact / covered / single-dispatch

**完整 3 秒仍未达到。** 当前自有 49161 加载 `307a19fe91e4`：pooled / 每源并发 2 / covered 原文审查 / low8192 / single 派发；它是诊断候选，不能称为更快的稳定版本。9 次提交、8 次实际模型调用，Goal 新增账本结算 **USD0.040951**，新 unknown 0、旧 2 保留。最终 36 次验收额度未使用；本阶段不再对同候选重复范围题或调提示词收费测试。

| 候选 / Q1或Q2 | HTTP 完整返回 | 模型 transport | 原生请求 | 独立业务核对 |
|---|---:|---:|---:|---|
| compact / none / 旧四轮，Q1 | 20.054s | 见机器记录 | 116 | **失败**：review accepted 但再次漏 C-01 的实际措施 |
| covered / none / 旧四轮，Q1 | 17.626s | 1.180s | 116 | **失败**：保留 C-01，但模型声明覆盖不完整；evidence_only 不算答案 |
| covered / low / 单审查出口，Q1 | 54.732s | 41.133s | 88 | 本次通过：timeout budget inspection、approved failover procedure 和未知最新顺序保留；仍有多余背景 |
| 同一候选，Q2 | 40.595s | 27.830s | 77 | 本次通过：五段 claim 文本与 paired-v1 Q2 完全一致，Done / In Progress / pilot-GA 正确 |

Q1 单出口三轮授权 wall 为3.639 / 3.684 / 4.324s（约11.648s），另关联种子1.871s；Q2为3.855 / 4.424 / 3.970s（约12.249s），另关联种子0.446s。均非嵌套 HTTP 耗时相加。Q2 从上一阶段26.025s变40.595s，虽原生请求102→77，模型却10.666→27.830s；不能用减少授权调用数宣称整体加速。把本次模型耗时扣掉，当前其余关键路径仍约13.60 / 12.76s；这只描述当前实现的实测，不是所有架构都无法达标的证明。

### 本轮代码与边界

- `compact` 将每份原文仅发送一次，按 evidence ID 分组，逐字校验所有分段重构完整原文；保留标题、定位、表格、限定和反证。模型输出结构保持原版。Q1输入3986→2417 tokens（不同配置输入），但关闭推理的质量失败仍在。
- `covered` 增加狭窄的服务端措施遗漏检查：操作类问题、同主题原文中的 runbook/procedure 等结构与实际动作共同命中才要求保留全文。没有题目、C-01 或答案硬编码；不声称通用语义完整性检测，不代替业务 oracle。拒绝模型自报支持/覆盖失败；强制 `filtered_answer_complete=true`，不能因保留所有段落就忽略 false；全文末尾限定不能仅凭相同证据 ID 被省略。
- `single` 仅接受服务端列出的三个源审查类：本地原文构造不外发，保留其后的完整 selected `review_dispatch`，省去该单调用路径在构造前的额外 `model_dispatch`。before_model、最终交付、History/preview 仍重新检查；没有跨阶段 allow 缓存。旧双调用路径不得启用此开关，默认 legacy。契约及证明见 [SINGLE_REVIEW_CONTRACT.md](SINGLE_REVIEW_CONTRACT.md)。

最终完整本地 **564 tests / 26.021s / OK**，其后加强审计链 valid 字段断言，22 项专项0.235s通过；不是合计586项。相关50项验证包含原双调用、安全、账本及计时；构造期与模型返回后的撤权/unknown/版本/删除均保留拒绝语义。首轮覆盖契约测试暴露旧 parser 对全部保留时 false-completeness 的忽略，已只在新候选修正；首次失败日志原样保留。单派发首轮测试设置错误及修正解释另见契约文件。

私有启动前备份 `pre-compact-backup`、`pre-covered-backup`、`pre-single-backup` 保留原账本/答案库/接纳/入口。重启均核实本人49161归属、无已建立连接和接纳锁空闲；没有操作8094/8100。四源每次complete/current后才提交。原始 response/audit/timing 在忽略的 `.runtime/query-goal-20261013`，本轮机器记录见 [VALIDATION_COMPACT_SINGLE.json](VALIDATION_COMPACT_SINGLE.json)。未运行浏览器提交到渲染、最终质量矩阵或三并发；真人G1/G2仍open。

下一项：逐源原生读取协议优化和结构化问题/证据覆盖。不能把“缓存正文后只看文件可读”当作当前版本和正文下载权限等价，也不能取消最终检查。低推理当前Q1消耗6631推理tokens，Q2总输出4702 tokens，关闭推理的Q1又会误判或拒绝；在另有证据支持的设计变更前不重复同类付费调参。

回退本轮模型/检查候选：`--source-review-input legacy --source-review-dispatch legacy --reasoning-effort low`；网络层另可回退 `--source-transport legacy --source-concurrency 1`。账本/历史/unknown不回退或重置。

## 前一阶段真实结果（历史快照）

Drive 原账号已由本人完成 Google 重新授权，原生身份验证后同一 Keychain 项已更新；无新 scope。原配置基线及网络候选均等待四源 complete/current 后才提交。当前 5 次提交、4 次实际模型调用，Goal 新增账本结算 23,922 microUSD（USD0.023922），新 unknown 为零；原 2 个 unknown 保持。原账本 settled 1,273,996 microUSD，未重置。

| 配置 / 问题 | HTTP 完整返回 | 结果 / 核对 |
|---|---:|---|
| legacy/1/low8192，Q1 | 76.186s | **失败**：length、completion/reasoning均8192、可见输出0；返回evidence_only，不算答案 |
| legacy/1/low8192，Q2 | 42.049s | 审查通过，Agent核对含PAY-102 Done、PAY-103 In Progress、pilot而非GA |
| legacy/1/low8192，SCOPE | 43.773s | 审查通过，Agent核对含controlled pilot、GA不批准、发布日期未知；仍有额外状态背景 |
| pooled/2/low8192，Q2 | 26.025s | 审查通过，五段claim文本与当前基线**完全相同** |

Q2 网络候选四轮原生鉴权 wall 分别3.687/3.612/3.624/3.694s，共约14.617s；基线5.882/5.868/5.820/5.790s，共约23.360s。模型transport同时从17.860s变为10.666s，配置相同但存在模型/网络波动；因此不能将42→26秒全部归因于连接池和并发。这是一组HTTP实测，不是浏览器渲染、稳定率或p95，未用剩余基线额度重复同配置收费测试。

Q1 当前瓶颈有直接证据：模型transport50.105s且完全没有可见答案；四轮鉴权仍约23.040s，另link_seed2.968s。继续提高输出cap会增加成本/等待，不能解决完整3秒要求。下一项为逐源等价读取及精简源审查输入/覆盖契约；保留当前实测失败。

**本轮新增集成缺陷已修复**：初次Q1在20.444s、四源检查全部通过后，被GoalLedger代理的类型不兼容阻断，0模型；旧HTTP分类把内部ValueError显示为source_unconfirmed。已用真实SourcePassageReview构造路径离线复现（goal-model-integration-first.log），改为承接原BudgetLedger的持久代理、所有非reserve绑定方法仍委托同一对象及计时包装，没有重开DB或放宽类型检查；34项相关通过。另增加internal_service_unavailable固定错误码，未知内部异常不再冒称源鉴权故障，31项HTTP/UX通过，无异常文本外泄。原失败原件与费用不改。

最后整合 **528 tests / 25.845s / OK**（integrated-final-local.log），包含两路源检查、额度模型集成、恢复入口、错误分类。日志末尾旧测试输出的`status: failed`是既有mock测试stdout；unittest最终exit0/OK。当前自有49161加载runtime39f7240a7cfd、pooled/2/low8192，原生Q2已验；原Q1/范围在此配置未测，浏览器、并发三问、最终质量矩阵、G1/G2均未完成。

## 初始额度与基线准备记录（历史快照）

[PLAN.json](PLAN.json) 冻结题目、配置、质量 oracle 与 60 次实际模型调用分配：基线 6、诊断 12、最终候选 36、预留 6。新增结算上限 USD0.50，沿用原共享 USD20 账本；每次 reserve 前再校验调用数、费用、保守 reservation 余量及新 unknown。双调用按两次计，未知费用不释放。`performance_allowance.py` 的 5 项专项及 40 项相关测试通过；旧三份 admission 和 entry 文件与启动前备份逐字节相同。

初始原账本 1,037 settled、2 dispatched；原未知预留 648,808 microUSD 保留。当前这一步未调用模型。真实数据库、凭据、时序及细节留在忽略目录 `.runtime/query-goal-20261013/`，不加入 Git/公开包。

首次完整服务启动在 Drive refresh HTTP400 停止，未加载模型。仅确认保存的 refresh token 和客户端映射存在；原 JsonTransport 不读取 HTTP 错误正文，不能据此断言具体拒绝原因。失败及 0 调用记录保留。用户随后同意立即打开原账号、原只读范围的 Google 登录入口；恢复脚本等待本人登录，并在原生身份验证通过后才替换原 Keychain 项，无新 scope、模型或业务源写入。

## 已实现的网络候选

`brain/http_pool.py` 是 opt-in、有界、无依赖的 HTTPS 连接复用：每源至多 2 条连接，15 秒空闲失效；按配置 origin 和凭据摘要隔离。只支持原 GET 及 Slack 只读 auth.test POST；TLS 验证不可关闭；不跟随重定向、不读资源错误正文、不自动重试。正文完整消费且业务解析成功才复用，截断/超限/解析失败/断连丢弃连接。现有 cooldown、身份、ACL、正文、版本检查及模型 transport 不变。存在 HTTPS 代理时沿用原 urllib 路由，不绕过代理；因此代理路径暂不享有连接复用收益。

`--source-transport pooled` 启用；默认 `legacy` 回退。启动器在身份验证后、后台和查询启动前安装，并在退出时关闭池。`--source-concurrency 2` 是另一个独立 opt-in：每源同时至多两个完整 read，整对 join 后才接纳下一对；出现 unknown，已在途同伴可结束，剩余对象记录 unknown、不再读取。每阶段重新检查，全部工作 join 后按输入顺序更新 authority/审计。最多四个来源，不改变查询全局锁。试用入口要求并发 2 同时启用有界连接池，默认仍为 1。

上述并发只完成本地验收，未在真实四源问答启用，也未证明收益。没有合并鉴权阶段或缓存 allow。

## 实际验证与失败

- 初始 507 项完整本地测试通过（24.385 秒）。连接池后 105 项相关测试通过（1.556 秒）、521 项完整测试通过（24.811 秒）。这是 fixture/mock/loopback TLS，不是 live model 或前端验收。
- TLS 本地测试观察到连续 3 次 GET 共 1 条连接，覆盖凭据切换、连接上限/等待超时、部分读取、截断、403/302/429、cooldown、断连/旧连接无重试、证书拒绝、代理回退和关闭恢复。第一轮 10 项中截断测试失败；修复短读检测后通过，`pool-local-first.log` 保留原失败。
- 并发候选 23 项相关测试通过（0.734 秒），含请求 ContextVar 传播、两路在途上限、join 前不更新、unknown 停止下一对、review/交付前撤权/unknown/版本/删除阻断。并发修改后的完整整合结果另记日志，不继承 521 项为最终版本。
- Drive 恢复入口与既有 OAuth 共 15 项本地测试通过（0.048 秒），证明缺旧凭据不发起新授权、身份验证失败不替换凭据、成功后只写原项；未代替真实 Google 登录。

Confluence 原批准资料单源只读顺序比较（同一正文，正常网络，无模型、无前端）：

| 配置 | 耗时 | 原生 HTTP 请求 | 新 HTTPSConnection 对象 |
|---|---:|---:|---:|
| legacy first | 1.455949s | 3 | 3 |
| pooled cold | 1.014981s | 3 | 1 |
| pooled warm | 0.988990s | 3 | 0 |
| legacy last | 1.058669s | 3 | 3 |

四次都 allow 且返回内容完全相同。小样本及网络顺序效应明显，不推断稳定提速比例、p95 或完整答案时间。连接复用不能单独解释或消除几十秒差距。私有原件 `confluence-transport-probe-v2.json`。

单源探针首版用 Mock 替换 HTTPSConnection 类，破坏标准库显式 super，首次读取在构造连接时本地失败，未发出实际源请求；原 `confluence-transport-probe.json` 保留，不能当源故障。v2 改为只计数原构造函数，保留类对象后才执行以上四次真实读取。

## 接续与回退

1. 完成原 Drive 登录后，仅启动 legacy/单并发基线，等待四源 complete/current。不得将启动 HTTP200 当来源已就绪。
2. 按冻结题集先取 Q1/Q2/SCOPE 的真实阶段时间和完整质量，消耗 Goal 专用额度；新的 unknown 即停，原 unknown 不重置。
3. 再按实测比较 pooled、并发 2，并继续逐源等价读取、结构证据及模型覆盖契约。仅保留有实际收益且通过安全回归的组合。
4. 最终候选固定后才运行预留验收；前端完整显示、History/引用、三并发、真实模型和真人 G1/G2 分列。

回退启动配置为 `--source-transport legacy --source-concurrency 1`；不会退账、重置历史答案或 admission。未操作 8094/8100，未安装依赖、写业务来源、推送、合并、发布或提交。

标准库实现依据：[Python 3.14 http.client](https://docs.python.org/3.14/library/http.client.html)。原 Google 授权机制依据：[Google installed-app OAuth](https://developers.google.com/identity/protocols/oauth2/native-app)。
