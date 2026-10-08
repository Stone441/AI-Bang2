# 安装、启动、测试与演示

2026-10-08 本轮定向收尾及真实试用/反馈已记录：用户确认两题全部失败后停止使用，引用/History后续未做；首题输出拒绝、第二题Drive版本变化停答原件保留，实际试用failed。UX观察为等待计时/可感知工作状态缺失造成焦虑、模型和四平台连接信息不显性、页面简陋。用户明确当前只记录、等ChatGPT Chat后续指导，不改代码/界面/配置。49161自建实例已正常结束(exit0/无监听)，8094/8100未动；2次尝试/1次模型调用/11028microUSD，最终账本settled771913/available18903683，原pending1/324404保留。本轮信息收集完成不等于失败修复或验收通过；UX、原质量失败、重复自动测量/p95/完整native矩阵及G1/G2仍open。证据targeted-closeout-20261008/page-trial-final.json。下方等待反馈/运行中为旧快照。

2026-10-08 AUTH027实际试用实例已启动：http://127.0.0.1:49161，cdbd62b应用/eng_b/native四源只读＋DeepSeek v10 low8192，独立索引、原USD20账本，6次尝试及结算/新unknown停止限制。四源首轮complete，startup hash dc2903d72e3fec6c30156b84d351cee23d1d9be8bebfd5d756e1f5f2afe7ceb4；启动快照page-trial-startup.json，无ticket。实际入口已直接交给团队，首组两题/引用/History操作及反馈待做；启动与模型构造不等于真人或live问答通过。8094/8100/browser拒绝/G1/G2不变。下方“实例许可pending/未启动”为旧准备快照。

2026-10-08 页面试用启动准备（not_run，具体49161实例许可仍待回复）：`evidence/runs/targeted-closeout-20261008/launch-page-trial.py`为独立operator启动限额脚本，候选brain/scripts/tests/web不改；启动时先核cdbd62b无差异，新建私有`.runtime/page-trial-20261008`及隔离索引，仅symlink原USD20账本，拒绝重复使用已有trial状态。只在许可明确后执行`PYTHONPATH=. python3 evidence/runs/targeted-closeout-20261008/launch-page-trial.py`（私密启动日志含一次性ticket，不能提交）；eng_b/四源AUTH017只读/正常后台/DeepSeek v10 low8192。最多6次问答尝试；结算增量达到200000microUSD或出现新unknown即拒绝下一题，已在途调用完成，非供应商硬费用上限；原未知reservation保留。6次/结算阈值/new unknown/旧reservation/状态不可复用已用临时fixture账本验证，未绑定端口/读Keychain/访问native/调用模型。

批准启动且后台四源就绪后，才提供带一次性ticket的实际入口；由团队本人打开、操作。第一组操作：问`What is the latest approved mitigation for the payment incident?`，打开返回的一条引用核原文；再问`For payment-service, which code fix is complete, which preventive work remains in progress, and is general customer release approved?`；进入History重看刚才的问题、答案与Sources新鲜度，报告实际等待时间、结论是否有用及具体错误。答案须按当前native数据判断，不把fixture对照结果当live预期。Codex只记录服务审计/预算/模式和团队反馈，不自动化被拒绝的产品browser；非G1/G2审批。

2026-10-08 定向收尾：main已合并为 **2eabeb8**（PR8），应用仍 **cdbd62b**；当前独立fix/targeted-closeout-20261008无runtime修改。known05明确payment-service对照实际输入J03并正确回答Done/In Progress/no GA，15.026秒、5179microUSD；旧题/oracle/partial保留，不能推断仅歧义所致。统计细化core24=21直接事实＋1前提纠正事实＋2纯空；known12=3完整＋1部分＋1前提纠正事实＋6纯空＋1预期unknown。AUTH026仅3创建＋4更新已消费，7项均新值native发现/fake证据使用；三创建及Drive更新为持续自动，CF在原后台发布但fake恢复后成功，Jira/Slack更新为重启恢复，非全7持续时延通过。并发源版本变化停答原件保留，两审计链341/795有效仅本地；原生更新时间到发布不能称精确commit或SLA，多次自动样本/p95及完整native撤权删除仍未验。账本settled760885/available18914711、原pending1/324404保留；AUTH019不变。具体页面实例许可仍待回复，未启动49161、不动8094/8100；browser/G1/G2不变，新分支未push/merge。证据evidence/runs/targeted-closeout-20261008。


2026-10-08 Git交付补充：AUTH-025已批准本轮推送并通过PR合并main；下方未push/merge为性能证据冻结时快照，实际交付以PR状态和main commit为准。应用验证基准仍cdbd62b；文档/Git操作不重启或升级运行实例。

