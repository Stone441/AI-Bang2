# Acceptance coverage · local candidate

2026-10-08 AUTH030补验完成：总额度42→48已消费，仅补原known12的07–12六题，未重复前30题。07/09/11合理空答澄清；08有引用限定资料不足；10未编造retry但Atlas账户行不充分回答最小integration tier，记partial；12注入Drive unknown按预期模型前SourceUnavailable，非业务答案成功。原24＋known12完整36现已执行，known12为3完整/范围答案＋7安全不足/澄清＋1partial＋1预期来源故障，不称质量全通过。六题结算21044microUSD；本Goal累计165795microUSD，账本settled937708/available18737888，旧unknown324404保留、无新unknown，额度48/48。原quality36的not_run历史不改，补件quality-remaining6及quality-combined-review.json另存。第一题/known10质量及真人UX仍open；此次没有产品代码或模型配置变化，无需重复已通过436/三Node。

2026-10-08 DEV-PAGE-UX-01 当前增量（覆盖下方仅记录/不修改的旧快照）：基准main23ae62b，独立fix/page-failure-ux-20261008；本Goal授权本地修复，AUTH029单独授权49161/native/live复验。已实现安全输出诊断、模型调用前最多一次版本恢复、通用主题检索过滤/已授权关系扩展、会话独立进度与模式/四源状态、真实已用时间/防重复提交/分类错误/退出迟到响应保护及引用信息层级。原模型low8192、provider、权限/review/审计边界不变。436完整本地回归、三Node与五fixture通过；最后锁顺序测试改用History，因为health现在独立于查询锁，首轮失败原件保留。

实际产品HTTP固定三次/题：明确payment-service题3/3有依据答案（PAY102 Done、PAY103 In Progress、pilot与GA区别）；宽泛latest-approved-mitigation题为quote失败、review失败、一次范围受限但遗漏runbook的答案，不能称任务完成。原55.47秒请求finish_reason不可恢复，新拒绝均stop，不能据8192判定截断或擅自增加cap。新鲜度probe弱主题命中经通用相关性过滤解决；版本恢复/撤权/持续变化/模型后变化由mock验证，无源写入，未称native变更全矩阵通过。607次HTTP进度采样，最长0.00524秒；三当前native引用preview与History200，非浏览器/真人观察。原24题22事实+2合理空答；known12仅前6已跑（3完整/范围答案、3安全不足或澄清），后6未跑。全部失败及429记录保留，累计42次问题额度已耗尽，已申请48次总额度但尚未批准。

新增结算144751microUSD（USD0.144751）；账本settled916664/available18758932，原unknown1/324404保持，无新unknown。49161已重启加载最终工程guard，health/静态资源200；native六题是在此前加载版本执行，后续保守guard及UX改动由本地验证，不冒称最终全部native重测。新问答已暂停；8094/8100、AUTH019延期、旧证据、G1/G2、browser saved denial不变。无推送/合并/部署。证据：evidence/runs/page-failure-ux-20261008/README.md。Goal未完整完成：第一题质量与剩余6题、人类页面观察仍open。

2026-10-08 Git交付补充：AUTH028已批准本轮定向收尾及真实试用失败/UX问题记录推送并经PR合并main；下方“未push/merge”为证据冻结快照，实际以本次PR状态和main commit为准。应用仍cdbd62b，49161已停止，不部署、不新增费用或UX改动，失败与G1/G2状态不因合并升级。

2026-10-08 本轮定向收尾及真实试用/反馈已记录：用户确认两题全部失败后停止使用，引用/History后续未做；首题输出拒绝、第二题Drive版本变化停答原件保留，实际试用failed。UX观察为等待计时/可感知工作状态缺失造成焦虑、模型和四平台连接信息不显性、页面简陋。用户明确当前只记录、等ChatGPT Chat后续指导，不改代码/界面/配置。49161自建实例已正常结束(exit0/无监听)，8094/8100未动；2次尝试/1次模型调用/11028microUSD，最终账本settled771913/available18903683，原pending1/324404保留。本轮信息收集完成不等于失败修复或验收通过；UX、原质量失败、重复自动测量/p95/完整native矩阵及G1/G2仍open。证据targeted-closeout-20261008/page-trial-final.json。下方等待反馈/运行中为旧快照。