本轮本地应用 **cdbd62b**，synthesis-v10、显式low/8192（stored sampling=0，low时实际省略temperature）、模型60秒/native30秒，默认none/1024保持。运行中的8094/8100未加载本轮修改；不启动新live HTTP实例。后台每source串行、前台阶段最多四source lanes，来源共享429 Retry-After冷却、不自动retry；每阶段重新检查，不加总并发HTTP累计时间与wall。421 clean archive/两Node/五fixture通过；CLI query40.08/49.03秒、同对象preview1.66/1.05秒，后台运行。AUTH024单页创建及native/fake自动发现已完成，原24＋已知12语义分类与性能/预算在lock-contention-20261008/README.md；known05部分覆盖、query目标未全达，browser/G1/G2不变。下方旧启动命令/状态按版本保留，任何服务启动仍需具体实例授权。

封版验证候选 **80b9ffc**：`deepseek-flash-grounded-synthesis-v10`、显式可信low/8192、每阶段60秒有界模型等待；原生接口仍30秒上限。检索/分块/数据目标保持，默认operator none/1024不变。原0bc90ae主要质量证据为v8 low4096，不能代作v10结果。固定配置/hash及本轮实际证据见`evidence/runs/candidate-closure-20261008/`；本轮已知12题和native/model均为独立CLI验证，不证明任何页面实例已加载。

未来已有对应实例启动/访问授权后，使用以下完整可信命令；`<approved-port>`须为另行核准的具体实例，不沿用49161旧授权、不动8094/8100：

```sh
python3 -m scripts.model_readiness
python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port <approved-port> --live --model deepseek --credential-store macos-keychain --answer-style synthesis --reasoning-effort low --output-tokens 8192 --discovery-auth017
```

启动前还须读取原账本剩余/unknown reservation，核native身份及原固定容器；价格跨日失效就真实复核，不改旧日期绕过、不清账。不使用`make live-synthesis`默认参数冒称本候选。服务启动后保存startup fingerprint、health模式与一次实际回答/引用版本，不能只靠health或Git merge证明新版生效。此次未启动/重启服务，browser仍工具saved denial blocked。连贯18分钟回看在SAFETY_REVIEW顶部，页面现场补验须正式许可。

2026-10-07固定候选0bc90ae采用显式可信`--model deepseek --answer-style synthesis --reasoning-effort low --output-tokens 4096`；AUTH017统一发现另用既有`--source multi --actor eng_b --discovery-auth017`与原审核config/Keychain/Drive OAuth。默认仍none/1024；已有运行进程未加载此候选。启动前核具体服务/版本和对应授权，不启动49161或动8094/8100；先model_readiness/当日官方价格、原USD20账本及native身份，失效停用、不改旧日期、不清预算。当前核心命令/文件hash记录在candidate指纹和各verification.json；这些验证不是浏览器或G1/G2通过。

以下较早版本的状态描述为历史记录，由顶部候选记录覆盖；通用安全操作要求仍有效。

2026-10-07当前应用3ceb625（synthesis-v6，温度0）；2a039aa仅新增context篡改负测试，brain字节相同。两阶段现传原资源title/locator与text分开，不能充当quote/权限；标题/定位篡改在reserve前拒绝。3ceb clean archive388/同48世界五fixture/语法及两Node通过；2a039aa clean archive389回归通过。完整24开发题只读逐项核为22核心事实正确返回＋2正确空答，零运行异常；business12独立quote失败与business16跨事件误归本轮未重现，单次成功非稳定修复。business03未明确说明rejection无证据、business32两条无关背景仍open，整体完整性/相关性未通过，非AUTH019延期。eng_b两道本版本native＋真实模型正确，28窗口出现次数/四阶段allow/6claims/4usage；耗时含preview121.928/130.040秒，非SLA。开发诊断4题/core24/native2费用上界4137/22146/5100microUSD，原账本settled226368/pending0；共享起点含并发reservation不得用accounted差归成本。当前core全签名/native七边界与分页本地核验，非独立custody或人阅读。证据见source-context-v6-full-readonly-review、source-context-v6-native-readonly-review及candidate-source-context-v6-fingerprint。旧失败/保留题不改或重跑；Goal active。browser saved site denial blocked，49161停止，8094/8100未动，human/ROI/G1/G2/推送发布not_run。

2026-10-07最新局部结果：固定代码2a73bd0，380 clean archive/同48世界五fixture/两Node通过；当前eng_b两题native＋真实模型经只读复核5claims/28windows/四阶段当前allow/四usage与账本3207microUSD增量一致。配对272事件签名副本及混合208事件oracle另列local。全persona、故障live、四源native删除/新鲜度SLA、native正文关联、Docs支持未完成；browser saved site denial blocked，human业务判断/ROI/G1/G2 not_run。旧f8ecbed保留题失败及AUTH019延期保留，不从四开发题改称通过。完整证据见business-validation-20261007，旧版本表保持历史。