2026-10-08 AUTH027第二题实际HTTP停答：明确payment-service在18.411秒的model_dispatch发现Drive新探针version6不一致，未调用模型；后台随后发布version7，正文hash/modifiedTime相同，确切版本变化原因未知，不绕过gate。首两题均未完成任务，原失败保持；新增模型结算合计11028microUSD，原unknown324404保留。无自动重试/配置实验/应用变更，实际页面反馈及引用/History待核。详见targeted-closeout-20261008/page-trial-request2-failure.json。

2026-10-08 AUTH027首题实际HTTP试用失败：eng_b/latest approved mitigation，55.468秒服务端request，generation usage8192 completion/11028microUSD已结算，随后model_output_rejected、无支持答案、未到review。原始响应/finish_reason未存，不能确定截断或其他拒绝；不自动重试、不改cdbd62b。原pending1/324404保留；等待第二题和真人页面反馈，第一题引用任务未完成。原件page-trial-request1-failure.json及审计prefix；不是质量或人验通过。

2026-10-08 AUTH027实际试用实例已启动：http://127.0.0.1:49161，cdbd62b应用/eng_b/native四源只读＋DeepSeek v10 low8192，独立索引、原USD20账本，6次尝试及结算/新unknown停止限制。四源首轮complete，startup hash dc2903d72e3fec6c30156b84d351cee23d1d9be8bebfd5d756e1f5f2afe7ceb4；启动快照page-trial-startup.json，无ticket。实际入口已直接交给团队，首组两题/引用/History操作及反馈待做；启动与模型构造不等于真人或live问答通过。8094/8100/browser拒绝/G1/G2不变。下方“实例许可pending/未启动”为旧准备快照。

2026-10-08 定向收尾：main已合并为 **2eabeb8**（PR8），应用仍 **cdbd62b**；当前独立fix/targeted-closeout-20261008无runtime修改。known05明确payment-service对照实际输入J03并正确回答Done/In Progress/no GA，15.026秒、5179microUSD；旧题/oracle/partial保留，不能推断仅歧义所致。统计细化core24=21直接事实＋1前提纠正事实＋2纯空；known12=3完整＋1部分＋1前提纠正事实＋6纯空＋1预期unknown。AUTH026仅3创建＋4更新已消费，7项均新值native发现/fake证据使用；三创建及Drive更新为持续自动，CF在原后台发布但fake恢复后成功，Jira/Slack更新为重启恢复，非全7持续时延通过。并发源版本变化停答原件保留，两审计链341/795有效仅本地；原生更新时间到发布不能称精确commit或SLA，多次自动样本/p95及完整native撤权删除仍未验。账本settled760885/available18914711、原pending1/324404保留；AUTH019不变。具体页面实例许可仍待回复，未启动49161、不动8094/8100；browser/G1/G2不变，新分支未push/merge。证据evidence/runs/targeted-closeout-20261008。


2026-10-08 Git交付补充：AUTH-025已批准本轮推送并通过PR合并main；下方未push/merge为性能证据冻结时快照，实际交付以PR状态和main commit为准。应用验证基准仍cdbd62b；文档/Git操作不重启或升级运行实例。