2026-10-07业务增强候选实现f8ecbed：373 clean archive/五fixture/2Node/HTTP通过；binary-TF BM25、表格cell关系、资源方向审计、有界后台查询及版本反证停答已实现。四源AUTH-021新probe和两次修正native API/fake当前16断言通过，加载hash匹配候选；query约43–58秒，非SLA。12保留题冻结后一次live评测及只读语义审查已完成，具体见business-validation-20261007/heldout-review.json：有明确正确答案和safe unsupported，也有歧义/状态误答、部分答案和来源故障告知不足，不能称质量全通过；两项AUTH-019原延期不覆盖这些新失败。当前native/模型签名副本分别核验，同机测试key非独立custody；产品browser仍saved site denial blocked，49161停止、8094/8100不动；G1/G2、人类任务/ROI及发布提交not_run。Goal active，新增工程缺口仍由Codex继续负责。最新本地候选c825143非后台unknown通用修复有17定向、377 clean archive/五fixture/2Node/HTTP及只读复审通过；它尚未形成新native/live/browser结果，不能继承f8ecbed两题实际运行。

新增只读/隔离命令（每次新目录，勿覆盖历史）：`python3 -m scripts.business_native_changes --live --root evidence/runs/business-validation-20261007/native-change-owner --phase amber-return --capture-name <new-label> --background`；当前源码回归`python3 -m scripts.rebuild_acceptance --ref f8ecbed --output <new-directory>`。native model使用`python3 -m scripts.business_current_native_model --live --output <new-directory>`，先真实model_readiness/原账本，复用原AUTH与Keychain，不启动HTTP/源写入/新费用范围。保留题已消费，不再作为未见题重复调参。上传file URL许可只用于owner三版本上传，已完成，用户可关闭；不自动修改设置。

## 当前集成候选运行入口 · 2026-10-06

当前开发分支 `fix/review-integrated-candidate`，基准45d7b27；最新固定应用/测试331bd28已干净archive setup/357回归17.406s/五fixture场景/两Node/HTTP通过。323cb93的356项记录是早先里程碑，不能冒作之后HEAD通过。当前状态/模式及证据以[STATUS](STATUS.md)、[ACCEPTANCE_STATUS](ACCEPTANCE_STATUS.md)为准；以下历史段落的export/New question、仅memory/尚未授权/尚无native等旧陈述已被ADR-040和最新AUTH覆盖。

本地集中观看：在**新的隔离git archive目录**启动，保留原项目.runtime和审计，不停止8094/8100。先 `make setup`、`make test`、`make verify`；`python3 -m brain.server --demo --port 0` 打印本次实际loopback地址，模式fixture_fake_model。浏览器只访问获许可的该实例；端口变化/实例停止后按具体授权重新确认。fixture身份不是native员工登录，FAKE MODEL为原文摘录；真实模型的claims质量另看独立记录。

同一场五场景：按下方步骤顺序完成S-01当前原因/撤回解释/未完工作及pilot限制；S-02在**该隔离目录**使用fixture_admin更新runbook，旧引用与history失效；S-03 contractor禁止泄露security对象存在，并对照允许的pilot；S-04同一eng_a身份撤权后独立再问、旧引用/history拒绝，不自动继承上一问；S-05 auditor受限模板还原当前准备/发送意图或尝试/有效usage/输出及存储/HTTP交付尝试。Fake provider没有真实vendor调用，不能制造model receipts。签名覆盖另重放既有CodeBuddy verifier对R3A/R4候选快照，注明checkpoint seq/unsigned tail/old rollback和同机custody，不恢复用户答案下载。统一观看清单见[SAFETY_REVIEW](SAFETY_REVIEW.md)。

AUTH-017四个固定容器发现已实现并有当前native readonly/fake模型子集；`--discovery-auth017`只适用既有multi/eng_b，默认关闭，不扩product_ops。新建/修改/删除源端数据及目标服务重启按各自具体授权，不由本地fixture操作推导权限。完整四源native生命周期时延矩阵仍partial。

真实模型每次先 `python3 -m scripts.model_readiness`，再核对现有配置/授权及原USD20 ledger剩余/冻结状态；不注入旧today或重建账本。`python3 -m scripts.quality_acceptance --live-model --output <新目录>`仅固定fixture合成源＋真实模型，使用既有app-owned eng_b key和原账本；不是native persona/四源模型验收。会产生已批准预算内费用，输出capture不等于semantic通过，需逐条claims/quotes/omissions/relevance审查。旧检索harness只用于词法边界：`python3 -m scripts.retrieval_acceptance --output <新目录>`，拒绝覆盖旧记录，不称质量benchmark。

当前R5真实浏览器许可单独记录：新49161隔离fixture已核health并获用户重新批准，但mcp__cua_repl.js / Chrome正常重试仍被saved user site permission拒绝。工具无许可管理API，Codex应用界面访问也被策略禁止；用户回复“没有找到许可入口”，具体设置位置未知。真实browser/screenshots not_run，Node/HTTP不替代浏览器。仅自建49161实例已结束，8094/8100未动；未来先核新实例归属/模式并重新确认对应许可，不沿用旧地址授权。G1/G2仍not_run。

## 先前运行说明（版本/授权描述由上方覆盖）