2026-10-08 DEV-PERF-01本地交付完成，应用 **cdbd62b**（main仍a3a0060，分支fix/lock-contention-20261008）：后台发现锁外native读取/短临界区发布、四source有界阶段并发及共享Retry-After冷却已验证，原身份/正文/父线程/版本和四阶段当前权限检查保留。421 clean archive回归、两Node/五fixture/真实本地mock HTTP争用通过。相同native两题原13/15窗口字节一致：query40.083/49.034秒（旧78.287/97.225）、授权wall34.363/35.017秒（旧69.052/75.009）、同对象同版本单引用1.656/1.052秒（旧27.166/25.540）、锁等待0.000057/0.001621秒；后台正常运行，非浏览器性能/SLA，query团队30–40秒目标未全部达到。固定v10显式low8192原24题：21正确事实范围＋3合理澄清/无证据；已知12：3完整正确＋1部分覆盖（05未涵盖PAY103）＋7合理澄清/无证据＋1预期Drive unknown故障停答，零错误弃答/错误结论/非预期运行失败；不称盲测或质量全通过。AUTH024仅一次Confluence copper页1572865已创建，native自动60秒周期观测确认→发布35.60秒→首fake回答57.12秒；单源创建子集，非live model/SLA。原账本settled755706、available18919890microUSD，unknown pending1/324404保留；本轮结算202522microUSD，最终三流105121。原失败/AUTH019/四源十二行历史保留。未push/merge、未重启/部署8094/8100；产品browser saved denial、G1/G2/真人/提交不变。详见evidence/runs/lock-contention-20261008/README.md。

2026-10-07统一业务增强候选固定为 **0bc90ae**：synthesis-v8，可信显式low/4096；默认none/1024保持，当前8094/8100未重启。398干净归档回归、同48世界五fixture、JS语法及两Node通过；完整24作者开发题真实模型为22正确事实回答＋2正确空答，零异常，经只读Agent逐题核原问题/quotes/relevance，非稳定率或盲测。eng_b当前原生＋真实模型两题均正确，Slack最终amber替代green、产品pilot/GA/date/Done边界齐全；耗时含preview133.132/146.085秒，非SLA。本流费用上界core46985/native12302microUSD；原账本settled390875/pending0，不从共享差额归费用。当前core完整签名、native分页/七签名边界及fixture四结果审计已配对，非独立custody或人阅读证明。四源AUTH021创建/修正原native/fake证据按原版本保留。

剩余分列：原保留集f8ecbed失败未重跑、未改写为修复；AUTH019仅原长文Orion与自然题冗余两项延期，不扩大。native正文一跳解析、Google Docs/OCR/全附件/DM及生产SSO/KMS/WORM未实现或不支持；embedding方案C无已批准provider/依赖，blocked。完整native生命周期/故障/身份矩阵、新鲜度SLA及质量稳定性仍未验；性能仍有缺口。产品browser为工具saved site denial blocked（49161停止），不是产品失败；真人业务/ROI/G1/G2、录屏、外部开放、推送合并/发布/比赛提交not_run。本轮完成以EXECUTION_BRIEF5.3的业务增强与有模式边界的统一候选为范围，不宣称全部开发或技术验收完成。

下方较早阶段记录保留为历史，本段为当前状态。

2026-10-07当前应用3ceb625（synthesis-v6，温度0）；2a039aa仅新增context篡改负测试，brain字节相同。两阶段现传原资源title/locator与text分开，不能充当quote/权限；标题/定位篡改在reserve前拒绝。3ceb clean archive388/同48世界五fixture/语法及两Node通过；2a039aa clean archive389回归通过。完整24开发题只读逐项核为22核心事实正确返回＋2正确空答，零运行异常；business12独立quote失败与business16跨事件误归本轮未重现，单次成功非稳定修复。business03未明确说明rejection无证据、business32两条无关背景仍open，整体完整性/相关性未通过，非AUTH019延期。eng_b两道本版本native＋真实模型正确，28窗口出现次数/四阶段allow/6claims/4usage；耗时含preview121.928/130.040秒，非SLA。开发诊断4题/core24/native2费用上界4137/22146/5100microUSD，原账本settled226368/pending0；共享起点含并发reservation不得用accounted差归成本。当前core全签名/native七边界与分页本地核验，非独立custody或人阅读。证据见source-context-v6-full-readonly-review、source-context-v6-native-readonly-review及candidate-source-context-v6-fingerprint。旧失败/保留题不改或重跑；Goal active。browser saved site denial blocked，49161停止，8094/8100未动，human/ROI/G1/G2/推送发布not_run。

2026-10-07最新局部结果：固定代码2a73bd0，380 clean archive/同48世界五fixture/两Node通过；当前eng_b两题native＋真实模型经只读复核5claims/28windows/四阶段当前allow/四usage与账本3207microUSD增量一致。配对272事件签名副本及混合208事件oracle另列local。全persona、故障live、四源native删除/新鲜度SLA、native正文关联、Docs支持未完成；browser saved site denial blocked，human业务判断/ROI/G1/G2 not_run。旧f8ecbed保留题失败及AUTH019延期保留，不从四开发题改称通过。完整证据见business-validation-20261007，旧版本表保持历史。

2026-10-07业务增强候选实现f8ecbed：373 clean archive/五fixture/2Node/HTTP通过；binary-TF BM25、表格cell关系、资源方向审计、有界后台查询及版本反证停答已实现。四源AUTH-021新probe和两次修正native API/fake当前16断言通过，加载hash匹配候选；query约43–58秒，非SLA。12保留题冻结后一次live评测及只读语义审查已完成，具体见business-validation-20261007/heldout-review.json：有明确正确答案和safe unsupported，也有歧义/状态误答、部分答案和来源故障告知不足，不能称质量全通过；两项AUTH-019原延期不覆盖这些新失败。当前native/模型签名副本分别核验，同机测试key非独立custody；产品browser仍saved site denial blocked，49161停止、8094/8100不动；G1/G2、人类任务/ROI及发布提交not_run。Goal active，新增工程缺口仍由Codex继续负责。最新本地候选c825143非后台unknown通用修复有17定向、377 clean archive/五fixture/2Node/HTTP及只读复审通过；它尚未形成新native/live/browser结果，不能继承f8ecbed两题实际运行。

## 当前统一候选 · 2026-10-06（覆盖下方历史描述）

固定应用/测试331bd28，分支fix/review-integrated-candidate；最新clean archive **357项17.406s**、五fixture场景、2Node及本地HTTP全部通过，证据review-integrated-20261006/rebuild-scope-current。旧34281ad/352和323cb93/356原记录保留，不冒作最新源码通过。

| 对应验收 / 审查 | fixture/mock | native API | live model | browser / human / 缺口 |
|---|---|---|---|---|
| R2 / F-01–07 / S-02 | 当前357含固定容器发现/更新/删除/unknown与checkpoint子集 | AUTH-017 eng_b四源只读complete、发现KAN-6、8checks；非完整生命周期/SLA | 本次R2 fake，无native模型升级 | 当前browser not_run；原矩阵子集有效 |
| R3 / Q-01/02/05/06/07/10 | 词法compound/长窗口/引用ID/negative review定向及完整回归 | 质量runner不调用native | fixture_source_live_model真实8问题前后对照；6自然题原子facts覆盖/无证据正确，quoted-ID缺口修复 | relevance及long-event最终拒答仍partial；人类质量not_run，用户明确批准延期交团队语义验收，不称通过 |
| R3A / P-14 / Q-10 | 当前来源/精确窗口/guard回归 | 原native子集不升级为完整新窗口链路 | fixture合法晚段真实送模型且usage有效，非整体质量通过 | 浏览器/完整native模型矩阵not_run |
| R4 / A-01/03/04/10 | 当前model stages/历史字节/签名快照回归 | 不升级native auditor | 48本次fixture-source真实usage与原ledger逐笔匹配；output rejection保留 | 独立custody/生产DB角色/用户已读/人G1不证明 |
| R5 / U-02/03 | 安全链接/历史metadata/诊断折叠/等待/迟到保护Node/HTTP通过 | 不重复历史8100正负独立问答 | UI检查fake，模型结果另列 | 49161新实例文字批准，但同工具normal retry仍saved permission blocks；browser not_run |
| R6 / U-01/05/06 | 331bd28无runtime/env干净重建及连续五fixture场景 | native和历史subset分列 | 预算/模型readiness本日实查，不保证未来有效 | 团队集中观看及G1/G2/materials pending；固定候选已准备，browser工具许可待解锁 |