R2只读native runner：`python3 -m scripts.native_discovery_acceptance --live --output evidence/runs/<新的唯一目录>`。默认既有`.runtime/operator-bundle.json`与私有Drive desktop client；只复用app-owned Keychain和已保存refresh grant，不交互输入/新consent/保存凭据，不启HTTP或付费模型。输出存在即拒绝，首次失败也不覆盖；缺凭据或refresh失效直接停并记录失败类型。先验证AUTH-017配置再用凭据，native身份每源核对；原baseline IDs/原进程保持。已验证新增to-index只有既有KAN-6，不保证其他源有合格新对象。Jira支持完整末尾`[SYNTHETIC ONLY]`，完整原banner+精确J-lifecycle-20261006被认可，未知/篡改仍拒绝；不能将只读批准用于改标题/种植新源。
R2 AUTH-017 opt-in：原multi命令追加`--discovery-auth017`，仅eng_b及四个固定容器，默认关闭，独立`.runtime/multi-auth017-web.sqlite`；不改变8094/8100已有进程。启动后60秒为成功周期的最短间隔，失败按退避/Retry-After延后，不保证每分钟完成。operator-only状态在该DB discovery_state/catalog；不向浏览器开放来源列表。停止使用Ctrl-C，先结束poller再关闭DB；再次启动从已记录mapping精确复核，unknown不给权限。真实只读发现获AUTH-017批准，native新增/时延本轮未执行；种植/编辑/删除仍按各自具体授权。本地验证：`python3 -m unittest discover -s tests -p test_container_discovery.py -v`；实际mock trace重放请将capture.py复制到新运行目录并用`PYTHONPATH=tests:. python3 <新目录>/capture.py`，exclusive输出不覆盖原结果。
2026-10-06 R3A/R4 本地回归：`python3 -m unittest discover -s tests -v`；`node tests/frontend_operator_security.js`；`node tests/frontend_audit_review.js`。来源与审计定向：`python3 -m unittest discover -s tests -p test_synthetic_provenance.py -v`及`-p test_model_stages.py`。结果写新的运行目录，不覆盖旧附件；review-r4 capture.py是离线mock且输出exclusive，重放必须先复制到新目录并调整目标。真实模型前执行已有`python3 -m scripts.model_readiness`并保留账本，过期需真实复核；不凭health推断新代码已加载。R2仅AUTH-017固定eng_b容器读取获批，方案尚未实现；不自动重启已有8094/8100。
## 当前运行提示 · 2026-10-06

先看[STATUS当前总表](STATUS.md)。ADR-040独立问答已落实：无聊天历史依赖、New question或普通回答下载；下方相关旧说明为superseded。四源native/DeepSeek及独立product_ops Confluence已有子集，不重复开通。