当前候选[具体交接与未解决项](../evidence/runs/review-integrated-20261006/README.md)。ADR-040独立问答/无答案下载保留；根原docs01–05和历史review/audit/旧结果不改。AUTH-003/014/016/017具体批准持续有效，不能被下方旧pending/尚未开通表述撤销，也不能扩scope/write/account。browser真实许可待工具生效；不换入口绕过。以下日期段落及旧export/未实现状态属于历史，由本表/STATUS及最新ADR覆盖。

2026-10-06 R2真实只读增量：四源native身份/list/current-read complete，16.811s周期，原白名单外KAN-6/10015自动发现、fake问答当前Revision2 green、精确preview、8checks通过；只验证既有原资源进入新索引链路，非创建至可回答时延/四源新增矩阵。两个初始failed保留：精确Jira尾标签及既有fixture ID兼容断点，原文未改写；最新352 fixture/mock、21发现/4runner guard通过。native新增/编辑/删除多次生命周期、browser/live model、人G1/G2仍not_run；R1/R3A/R4新build验收不升级。证据review-r2-native-approved-fixture-20261006及两个失败目录。
2026-10-06 R2增量：19定向、346完整fixture/mock回归17.110s及两Node检查通过；四源实际mock新增发现/更新/删除/429 trace见review-r2-20261006。AUTH-017动态IDs仅eng_b，原生当前权限与R3A全文/精确窗口关系保留；不完整分页/读取失败不推进完整checkpoint。R2为verified local subset，native新增发现/生命周期时延及新browser/live model仍not_run；不是完整S-02或新鲜度SLA/G1/G2通过。下文方案未实现描述由本段覆盖。
2026-10-06 最新增量：R3A/R4 verified local fixture/mock，327完整Python方法16.645s、6来源定向/5审计定向及2Node检查通过。R3A合法无banner窗口按服务端已批准原资源/版本/原文精确关系放行；负例仍网络前拒绝。R4仅区分准备、发送意图/尝试、有效usage及输出、回答交付尝试，历史日志不改写。证据review-r3a-20261006、review-r4-20261006。新build native/browser/live model全部not_run，A-10/A-12/13完整验收及G1/G2不升级。R1本地完成，旧下文R3出口blocked/R4未修描述由本段覆盖；业务质量仍待验证。AUTH-017发现范围获批不等于发现实现/时延通过。8100历史独立问答验收继续有效。
## 当前验收增量 · 2026-10-06

以[STATUS当前总表](STATUS.md)为模式/版本/人工状态入口。DEV-REVIEW-R1：316完整fixture/mock方法16.309s、18模型定向、2Node检查通过；当前checkout，不是新的clean archive/native/model/browser验收。U-01/P-14/A-10仅新增价格跨日拒绝、预算保留、503操作员提示及非敏感health启动指纹子集；R4实际发送语义仍未修，不能将A-10整体标通过。R3长窗口synthetic guard与词法miss在当前模块复现，未用历史snapshot。证据review-r1-20261006。

ADR-040已实现，8100历史native/fake独立正负问题已验证；下载404是fixture/mock HTTP。AUTH-016 product_ops CF及AUTH-014有效；产品其他源/G1/G2/not_run。以下旧数字、导出能力和pending为历史记录，以顶部及最新决定覆盖，不改写原oracle或旧证据。

2026-10-06 AUTH-016已记录，Confluence-only product_ops token及app-owned本机Keychain复用获用户明确批准。已准备独立.runtime/confluence-product.json与nonsecret example、单源Confluence Keychain入口：新输入native身份匹配后才保存，saved免TTY复用、OS拒绝/wrong account不回退，actor/tenant/native-account摘要隔离SQLite0600。32针对性/307完整fixture/mock回归实际通过；初始test_keychain sibling import调用错误记录后按已有discovery路径重跑，不删断言。Atlassian页已填2918379149@qq.com，当前用户登录/邮箱验证pending，token未创建/产品Keychain项未写，native权限验收not_run；待“产品账号已登录”后继续只读scope准备及用户最终创建，再执行fake产品正/负query。不扩Jira/Slack/Drive/DeepSeek授权、不改8094，G1/G2 not_run。