每次live启动前运行`python3 -m scripts.model_readiness`，只检查价格日期，不读取凭据/账本/联网；返回0仅表明当日价格已复核，不保证预算、源或模型可用。当前复核SGT Oct6，Oct7过期；实际核对官方[价格](https://api-docs.deepseek.com/quick_start/pricing/)及接口并记录新依据后更新构建。不得传旧today、删除/换目录重建USD20账本。跨日非空请求503/model_price_review_required，联系操作员，重试问题不能解决。

新进程启动日志与GET /api/health携带startup_source_sha256和process_loaded_at（源码快照，不是签名证明）；静态UI可独立变化，不热更新后台。只读现场8094=四源/native/live synthesis、8100=CF/native/fake且无该字段；准确loaded commit未知，本轮保持不重启。运行时验收另行记录，不能以磁盘代码/本地回归代替。

要求 Python >=3.11（本次实际 3.14.7）、可绑定 loopback 端口。应用零第三方 Python 依赖，无 npm/pip 安装步骤；无需 API key。签名工具及完整测试另需 PATH 中的 OpenSSL（已验证 3.6.3，需支持 Ed25519 pkeyutl -rawin）。Node 仅用于 `node --check web/app.js`。在仓库根目录执行。

```sh
make setup
make test
make demo
```

浏览器打开 `http://127.0.0.1:8080`。界面显示 LOCAL DEMO / FAKE MODEL；可选六个合成身份。`python3 -m brain.server` 不带 `--demo` 会拒绝启动；绑定地址不可从命令行改为外网。退出 Ctrl+C。

运行数据在 `.runtime/`（Git ignored）：SQLite 保存索引/审计/历史，source.json 为独立的 fake source 当前权威；session 仅内存，重启需重新登录。源文件替换为原子写入，demo 管理命令请串行执行。全链路只含合成资料，不能把此目录替换为真实企业资料。

## 五场景现场回放

1. **S-01**：以 Alex / eng_a 登录，点 Understand the incident，提交问题。核对 root cause、withdrawn hypothesis、PAY-102 Done、PAY-103 In Progress / Maya、runbook 和四源引用。以 Product & operations 登录查 release readiness，核对 pilot、GA not approved。
2. **S-02**：先查 runbook v1，再在另一个终端执行：

   ```sh
   python3 -m scripts.fixture_admin runbook-v2
   ```

   回到同一网页再查 latest runbook，看到 v2 和 standby queue 步骤。当前是请求驱动的本地事件处理，**不是已实现的真实 webhook/定时同步延迟**。
3. **S-03**：以 External partner 登录，问 `Show me the Q3 security incident report.`；不得确认受限对象存在。再问 external partner pilot，应有正常获准资料。
4. **S-04**：以 eng_a 获取 incident thread 回答，保留该会话。另一个终端执行：

   ```sh
   python3 -m scripts.fixture_admin revoke --resource S-01 --user eng_a
   ```

   同一登录身份独立再次查询payment-service线程及retry safeguards；不得再次输出线程独有标记。打开旧 S-01 引用应不可用；Recent answers 中依赖已撤权资料的整条旧回答应不可用。无需全库重建。可分别对 C-01/J-01/D-01 重复。
5. **S-05**：以 Scoped auditor 登录，打开 Audit explorer，提交预置问题。展开事件查看身份、问题、逐资料授权、prepared_for_answer/review、model_dispatch_intent/attempted、有效usage、引用和最终答案；支持稳定 snapshot 分页。HTTP 场景还记录 dispatch_attempted。CLI 回放不伪装成 HTTP dispatch。

完整自动回放使用隔离内存状态，不改变正在演示的 `.runtime`：

```sh
make verify
make verify-lifecycle
make test-report
```

输出 `evidence/runs/local-latest/scenarios.json`、`audit.json`、`tests.json`。S-05 检查仅是内存保留 trusted head 的本地演示，未具备独立签名根。离线签名另由真实 CodeBuddy 实现并经 20 项测试验证；命令见 CODEBUDDY_AUDIT_DELIVERY.md，同机同账号不代表生产独立保管。

`make verify-lifecycle` 单独生成 `evidence/runs/lifecycle-local/results.json`：四源各自更新、撤权、删除共12组隔离检查，先保留旧索引验证即时拒绝，再应用事件验证单对象发布及重复处理。只使用 fixture/fake model，不访问正在运行的服务、不修改真实平台。团队观看与最终提交检查见 [SAFETY_REVIEW.md](SAFETY_REVIEW.md)，自动回放不代替人工安全验收。

要重新开始人工演示，停止服务后仅将 demo 数据文件改名备份，再启动；先确认备份名称不存在。不要整体移动 `.runtime`：目前其中有 `.runtime/codebuddy-dev09` Git worktree。不要删除旧审计。自动测试均使用自己的临时/内存状态。

## 故障与边界

Confluence 只读 API pilot 的配置、诊断及共享 Engine 查询命令见 [CONFLUENCE_PILOT.md](CONFLUENCE_PILOT.md)。独立操作员入口已接通本地索引/检索/引用/审计，Confluence API操作员查询/撤权已实际运行；新网页入口已通过mock源+真实loopback HTTP测试，真实网页运行待用户完成。以上demo命令仍fixture。

- 沙箱报 `Operation not permitted` at socket.bind：是 loopback 执行权限，不是测试通过；在获准环境运行同一测试，不跳过 HTTP 测试。
- 浏览器 `ERR_BLOCKED_BY_CLIENT`：本次自动化环境阻止 localhost 浏览器访问，视觉/交互验收未完成。不要关闭安全设置来绕过。
- 端口被占用：`python3 -m brain.server --demo --port 8081`。
- 审计不可写、授权 unknown、源/索引版本不一致：不返回无法安全完成的成功答案。
- 无跨用户答案缓存，无 reranker/compressor，因而这两类真实模型入口尚无效果验证。
- 仅 loopback、无 TLS/SSO、无独立数据库权限身份，不能作为公开部署方案。G1/G2 由团队验收。


## Confluence 操作员网页（已批准eng_b只读token）

```sh
python3 -m brain.operator_web --config .runtime/confluence-pilot.json --actor eng_b --live
```

在真实TTY隐藏输入邮箱和token（不保存），打开终端输出的一次性本机链接。链接10分钟有效，消费后不能复用；它是会话入口凭据，不要截图/分享。启动时服务端核对token的native account ID；浏览器仅获opaque cookie/CSRF，不能选择用户或role。问 `Show the payment-service runbook`，核对引用、Recent answers。DB在ignored `.runtime/confluence-web.sqlite`，退出Ctrl+C；不要与8081已有服务冲突，可用`--port 8082`。

这是LOCAL OPERATOR / LIVE API / FAKE MODEL试点，不是员工SSO/OAuth。只有白名单合成Confluence页面，不发收费模型请求；源授权在查询、模型前、返回前及history/export/preview仍重查。默认不带`--live`不读凭据/联网。代码已mock HTTP验证，C-01真实网页问答已记录，引用/历史获用户确认；不是完整Confluence权限矩阵或G1通过。

Jira只读诊断/问答命令、原生ID配置与权限缺口见 [JIRA_PILOT.md](JIRA_PILOT.md)，不能复用Confluence token或将模板中的占位ID当真实ID。


操作员启动故障（2026-10-05修复）：先预留loopback端口，再隐藏输入凭据；服务只在native identity验证后开始处理HTTP。`[port_in_use]`表示监听端口已有服务，不请求凭据、不调用平台；保留已有服务或在命令末追加`--port 8082`（不要擅自kill占用者）。其他安全诊断分为configuration_or_hidden_input、local_store、native_identity、runtime；不会打印异常原文、token或上游body。身份未知仍停止，不能靠诊断降低授权要求。


### Jira operator web（一次启动输入，进程内复用）

已批准 Jira 凭据、核验 native IDs 并配置 `.runtime/jira-pilot.json` 后：

```sh
python3 -m brain.operator_web --source jira --config .runtime/jira-pilot.json --actor eng_b --port 8083 --live
```

启动时隐藏输入实际 eng_b 邮箱与密码管理器 Jira token 一次，打开输出的一次性入口链接（不要截图/分享 ticket）。同一运行进程中，网页 query/history/citation 不再请求输入 API 凭据，但每次仍重查源身份及当前权限。不是将授权结果缓存成永久 allow。DB 独立为 `.runtime/jira-web.sqlite`；Ctrl+C 停止后内存凭据消失，下次启动需重新输入。默认不读取系统密码应用，不保存 token 文件。保留已有 Confluence 服务，不 kill 端口占用者。网页是操作员 pilot/fake model，不是 SSO 或 live LLM。

可问 `What is the status of the payment-service retry configuration fix, and does completion approve general customer release?`，点击引用及 Recent answers；实际结果由 DB 验证，不能把 mock 测试当 live 问答通过。

前端安全视图回归：`node tests/frontend_operator_security.js`（需Node，独立于标准库Python运行时）与 `node --check web/app.js`。验证导航/preview拒绝/待返回query/history请求清除旧视图。页面跨视图不复用旧答案；请用Recent answers重新鉴权访问。前端静态文件修正可直接刷新当前网页，session仍有效，无需重启或重新输入API凭据。


### Slack operator pilot

见 [SLACK_PILOT.md](SLACK_PILOT.md)。一次隐藏输入 USER OAuth token，不需要邮箱；配置 native IDs 后可使用 `--source slack --actor eng_a --port 8084`。既有app已由用户授权并保存token，真实root/reply问答、引用与历史已核验；频道撤权仍待独立reader。不要直接运行含占位ID的模板，当前结果仅live API + fake model。


### Drive operator preparation

见 [DRIVE_PILOT.md](DRIVE_PILOT.md)，本地mock已接同一Engine/网页入口，首版personal Drive UTF-8 text/plain；真实scope、OAuth、原生IDs/种植尚未批准配置。准备的`--source drive --port8085`命令不可用占位模板直接当live启动。

### Unified multi-source operator

`--source multi` supports two to four reviewed source configurations under one tenant and one operator actor. Copy `config/operator-bundle.example.json` into ignored `.runtime/operator-bundle.json`; include only approved/configured sources. Paths are relative to the bundle. Keep the example review flag false until each source account is verified as belonging to the intended operator persona, then set `identity_mapping_reviewed` to true. This local flag records a trusted configuration review; it does not verify ownership or grant source rights. Do not rename existing eng_a/eng_b mappings merely to make a bundle load.

```sh
python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --port 8086 --live
```

The loader validates all configurations and matching tenants before prompting for any missing credential. Approved environment references can supply already-configured credentials; otherwise each source asks once using its existing hidden-input helper. Every configured native identity is checked before the browser bootstrap is issued. Each later read still checks current source rights. The local database is `.runtime/multi-web.sqlite`; no secret is stored in it or sent to the browser. Keep existing single-source processes running. Do not extract their in-memory tokens or reuse an identity mapping that belongs to another persona.

Four-source HTTP integration and one-source revocation are mock-verified. The current live Slack eng_a and Confluence/Jira eng_b configurations are not a reviewed same-persona bundle. Real unified integration, Drive OAuth, SSO, live model and G1 remain pending; no restart/input is requested for this new feature yet.

### Drive Google desktop consent (no manual token copy)

After the approved Google desktop client and exact synthetic files are configured:

```sh
python3 -m brain.operator_web --source drive --config .runtime/drive-oauth-pilot.json --oauth-client .runtime/drive-oauth-client.json --actor eng_a --port 8085 --live
```

The downloaded desktop client JSON is private, ignored by Git and must be owned by the local user with mode 0600, not a symlink. Use `config/drive-oauth-pilot.example.json` as the configuration shape; all placeholders are deliberately invalid. Review the Google client ID, operator email and exact file→parent IDs. The server reserves 8085 before consent; leave other source processes running. It prints a Google authorization URL with one-use state and S256 challenge. Open it and complete only the approved Drive read-only consent yourself. Do not share the authorization URL, callback code, client JSON or bootstrap ticket. The callback listener is loopback-only and waits up to 10 minutes.

The program exchanges the one-use code, checks the exact granted scope and native Google account metadata, then serves the same operator UI. It does not ask for email/token input. Tokens are in process memory; no refresh is persisted or used, so expiration fails closed and a later start requires browser consent again. The callback page says received before native account verification: only successful operator startup confirms that verification passed. This is not employee SSO, and Drive native read/revocation acceptance remains separate.

OAuth callback成功页是临时页面：看到Google authorization received后不要reload。账号检查通过后临时listener关闭，旧callback URL重载可出现ERR_CONNECTION_REFUSED；这不等于Drive服务退出。使用终端后续8085应用入口即可，不发送ticket/code。若Chrome拦截agent自动打开localhost（ERR_BLOCKED_BY_CLIENT），由用户在应用入口地址栏Enter，不关闭安全设置、不重复Google授权。health显示drive_live_api_fake_model/operator才确认正式服务启动；应用查询仍单独验收。

### Approved DeepSeek pilot (price reviewed 2026-10-05 Singapore)

Keep the existing port 8085 process. In a new local VS Code terminal:

```sh
python3 -m brain.operator_web --source drive --config .runtime/drive-oauth-pilot.json --oauth-client .runtime/drive-oauth-client.json --actor eng_a --port 8086 --live --model deepseek
```

Complete the existing Google read-only consent through the terminal URL, then enter the DeepSeek API key at the hidden prompt. Do not paste the key or bootstrap URL into chat. Open the application link after startup. Google callback is temporary: do not reload it. Subsequent questions reuse credentials held in this process. Default commands without `--model deepseek` remain fake-model pilots. No live model call occurs during startup.

Only explicitly marked synthetic evidence is sent. The model selects evidence; the server renders original excerpts. Free-form synthesis is not enabled. `.runtime/deepseek-budget.sqlite` is the shared USD20 ledger across all operators: never delete, reset, replace or change working directories to bypass pending charges. Peak/cache-miss accounting is conservative, not a billing invoice. Unknown consumption keeps its full reservation. Price review expires at the end of the reviewed Singapore date; future startup or nonempty model use stops until prices are reviewed again. Existing fake services continue running. Real DeepSeek results remain not_run until actual call/output/ledger/audit are inspected.

Actual first DeepSeek checkpoint: [live-drive-query.json](../evidence/runs/deepseek/live-drive-query.json), native Drive + real model selection, query/preview/history verified. Original fake commands and comprehensive live acceptance are separate. Keep port8086 running; no further key input is required during its lifetime.

Model usage receipts: new answers expose validated token counts and a conservative USD cost estimate under “Model usage receipt”. This is not the vendor invoice. Older answers without a receipt say “MODEL CALL NOT RECORDED”; do not infer a live call or zero usage from their evidence list. Native/history/export authorization still gates the entire record. Static UI updates require refresh; already running Python processes do not load changed Engine code automatically.

Atlassian hidden input: enter the mapped Atlassian email only, then paste only the scoped token value from the password field. Nothing appears while typing/pasting. Invalid input retries just that field (at most3 attempts): `credential_email_invalid`, `credential_token_empty`, `credential_token_multiline`, `credential_token_too_long`; `credential_secure_tty_required`, `credential_hidden_input_unavailable`, `credential_input_ended` stop without echo fallback. These local diagnostics do not indicate whether a token is valid on the platform. Share only the fixed error code for troubleshooting, never entered values.


### Approved one-command four-source startup (AUTH-014)

在仓库根目录的新 VS Code 终端只运行：

```sh
make live
```

使用已审核 eng_b 的 ignored bundle，8088，真实四源及 DeepSeek，显式 opt-in 本机钥匙串保存。首次仍需逐项隐藏输入 Confluence/Jira 邮箱与各自 token、Slack reader token，完成 Google 只读浏览器授权，再隐藏输入 DeepSeek key。程序不读取你在「密码」应用里已有的条目；创建自己的钥匙串条目。已保存项在后续启动复用，后续步骤失败也不丢失前面的已保存项。操作系统可能要求解锁或允许钥匙串访问。不要关闭安全设置，不发送密钥/完整入口链接。

Google refresh 只在原生账号核对成功后保存；以后重启自动换 access token，scope 固定 drive.readonly。撤销/过期可能需要只重新完成 Google 授权；运行中的 access token 到期仍拒绝访问，可重启。源 token 的格式校验不等于平台授权通过：启动仍核对全部原生账号，每次问答/引用/历史仍核对当前权限。DeepSeek 价格日期及 USD20 账本限制不变。

如只有某枚凭据错误，复制下列命令，将最后的平台选择为 confluence、jira、slack、drive 或 deepseek，只重新输入该项：

```sh
python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port 8088 --live --model deepseek --credential-store macos-keychain --replace-credential slack
```

默认未指定 credential-store 的旧命令依然仅内存保存。钥匙串拒绝读取时停止，不回退明文。只读平台与模型真实集成另行验收；本次合成钥匙串 smoke 和 mock refresh 不代表统一四源 live 已通过。


2026-10-06该回答下载功能已取消：无Export answer入口，GET /api/export/*对已登录请求返回404。旧下载验收仅为历史证据，不代表当前能力。每次query独立，客户端history_id返回400；旧服务须重启加载后端修复，凭据按已批准的程序Keychain复用。

### Opt-in grounded synthesis (synthetic pilot)

Default `make live` retains source-excerpt selection. Use `make live-synthesis` for the reviewed mode, or add
`--answer-style synthesis` to the reviewed multi-source command:

```sh
python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port 8088 --live --model deepseek --credential-store macos-keychain --answer-style synthesis
```

Do not start a second process on an occupied port. Keep the current service or
stop it yourself before selecting this mode; app-owned Keychain reuse avoids
re-entering saved credentials. Native account verification still runs. Existing
source scopes and the same `.runtime/deepseek-budget.sqlite` USD20 ceiling apply.
Do not change the working directory to create another budget ledger.

Ask `What is approved for the payment-service pilot, what remains blocked, and what incident safeguards must be in place?`.
The answer displays a concise conclusion per claim, citation buttons, expandable
exact supporting quotes, and separate generation/review usage receipts. History
and raw export preserve grounding and both receipts; current access is checked
again. The review reads full authorized evidence after another native check.

Review is a fallible quality filter: exact quotes prove source provenance, not
semantic correctness. Human acceptance must check scope, negation, contradictions
and whether conclusions actually follow and answer every requested part. The v2
review requires explicit boolean `question_covered: true` as well as support for
all claims; this remains a fallible model judgment. Missing quote/citation, unknown or
negative review, changed access/version and incomplete output reject the answer;
no automatic paid retry or silent fallback occurs. Fake-model mode does not
simulate passing synthesis review. Complete five-scenario live acceptance and
G1/G2 remain separate from local/mock results.


To preserve an existing8088 service while opening another reviewed synthesis operator, use `make live-synthesis LIVE_PORT=8094` from repository root. The same budget ledger is used, with no scope change; native identities are verified again. Open the new terminal one-use link yourself and keep it out of chat/screenshots. `LIVE_PORT` defaults to8088; existing listeners are never killed automatically.

Frontend navigation/expiry/sign-out invalidate prior requests. A late answer/quote/history/export does not repopulate the newer view or create a file; this does not undo an already-dispatched model call or recover a downloaded copy.


Local port-session fix (2026-10-05): newly started servers use separate cookie names per bound port. Existing services continue using their loaded implementation: restart each affected service once and open its new terminal entry. Keys are reused from the approved app-owned Keychain. This prevents accidental login/logout collisions between local ports; cookies are still scoped to a host, so this does not provide security isolation from hostile local HTTP services. Never copy an old cookie/ticket to recover an expired session.

### Local retrieval windows

Run `make verify-retrieval` for authored long-document/lexical cases (fixture source, fake model). Results: `evidence/runs/retrieval-local/results.json`. The current retrieval uses lexical overlap and a small explicit English alias map, not embeddings. Long evidence previews include Unicode character offsets and return the exact source window. Fixed windows may cut sentences. DeepSeek still rejects any window without its approved synthetic marker; this local test does not prove live long-document model support. Existing running services load this code on their next normal restart; no credential re-entry is needed for the approved Keychain configuration.

### Clean candidate validation

`python3 -m scripts.rebuild_acceptance --ref HEAD --output evidence/runs/rebuild-<new-label>` exports only a committed snapshot into a temporary directory and runs setup, the full test suite, fixture five-scene replay, Node frontend checks and a newly started HTTP demo through login/query/preview. It preserves prior evidence, needs loopback permissions/OpenSSL/Node, and does not use existing runtime credentials or paid services. Current candidate e9a55e6 passed; initial test-isolation failure is retained separately. HTTP smoke does not establish browser visual acceptance.

### Audit interface checks

Mixed-outcome audit acceptance (fixture/fake only, no credentials or costs):

```sh
make verify-audit-mixed AUDIT_OUTPUT=.runtime/audit-review-01
```

Use a new output directory on each run. This executes successful, partly authorized, denied and failed questions, compares paginated inquiry with captured event IDs, checks a fixed snapshot during a new request, denies out-of-scope audit access, and runs the existing CodeBuddy signature CLI against original/tampered copies. The disposable local private key is deleted; same-machine signing is not independent production custody. Team observation remains a separate step in `SAFETY_REVIEW.md`.

`node tests/frontend_audit_review.js` checks same-view query ordering, stable-snapshot pagination, duplicate clicks, navigation guards, HTML as text, and honest display of integers outside JavaScript precision. Audit rows distinguish candidate, authorization, model input, citation and delivery. The browser timeline does not verify a signature or prove human reading; use the offline verifier for signed boundaries and the authoritative backend export for exact fingerprints. Current visual browser check was blocked by Chrome and remains not_run.

### Approved independent Confluence product reader

AUTH-016 approves only the specified product_ops Confluence token and app-owned Keychain reuse. Follow `PRODUCT_READER_PILOT.md`. Single-source Confluence supports `--credential-store macos-keychain`; new input is verified against the native account before saving, and subsequent startup reuses the item. Its database is isolated by actor/tenant/native-account digest. Other single-source Keychain modes remain rejected. Native product permission acceptance is still pending login/token creation; use the prepared fake-model command, not an unapproved product model credential.