2026-10-06 最新checkout完整301项Python回归实际通过（native-jira-update/full-tests.log），含新增mixed audit及Jira guard；既有native Jira13checks另列。full suite为fixture/mock，不增加native/model验收覆盖，当前新提交尚非新clean archive/browser视觉通过。独立Confluence product_ops凭据及本机Keychain复用具体候选PRODUCT_READER_PILOT已发确认，未回复前不创建token/读取新凭据/调整权限；其他源更新与真人观看保留pending。

2026-10-06 DEV-12-JIRA-UPDATE verified native API/fake model subset：AUTH-003在KAN独立新建合成KAN-6/10015并仅UI更新正文Revision1 amber→Revision2 green；eng_b AUTH-014已有Keychain复用，隔离memory index/两issue allowlist，不改原配置或8094。13checks/23event unsigned链通过：旧index保留时native old fingerprint/preview/history-export projection拒绝，refresh后新text/model evidence/preview正确、旧marker消失，KAN-4不变。版本是fingerprint，数值变小不代表回退；无新凭据/scope/模型费用。6guard tests（2新）通过；非worker/SLA/浏览器下载/真模型/完整persona或人G1。下一：独立产品身份具体凭据授权尚缺、Slack/Drive内容更新及真人观看仍待完成。

2026-10-05 DEV-12-AUDIT-MIXED verified local subset：实际fixture Engine生成成功/部分授权/全部deny/模型失败四类请求，独立request边界oracle116events与17页NL审计一致；page1后新请求不混入固定snapshot，scope/actor噪声排除，eng_a/security及越范围auditor拒绝，失败无committed/stored answer。CodeBuddy既有CLI实际4次原始/正文改/中间删/covered尾删验证通过，临时private key删除；同机custody仍非生产独立。4针对性tests通过（2新增），首个test mock影响Git revision的失败保留后修正test-only标记，不删断言。make verify-audit-mixed新目录可重放，团队一次集中观看清单已整理；无真实API/model/费用/8094重启，G1/G2 not_run。下一P0实际团队观看及未批准独立persona/native更新范围，其他质量评测可继续。

2026-10-05 最新提交b541c02 clean archive验证完成：无.runtime/.env，setup/297Python/5fixture场景/2Node脚本/真实fixture HTTP assets+login+four-source-query+exact-preview全部通过，evidence/runs/rebuild-native-restricted-approved。首次rebuild-native-restricted在沙箱内因23项HTTP bind EPERM失败，完整日志保留；获准本机loopback测试后同一提交通过，不跳过测试/关闭保护，不调用真实源或模型，不改8094。原生S-03仍single eng_b/fake model subset；下一P0集中团队观看与剩余native persona/更新范围，G1/G2 not_run。

2026-10-05 S-03 native subset：管理员在既有合成空间新增Restricted C-03/557057，仅owner访问；eng_b原生身份200、C-03 metadata404且无正文请求，C-02正文200。隔离受控synthetic旧索引保留，负面问答/模型evidence不含受限资料，旧preview原生deny；13checks/16event unsigned链通过（native-restricted-fixed）。首次fake空证据调用计数探针错误保留native-restricted失败与实际harness，修正探针后通过，不删安全断言。新增2个runner guard、4项针对性测试通过；未重跑完整295回归，runtime代码未改。无需输入凭据/模型费用/重启8094；不是contractor矩阵、统计侧信道或人工G1。下一P0整理团队一次性安全观看与剩余native persona/更新范围；G1/G2仍not_run。

2026-10-05 审计UI/分页候选0278bab：clean archive295 Python、五fixture场景、原frontend与新增audit Node、fixture HTTP smoke通过，rebuild-audit-ui。同view query旧响应/分页/重复点击/导航竞态已复现修复，process stages区分、HTML纯文本、unsafe整数提示；不扩大A签名/真人已读/G1声明，Chrome visual blocked/not_run。

2026-10-05 最新候选e9a55e6在无本机.runtime/.env的git archive中实际295/295、五fixture场景、Node及新启动HTTP前后端烟测通过，evidence/runs/rebuild-fixed。首次archive294/295及test环境依赖失败保留rebuild-candidate；用独立真实临时DB修复、不删安全断言。U-01更新为本地候选可重建subset，浏览器视觉、native矩阵、人工G1/G2不升级。

2026-10-05 更新：长文窗口10新测试（293总方法）local verified subset；Q-02本次eng_b真实产品四结论/四源input/1529microUSD、缺证据控制0模型调用，精确quote/逐阶段native/双ledger/developer review通过，非product_ops权限persona。NL audit对实际live合成日志副本分页与oracle一致，7签名边界通过，包括未覆盖尾部删除可逃过旧checkpoint；offline test auditor/同机临时key，非native审计身份/G1。runner stale mode后缀问题及未来修复均记录，原回答/hash不改。集中候选缺口见DEMO_CANDIDATE。

2026-10-05 S-01工程事实single eng_b live subset：新增J-03/KAN-5实际In Progress，正文scenario owner Maya fictional、native assignee Unassigned分别表达；四源8证据/4claims覆盖原因、撤回猜测、J-02 Done与J-03仍open、当前CF native3/runbook v1。7fact checks+agent全原文语义对照/quotes/native四阶段/双回执账本独立核验通过；不是原eng_a及product_ops矩阵或人G1。283回归方法数量不变，新增J-03正/负subtests；evidence/runs/live-s01。

当前完整301项unittest实际通过，证据 `evidence/runs/native-jira-update/full-tests.log`；旧297 clean archive记录保留为历史。fixture/mock与live结果仍分列，不等于51个计划案例全部通过。五场景 `scenarios.json` 仅为本地子集；四源真实查询/各源撤权子集与DeepSeek原文选择及opt-in综合另列。综合已有一次成功四源测试与agent语义对照，完整live矩阵、SSO、人工G1/G2仍未通过。以下未覆盖部分保留，不改写05的oracle。

| IDs | 当前状态与实际证据 / 缺口 |
|---|---|
| Q-01/02/04 | local subset verified；Q-02 live synthesis subset：pilot/GA、Done/发布及未确认日期已agent对照；Q-04首题保留Slack撤回时间线。完整S-01五事实及非作者人工综合质量仍pending |
| Q-03 | partial：关键词实体路径已实现，尚无专门错误相似对象对照 |
| Q-05/06/07 | local/mock subset：缺证据、伪造ID、quote不匹配、负面/未知review拒绝；live synthesis 4claims精确quote和agent语义支持subset。模型review非准确性证明，人工语义支持not_run |
| Q-08 | partial：固定四源授权范围检索；没有模型路由 |
| Q-09 | local one-hop verified：authorized seed + 每目标授权；两跳未实现 |
| Q-10 | partial：候选 24、输入 16000 字符预算；长窗口/规范offset/撤权保护local subset verified；近重复与独立语义质量未完成 |
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
| F-01/02 | local verified四源创建/更新及单对象发布；native AUTH021旧人工三阶段/十二行保留。AUTH024 CF一次自动创建已验；AUTH026三创建＋四更新native/fake新值使用已验，其中三创建＋Drive更新持续后台，CF原后台发布/fake恢复，Jira/Slack更新重启恢复。原生timestamp→cycle/失败原件见targeted-closeout；非精确commit/完整持续时延，多次自动样本、p95/max/失败率仍not_run |
| F-03/04 | local verified：lifecycle-local四源各撤权/删除，旧索引模型输入、旧历史/导出projection/引用全部保护，不重建正文，再 tombstone；native Slack既有撤权/恢复子集证据保留（synthesis-native-revocation）；完整四平台native撤权/删除矩阵not_run |
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
