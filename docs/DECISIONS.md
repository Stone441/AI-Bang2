# Decisions / ADR

2026-10-15 ADR-SEMANTIC-WORKSPACE-01：采用用户本轮 goal-objective.md 明确方向，在 0d5be30 独立候选复用 sectioned-synthesis 与原生前端，移除常驻侧栏、顶部 Workspace/Recent answers、英文业务题卡、原文折叠及响应式引用抽屉。保留独立问答、严格 JSON/独立复审/全部授权及版本边界。普通本地可逆实现、文档、测试、隔离预览已授权；不新增源写、scope、付费服务、生产重启切换、push/merge 或上传提交。历史一次性 grant 结束及人工额度不可转用；真实验证前核当前 AUTH/readiness/账本。Embedding 首轮投入上限两小时本地诊断与可行性准备，只有真实可重复收益且无安全回归才纳入默认；无 provider/下载等授权则记录条件缺口。候选不改生产，可直接弃用独立 worktree 回退。

2026-10-15 AUTH-MAIN-CLOSEOUT：用户明确“先合并到main”，授权本轮修复、测试与非秘密报告通过PR推送并合并到GitHub main，之后继续前端／项目亮点／候选题问答／开发细节。执行前fetch核对远端、干净源码验证及新增历史blob凭据扫描；保留原main脏证据、私有运行态及队友工作。此授权不包含生产切换、源端写入、上传私有证据或比赛提交。

2026-10-15 ADR-CLOSEOUT-05：10cc970单次四源诊断生成/审查均通过，当前四源原文均amber、引用正确，2调用/USD0.003454，新unknown0。当前JSON语法与重复键均合法，原json故障未复现，不将单次成功视为根因修复或稳定性证明；无证据不修改解析规则，不花剩余6次重复挑成功。本轮只记录真实通过与开放风险，不改业务代码、不部署，77定向离线通过。

2026-10-15 AUTH-JSON-DIAGNOSIS：用户在要求继续后明确“没事，额度都满足你，不用担心”。据此继续诊断和修复所需真实模型调用，不再逐次询问；本轮自限独立最多8次调用/USD1，仍在原USD20全局账本内，使用sectioned-json-diagnostic-20261015-8新grant，不使用人工额度。旧unknown不重置，新unknown即停；只读现有合成源，不扩scope、不切换生产或推送。固定10cc970先获得可区分语法/重复键的实际响应；私有传输包装仅记录固定结构枚举和有界位置，不保存草稿、不修改模型响应。每次付费验证需服务定位或具体修复决策，不刷成功记录。

2026-10-15 ADR-CLOSEOUT-04：e1b032f两题真实复验止于3次调用；冲突题通过，四源题新json阶段拒绝保持P1，不用剩余1次付费重试。没有被拒草稿，不能猜测语法或重复字段原因；仅补固定json_syntax/json_duplicate_field枚举，保留严格解析和重复键拒绝，26定向/763完整通过。该诊断补充未真实模型复验，试验仍归属e1b032f；生产不切换，原始证据私有。

2026-10-15 AUTH-SECTIONED-REVALIDATION：用户对两题复验计划回复“都批准”。批准固定候选e1b032f独立最多4次DeepSeek调用/USD0.50保守上限，每题一次、不自动重试、不占人工额度、新unknown即停；使用现有四源已授权合成资料，只读真实API。新grant为sectioned-revalidation-20261015-4，保留原USD20全局账本和两笔旧unknown。按计划在隔离本机服务执行，不包含生产切换、推送／合并、上传私有证据或比赛提交。已冻结不可变发布、备份账本并核对官方当日费率；实际结果另记，不预填通过。

2026-10-15 ADR-CLOSEOUT-03：用户要求继续修复剩余缺陷。本轮改变分题生成内部传输格式，按分题嵌套断言，服务端确定性派生claim_indices及evidence_ids，对外／历史／审计契约不变；旧格式严格兼容，不混用。独立审查发现的继承提示字段冲突已修复。受限诊断只记录固定字段原因及有界索引，不存被拒草稿。762项/14DOM/25组本地验证通过；历史真实模型失败保持开放，禁止用作者模拟输出回放冒充修复后的真实模型通过。前次明确禁止自动付费重试；新两题最多4调用/USD0.50复验计划独立待授权，不使用旧余额或人工额度、不切换生产。

2026-10-15 ADR-CLOSEOUT-02：独立真实验收停止于已计划的8个案例/10次实际调用；保持两笔新生成拒绝，不用剩余2调用重复挑成功。原始零调用配置/429失败与更正测试器后的结果分列。Chrome揭示public匿名静态GET误被cross-site全局拒绝；f2f0633仅允许精确Host下三固定GET资源，API/POST鉴权不变；新红灯、原HTTP9项及758完整通过，独立审查后同域切换。真实模型仍归属498239e，最终静态入口补丁不重跑付费问题。CLI Cloudflare1010保留，未改规则；实际Chrome登录页已显示live角色模式，认证后browser/真人G1G2仍not_run。



2026-10-15 AUTH-CLOSEOUT-LIVE：用户明确选择“批准切换及独立真实验收”。批准候选498239e精确账本迁移（保留两笔旧unknown）、现有49161/同一域名切换、仅三个演示账号精确revision/payment-service的应用审计员，以及独立自动DeepSeek最多12实际调用、新增保守上限USD0.50；不占人工USD1，新增unknown即停，不自动付费重试。不扩源scope/源端写入、凭据/私有证据上传、push/main合并或比赛提交。旧36次/USD1验收属历史，不与本轮12次/USD0.50叠加扩额。



2026-10-15 ADR-CLOSEOUT-01：用户在系统审查后明确“可以，按后续顺序完成”。仅在独立修复分支实施，旧main证据/服务保留。先red复现再最小修复及回归；费用隔离不弱化账户new unknown停止；迁移以明确外部17笔settled回执和不可变计划为依据，不自动放弃历史费用/unknown；拒绝草稿不作为答案，原文转显式引用检查；审计员仅显式精确viewer/revision及payment-service，不能获取源身份。固定构建复用原私有state-root，静态UI与后端启动配对；无新收费授权、push/main合并/源写/提交扩展。候选757本地/14DOM/25组通过；真实模型、迁移/切换及实际线上审计身份分列待办。



2026-10-15 ADR-PD-09：用户明确要求推送优化到远程供队友切换测试，因此提交本会话已实现/验证的源代码、测试、合成题集及非秘密文档证据到pd。只进行非强制推送，不合并main、不部署、不上传.runtime或私有工具证明。旧报告hash与committed/pushed字段保留测试时事实；交接使用实际远程commit。远程若出现队友提交，不覆盖，先核对并安全整合。

2026-10-14 ADR-PD-08：用户要求完成剩余优化。本轮独立ScenarioLab只创建自己的内存Store/FixtureWorld，固定四步操作没有任意资料/身份参数，CSRF/Host/Origin保护，员工server无管理路由，不能接live配置。模拟版本直接发布与实时撤权只说明既有Engine保护，非native worker SLA。操作员实验记录保留已合法观察内容并明确不同于员工History；失败停止且可导出，重新启动清空临时状态。8类安全挑战走实际后台边界，fake模型仍不能证明语义注入抵抗；初次夹带指令测试因同版本未发布而失败，改为实际发布version2后确认到达模型，再验受限关联拒绝，保留原失败。审计时间线只汇总原权限范围内已加载事件，不新增审计API或下载员工答案，原始事件不变。提交材料描述最新pd能力及旧运行模式差异，原图文归档；私有原始工具证明15项缺失须真实交接，不制作替代品。无新模型费用/原生写/线上切换/上传/提交/推送；回滚可不启动lab并撤销timeline展示，既有运行模式保留。

2026-10-14 ADR-PD-07：用户同意检索补漏，先通过实际Engine记录模型输入必要证据；不以资料存在或作者参考命中代替检索结果。发现中文被原正则丢弃、postmortem与incident未关联，以有限静态双语词表和单个别名修复，不新增embedding/翻译模型、外部调用或更改证据预算。词表仅影响候选匹配及排名，不授予权限，不改原文/定位/当前源鉴权；不推断状态或自动生成事实。代码完成题原要求C-02过严，J-02原文已充分说明Done不等于发布，故修正最小依据及参考后重新测基线，报告同一题集11/18→18/18；原始9/18保留，不混比。词表是已知业务词汇匹配，不是通用中文支持，下一阶段用未见改写/更大干扰语料另评；不将必要召回率当作精确率或语义正确率。回滚仅撤销retrieval词表/别名；本轮无UI或在线服务切换。

2026-10-14 ADR-PD-06：用户同意进一步优化，本轮先落实固定难题集与前提/冲突处理，不引入新模型、代理或数据库。沿用分题claims/supports格式，将前提纠正与冲突限定写入有引用的既有结论；复审在parts_supported之外必须明确返回premise_handled/conflicts_handled=true，否则拒绝草稿，仍有证据时两次调用而非增加第三次。普通是非问句不是错误断言，缺批准不是拒绝，未记录不是不存在；相同实体/事项/范围/有效时间才比较冲突，只有显式撤回/取代能解释解决，平台名/更新时间不充当权威。12题使用显式允许的合成证据，检索和原生权限另测，不向模型提供rubric或参考答案。离线工具仅验形状/精确引文，实际回答与作者参考分列，语义保持not_run，所有失败和旧输出保留。回滚为选择原answer-style；复审仍可能误判，真实质量/费用不从模拟结果推断。

2026-10-14 ADR-PD-05：用户接受S-01下一步优化。以可选--answer-style sectioned-synthesis新增逐子问题输出，不更改默认或既有实例。复用既有精确quote核对、生成/复审独立预算收据及逐阶段授权；新增answer_parts包含原问题连续子串、supported/insufficient及claim_indices，每条结论恰归一处。第二次模型调用额外判断整个问题的分题/覆盖及不足声明，必须接受全部结论，不允许过滤后错误索引。无证据不调用；全不足但存在证据仍复审；任一拒绝按既有机制回退原文。模型审查可能出错，不声称确定性语义保证。已有合成资料边界不变，无新provider/原生写/费用。旧记录无分题字段兼容；新记录打开时重新鉴权及校验映射。回滚方式是选择旧answer-style；两次调用的真实费用、时延和质量未测，不能直接替换现有单调用source-review。

2026-10-14 ADR-PD-04：按用户要求继续S-05优化。过程单仅在浏览器汇总既有Audit.inquire授权范围内已加载的事件，不增加查询接口、SQL或审计权限；按(actor,request_id)分组，稳定as_of合并分页，原始事件可逐条核对。summary的终态只描述已加载记录，缺失可能由分页/过滤产生；prepared不等于sent、stored不等于read、evidence_only不等于成功综答。资料多阶段allow/deny/unknown全部保留，未用最后一次allow抹掉拒绝。UI不声称验证签名；既有CodeBuddy离线工具只对导出副本做签名及篡改演练，原数据不改。前端文本均经textContent；无数据库迁移或密钥新增；回退只撤销过程单渲染/样式。

2026-10-14 ADR-PD-03：继续用户要求的五场景优化，第三轮针对S-02可解释新鲜度。复现worker已死但runtime显示current，改为同时验证线程存活/stop/完整状态/120秒有效期，查询端阈值提取共享常量，未延长时效或放宽权限。runtime仅提供当前有效源身份的同步状态/无对象时间元数据；last_check_at是尝试开始时间，last_successful_check_at是完整周期结束时间，UI不得混用。引用在现有鉴权/版本通过后附source_updated_at/indexed_at/checked_at；历史仍返回原保存回答，不将其时间冒充本次检查，打开preview才有本次检查时间。fixture明确非原生时效。无DB迁移/模型调用/新scope；回退本轮状态/UI字段即可，旧调用方可忽略新增字段。

2026-10-14 ADR-PD-02：用户要求继续优化并说明前后区别。本轮增加问题主题到完整证据区块的导航，复用已返回给该用户的claims/evidence，不重新检索、不增加模型调用。四类常见中英文关键词只作导航提示，不能宣称语义覆盖/事实总结；目录中的同一完整区块可以归属多个主题，原文不移动、截断或过滤。缺失匹配仅提示未识别，不等同资料不存在。失败原文、综合路径和不可用旧历史不显示导航；未知问法回退完整原答。8DOM、1fixture HTTP与IAB点击/聚焦验证通过。回滚仅移除导航函数/调用和CSS；未改服务端契约、身份/费用或数据库。

2026-10-14 ADR-PD-01：用户要求在pd按五场景优先级修改，后选择原团队测试环境；配置待队友交接。本轮仅本地可逆实现与验证。Jira/Slack内容指纹变化和CF/Drive数字版本变化共用既有一次模型前恢复；重新读取当前权限，拒绝/unknown不掩盖，版本不前进/持续变化拒绝，模型调用后不重试。复现8项中的2项error，修复后8项通过；四源后台连续两轮和错误身份/撤权矩阵另测。UI仅相邻相同证据归组，不重排、不省略、不引入未验证结论。保留原provider/费用/身份/审计边界；不继承历史已消耗的原生写入授权或人工专用模型额度。新增统一离线验收命令，输出目录必须不存在，失败也持久化。回退为撤回本轮engine/UI小改；无DB迁移。完整675项与8DOM通过，原生时效、员工身份及真人G1/G2待办。

2026-10-14 用户明确授权合并 GitHub main：候选 d64084e 已在独立检出验证666项40.356秒、7前端DOM及无凭据本地启动；509个待发布blob敏感模式/当前密码扫描无命中。仅提交代码、文档与非秘密证据，原本机运行状态保持；验证记录 reviews/2026-10-14-main-merge/VALIDATION.md。

2026-10-13 已上线 contextledger.hellokyleshi.com：用户远程不便明确委托代理确认，采用代理HTTP/API验收例外，不称真人G1/G2。三账号公网登录、安全cookie/Origin/跨账号拒绝通过；公网Blair问答8.855s四源accepted，Jordan仅授权能力页evidence_only。修复Drive仅启动刷新token导致约一小时失效，37专项/666完整通过；长期一小时自然续期尚未观察。用户级LaunchAgent app+tunnel与caffeinate运行；新增启动/停止命令。人工额度余额USD0.997920，本轮3次问答，无新unknown。浏览器公网被工具拦截未绕过；详见 reviews/2026-10-13-hosted-demo/README.md。

2026-10-13 本机域名部署准备：用户批准电脑托管和组员真实四源试用；专用 Cloudflare Tunnel 与 contextledger.hellokyleshi.com DNS 已创建，ingress 校验通过；未启动隧道、未开放公网。项目级 cloudflared 2026.10.0 哈希核验通过；新增入口公共域名兼容，6入口/9账号HTTP测试通过。G1真人安全查看尚待确认，不能以自动测试代替；现有本地服务保留，无新增模型调用。具体切换及人工查看步骤见 REVIEWER_DEPLOYMENT。

2026-10-13 命名最终确认：用户要求恢复最初的 ContextLedger。页面品牌、标题与最终交接标题已恢复；拟部署子域名统一 contextledger.hellokyleshi.com。Aveniq 与 TeamLens 系列不采用；历史讨论记录保留。域名尚未上线。

2026-10-13 品牌命名更新：用户否定 ContextLedger 并要求更高级的名字；采用自造名称 Aveniq，拟用 aveniq.hellokyleshi.com。当前页面标题、品牌及交接标题已更新，历史证据/归档仍保留原名。未进行商标或同名排查。域名授权页面已打开，尚未创建隧道或 DNS 路由，未上线；项目私有目录已准备并校验 cloudflared 2026.10.0。

2026-10-13 连接展示名称：按用户要求，将私密账号卡片中的 Native connection: eng_b 改为 Knowledge connection: Team Knowledge Connection (team_knowledge)，交接与接入说明同步。此为展示别名；底层授权、凭据映射和历史审计的 eng_b 兼容标识保留，不冒充已新建平台服务账号。仅文案更新，无服务重启、源请求或模型调用。

2026-10-13 演示人物命名：按用户要求将登录名改为 engineer_blair / product_morgan / partner_jordan，显示 Blair / Morgan / Jordan 及岗位；明确权限按具体账号配置，岗位不代表所有员工权限。内部账号键、revision、密码与权限不变，历史连续；9项账号HTTP测试、6项应用权限测试和前端登录DOM通过。自有49161已重启加载新源码，3个新登录名实测通过；未提交模型问答。历史冻结源码包保留，尚未包含本次命名增量。证据：reviews/2026-10-13-application-roles/personal-login-check.json。

2026-10-13 三角色真实四源版已切换：engineer/product/partner应用账号均可登录，共用获批eng_b原生连接并分别施加工程/产品5资源/外协1资源白名单。源码b6f2ffbadef0；四源当前可用，4项原生读取通过，三个账号登录与运行状态通过。新包378文件独立解压661项39.447s通过，7个前端DOM通过；本轮未自动提交live模型问答，人工USD1余额未使用，旧55调用/两笔unknown保留。实际角色真人问答/浏览器G1G2、公网部署和提交仍待完成；这是已批准的应用角色演示，不是三个原生员工权限矩阵。当前入口FINAL_HANDOFF/REVIEWER_ACCESS。

2026-10-13 应用角色范围获批：用户明确回复“接受，用应用演示角色＋真实四源，清楚标注边界”。工程/产品/外部协作方使用独立应用账号，共用已批准eng_b源连接，在原生权限内施加精确资源白名单；不冒充三个原生员工身份。已加入请求级权限上下文，覆盖检索、授权/模型发送、最终返回、历史与预览，并记录双身份/策略摘要。人工USD1不供自动模型测试；不新增scope、provider、外部写或公开服务。原多原生身份缺口不再作为本轮应用角色交付的前置条件。

2026-10-13 团队/评委账号增量：用户批准本机人工试用取消次数上限、新增USD1，自动验收不使用；并选定固定账号密码按身份演示。新增服务端账号映射、scrypt密码、到期/撤销/会话revision、账号历史/引用隔离、关联有效源身份审计、HTTPS Origin/Secure Cookie配置；均不提权。654完整本地35.911s通过，另5项入口检查及7个前端DOM套件通过；三fixture角色真实HTTP问答通过。自有49161核闲/备份后更新，工程账号登录、人工余额USD1和四源complete/current已验，无新增live模型调用。原Goal55调用/USD0.062807及原2unknown保留，旧冻结包不改。真实四源仅eng_b完整；product/partner暂仅fixture，新增原生角色需要团队授权。当前准备的是新增账号版本，不等于公网部署或G1/G2。入口REVIEWER_ACCESS，部署缺口REVIEWER_DEPLOYMENT。

2026-10-13 最终交付准备完成，最终待签核：用户在听取“原文正确但可能不主动解释错误前提”的具体示例后回复“可以”，明确接受该项比赛原型交付例外；不代表功能已修复、G1/G2通过或外部提交授权。其余可自主完成的开发、集成、验证与材料准备已收口。当前服务归属/健康、355文件源码包hash/CRC及原账本再次核验通过：52调用/USD0.060992/new unknown0，原2笔保留，剩余8次。无新增模型调用、重启、push/merge/上传。源码包保留冻结内容；最新质量接受记录见FINAL_HANDOFF及COMPLETION_AUDIT，包内较早pending记录为历史。

2026-10-13 最终完整性审计：原打包主文档缺DEV09非秘密manifest链接，已补入最终包（355文件、sha b466d6ca971b），旧已测包私下保留。所有旧包内容逐字节沿用，未改代码/测试/数据；ZIP CRC、内部hash与四份主文档相对链接通过，不为仅添manifest重复642测试。逐条Goal审计见COMPLETION_AUDIT：技术包就绪，但前提解释要求仍未满足，等待已发用户例外决定；无答复不算同意。本轮无模型调用，服务归属健康检查通过，未重启/外部写/标完成。

2026-10-13 ADR099 / 最终封版：已备份并确认原39081空闲退出，仅重启自有49161；最终source09f67454ef93，structured/none8192/single/pooled4/batch/serial，实验不启用。642本地31.131s通过；最终原生Q1/Q2=13.263/9.597s，三请求9.136/22.107/28.638s，5次核心事实通过、queued状态实见。History1.893s/preview0.749s原文一致且0模型；28602事件本地链有效、非独立签名。累计52调用/USD0.060992/new unknown0/原2保留。最终源码包354文件已独立解压642项30.084s通过，首次漏历史测试资料导致6errors的失败日志保留并修正；配置/演示/提交材料已对齐。前提解释仍未满足原要求，已集中询问是否接受交付例外；browser/G1/G2及外部动作未完成，Goal保持active而非完成。入口：[FINAL_HANDOFF](FINAL_HANDOFF.md)。

2026-10-13 ADR098 / 前提解释有界诊断：新增可选explained单review严格enum＋已选证据别名契约，642完整本地30.947s通过。四次fixture源＋live模型诊断已耗尽专项4调用：v1正确区分撤回/拒绝但误把中性GA问句当断言；v2修正中性问句却遗漏03前提解释，均不采用，保留失败和冻结manifest。最终配置仍structured/serial，事实原文保留但前提纠正措辞仍为待签核限制，不宣称已修复。预算真实核47调用/USD0.057982/new unknown0，原2unknown保留；无native/浏览器调用/重启。架构SVG已更新none及实测范围并渲染检查，封面1600×900已目视检查。

2026-10-13 ADR097 / 最终收口：HTTP合法query在等待原查询锁前创建session run，使queued阶段及elapsed可被刷新读取；原request/store锁仍覆盖refresh、模型、最终审计及响应发送，排队后重验session防退出后调用。非法字段/CSRF不创建run，同session409保持。新增3真实loopback测试通过，隔离路径14项通过，完整635项31.837s及6前端DOM通过；均本地fixture/mock，不是browser/native。未重启49161/新增费用，原structured-v2运行不变。

2026-10-13 最终交付Goal接续：用户取消3秒硬门槛，目标改为可演示/可交接/可提交的最终待签核版本。选定structured/none8192/single/pooled4/history batch/window structured及serial查询，isolated3仅保留实验不启用。真实账本核43调用/USD0.056704/new unknown0/原2保留，剩余17在独立CLOSEOUT_PLAN重分配，旧PLAN不改。15份CodeBuddy证据哈希全匹配；SUBMISSION_CANDIDATE与DEMO_CANDIDATE已更新旧配置及过期耗时，原文归档保留。产品排队可见性、前提解释、最终封版/浏览器与材料核验仍in_progress，未宣称完成；本轮无API/模型调用、重启或外部写。入口：[最终交付清单](reviews/2026-10-13-final-delivery/README.md)。

2026-10-13 AUTH036 / ADR096：isolated3可选请求隔离接入HTTP/试用启动器，默认serial；每请求独立Engine/证据快照，发布代次防ABA，模型发送与最终响应保留发布屏障，SQLite读取补锁。630完整回归29.109s通过；追加版本恢复/失效源专项10项0.132s通过。初始三并发503真实失败保留：完整上下文每调用预留>USD0.30，USD0.50上限不能容纳多路模型在途；拆分HTTP隔离证明与额度拒绝证明，未缩减预留或扩授权。下一项安全模型阶段排队/可证明预留上界，未启用live。49161未重启，仍43实际调用/USD0.056704/new unknown0；3秒目标未达，详见[REQUEST_ISOLATION](reviews/2026-10-13-query-goal/REQUEST_ISOLATION.md)。

2026-10-13 AUTH036 / ADR095：新增未接线的ConcurrentPerformanceAdmission/ConcurrentGoalLedger，原账本事务内原子检查调用名额与结算＋in-flight上界，短文件锁不包住网络；进程owner lease＋请求所有权区分在途/unknown，query退出或进程崩溃保留预留并停新调用，已派发仍记录真实回执。7专项含三线程、额度竞争、prepared停派发、真实子进程强退及原模型类集成通过；完整618项26.223s通过。仅本地，HTTP/store串行锁仍在，当前49161冻结v2未改；Goal仍43调用/USD0.056704/new unknown0。下一项请求状态隔离＋最终发布代次检查后统一接线，不能据此宣称并发或3秒达标。见query-goal/CONCURRENT_ADMISSION.md。

2026-10-13 AUTH036 / ADR094：继续并发前置安全修复，authority.state_lock与pilot.lock统一；完整native read前复制资源/映射，回写前对比当前版本/正文/定位/tenant/active，变化返回unknown且保留新发布，避免未来缩小外锁后旧响应回滚状态。未移除HTTP/store/Goal整查询锁，非已支持并发。离线两线程负对照7个预期失败；保护后2项、完整611项26.878s通过。运行实例仍冻结structured-v2（365b5decf187），本次代码未加载；43调用/USD0.056704、新unknown0，无新费用/源写/重启。下一步请求隔离和原子预算预留；3秒/浏览器/G1/G2仍未完成。证据query-goal/CONCURRENCY_SAFETY.md。

2026-10-13 ADR093 / AUTH036：结构窗口以新s1 ID保留原文及标题偏移、表格/列表/相邻限定，旧窗口解析与History兼容；逐字引文按自然边界分段，不改模型提示词/权限/审计/预算。依据whole-v1 business_16实测缺陷，v2已见开发对照修复，非盲测。固定原生12题事实通过但完整3秒0/12，全局request/store与admission跨查询串行是三并发排队证据；不可直接删除锁或缓存allow。保持v2冻结与旧失败，停止相同候选收费重复，下一项先做隔离/阶段等价性本地审查。43模型/USD0.056704、新unknown0，最终native额度已用；详情STRUCTURED_WINDOWS_CONTRACT与VALIDATION_STRUCTURED_V2。

2026-10-13 ADR092 / AUTH036：whole源审查契约将逐claim布尔列表改为完整段落别名选择＋selection_safe/question_covered，严格未知/重复别名、字段集合、两个true及必要操作段落；服务器逐字重构和parse复核，不生成或修复事实，保留原审查语义义务及旧模型解析器。精确类加入single出口白名单，其本地构造不外发，review/final仍重新鉴权。原生三题8.842/7.553/6.388s事实通过；冻结v1后12开发案例机械通过但business_16冗长断句是质量缺陷，不据此称完成。新candidate改结构须另记已见对照，不改冻结PLAN/失败原件。21调用/USD0.046237、新unknown0；浏览器工具ERR_BLOCKED_BY_CLIENT不绕过，仍无3秒/稳定性/G1/G2证明。回退对应covered/legacy已记录启动配置，账本历史不变。

2026-10-13 ADR091 / AUTH036：新增opt-in四路完整原生读取与History批量本次鉴权。保留原生身份/正文/版本/子资源检查，无跨请求或跨阶段缓存allow；每批最多4、join后接纳下一批，unknown停止，HTTPS同上限。History按不可变资源去重本次读，窗口和当前存储版本先验证，全部权限/版本通过后保留原引文校验再返回原record，失败仍generic unavailable。默认serial，回退并发2/history serial不重置账本和历史。Drive热读取3.644→1.994s、同Q2History9.392→1.968s；分别仍12/25HTTP，0模型/费用；不冒称新问答3秒。578完整本地通过，证据query-goal/FOUR_READS_HISTORY.md。当前Goal8模型/USD0.040951、新unknown0；无新依赖、source写、scope、push/merge。

2026-10-13 ADR090 / AUTH036：引入默认关闭的compact/covered模型输入及single源审查派发。compact只去除重复发送，不丢原文；covered为通用主题与操作结构的狭窄遗漏拒绝，保留必要段落完整文本，强制支持/覆盖/过滤完整性，不修复被拒绝输出，不能当通用业务oracle。single仅三个明确代码类；source_claims无外发，完整selected的review_dispatch在其之后，故省去构造前model_dispatch，保留before_model/最终/历史/引用检查；旧双调用禁用，默认legacy。50相关/564完整本地通过，首轮失败保留，审计valid断言加强后22通过；契约SINGLE_REVIEW_CONTRACT.md。当前真实Q1 54.732s/Q2 40.595s事实核对通过但慢，none两次Q1仍失败；不据局部原生请求116→88/102→77称整体优化完成。配置回退legacy输入/legacy派发/low，网络另可legacy/1，不回退账本历史。当前8模型/USD0.040951、新unknown0；最终验收未运行，继续已授权本地等价协议与覆盖设计，不盲目重复prompt测试。

2026-10-13 ADR089 执行补充：真实Q2同正文由42.049→26.025s，四轮鉴权23.360→14.617s；模型自身17.860→10.666s波动单列。当前pooled/2/low8192仅一题native/model通过，非最终稳定候选。基线Q1 76.186s以8192reasoning耗尽失败，不增加cap、不隐去失败、不将evidence_only算答案。GoalLedger类型不兼容导致首次无模型停答，已真实类路径复现并委托同一BudgetLedger修复，保留原类型要求及计时；未知内部异常分类internal_service_unavailable，不暴露内部文本。最终528本地通过；5提交/4模型/USD0.023922、新unknown0。Drive原授权已由本人恢复。其余三秒/覆盖/稳定性要求继续，不据局部提速宣布Goal完成。

2026-10-13 ADR089 / AUTH036 网络候选：仅连接生命周期复用，不缓存正文/ACL、不合并检查。每源HTTPS池上限2、idle15秒、origin/凭据隔离、完整成功读取才归还；TLS/no redirect/no retry保持，代理沿用原urllib，不直接绕过。独立opt-in每源完整read并发2、成对join、unknown后剩余记not-attempted，已在途可完成；只在正常bounded discovery上下文生效，全部join后按输入顺序更新，默认1回退。启动器要求并发2配有界池。代码/失败/测试/单源真实比较见query-goal；收益当前只证明四次同正文Confluence样本，未证明完整问答提速。成本无新依赖/模型调用；回退legacy/1且保留账本历史。Drive刷新400阻断后用户明确选择“现在方便，请打开原授权登录入口”，仅恢复原账号与原drive.readonly，验证身份后替换同一Keychain项；入口已打开，真实恢复状态待回调。不是新scope/新账号/业务源写入授权。

2026-10-13 AUTH036 / 查询优化Goal：用户已将完整优化目标设置为active Goal，授权本地可逆开发及既有合成四源只读验证；核自有49161归属/空闲、备份后可加载/重启，不动8094/8100。新Goal最多60次实际模型调用、累计新增结算≤USD0.50、原USD20共享账本剩余额度约束，新unknown停接纳；独立Goal基线/计数，不重置任何旧admission/unknown。计划docs/reviews/2026-10-13-query-goal/PLAN.json冻结6基线/12诊断/36最终/6保留，按actual calls计；基线source-review low8192/none排名/旧urllib及后台正常。当前49161无listener，旧三admission/答案库/账本/entry控制共六产物已私有备份；账本原有2dispatched未知保留，不冒称本Goal造成。新增接纳类在每次reserve前复查实际calls/newunknown/成本及保守reservation余量，旧双调用不能越过上限；5专项/40相关通过，完整本地回归运行中。今日官方price实读仍Flash peak input0.30/output1.20 USD/M，PRICE_DATE更新10-13；运行基线/live/browser仍待实际结果。本授权不扩provider/embedding出口/依赖安装、源写、scope/账号、公开部署、push/merge/披露/提交，不自动代替G1/G2。

2026-10-13 ADR088 / DEV-PERF-REVIEW-03：用户要求逐环节重新分析并争取完整答案≤3秒，后续确认不是首字/仅检索时间；同学权限条件未知。本轮进行无费用研究/离线分析，不扩模型/provider/费用、实例更新或外部操作。历史192/208次native HTTP与33/37秒授权wall，加本轮1048对象CPU23ms及完整fake190ms，支持先处理重复网络/连接复用和模型覆盖，再做结构切块/混合召回。AOCI-CODE已读官方README/对比并固定上游7586820，定位开发Agent代码认知而非四源员工RAG。报告docs/reviews/2026-10-13-query-optimization；连接池、阶段内去重、single response、来源内并发、紧凑模型输入和阶段重排均为候选，尚未实现/验证/上线。保留ADR087、八类变化阻断、旧双调用、权限/审计/预算；下一项优先本地连接复用，无新依赖。3秒设计预算不是SLA，不以快速空答/evidence_only/timeout代替成功，阶段合并须等价证明。未改runtime/重启/新native/model/发布，G1/G2不变。

2026-10-13 ADR087 / DEV-SR-TIMING-02：用户明确同意上一轮“实现受限计时”，仅在独立本地分支实现默认off、操作员启动--timing-dir启用的私有诊断。复用Measurements/TimedNativeTransport，ContextVar按请求及阶段传播，span有界且只存白名单；真实请求出口、来源串行lane与ledger/锁不改语义。初始ObservedLock失败证明必须保留__enter__/__exit__而非假定acquire/release；已用ExitStack保留原协议、抑制异常和锁顺序。诊断完整写入后发布，clock/sink故障不改变业务返回、不重试模型。12专项/502最终整合通过，保留所有初始失败/历史误接受；原证据9文件不动。成本无新依赖/付费调用，回退为省略--timing-dir；没有计时HTTP接口、公开上传、trial重启或native性能验证。此决定不合并任何鉴权阶段，不改变provider/cap/价格日期/原unknown、也不扩大G1/G2或发布授权。

2026-10-13 DEV-SR-CONTRACT-01 审查决定：用户在架构诊断后明确“可以”，落实本地契约审查、计时设计及三份首题固定反例，独立review/source-review-contract-20261013、基准1649e30；不扩大付费/来源/实例/发布授权。检查名称相邻不代表安全等价：原文构造期四类变化由review_dispatch阻断，模拟模型后四类变化由before_dispatch阻断。保持所有现有检查；专用单review出口合并只为未实现候选，须证明输入/版本/权限/审计/账本及旧双调用兼容。既有Measurements实际已存在，本轮设计复用而非声称缺失；完整计时接入尚未开始。新增测试离线重放v2 accepted但漏C01，明确parser通过不等于业务覆盖；原始9份response/result/audit hash固定，不改失败或推断未记录模型理由。5专项/56相关本地通过，无runtime改动或真实调用；审查证据docs/reviews/2026-10-13-source-review-dispatch。

2026-10-11 ADR086 / AUTH035延续：用户明确“继续不要停”，同provider/原资料/成本基线下定向推进。v2 disabled原Q1 6338c118 review accepted但漏C01，记业务失败，不据accepted宣称修复；停止同类prompt叠加，采用原可用low推理作为单review回退，cap8192不变，不配置题集对比。新增--review-reasoning-effort仅none/low，low仅human source-review，旧none仍默认回退；19定向通过。实际启动后四源complete/current再调用：Q1 18a99f38 66.140s含timeout budget与批准failover procedure及顺序未知；Q2 cf6fd9c6 40.371s三部分完整；范围ba11fb5b 44.174s未扩pilot为GA，一题一次。原失败全部保留，非稳定率/真人验收。Q1 History/C01preview当前HTTP相同正文通过、0模型；新失败刷新被旧成功答案盖住的问题由整合回归发现并修复，相关HTTP/三Node通过，首轮full失败保留，修复后485完整本地25.091s通过。当前9提交/8调用、24688microUSD、新unknown无，旧账本/unknown不重置；G1/G2与录像仍团队执行。

ADR085执行补充：按用户充分授权加载v2并进行一次原Q1验证，aac7a2fa真实retrieval/source_unconfirmed停止、0模型调用，未评价review质量；49本地只证明契约未放松。入口health与price readiness不等于startup来源全部就绪，后续付费验证须检查实际source状态；旧失败保留、不即时自动重提。当前5提交/4调用、新结算5216microUSD、newunknown无。

2026-10-11 ADR085 / AUTH035：用户在定向调用授权提示后明确充分授权，执行一次原首题6cc1cb6b、同provider/disabled8192/原合成资料/保留USD0.10基线与新unknown停止；不恢复42题/全配置。29.630s evidence_only失败，一review调用1374microUSD结算，新累计4提交/4调用/5216microUSD、新unknown无。新增索引诊断与实际派发证据离线重建逐字吻合：C01为index2、supported=true但responsive=false，整体coverage=false；不推断未记录的模型理由。新增专用于source-review的精简SourcePassageReview/v2，替代继承的综合system要求，明确含请求操作的原文不能仅因标签/背景而整体不相关；仍要求支持、审批/完成差异、具体措施、范围、未知顺序和过滤独立完整性，parser/权限/版本/回执不变。旧ExcerptReview及综合/selector作为回退保留；49定向本地回归通过，新候选未加载、live未验证，不称首题已修复。

2026-10-11 ADR084：原首题review失败只保存布尔数组、未保留claim index，不能据数组位置定位被过滤片段。新增有界整数index（0–51、排除bool/字符串/越界）及filtered_answer_complete严格布尔诊断；它们是未可信的模型返回元数据，不是授权或验收结论。parse_output的唯一索引、支持、问题覆盖及过滤完整性条件全部不变，不保存自由文本理由/原始输出，不改prompt、不补造旧失败解释。37相关离线回归通过；当前49161仍运行旧加载版本，本增量待下一次授权空闲更新，未新增在线调用。

2026-10-11 ADR083 / AUTH034：用户明确要求不限制真人查询次数，取消真人提交次数及相应总模型调用次数上限；仍仅当前单review/同provider/disabled8192/原合成资料，无自动付费问答。human-open-admission从AUTH033复制其既有2次计数/2次调用、原费用基线和原pending IDs；旧12次state及2次state原字节保留，不重新获得USD0.10预算，已结算2608microUSD计入该阈值，新unknown继续停接纳。旧有限模式保留为回退。真人Q2成功且审查accepted，Q1仍failed。返回Workspace计时bug已Node复现：terminal run被当作running启动elapsed；改为仅running启动计时，terminal只重新鉴权读取saved result，History选中引用优先于另一terminal run。保留真正刷新接续、view/session迟到保护及当前权限检查，不增加模型重试。

ADR082执行补充（2026-10-11）：真人原Q1 source-review失败，全9授权原文含C01送审且各supported=true，但整体question_covered=false。保留失败/真实回执/原文接续，不把失败当完成；不声称具体review理由，因为只记录布尔值无index/解释。stop/129输出tokens非截断，新增1374microUSD结算、新unknown无。原12次账本不动；新增2次已用1，余一仅原Q2真人，不追加同类提示词或自动重试。

2026-10-11 ADR082 / AUTH033：用户明确批准新增2次真人问答（原首题、原第二题）、最多2次同DeepSeek调用、新增结算USD0.10或新unknown停接纳。同provider/disabled8192/原合成资料/USD20账本，不恢复自动测试。新human-retest-admission.json独立基线及0/2计数；旧trial-admission保持12/12原字节，旧失败/unknown/reservation保留。仅--human --human-retest --answer-style source-review可启动，双调用style和automatic拒绝；source-review每问一次且无付费重试，额外ledger调用达2同样停接纳。旧最后一次请求c6e284b9在prepare阶段request_stopped且无模型；当前Drive失败/unconfirmed快照与停止一致，底层原因未证实。空闲保存状态后更新自己的49161，刷新原生身份及来源；真实答案/G1/G2仍未完成。

2026-10-11 ADR081：根据ADR080两次同路径遗漏措施，停止模型选段提示词调整。新增opt-in `source-review`：代码将全部当前授权检索片段完整构造成连续原文claims，再用同DeepSeek一次review检查全部支持、范围、问题覆盖及安全过滤。不硬编码首题/C01，不改检索或权限；同一证据窗口保留所有已受支持片段，防止过滤掉末尾限定。使用新 `reviewed_source_v1` 契约，只允许精确原文及真实review回执，绝不伪造generation调用；旧综合/选段双调用契约与配置保留。当前原首题历史输入离线重放证明9份输入完整进入review、含C01；不证明当前native权限或live答案通过。剩一问仅真人，无自动提交、额度不扩大；核心答案仍未验证。

2026-10-11 ADR080：两次真人原首题实际进入reviewed-excerpts路径，均把pilot/release材料选成答案，却遗漏输入中已有授权C01操作；review明确question_covered=false，最终返回evidence_only。阻断有效，不能忽略coverage、把真实但不完整的选文算成功或推断是review误拒。不追加同类选择提示词，不后台占用最后一问；两次完整native结果及私有草稿hash保留，旧配置/失败不改。新路径Q2尚未执行，旧Q2成功不可继承。当前11/12、17/24calls，USD0.016143、旧unknown324404/newunknown无；余一仅真人，G1/G2/核心答案仍未完成。

2026-10-11 ADR079：保留十分钟一次性登录码及一小时会话，不靠拉长凭据期限解决本地入口过期。显式双击入口通过本机OS owner、私有文件权限、同runtime指纹和同loopback listener PID核验，向本任务进程SIGUSR1续签；服务端固定actor，既有session/run不变。无新HTTP管理接口/外部写入/模型调用。expired旧ticket仍拒绝；新ticket一次使用后拒绝；错实例/错listener/软链/宽权限文件不发送signal。空闲首次加载前保存原taskstate；真实续签HTTP及24项定向证明入口和会话连续性，不代表真人页面或业务质量通过。源ACL/version鉴权、预算和未知账本不改变。

2026-10-11 ADR077：仅用一项剩余后台额度诊断实际首题，未改问题/提示词/配置。已确认v13拒绝未知措辞“The latest … is not established in the accessible evidence”，原草稿也遗漏授权C01 runbook。未知措辞豁免仅限明确、分开的否定句；肯定latest及夹带肯定句仍阻断。旧失败不改成成功。私有诊断只保留有界可见claim字段、不保留reasoning、不显示草稿；调用价按当日官方pricing复核及readiness，旧unknown不变。

2026-10-11 ADR078：自由生成同路径两次无实质进展后，停止追加同类提示词。新增可回退的reviewed-excerpts技术路径：第一次模型只选择原文ID/连续quote（≤4、12–600字符），服务端构造text=quote的有支持claim；第二次模型独立审查支持、关键范围和问题覆盖，遗漏措施仍阻断，真实冗余仍须明确可过滤且完整。固定服务器说明不推断最新顺序，不替代缺失事实。两次当前授权、最终版本检查、History复查、审计/账本不变，同DeepSeek/disabled8192。与未验证失败接续区别显示Reviewed source answer；旧synthesis/excerpts配置保留。候选本地6专项通过，首次启动旧guard拒绝已修并回归；当前真人实例加载，但候选在线质量not_run，不继承旧Q2成绩，不宣布Q1或Goal完成。剩三次真人，后台问答停止。

2026-10-11 ADR076：阶段颜色反映服务端实际结果，而非仅到达过某阶段。正常推进保留前阶段完成；生成/审查拒绝标失败，证据接续只完成自己的最终鉴权检查；未执行审查标not_run。旧实例仅提供observed时明确结果未报告，不从phase列表推断成功，不伪造进度百分比。真人报告原首题综合失败；保留历史失败及当前试用session，不追加付费复验。新后端待安全实例更新，不能声称真人已验证修复。

ADR-075 · 2026-10-11 技术取舍：v13首题15.48秒在generation阻断，第二题26.00秒成功；不再追加相同提示词/全套实验。获批delivery operator显式启用证据接续：仅known-usage输出拒绝时，丢弃整份草稿，保留失败/调用审计，经正常final native权限/版本检查提供selected原文。显式answer_status=evidence_only及“synthesis blocked”UI；不声称综合答案成功或首题已完整解决。原文含C01措施且不推断最新顺序，不硬编码题目/内容。unknown/撤权/版本改变/预算/transport异常仍阻断，无付费重试。History与刷新以evidence_only终态取回，并再次当前鉴权；默认Engine不启用该选择。

ADR-074 · 2026-10-11：v12首题原生28.52秒HTTP200，但语义失败：将pilot approval称latest mitigation，遗漏C01；同模型review误放行，完整答案/审计保留。v13增加保守latest/newest断言的quote词项检查，明确顺序未知不代替支持的操作措施。历史综合答案读取也按当前确定性claim校验；旧失败原记录不删除，不把不可提供的旧答案当成功。此检查只是词项来源保护，不能证明语义排序；模型复核/人工仍必要。一次定向修正后仅原两题各一次；若首题仍无实质进展停止同类提示词叠加，其他交付继续。


2026-10-11 本轮独立交付任务已明确授权，覆盖旧阶段stop对继续开发的限制，但不恢复旧Goal额度或大规模测试流程。基准main b34a055；当前独立delivery/2026-10-11-demo-candidate。保留所有旧文件/失败；不动8094/8100，不写业务源，不push/merge/deploy。

ADR-072：采纳同DeepSeek Flash thinking disabled、cap8192；排名默认none，旧low8192及v11通过Git基准可回退。今日官方readiness已真实复核，价格未变；本地接线不等于live通过。新独立额度12问/24调用、自动≤9/真人≥3、新增结算USD1或新unknown停新提交，在途按原规则收尾；新state保留原ledger全部未知与reservation，旧Goal state只读。

ADR-073：简化generation/review为语义核心与服务器确定性验证。所有草稿结论仍须supported=true、当前权限/版本、真实ID/连续quote有效；unknown/unsupported整答阻断。supported但responsive=false可过滤，仅当复核明确filtered_answer_complete=true、非空其余结论独立且question_covered=true。过滤后的claims才交Engine再次校验；关键限定不可删除，未验证草稿不展示。此决定覆盖本轮整答拒绝冗余策略而不改写旧失败/ADR；同模型复核仍可能误判，G1不替代。首题保留原问题，需报告当前证据支持的批准措施及顺序未知；未通过前不宣布产品完成。

2026-10-10 阶段停止（用户明确指示）：开发Goal paused，停止继续测试/付费验证与模型候选推进；仅交付当前分支到GitHub并合并main。详见docs/reviews/2026-10-10-page-failure-stage-stop.md。135/138，Goal结算0.437330USD、旧unknown324404保留、新unknown无；idle49161/PID87323已停，临时入口token已移除，8094/8100不动。none8192与新增42次申请不获批准、不执行；Q1/最新真人UX未完成，不批准G1/G2。下一步由ChatGPT审查并决定，不能自动重启或继续付费测试。


2026-10-10 ADR070：同一获批质量进程消费共享额度会让旧instance仅内存public_status显示过期次数，实际gate仍安全。改为仅读原子trial-admission.json，读取异常退回缓存，不取query/flock/ledger锁、不触发四源；另一进程消费及flock占用对照20targeted/445full通过，只读审查无新增问题。human新实例加载，非源状态/current权限替代。

2026-10-10 ADR071（仅提议未批准）：新原题截断length/8192含reasoning7925，候选为同DeepSeek Flash thinking disabled / effort none / cap8192，使用既有可信构造支持，不增加provider/cap、quote/review/授权gate不变。官方thinking_mode/API文档本日实读支持disabled和none；预计减少reasoning输出/耗时费用但未经实测，可能降低综合与review判断质量，不保证消除两空或其他reject。non-thinking-proposed-schedule.json冻结原两题6＋原36；拟总138→180新增42，保留当前3human，原Goal累计0.50与旧unknown不重置（余0.06267USD），达到阈值停止并保留not_run。当前live low8192不变，待用户明确配置/额外次数批准。


2026-10-10 AUTH032实际42次完成：排序action-terms-v1/同DeepSeek low8192，固定native两题各3，Q2三次完整；Q1两空＋一次generation截断（length/completion8192/reasoning7925/visible894字符），不推广候选、不推断旧55.47秒finish_reason。质量core24=22事实＋2预期安全空；known12=01/06事实＋8合理空/澄清＋02review拒绝（stop、额外claim responsive=false）＋12预期注入Drive unknown模型前停答。引用preview3条、Recent列表、单条History HTTP200，非browser人验。445本地/6Node/只读复核通过；共享额度snapshot仅读原子state不等待query/flock/ledger或四源，当前待human实例加载。额度135/138、余3human；Goal累计437330microUSD，距原0.50仅62670，旧unknown324404保留、新unknown无。新的推荐可信配置none8192（同provider/cap、thinking disabled）仅提议，可能减token/时间但审查质量风险待完整验证，未启用或自动扩额；不自动通过Goal/G1/G2/AUTH019。


2026-10-10 AUTH032：用户“批准”，明确批准此前action-ranking候选及45次集中复验：总93→138，原两题各3次产品HTTP＋原24/known12质量36＋最多3human；49161/eng_b/AUTH017合成四源只读、原DeepSeekFlash/low8192/USD20账本与旧unknown保留。原Goal累计结算USD0.50（本次前0.320468USD）或新unknown停止接纳，在途收尾，不重置阈值。不得写源、动8094/8100、push/deploy或绕过browser拒绝。审批不证明质量，不批准G1/G2。


2026-10-10 ADR069：用户刷新看到operator link错误。旧实例06:01:30UTC启动，07:23UTC检查已约82分钟；session和cookie硬过期3600秒、ticket600秒，与症状相符，但未读取真人cookie或捕获其具体HTTP，不能断言唯一原因。boot以前所有异常统一归因ticket，现仅session403可尝试一次ticket，503/网络不消耗ticket；有效session优先且不会重复使用旧ticket。分别显示session到期/入口失效/服务暂不可达。用户恢复入口范围内仅重启自己49161旧PID54280，新PID66918/PTY35356/启动hash80d447c58738d9d1220c8d17d17f5cf75a9d6251aee7d5d54b2cebab91463002，查询candidate默认none，93/93、账本与原unknown保留；新后端ADR067额度状态已加载。private token0600，command --check通过；不执行浏览器工具、不提交问题、不动8094/8100。重启后原session内存终态不保留，成功答案仍需History当前权限检查；不声称恢复已过期session的失败记录。真人新入口观察pending。

2026-10-10 ADR068（本地默认关闭排序候选）：Q1原生请求69af1515dcfc4d109ea3180e0e454245的generation/review均接收同9条证据含C01，accepted claims未引用C01；排除仅传递引用子集，未保留原provider review原文，不推断模型内部原因。新增query_expansion=action-terms-v1，仅mitigation词触发procedure/workaround/safeguard/protective通用排序词，不改变原问题、主题过滤、当前权限、证据窗口/预算、模型low8192、quote/review。默认none，现有live仍none。历史合成索引离线C01排序3→1、主题候选集合不变；可能挤掉有限窗口内的限制性证据，真实业务覆盖/时间/费用尚未验证。原24+known12及两原题固定各3次均须重新验证，不能用排序或fake review通过替代。回滚query_expansion=none。离线444完整测试通过，uncited action传入review且mock coverage=false停答；只读审查通过。已备可选launcher/quality参数，次数白名单仍93，未执行候选live、未扩额。


2026-10-10 ADR067：93次是90后台验证＋3human，非USD20余额耗尽；goal settled0.320468USD/available18.583215USD/legacyunknown0.324404USD，新unknown无。新增查询在gate before engine/reservation/model停止，不增加attempts或费用；用户具体失败HTTP/rid尚未捕获，保留证据限制。前端显示trial暂停、禁用Ask、失败保留自己原题/rid/实际停止phase/固定elapsed，刷新恢复终态失败而非假装继续计时。runtime新增query_admission只读内存快照，actual gate仍每次持久计数/费用/unknown检查；503附当前session安全run，不草稿。已修复只读审查发现的候选constructor无锁save竞态：existing仅内存load，首次creation同flock重查，未加载问题候选到live。440本地/5Node/只读复核通过。当前不重启以保留用户session失败state，static UI已更新；新后端snapshot/503 metadata在下一次同获批49161启动加载，旧runtime仍可供前端恢复失败并暂停。不得自动扩额、模型重试或恢复旧unknown。

2026-10-10 ADR066：真人确认运行中刷新原题/计时及答案出现，Recent answers始终Checking current access，完成后刷新答案消失。最新6626397006424963ad09ff9e23ab8add已持久保存3claims。复现完成后的前端丢失关联：接续改为当前session terminal run重新safe_history；History选中答案仅在tab/sessionStorage保存rid及自己的问题，刷新无run时重新safe_history，不缓存正文、不模型重试，退出/过期清理；输入值guard保护慢runtime不覆盖新草稿。新增GET /api/history/recent只列actor自己的question/time/rid，无来源标题/数量/正文或源请求；点击单条才做当前权限/版本检查，失败内联，SourceUnavailable不把整个列表请求异常中止。旧History全部来源串行检查机制确认，旧具体HTTP耗时/异常不可恢复；新native HTTP summary0.0013075s、单条9.134388s并取回3claims。summary仍可能等待store锁，不宣称运行中完全免长锁。SessionRuns新增实际观察phases，前端突出current/observed/not reported，不推算百分比/阶段完成、不显示草稿。439本地、5Node、只读审查通过；真人最新修复/引用仍待观察，93/93停止新模型请求，G1/G2不自动通过。

2026-10-09 ADR065：真人刷新已恢复计时/阶段，但原问题不可见；实际浏览器存储丢失机制未确定，ADR064测试仅覆盖可用storage。本轮补充当前已验证session运行状态保留自身提交问题（<=4000字符、仅内存、退出discard），/api/runtime只返回该会话原问题，另一同身份session无run；不加入来源/草稿正文、不自动模型调用。进度区以textContent固定显示Submitted question，等待输入只读、快捷题不能改写；可用storage仍作辅助，无storage也恢复。保留当前权限History取回及所有迟到响应隔离；只读审查无新增发现。原不可见问题请求974047bc843a4144a7d785f1a4f8b32a已保存3事实，attempt92/93，真人最后1次复验待完成，不宣称G1/G2通过。

2026-10-09 ADR064（刷新接续本地与mock验证）：真人刷新运行中页面丢失问题/进度，重复提交409；原请求406c7185e46e44b2b14ce7fba5633978已42.403秒提交，不重复计费。前端按session.csrf在tab-local sessionStorage保存冻结的原问题/rid，刷新仅接续/runtime实际运行及真实elapsed；完成后一次带rid的History当前权限/version检查取回结果，失败恢复安全类别，不保存/显示draft或源正文、不自动生成。未知rid不绑定旧完成答案，迟到响应/导航/退出隔离；退出/过期清理问题与存储，409保留原请求。GET /api/history?request_id只接受单个32位hex，沿用safe_history(actor,rid)，进度不查四源。437完整本地及四Node/只读审查通过；重启仅已获批49161加载后端，四源正常后台complete，新真人刷新验证pending，尚余2次human，不挪作自动测试。

2026-10-09 AUTH-031：用户明确“批准此前申请，继续任务”，批准v11集中复验，总额度48→93，仅原两题各3次产品HTTP＋原24/known12质量36题＋团队本人最多3题。原49161/eng_b/AUTH017四源合成只读/DeepSeek provider/low8192/USD20账本/旧unknown保留，累计新增结算USD0.50或新unknown停止接纳，不写源、不动8094/8100、不推送部署、不绕过browser拒绝。

2026-10-08 ADR-063（candidate/local，live未验证）：AUTH030复验holdout10返回账户资格行而非请求的integration tier/region/retry，第一原题已检索C01批准操作但仅给审批未知。v11只收紧“未建立请求状态时可报告实际状态”的例外为同对象同属性，并要求latest顺序未知时覆盖已有支持的批准操作且单列顺序限制；generation/review一致。原结构/quote/gate/provider/low8192/预算不变，可能增加拒答，时间与费用改善未验证。回滚还原synthesis.py为v10。当前49161仍加载v10，不继承新候选结果；集中申请45次额外验证（native6/quality36/human最多3），总93、原累计USD0.50/newunknown停止，许可pending，不执行。

2026-10-08 AUTH-030：用户明确“批准解锁动作”，批准AUTH029总问题额度42→48，仅补跑原known12剩余07–12六题；原USD0.50新增结算停止阈值、新unknown停止、provider/low8192/USD20账本/旧unknown/实例与源只读边界保持，不批准额外native问答、源写入、推送或部署。

2026-10-08 AUTH-029：用户明确批准本轮修改后新127.0.0.1:49161仅本机eng_b实例与复验；AUTH017四源合成容器只读、原DeepSeek provider、USD20账本及原unknown324404保留。两原题各固定3次HTTP＋一次原24/已知12质量回归，最多42道问题；新增结算达到USD0.50或新unknown停止接纳，在途收尾。可信模型配置变化需另给具体候选后批准；不写源、不动8094/8100、不push/merge/deploy、不绕过browser拒绝。此授权独立于已结束AUTH027。

2026-10-08 ADR-062（implemented；native业务质量仍partial）：本Goal替代此前仅记录UX的临时决定。仅模型调用前明确source-version-changed可一次同步重新读取当前资料、重新验证同身份/容器/完整正文并原子发布，再从检索重做；不等待后台publisher，不复用旧allow/旧证据，不覆盖旧versions/audit。unknown、权限拒绝、429/网络及模型调用后变化不恢复；持续变化停答。恢复尝试/结果append-only记入新version_recovery事件。模型诊断仅保存allowlist finish_reason/returned_model、usage/reasoning token计数、可见输出长度与本地校验类别，不保存内部推理/原始response/上游任意标识。会话runtime接口只给模式、模型、四源配置/最近核查/核查中与已完成答使用状态，独立内存锁，无源调用/对象信息/审计权扩展。默认及可信low8192不变；436本地/三Node/五fixture通过，HTTP第二题3/3完成、第一题两拒绝一次partial，质量30/36已执行，剩余6受额度限制；回滚本分支实现，无数据或凭据迁移。


2026-10-08 AUTH-028：用户明确“合并并提交到main，同时给出阶段性反馈”，批准本轮fix/targeted-closeout-20261008的定向known05、AUTH026合成自动新鲜度、AUTH027实际试用失败/人工UX反馈及本地operator辅助脚本和状态文档推送既有Stone441/AI-Bang2，经PR合并main。应用brain/scripts/tests/web保持cdbd62b字节；不上传ZIP/SQLite/.runtime/凭据/一次性ticket，不新增源写入、费用、服务启动或UX实现，不改变G1/G2。未push/merge为此前证据冻结快照，实际Git交付以此次PR状态和main commit为准。

2026-10-08 用户试用反馈决定：两题均失败，停止进一步使用；等待计时/工作状态、模型和四源连接信息展示及整体简陋UX仅记录问题。用户明确本轮不进行改动，由ChatGPT Chat思考后给后续指导。保留cdbd62b/main基线与失败；结束此次临时49161实例，后续新启动仍按具体实例授权，8094/8100/G1/G2不变。

2026-10-08 AUTH-027：用户在49161具体实例授权待回复的上下文明确“批准授权”，批准新的http://127.0.0.1:49161仅本机试用实例，应用cdbd62b/main2eabeb8字节、eng_b、AUTH017四源合成容器只读、独立SQLite、DeepSeek synthesis-v10 low8192及原USD20账本；最多6次问答尝试，新增结算达到USD0.20或出现新unknown后停止新问题，已在途调用完成（非供应商硬费用上限）。使用已准备launch-page-trial.py，团队本人打开操作，不自动化被拒绝产品browser，不动8094/8100、不写业务源、不增加预算、不推送合并、不授予G1/G2。已启动本次实例；四源首轮complete、隔离索引与原账本及限额接线核实，页面由团队操作/实际问答和反馈仍待完成；一次性ticket不入Git。

2026-10-08 AUTH-026：用户明确批准“这3次创建＋4次更新及测量”。仅AUTH017既有Jira KAN、Slack C0C6R70SGG4、Drive指定文件夹各新建1个独立[SYNTHETIC] CLOSEOUT-20261008 automatic freshness probe/copper，再各1次silver修正；Slack以该root新增reply。另仅允许AUTH024页1572865 copper→silver一次。owner管理UI执行，独立只读CLI持续自动60秒后台＋fake测量；零新模型费，不删除/改权限/旧业务资料，不重复AUTH024创建。执行完成，3创建＋4修正一次性额度已全部消费；原观测被并发版本变化问答停答中断，失败保留、独立只读恢复，持续与恢复样本分列，详见targeted-closeout-20261008。新页面服务实例启动仍待独立授权，源操作不授予服务/推送/合并/G1/G2许可。

2026-10-08 AUTH-025：用户明确“推送并合并到main”，批准DEV-PERF-01已验证应用cdbd62b及32cb71c证据/状态增量推送既有Stone441/AI-Bang2，经PR合并main。只含本任务代码、测试、公共合成证据和文档；未跟踪ZIP/SQLite/队员产物不上传，不部署/重启8094/8100，不扩源/费用/权限，不改变G1/G2。下方“未push/merge”为证据冻结时状态；实际Git交付以本次PR合并状态及main commit为准。

2026-10-08 AUTH-024：用户明确回复“批准这一次单页创建及测量”，批准按lock-contention-20261008/NATIVE_FRESHNESS_PROPOSAL.md，在既有Confluence space131227通过owner管理UI仅创建一页[SYNTHETIC] PERF-20261008 automatic discovery probe及提案精确copper正文，并用cdbd62b独立只读CLI后台＋fake model观测。先前“按推荐”未当作写许可，澄清后才执行。不得修改/删除旧资料或该页、扩scope、改源权限、新模型费用、重启8094/8100或公开服务；不继承AUTH021，G1/G2不变。执行完成：仅页1572865/version1、继承C01限制未改；UI发布确认→自动发布35.60秒→首fake回答57.12秒，0模型费用，细分时间与限制见native-freshness/summary.json；本次一次性授权已消费。

2026-10-08 ADR-061补充限流修复（固定cdbd62b）：原Reader吞SourceRateLimited为unknown时丢失Retry-After的真实缺口，新增每来源共享SourceCooldownTransport，仅native JsonTransport自动装一次、authority/base/expanded reader共用。get/media在429记录monotonic deadline，冷却内本地unknown，不持网络锁、无自动retry；Drive media保留numeric Retry-After。冷却后不接纳新请求，此前已接纳/在途最多两路可收尾；不声称平台全局或跨进程限流。5定向验证600s冷却、吞unknown共享、mediaheader、装一次、在途交错；最终cdbd62b已完成独立24＋12/native/421 clean回归及逐题只读审查；known05部分覆盖和query40.08/49.03秒目标缺口保持。514831d为中间实测，原件不改。

2026-10-08 ADR-061（DEV-PERF-01）：在独立fix/lock-contention-20261008、main a3a0060基准上，固定514831d实现发现cycle单独串行锁＋锁外native读取、pilot→store短临界区失效/原子发布。请求仍持pilot锁；HTTP原store锁序不变。锁外读取保存baseline，发布/失效遇期间版本或active状态变化拒绝旧结果；numeric版本不回退、fingerprint冲突不覆盖，durable审计/report完成后才更新本地eligible快照。停止期间不发布，unknown/failure/backlog/expired仍fail closed。后台运行的eng_b bounded路径每阶段最多四source lanes，来源内串行；worker和前台同来源可各有一个native读取，不承诺全局单路。workers只读请求局部映射，所有authority更新/有序审计由请求线程完成；异常转unknown并停止本lane后续读取，不retry，不跨阶段复用allow，保留identity/channel/parent/body/version全部检查。默认none1024、v10显式low8192/模型60s、native30s及预算不变。回滚还原本提交三个brain文件即回到旧串行锁实现；无schema/源/凭据迁移。当前同13/15原窗口两native问题41.873/51.226s、单preview1.646/2.034s；query目标30–40s未达到。证据lock-contention-20261008；未推送/重启/部署，原失败/AUTH019/unknown324404保留。新native source-write测量具体提案未授权，不能继承用完的AUTH021。

2026-10-08封版Git交付：沿用用户本轮明确“推到GitHub并合并到main”的既有指令，交付同一封版任务的必要修复80b9ffc及公共合成证据，目标仍Stone441/AI-Bang2/main；不是部署、服务重启、范围/预算扩张或G1/G2。保留PR #6准备提交与Git服务错误原件，本轮修复另经PR交付。ADR-060为本次诊断决策；旧ADR-047原记录不改。

2026-10-08 ADR-060补充真实诊断：805c05d/v9 low8192的02不再截断，但can consult→only directs被review正确否决；09 review30秒超时无回执，保留324404microUSD reservation；11仍过泛any migration且无ledger范围。v10强化许可/义务/独占范围保真及未指定单事件的澄清空答；模型专用ModelTransport对8192有界60秒，原生JsonTransport30秒上限不改、无自动retry。native本轮两题均有最终答案和单preview计时，仍须新v10回归确认。

2026-10-08 ADR-060封版诊断：固定8f40ca6/v8 low4096实际known12的02/09 review与native product generation均finish_reason=length、4096全部reasoning，原失败保留。增加可信显式8192上限（每次保守reserve 324404microUSD），默认none/1024不变，原USD20 ceiling/账本不变、无自动重试。v9仅加强不明确referent必须在claim用引用正文标业务对象/事件，不能自动选检索规则。原全文/quote/coverage/review/权限gate不放宽。独立运行验证后才选候选，若失败保留并继续诊断；回滚可恢复4096集合及v8。耗时runner仅加RLock acquisition计时，同锁重入不改runtime。

2026-10-08 AUTH-023：用户本次再次明确“推到GitHub并合并到main”，批准当前fix/candidate-closure-20261008增量经本地检查后推送既有仓库并通过PR合并main。仅交付现有验证runner、当日实际价格复核及准确状态；原ZIP/SQLite/秘密不上传，不重启、不部署、不新增模型费用。尚未执行的封版live回归/耗时/时间线任务保持未完成，G1/G2不变。

2026-10-08 AUTH-022：用户明确“推到GitHub并合并到main”，批准本轮feat/business-validation-20261007已有已验证代码与公共合成证据推送至既有Stone441/AI-Bang2，并通过PR合并main。保护原ZIP、未跟踪运行数据库/私密工具证明；不改变仓库可见性、不重启服务、不部署/新增模型费用、不替代G1/G2或比赛提交。运行模型的每日价格guard保持，Oct7证据不当作Oct8readiness。

2026-10-07 ADR-059（固定本轮候选）：选择0bc90ae synthesis-v8可信low/4096。2048在完整开发03 review及native产品generation实证length/no final，失败与费用保留；4096单题诊断、全24及当前native两题均返回正确且精确引用。398clean/五fixture/Node和当前审计签名配对通过。选择依据是这些实际观测，不宣称sampling因果、稳定率或旧保留失败修复；不再继续提高cap。默认none/1024不变，opt-in可信启动，不新增HTTP参数/权限/费用上限，不自动retry。回滚省略flag或保留v6候选，无schema/源修改。业务增强范围按5.3收尾，与G1/G2、完整技术验收及未支持能力分列。

2026-10-07有界cap跟进：a3569a1完整24题为21正确事实返回＋2空＋03复核length失败（2048个reasoning tokens，无final）。仅新增可信4096候选档，生成/复核同cap、按实际cap预留和usage上限检查；默认1024保持，未知cap8192等仍拒绝，4097超4096实测mock冻结并保留reservation。原03失败保留、不自动重试；先单题诊断，再据实际结果决定是否形成候选，不预称全通过。原生a3569a1进程仍保持启动时加载的2048配置。

2026-10-07 ADR-058（有界同模型推理诊断）：v7/v8 none/1024的7作者开发题分别6/5返回，03正确未知仍被review拒绝、32冗余仍存在；原记录保留。81dd33e low/1024实际六题正确，一题1024输出全用于reasoning后length无final；73b1e3e新增可信cap1024/2048、两阶段一致预留和usage校验，395回归；low/2048七题本次正确、18137microUSD原预算结算。只读复核不是独立人工或稳定性证明。为形成可检验应用配置，operator允许可信启动low/2048 opt-in并拒绝fake/excerpts滥用，默认none/1024不变；不增加HTTP客户端控制、不改quote/whole-review/权限、不自动retry。native runner同cap动态preflight。回滚可省略两个新flag，无数据/凭据迁移；采用为统一候选需完整当前开发和native证据，不据七题提前完成Goal。

2026-10-07 ADR-057（DEV-BV-02原资源上下文）：当前捕获的D-01正文只说Final root cause，v5传给模型时丢失已鉴权title里的payment-service。3ceb625/v6将原title/locator作为source_context单独送gen/review，明确识别来源事件、context不作指令/quote/权限；SyntheticProvenance已核这两字段一致，新增2a039aa负测试实证篡改在reserve前拒绝。18synthesis/7provenance定向、388＋追加test389 clean archive及五fixture/Node通过。同48世界4开发诊断和全24题均返回，原12/16错误本次未重现，但03未知表达、32无关背景仍open。两native/model题本版本正确，费用按回执4137/22146/5100microUSD，各原件/共享snapshot保留。原quote/parser、预算、温度0/逐阶段权限及whole-answer gate不变；收益只能归本次上下文输入及说明整体，非组件因果或稳定准确率。可还原synthesis.py到64b705a回滚，无schema/凭据/源写入迁移。Goal active，原AUTH/人工/发布边界不扩。

2026-10-07 ADR-056（DEV-BV-02受控采样）：同代码/世界/三开发题，各4次temperature1为9返回/3失败，temperature0为12返回，同题文字一致，成本12081/12016microUSD；不是12独立题、盲测、稳定性或成本收益证明。选择64b705a温度0为可回滚默认，generation/review一致，None显式省略配置；非有限/越界/bool配置在reserve/dispatch前拒绝。原thinking disabled、v5、逐阶段权限、精确quote与整答gate不变，不新增客户端控制。386干净archive/五fixture/Node通过；24开发题实际20核心正确＋1跨事件误导＋2空＋1结构失败，native两题正确，仅局部改善。原失败不改，新问题继续open非AUTH019；回滚可由可信构造配置1/None或还原本次代码，无schema/凭据迁移、费用/授权扩大。

2026-10-07 ADR-055（费用归属，验收harness）：并发两个获批验收使native预算起点含另一任务pending315802，global accounted差不能当退款或本轮费用。新增run_cost仅按本流unique settled usage receipt汇总，重复不重计、冲突/非法/未结算receipt拒绝，缺usage单列且不清原reservation；报告保留共享snapshot并明确限制。原captured JSON不改，另parallel-v5-cost-attribution证明core18392/native3155/settled增21547。3定向及当前实际44+4receipt离线核验通过，应用brain和模型v5未改变。

2026-10-07 ADR-054（DEV-BV-02上下文/量词）：当前v4完整24开发集实际20核心事实/2正确无调用空答/2有证据失败；20并非全部质量通过，因背景和MYR唯一来源过概括。另5独立措辞开发题再次复现逐claim ID上下文校验拒绝。仅synthesis-v5补通用prompt：每claim独立含ID、可复制邻接连续原文但禁止补造quote；one draft/example不推出所有说法/唯一来源，review显式拒绝该扩大。parse/gate/权限/预算未改。5题同世界同问题v4→v5为1结构拒绝→5返回，需语义复核/完整新版证据，不称盲测或旧保留失败修复。381完整fixture/mock与15synthesis定向通过；不重新开放AUTH019，旧24失败保存。

2026-10-07 ADR-052（DEV-BV-02关联cutoff）：复现1048对象下J-03虽有弱词匹配却在保留16项之外，旧全部候选seed集合误阻止D-01原有链接扩展。仅将去重集合限制为保留16项，保持12种子/8扩展/24窗口及各阶段目标鉴权；不改原文、添加问题关键词或继承历史。相同资料/24题1000压力BM25的J-03诊断关闭，lexical对照仍漏，非整体质量通过；3新增撤权/原文测试、380完整fixture/mock通过。原生链接解析仍未实现，不能将fixture链接结果称为native一跳能力。

2026-10-07 ADR-053（DEV-BV-02状态/歧义）：synthesis-v4通用区分提案、审批、完成与撤回；未批准不意味着取消，指代未明确时只能给有范围的候选事实或空claims。review保持整答gate、精确quote及全部verdict/coverage断言；空claims加通用范围澄清提示，不引入历史继承。4独立开发问题实际v3/v4比较，资料/问题/输入保持相同，engine及prompt变化均保留hash；v3首题正确受限草稿被review拒绝，v4四题返回正确受限或有范围事实，单次开发诊断非稳定质量率。费用3833+4004microUSD，原账本累计99483，不清预算。f8ecbed保留题不重跑/不调成通过，AUTH-019延期不变；当前新版native/live全矩阵仍需另证。


2026-10-07 ADR-051（DEV-BV-03 legacy completeness）：为补齐已识别的非后台来源故障断点，按actor/request参数化读取当前unknown记录。真实synthesis首次发送前发现unknown则零调用；review/最终提交前新unknown停止后续阶段，不抹去已有attempt/usage/费用。fake仅保留允许摘录并显示通用coverage不完整提示，不泄露源名/隐藏对象/计数；ACL deny仍过滤，preview/history不可用语义不变。17定向/377完整fixture/mock及只读复审通过；不是重开AUTH-019或按保留题调f8ecbed，新native/live模型证据不继承。回退f8ecbed可恢复旧行为，旧证据保留。

2026-10-07 ADR-050（DEV-BV-03 有界查询）：仅可信operator的AUTH-017后台模式启用bounded_queries；活跃worker最新四源cycle完整/无backlog且进程内发布距今不超过120秒，同tenant/actor/resource/version候选可用本地snapshot，不把它称为当前allow。选中资料仍有before_model/model_dispatch/review/before_dispatch及preview/history native复查；同一请求同阶段的resource/version多个窗口共享一次native check，阶段间不共享allow，每个窗口仍核对版本；unknown及明确content/version-changed deny停止整答，防止漏掉新版反证后仍回答；真实ACL deny仍过滤，旧preview/history仍返回不可用。worker失败、积压、过期或停止明确503，不将缺可能改变结论的源当知识不足。进程重启必须重新发布，DB checkpoint不恢复trusted snapshot。旧库默认显式逐问刷新保留；HTTP统一pilot.lock→store.lock顺序，避免发布与HTTP锁反转。120秒是保守运行有效性阈值，不是freshness/SLA；100对象/page上限及全局锁仍限制规模。无旧服务重启。

2026-10-07 ADR-049（DEV-BV-02选择，待当前完整回归/保留集）：采用本地binary-TF BM25作为当前候选默认排序，保留Engine显式lexical回退；只在actor权限预过滤后的精确原文窗口统计IDF/长度，不增加embedding/向量库/模型重排，不改窗口、引用、预算或各阶段native鉴权。相同48对象/24开发题、模型/prompt与资料字节的单次live A/B中，A为16条事实回答+2条正确空回答+6条失败，B为20+2+2；这是单次随机模型诊断，非稳定质量率。1000干扰两者仍漏J-03，B并未证明全质量通过；AUTH-019保留。本实现只是CPU查询时评分，尚非持久FTS/章节索引；回退参数不改旧证据，后续须验证安全及未见题。

2026-10-07 AUTH-021：用户对R2_DISCOVERY_PROPOSAL具体范围回复“批准上述具体合成种植/修正范围”。仅四AUTH-017固定容器内各新增独立[SYNTHETIC] BV-20261007资料及amber→green→amber修正，Slack独立新root/reply；不改旧资料、不删除、不扩scope/账号/费用、不重启服务。通过已批准owner管理渠道写，现有程序凭据保持只读；记录发现至正确fake回答逐次时间，不宣称SLA。

2026-10-07 AUTH-020（本轮具体指令）：用户采用Business_Iteration_Pack方向，延续既有本地可逆开发与验证；不扩大新权限/provider/费用、外部写入、服务重启、推送合并、公开部署/提交。保留ADR-040、AUTH-019及原共享预算；Orion仅短诊断，不自行重新开放修复或改变整答拒绝。基准9b9c193，feat/business-validation-20261007；01/旧研究审查证据不改。


## AUTH-019 · 2026-10-06 · Explicit quality deferral for consolidated team candidate

用户对固定331bd28、357archive/五fixture场景、实际真模型失败/诊断与影响的具体提案明确回复“批准明确延期并交团队验收”。仅允许将long named-event/similar-event review拒答及部分自然回答非必答背景两项保留为已知质量缺口，交团队集中语义验收；冻结时不能称通过。原review gate、所有有效断言/失败与原USD20账本保留，不是G1/G2/发布/提交批准，也不改变浏览器实际工具许可。browser保存站点拒绝仍须通过正常许可机制解除；用户回复“没有找到许可入口”，位置未知，browser/screenshots not_run。仅Agent自建49161 fixture已结束，未来新实例需重新核归属/模式及许可。不能换端口/工具/代理/关闭安全设置。

以下ADR-048/047为此前执行时记录；其中等待回复/in_progress由AUTH-019及STATUS当前表覆盖。

## AUTH-018 / ADR-048 · 2026-10-06 · Same-target browser instance permission and review scope

用户明确批准当前浏览器工具访问http://127.0.0.1:49161用于本轮本地合成问答/history/引用/navigation/keyboard及无秘密截图；不扩native/模型/外部写/凭据。原实例已停止后遵照用户要求重新确认，并批准新隔离memory Store、fixture_fake_model/live_enabled=false实例。mcp__cua_repl.js→cua.createBrowserTab(chrome,same URL)正常重试仍返回browser tool security policy saved user permission blocks；文字许可不等于实际工具生效。工具无许可管理API，Computer Use禁止访问com.openai.codex，具体设置位置未知。已请求用户仅解除该地址的保存拒绝，无绕过/换端口/代理或关闭保护。旧8094/8100不重启；新实例startup hash/time单独记录，加载R5早于后续review-scope代码，不冒称最新全部runtime。浏览器not_run，普通local开发继续。

R3有界诊断后仅作通用event/scope review澄清：不同或未知事件不能无明确关系被当作命名事件反证，仍检查所有同事件证据、拒未知/未支持细节，不把问题当事实。新增cross-event负面review拒绝回归，不把部分accepted verdict拼成成功答案。331bd28 clean archive357/17.406s、五fixture、2Node/HTTP通过。最新长文draft正确Orion句外仍增加无关payment-service背景，review有false而整答拒绝，保留quality failure，停止无诊断依据的付费循环。另自然题仍有多余背景，原子覆盖不等于relevance全通过。未自动批准延期；已给固定candidate/实际失败/影响与团队延期或继续定位的具体选择，等待回复。

六轮实际模型保守账本增28194microUSD，原总额45219、余19954781/pending0/frozenfalse；48usage事件对原账本只读逐笔匹配。不是invoice、native ACL或human acceptance。R2再次native readonly/fake 8checks真实通过，不计完整创建更新时间矩阵。固定candidate331bd28与所有phase source hashes、native/model/local/browser/human证据分列；最新状态/入口已收敛，完整Goal仍in_progress，G1/G2不升级，无push/merge/source write或目标服务重启。

## ADR-047 · 2026-10-06 · Integrated review worktree: R3 quality and R5 existing experience

基准45d7b27，fix/review-integrated-candidate。本目标扩大到剩余可授权推进的统一候选，不因R3A/R4团队未观看而阻塞其他开发。R5新回答保存服务端question/answered_at，缺字段旧记录明确缺失；不可用历史不泄露问题/时间。preview逐次鉴权后才返回source映射URL，UI只允许对应平台HTTPS host、无凭据/非标准端口，noopener noreferrer，fixture://无伪原链接。诊断折叠，保持ADR-040与旧响应丢弃。DOM/8HTTP定向通过、实际只读Agent复审无阻断；Chrome localhost访问被工具security policy/user denial拒绝，浏览器not_run，不绕过或换入口。

R3冻结6条只读Agent编写的未参与主Agent调参变体，另有无证据和长文/相似事件。不是人类blind benchmark。首轮fixture_source_live_model_synthesis真正出现明确问题失败：D-01到达模型、S-01未召回、review拒绝。分词完整保留数字ID并通用拆分alphabetic hyphen compound，修复payment与payment-service匹配；不是添加展示专用词表。定向11项及撤权assertion通过。第二轮最终claims暴露PAY-101在对应quotes不存在，以及无关背景；synthesis-v3加入显式结构编号须被quote支持，生成/review强调最小必要claims与事件归属。引文匹配与编号检查仍不能证明完整语义，同模型review仍可能漏检。13synthesis定向通过；第三轮6自然问题+无证据均返回，长文review拒绝，质量工作仍in_progress而非全部通过。

当日实际model_readiness通过；AUTH-003/014固定app-owned模型key、原USD20账本存在/未冻结、剩余预算预检，未改变日期或重置账本。三轮6349+8701+7320microUSD保守结算，非vendor invoice；进一步单题diagnostic另记录。仅fixture合成源，不能冒充native permission persona。R2当前AUTH-017四容器native只读再次verified subset，原对象不写；完整原生新建/更新/删除时延矩阵仍partial。所有新结果review-integrated-20261006独立目录，旧审查与证据保留；runner加exclusive output纠正旧限制说明，不覆盖旧retrieval-local。新scripts/quality_acceptance是受控开发验收harness，不添加用户诊断/下载功能。最终固定候选/相关完整回归及五场景还待本目标后续完成，G1/G2保持not_run，未push/merge或目标服务重启。

## ADR-046 · 2026-10-06 · R3A/R4 fixed local candidate and signed coverage handoff

本轮只完成R3A/R4团队可验收本地候选；不重做fa515a9、不扩建R1检查体系或产品功能。基准dfa40c3，分支fix/r3a-r4-team-candidate；固定应用/测试34281adfe22c839ed463a51cb3536255f47175b4，后续状态/证据提交不改变runtime。真实只读子Agent独立10项离线方法审查没有复现阻断代码问题，P2发现新R4事件尚缺签名快照对应关系，接受并补齐；follow-up独立2方法及13条验签命令通过。非阻断observer/audit故障注入建议未扩建，未宣称已测试该新增组合。

首次dfa40c3 clean archive 352中351通过，唯一test_product_acceptance在读取缺失.runtime配置时提前停止，未到原生mock权限断言。test-only修复精确路径mock config、保留原异常allow必须失败/不能query/无凭据输出断言，增加精确账号及3次read证据。34281ad新clean archive setup/352项16.920s/五fixture场景/2Node/自有新loopback HTTP烟测通过；失败原件保留，不改变产品或原生权限代码。回滚测试修复将恢复无本机配置的archive失败，不需要删除任何证据。

受控操作员离线snapshot不是普通用户下载功能。六份当前fixture/mock R4审计流各自保留旧prepared事件并签至seq42/31/31/31/33/51；既有真实CodeBuddy CLI不改，实际13验签含原件/正文改/中间删/覆盖尾删/全链重算/未签名尾/旧checkpoint回滚。临时private key删除，仅public key保留；同机同账号临时signer不能证明独立custody或生产DB角色。旧checkpoint+对应旧截短流可通过，只有另外可信保留的更新checkpoint拒绝覆盖尾删除；未新增自动freshness authority。audit capture精确绑定dfa40c3 source hashes，与最终34281ad archive runtime hashes比对一致，不能冒写capture提交。证据review-r3a-r4-candidate-20261006。

历史ZIP六文件逐字节一致，原审查/证据不覆盖；Markdown硬换行保留原字节而不改全局规则。ADR-040独立问答/无答案下载不变；旧8100独立问答继续有效。每日价格expiry及真实模型前model_readiness不变，不清账本或传旧日期绕过。没有外部API/model/new scope/费用/源写入、用户进程重启、推送合并或发布。新build native/browser/live model与G1/G2 not_run；团队实际本地观看、完整native/质量矩阵及生产独立保管是明确后续，不能由本地mock/Agent审查替代。

## ADR-045 · 2026-10-06 · R2 native discovery and exact legacy fixture compatibility

基准0dda56a5b0c1db4a427d7d5e49e0183cafdc624c，verify/review-r2-native。AUTH-014 app-owned Keychain只读复用、已有Drive refresh grant换token并核对原生账号；没有prompt/consent fallback、凭据put或源业务写入。新runner显式--live、独立内存Store、新目录exclusive证据，未启动/重启服务或读取DeepSeek凭据/账本。配置与AUTH-017固定四容器先验证，再读取凭据；缺失/失效/unknown失败，不申请scope。

初始真实四源list/read周期全部complete（18.3567s），但无动态新对象、目标问答无证据，新增验收failed。当前native metadata说明既有获批KAN-6/10015标题以完整`[SYNTHETIC ONLY]`结尾；Jira方案允许明确合成标记，实现却只用开头`[SYNTHETIC]`。仅Jira补这个精确完整后缀，CF/Drive/Slack规则不变；不是任意synthetic子串匹配。第二次周期complete（16.7914s），但原文guard仍拒绝：当前原文完整原banner保留，Fixture ID是既有批准`J-lifecycle-20261006`，原精确清单仅J-02/J-03。补入这一精确既有fixture ID与原完整banner组合，不接受未知fixture/缺banner/改banner，不补造原文、改源标题、自动继承历史或给模型自报授权。容器/actor/权限/版本/精确切片关系继续服务端验证；不将此兼容视为放宽数据类别或新scope授权。

第三次新目录实际native周期16.8111s，四源native身份及list/read complete；自动发现原固定白名单外Jira10015/KAN-6，实际fake回答仅引用当前指纹440116571589157286的Revision2 green，精确preview一致；原reader IDs不改、动态IDs不授予product_ops、审计链有效。8checks verified native subset；其余源本次没有符合规则的新对象，所以不是四源新对象矩阵、发布至回答时延SLA、真实模型或persona完整矩阵。原两个failed记录及各次源码hash保留，不改写通过。证据review-r2-native-20261006 / review-r2-native-fixed-20261006 / review-r2-native-approved-fixture-20261006。

4新runner guard、21发现定向及352完整fixture/mock方法16.913s通过，验证精确标签/fixture仅候选、原文不符及未批准来源仍拒绝。native周期另列，不升级R1/R3A/R4新build native/browser/live model或G1/G2。未推送/合并、费用、新scope、平台业务写入，8094/8100保持运行。回滚关闭发现opt-in或去掉两个有限兼容项即可恢复原拒绝；旧审计/版本/附件不删除。R2新增/更新/删除多次生命周期时延仍待具体管理操作验收，AUTH-017只读不授权种植。可继续本地R3清晰问题漏召回与歧义质量评测。
## ADR-044 · 2026-10-06 · AUTH-017 bounded discovery (R2 local increment)

基准fa515a9984a773934dc37da96cd1dba55a05dc1f，独立fix/review-r2-discovery。默认关闭的`--discovery-auth017`仅multi/eng_b可启用，要求现有reader配置恰好落在四个批准容器；不改原对象配置/Keychain/scope/product_ops。独立multi-auth017-web.sqlite保存catalog/state，重启先精确当前读再开放动态IDs。CF空间metadata、固定Jira project enhanced JQL（加project元数据验证容器）、Drive direct children、Slack固定频道/时间窗；候选标题/名称/root标签不单独授予模型出口，完整原文仍通过synthetic guard。列表只决定候选，动态对象只对eng_b有候选权，逐阶段native读仍必需；Slack动态回复每次模型/引用/历史检查另复核当前合成父消息。

每源最多10列表页（50条，Slack15）与100精确原文读取，含父消息复核；记录实际adapter HTTP尝试数，不把单次read误当一次HTTP。对象超限轮转，页超限保留backlog，均不推进完整checkpoint。已知对象即使从列表消失仍精确复核，不以列表缺席判删除；deny/unknown先停止服务，unknown不作为删除事实。事务切换新版本/catalog，先记录发布准备审计，完成审计持久化后才推进checkpoint；失败可重试，无全库重建。CF/Drive原生递增版本不回退，Jira/Slack指纹不作数值排序。重复读取未变化对象保留indexed_at。HTTP429 numeric Retry-After保留、其他失败退避，缺scope不放行、不自动申请权限。线程共享pilot锁，停止后才关闭store；慢源会阻塞查询，非生产worker或SLA保证。

19项定向、346完整fixture/mock方法17.110s通过；现有两Node检查通过。实际离线trace包含发现前无新增证据→四源发现后可问答、CF更新/Drive删除/旧历史拒绝、product_ops不继承、429不前移checkpoint；合法长窗口经R3A服务端来源进入MOCK模型通过。原审查/R1/R3A/R4证据、原ZIP和保护路径未改。新native/browser/live model not_run，G1/G2不升级，未重启8094/8100、真实API/模型调用或新增费用。首轮真实父消息复核断点及测试harness错误均保留日志，没有删除安全断言。证据review-r2-20261006。回滚关闭opt-in即可回到原固定ID流程，catalog/旧版本/审计不删除。下一：AUTH-017下独立native只读发现及新增/编辑/删除时延验收；种植操作仍核对具体原AUTH-003范围，不将此次读取批准解释为写授权。
## AUTH-017 · 2026-10-06 · eng_b fixed-container discovery reads

用户对具体问题明确回复“批准上述四个固定范围”：Confluence space 131227；Jira KAN/10001；Slack workspace T0C6FQ246TF、频道 C0C6R70SGG4，从既有合成 root 1791142152.858189 起；Drive 文件夹 1EMYjaNhzBFQ3TXHC6ukEwN6otVIIeOEv 的直接子项。仅既有eng_b、既有只读scope/Keychain；不扩费用、scope、源写入、公开范围或product_ops AUTH-016。详见[R2方案](R2_DISCOVERY_PROPOSAL.md)。本轮只准备方案并核对权限范围，没有执行新发现或重启服务；缺scope/身份变化/计费提示须停止该源。

## ADR-042 · 2026-10-06 · Trusted synthetic exact-window provenance (R3A)

基准97c2a08当前模块先复现合法晚段窗口因不含原文开头banner而在网络前拒绝。最小修复使用服务端冻结的已批准原资源ID集合（fixture baseline / native配置固定IDs）与实时原资源lookup；进入每次draft/review前验证active、source、严格整数version、完整原文原有合成marker、canonical evidence ID及resolve_window精确文本/locator/元数据。保留原生逐阶段当前权限检查；此来源类别批准不授予员工权限。indexed_at是本地摄取时间，不作为原文版本关系。不给切片补banner、不向模型/客户端输出可自报的synthetic字段。完整原文marker仍必需；固定ID配置也不是独立签名真实性证明。独立provider旧whole-document调用保持旧marker策略，但任何窗口都必须有服务端来源。回滚去掉此桥接会恢复合法晚窗口拒绝，不能改成窗口自报放行。

6项定向测试覆盖合法窗口、未批准资源、版本/正文/source/locator/窗口篡改、draft与review间原文变化、当前preview/history撤权，以及delegated Confluence MOCK路径。完整327项fixture/mock回归通过；真实native/model/browser均not_run。证据review-r3a-20261006。R3业务质量仍待测：明确问题漏召回与歧义分别评估，Which hypothesis was abandoned?只是单资源诊断，不添加展示关键词或继承历史。

## ADR-043 · 2026-10-06 · Model attempt and receipt audit (R4)

新增evidence_used阶段prepared_for_answer/review；provider输入guard、价格、预算通过并持久化dispatch后记录model_dispatch_intent，transport调用前记录model_dispatch_attempted；有效HTTP/usage结构与计数校验、预算settle后记model_usage_received；输出结构/证据校验后记model_output_accepted或rejected。有效usage不是有效答案，超时保留pending预留且called未知；attempt不证明服务端收到。draft/review各自reservation_id与stage独立。HTTP成功另记response_dispatch_attempted，不证明用户阅读。审计schema仅增加事件枚举；旧sent_to_model/review事件原字节不回写，UI解释为输入准备而非已发送。失败原因固定安全分类，不回显原始错误或凭据。

5项定向测试含guard/价格/预算零transport、成功/超时、review输出失败、实际本地HTTP成功交付尝试与503无交付事件；原历史事件保持且链有效。两项Node前端检查及327完整fixture/mock回归通过。真实模型收据/native/browser新build未运行，独立防篡改保管与人G1仍未完成。证据review-r4-20261006。回滚新事件/UI无需改写已有审计；不能把历史准备日志重新当网络成功。
## ADR-041 · 2026-10-06 · Review R1 price readiness and startup identity

当前HEAD与审查基准cf827bb一致；实际模块离线复现当天日期阻断及R3缺标记/漏召回，原审查附件逐字节保留，不能当当前运行结果。官方DeepSeek pricing/chat-completions页面本日实读，deepseek-flash/V4.1-Flash及peak cache-miss USD0.30/input、USD1.20/output每百万不变，复核日期更新为SGT Oct6；保留当日有效、未来/过去日期拒绝，不能自动延长、传旧日期或重置既有USD20账本。`scripts.model_readiness`仅离线检查价格准备，不读凭据/账本/源。跨午夜请求仍在reserve/network前停止；HTTP用固定503/operator-action提示，启动错误给官方复核与保留账本步骤。代价：每日人工/Agent实际复核仍需要，未保证全天候可用。

health/启动日志新增进程导入时固定的brain/scripts源码SHA256与UTC加载时间；不读.runtime/env/Keychain，不每请求按磁盘更新，不把静态刷新当后台升级，也非签名构建证明（假设启动期间不并发改源码）。8094/8100现有健康接口分别live synthesis/fake model且无新指纹，未重启，准确loaded commit未知。保留ADR-040，不恢复聊天/下载。18定向及316完整fixture/mock测试通过，Node两个安全检查通过；官方文档核对非live模型验收。首次新测试harness错误/沙箱bind失败保留。证据：`evidence/runs/review-r1-20261006`。回滚可移除readiness/指纹与错误投影；不得回滚为使用已过期价格或删除账本。新API契约：GET health增加runtime_version；价格过期query返回503/code=model_price_review_required，其他授权边界不变。

## 2026-10-04 · AUTH-001 · approved local scope

用户本次明确授权本仓库内本地、可逆、无新增费用的完整开发、测试、独立分支和小步提交，范围不再限于 Phase 0。G0 **仅本地开发部分获批**；四源真实账号/数据/scope、运行时模型、费用及数据出口待定。G1/G2 未通过。凭据存在不代表可用。无远端推送、公开部署或业务系统写入授权。

## ADR-001 · local implementation baseline

盘点基准 `68e65c8`：只有文档，Python 3.14.7 / Node 22.23.2；未发现 Docker、uv、FastAPI、pytest 等依赖。先用 Python 标准库、SQLite 和同源原生 Web UI 构建可重现本地闭环，避免安装/云资源依赖。Python unittest 实测安全边界；SQLite 事务维护版本与日志顺序。关键词检索先建立确定性基线，语义检索/真实模型效果仍待实现与授权。

代价：stdlib HTTP 服务仅允许 loopback 合成演示，不可作为生产部署；SQLite 不具备 PostgreSQL 独立数据库写角色隔离，A-02 不能因此通过。后续公开部署前迁移受支持 Web 框架、生产身份和数据库角色。迁移保留 SourceAdapter、Evidence、Model 接口和回归测试；不得放宽安全要求。

## ADR-002 · Tencent task reservation

当前工具注册表无 CodeBuddy/WorkBuddy 调用工具，PATH 未发现 CLI；不扫描/使用凭据、不调用收费开发入口。预留 DEV-09-CB：独立签名审计检查点及验证器（`tools/audit_verifier/`、`tests/codebuddy/`），由真实 CodeBuddy 实现；Codex 完成日志契约和基础 hash-chain，持续推进同步主线。选择此任务替代原 DEV-05，是为了在人工接力前不阻塞动态更新与五场景本地开发。签名与独立信任根未交付前 A-03/A-04 仅可报告局部链检查，不能标全通过。

## ADR-003 · source-linked retrieval and durable demo authority

自然语言 S-01 回放首次遗漏 PAY-103，证据保存在 first-scenario-failure.json。保留原 oracle，增加最多一跳、逐 seed 和目标授权的链接扩展；固定候选/字符预算。没有按题目硬编码业务答案。来源权威独立持久化到 `.runtime/source.json`，每次授权检查重新读取，避免生成期间的磁盘撤权只在下一 HTTP 请求才可见。源事件处理是 request-driven demo 模式，未实现真实 webhook/后台定时同步。

## ADR-004 · honest audit scope and acceptance

审计范围先在参数化 SQL 按获准 actor 过滤，再按精确 source/resource_scope 定位请求并返回其生命周期；因此可还原问题和最终回答，而不只看到孤立资源事件。自然语言仅支持文档模板，模糊/任意 SQL 拒绝。签名检查点由真实 CodeBuddy 独占实现；在此之前 S-05 只能标 passed_local_subset，A-02/03/04 的完整验收不通过。浏览器工具 localhost 被 ERR_BLOCKED_BY_CLIENT 阻挡，视觉验收不伪造。


## 2026-10-04 · AUTH-002 · CodeBuddy execution and local evidence

用户明确授权 Codex 直接操作已安装的 VS Code CodeBuddy、必要时安装官方 CLI、协助过程截图。已验证插件 4.12.38765564 可用，因此采用真实插件入口，无需新增 CLI。允许将本项目开发任务与代码交给该工具使用现有开发额度；不将此扩展为应用 runtime 费用/真实业务数据授权，不自动充值。截图与对话证据只保存在 ignored 本地目录，不自动上传。

CodeBuddy worktree 基于已合并的 81df3ef，避免从旧基准遗漏最新任务包；v1 hash 契约不变。Codex 仅进行任务下发、命令审查、测试和后续集成，签名验证器代码由 CodeBuddy 实际生成，分别记录来源。未自动合并或推送本轮分支。

## ADR-005 · 2026-10-04 · 真实 CodeBuddy 审计签名集成

CodeBuddy 插件在隔离 worktree 实现 DEV-09-CB；原提交 `4165ee6`，Codex 审查后 cherry-pick 为 `8cd5088`。使用系统 OpenSSL Ed25519，无新增 Python 依赖或应用运行时费用。Codex 指出初版密钥算法与 bool/int 验证问题，由 CodeBuddy 修正并增加测试；Codex 独立复跑 20 新测试、全仓库 52 测试通过。签名只证明 trusted checkpoint 覆盖的规范化事件，未覆盖尾部、检查点回滚/新鲜度、v1 跨流身份、同账号全面失陷和密钥轮换未被此实现解决。回滚可单独 revert 集成提交，不改变问答链路。真实截图/对话留本地 ignored evidence；未上传/提交比赛。

## 2026-10-05 · AUTH-003 · synthetic live sources and DeepSeek pilot

用户“可以，按你说的来”批准上一轮明确提案：建立比赛专用 Confluence/Jira/Slack/Drive 测试空间，仅写入合成资料，允许在这些空间调整测试身份权限；不接入 NTU 课程 Slack 或既有个人资料。站点/文件白名单和真实账号映射仍需落实。注册验证码、条款接受和授权确认由用户完成。平台采用可用免费/试用方案，不授权收费续订。

DeepSeek 直连首轮总预算上限等值 US$20，仅处理合成资料，不自动充值；OpenRouter 仅备用，未批准额外调用。密钥通过本地忽略配置提供，不能发到聊天或提交 Git。配置存在不等于 live 验收完成；预算控制与输出校验完成后才开启调用。G0 部分授权扩大，不标整体通过；G1/G2 仍待人工验收。

## 2026-10-05 · AUTH-004 · Confluence trial agreement

用户在展示具体 Customer Agreement、隐私政策与 30 天 Premium 试用后明确回复“同意接受”，已点击 Try now 并验证开通。仅授权免费试用，不授权付费续订。账单显示 2026-11-04 到期、Payment info None，且提示未补付款方式将停用；不能把通用自动降级说明当成本账户保证。到期前人工检查并选择 Free，避免演示中断。截图仅本地 ignored 保存，API/ACL live 验收仍 not_run。

## ADR-006 · 2026-10-05 · 委托读取与集中端到端验收

根据用户明确反馈，停止逐页人工平台权限点验，保留一次接通问答链路后的真实撤权/同会话/引用历史验收。实现首个只读 Confluence pilot：凭据身份用 current user accountId 实测比对，不回退到管理员；页面与空间 ID 白名单，metadata/body 双读取一致性，无允许缓存。平台不提供 ACL revision 时 policy_version=0，不能替代真实 ACL 版本。仅支持普通合成 storage 文本；宏/附件拒绝使用，避免忽略子资源权限。暂不接入原 FixtureWorld/Engine，以免假身份及 fixture 模式掩盖真实模型/权限差异；下一步显式 live authority 与服务端 session 接线。配置只保存 env reference，CLI actor 是操作员诊断参数，非产品身份。真实 scope/token 创建仍未执行。回滚可单独移除 reader/probe，不影响 fixture 应用。

## ADR-007 · 2026-10-05 · 未知模型消耗保留预算

预算使用 integer micro-USD（总上限 20,000,000），SQLite BEGIN IMMEDIATE 串行预留。网络发送前持久化 dispatched；超时/进程崩溃不自动退款，未知用量继续占用全部预留。只可取消未发送请求。真实费用结算超过预留时先记录实际值，再冻结后续发送并报错，不能把超支隐藏为成功。账本不控制供应商账户其他调用；需固定模型价格/token 上界与官方计价后接入 provider，未接入时不声称预算保证。

## ADR-008 · 2026-10-05 · 共享问答引擎的操作员 pilot

保留 fixture 应用默认身份和模式；为 Engine 增加显式 tenant/mode 与 authority prepare/prefilter 接口，Confluence 每次查询重新委托读取白名单页面，用本次获准快照过滤持久索引。model_dispatch 增加整组证据重查；历史无证据时也验证 actor/tenant。操作员 CLI 没有前端登录路由，不能将 --actor 当员工认证。native 读取/索引/审计使用同一问答引擎，避免另写一套绕开安全测试的展示逻辑。

依据官方 scoped token 文档，API base 固定到 api.atlassian.com/ex/confluence/{cloudId}，而引用仍由后端构造站点 URL；UUID 与站点分别严格校验。代价：小范围每次读取并非后台同步，多轮 HTTP 无原子撤权保证，真实身份/前端及传播延迟仍待测。14 新 mock query 测试与全回归 91 测试通过；无真实 API 调用。回滚可移除 query pilot/CLI，恢复 Engine 的默认 fixture 路径，保留新增租户校验。

## 2026-10-05 · AUTH-005 · eng_b scoped token 配置

用户在具体行动时选择“批准此范围”：eng_b 的 `AI-Bang2 eng_b read-only pilot` token，2026-10-20 到期，拟选 `read:page:confluence` 与 `read:content-details:confluence`，程序只读白名单合成页面；最终创建和密钥保存由用户亲自完成。此批准不覆盖 product_ops token、写入/admin scope、既有个人资料或新增收费。先前自动审批拒绝配置动作；得到这次具体批准后方继续，不绕过拒绝。


## ADR-009 · 2026-10-05 · 多源委托与Jira内容版本

证据：官方Jira Get issue/current user/Get comment约束、现有Engine整数version契约、Jira字段/评论无可依赖整数正文revision。采用固定native ID/key/project白名单、每次myself验证员工、评论单独GET，不将父权限推广到子资源。Jira locator保存完整SHA-256；兼容version为前15hex整数，非原生revision/非单调序号。事务中碰撞检测，最终当前读取还比较完整payload，不能因短hash相同复用旧正文。共同DelegatedAuthority保留Confluence接口/CLI兼容；不足：白名单按请求刷新、无后台worker/原子ACL事务/附件。可回滚Jira/general pilot改动，保留原Confluence基线。

## ADR-010 · 2026-10-05 · 本机操作员网页会话

为尽早联通真实reader与现有产品UI，提供单一已映射操作员的loopback入口：TTY隐藏输入→服务端验证native账户→随机一次性10分钟ticket→HttpOnly/SameSite/CSRF session。浏览器不接API token、user/role选择；每次业务读取仍验证源身份/权限。ticket是本机入口凭证，不入Git或截图，消费后不可复用；退出/重启需新入口。此方式只满足本机操作员试点，不能宣称员工OAuth/SSO或多用户生产鉴权；网页真实验收仍需实际执行。保持fixture demo独立路径，避免bootstrap入口让fixture身份转入真实API。无新增平台scope、费用或公开监听。


2026-10-05 ADR-010修正：8081实际已有operator服务，复现启动端口冲突；将监听socket预留移到隐藏输入前，避免重复输入token后才发现端口不可用。使用同一reserved listener，identity通过后才挂接application和serve，避免预检查释放端口的竞争窗口。固定阶段错误码代替统一失败，禁止异常原文/上游响应日志；不终止未知归属的已有服务，不改变身份/ACL验证。新增失败路径与资源释放验证；无新增外部调用。


## 2026-10-05 · AUTH-006 · eng_b Jira read-only pilot

用户明确“批准此范围”：必要时仅在免费额度内启用 eng_b 普通 Jira User；token `AI-Bang2 eng_b Jira read-only pilot`，2026-10-20 到期，拟用 `read:jira-user` 与 `read:jira-work`，无 write/admin scope。scope 覆盖账号可读 Jira 内容，程序另限 KAN 合成工单白名单。最终创建、密钥保存由用户完成；收费、条款或不同 scope 需要另外确认。授权不等于凭据已创建、API 已验证或 G1/G2 通过。

AUTH-006 执行限制：只读账单核验显示 Jira 已为 Premium 免费试用而非 Free；2026-11-04 到期，付款方式 None、未来估价 USD18.30/1 user。自动审批拒绝保存新增 Jira User，要求具体试用范围确认；配置仍未提交，不将拟选 User 当已授权访问，不自行购买或接受新条款。


## 2026-10-05 · AUTH-007 · existing Jira free trial User access

用户明确选择“批准仅现有免费试用期内添加 User”，覆盖当前 Jira Premium 免费试用内 eng_b 普通 User，至 2026-11-04；不添加付款方式、不购买、不授权付费续订，到期前人工降级或停用。解决 AUTH-006 执行时的自动审批范围拒绝后已保存，页面核验 Jira User。随后平台显示 Teamwork Collection upgrade 推广，关闭且未下单；不据此扩大资源/收费授权。Jira token 仍按 AUTH-006：用户最终创建/保存。


## ADR-011 · 2026-10-05 · 复用操作员进程中的 Jira 凭据

用户指出独立诊断命令反复要求邮箱/token 造成操作负担。每次权限重查不要求重复人工输入凭据，因此扩展现有 operator web 到 Jira，并保留默认 Confluence 兼容。token 只驻留服务进程，固定 source/actor、独立数据库、一用 ticket/opaque session，查询仍 native identity/current access 检查；不缓存允许决定、不读取密码应用、不持久化秘密。代价：进程停止后再次输入，当前每进程单源/单操作员，SSO/多源同入口后续实施。可单独回滚 --source Jira 分支。


## ADR-012 · 2026-10-05 · 导航时清除旧答案视图

真实Jira撤权后，后端query/citation/history正确deny，但Workspace导航复用之前渲染DOM，违反新访问不恢复旧内容的产品要求。选择导航清除答案/隐藏历史、query开始清除旧答案、preview失败清除相关视图；继续保存historyId以便服务端重查追问依赖。代价是返回Workspace需新问答或Recent answers获取重新鉴权的历史，不能保留不经检查的旧视图便利。不声称能消除用户已看到/截图保存的内容，也不承诺平台ACL变更瞬时推送。node frontend安全验证及真实会话重载后UI验证通过，无服务器重启/凭据重输。


## 2026-10-05 · AUTH-008 · Slack user read-only pilot

用户明确“批准此只读试点范围”：AI-Bang2 workspace T0C6FQ246TF 准备/安装 AI-Bang2 Read-only Pilot app，user scopes channels:read/channels:history/groups:read/groups:history；无 Bot/write/DM/files scope。首轮使用个人Google登录身份，程序另限合成频道/消息白名单，不接NTU Slack。10月20日前人工撤销试点 token；最终授权/密钥保存由用户完成，新条款/费用另确认。批准不证明实际安装或API/ACL验证完成。


## ADR-013 · 2026-10-05 · Slack 原生用户读权限与精确消息试点

采用固定 workspace、user delegation、channel type 与 exact message/root mapping；每读先 auth.test/info，再正文，无 bot/admin fallback。公开频道不以 is_member=false 伪造撤权，真实撤权使用 private channel；不支持的共享频道/附件/富文本 unknown，不静默剥离后声称完整覆盖。成本是首轮对象覆盖有限且重复原生检查可能遇限流，后续仍须 native root/reply/API 验证；可单独停用 Slack reader，不改变其他源。错配 source/reader 在构造时明确拒绝。用户最终安装遇应用创建限流，未创建成功/取得 token；保留审核页面，相关 live 任务 blocked，其他本地工作继续。


AUTH-008 补充（2026-10-05）：原生OAuth审核另显示基础identify与应用隐私/条款，已明确交用户审核；用户回复“授权完成”。授权/接受为user_confirmed，agent未点击Allow或读取token。Chrome更新后的列表实际已有四个同名app，选择A0C6F96HFNX继续，其他保留；早先“未观察创建成功”不代表未创建，停止重复新建。等待用户保存并离开token页。

## ADR-014 · 2026-10-05 · Drive 最小委托文本文件边界

先支持固定file→parent白名单的personal Drive text/plain UTF-8文件；about.user.permissionId/me验证当前用户，文件原生GET与canDownload而非本地permission列表授予权利，正文前后重复metadata排除读写竞态。验证size/MD5传输一致性，另保存SHA256证据指纹和headRevisionId/native version，不编造页码。缺点为暂不支持Google Docs/PDF/shortcut/shared drive、后台changes与完整继承传播矩阵；这是覆盖范围限制，不能当四源live通过。移出白名单目录unknown、删除/原生deny停止，网络/过期未知不放行。尚未申请Drive scope或使用凭据；真实OAuth/平台种植需具体授权。本地可回滚停用drive reader。


## ADR-015 · 2026-10-05 · Slack reply诊断与受限父消息响应

真实root问答通过但reply为统一unknown，尚未得到具体失败原因。增加只由固定枚举组成的unknown method，区别rate/scope/identity/argument和message selection，不存上游错误body/秘密。回复limit2且只允许exact target与预先allowlisted parent出现，父消息不替代目标、非白名单/重复/缺目标unknown；补两项边界测试，199全回归通过。此兼容只是候选修正，非实测原因结论；需重启原生API复验才能判断。代价为诊断需加载新代码/一次重新输入秘密，后续仍凭据进程内复用。四源安全要求不变。

ADR-015实测补充（2026-10-05）：用户重启后，受限父消息响应兼容实现的root/reply问答、引用与历史已native验证通过（web-thread-query.json），可保留此实现。未记录旧unknown响应内容，不把本次成功当旧失败原因的确定证明。未扩大scope或消息白名单，真实频道撤权仍待独立reader。

## ADR-016 · 2026-10-05 · 统一操作员多源入口

复用DelegatedQueryPilot与现有HTTP路由，使2–4来源在同一tenant/actor会话中检索。可信本地manifest记录身份映射已核对；该标记不是账号所有权证明，也不授予权限。所有source配置/actor映射/tenant先验证，缺少凭据才隐藏输入一次；全部native身份通过后才签发bootstrap，任一失败停止启动，查询时各源unknown/deny只隔离该源。同一历史含撤权依赖则不展示，新的独立查询仍可用其他授权源。代价是尚需人工核对跨平台persona，不能将现有eng_a和eng_b直接改名拼接；每进程独立credential/session/DB，SSO/OAuth refresh另行实现。可回滚停用multi入口，不改变单源行为。

## 2026-10-05 · AUTH-009 · Drive personal-account read-only pilot

用户明确选择“批准此只读范围，使用现有个人 Google 账号”，账号ssy44199@gmail.com；创建比赛专用Google Cloud项目，不启用Billing，仅启用Drive API，OAuth测试模式申请drive.readonly。该scope本身可读授权账号全部Drive文件，程序仅白名单合成文件；不读取个人资料，不扩scope，不付费。最终Google授权由用户点击，凭据按现有本地隐藏输入/进程内复用，不入Git/日志/浏览器。授权不证明项目/OAuth/原生ID/API/ACL完成。新条款或安全敏感持久凭据最终创建按页面另确认/交用户，不自行绕过。

AUTH-009执行补充（2026-10-05）：用户已亲自完成Google Data Policy确认/Create，UI核验OAuth配置成功；唯一drive.readonly配置保存、External Testing和单一test user已核验，尚未授权任何token。Desktop客户端在审核页准备，按UI AI-agent分类help标记agent用途，不创建standard-user第二客户端。最终Create/Download JSON交用户；不读取生成密钥页面，不新增write/profile/email scope或Publish/Billing。

## 2026-10-05 · AUTH-010 · exact Drive synthetic seed writes

用户明确“批准创建文件夹并上传这三份合成文件”，覆盖ssy44199@gmail.com个人Drive根目录AI-Bang2 Synthetic Read-only Pilot和D-01.txt/D-02.txt/D-03.txt，内容来自baseline fixture并标记SYNTHETIC，不修改已有文件/共享权限/公开分享。此前自动审批因只读scope授权未明确覆盖持久写入拒绝create_folder；这次具体确认后工具允许创建与上传。Google Drive plugin确认账号及种植读回，应用runtime仍只读。

## ADR-017 · 2026-10-05 · Drive Desktop PKCE loopback

为减少手动token复制，--oauth-client仅Drive/live入口支持，先预留operator端口并验证全配置，再读取用户下载的0600/no-symlink桌面client JSON。固定Google授权与token端点、唯一drive.readonly/S256/random state/10分钟/随机loopback端口，callback不记录URL/code，不反射秘密，拒绝错Host/Origin/state/重复/扩展参数，code单次交换。验证实际授予scope与Bearer/寿命，再about metadata-only核对me/emailAddress/permissionId，按可信配置绑定actor；login_hint不作为身份依据。秘密只进进程，忽略refresh token，不持久化、不读个人文件列表、无写权限/自动打开浏览器。代价：当前access token过期需重新Google授权，非员工SSO或后台refresh。11新模拟测试/全218通过，真实Google最终grant仍待用户，不能称live OAuth验收通过。可回滚--oauth-client分支，保留hidden token路径。

ADR-017修正（2026-10-05）：Google官方discovery声明authorization_response_iss_parameter_supported=true/issuer=https://accounts.google.com；旧callback未知参数过滤会将含标准iss的合成合法响应拒绝400，已复现。新增iss且必须精确Google issuer，缺失/错误/重复仍拒绝；不放宽state/PKCE/scope/账号。固定枚举诊断仅记录reason，不记录请求URL/code/上游body。旧真实callback未记录原因，因此此项是确定兼容缺陷，不是旧现场根因的已证实结论。参考https://accounts.google.com/.well-known/openid-configuration 与RFC9207。

## ADR-018 · 2026-10-05 · DeepSeek evidence selection and conservative accounting

AUTH-003批准的DeepSeek直连/合成-only/总USD20保持不变。实读官方pricing与chat-completions页面（evidence/runs/deepseek/price-review.json），采用deepseek-flash/非thinking/JSON/1024输出tokens；固定HTTPS端点，无redirect、tools、stream或自动retry。价格按peak/cache-miss输入USD0.30/百万和输出USD1.20/百万保守记账，不冒充发票实际费用；每请求预留整个1M上下文上限+输出上限，不将字节误当token。未知usage/timeout保持全额预留，使用既有持久USD20账本；所有operator共用.runtime/deepseek-budget.sqlite，不能换目录/删账本重置预算。账本只限制本程序，不控制账号其他客户端。

Engine原生鉴权链保持，模型只输出已提供evidence IDs，后端从当前授权证据组装完整原文，不允许模型输出新事实/URL/自授权限；重复/未知ID、额外字段、工具调用、截断/错模型均失败，已知usage仍结算。这个阶段是live model evidence selection接口，不是自由综合回答或效果已验收；遗漏相反/限制证据的语义完整性仍需真实效果验收，不能用引用校验代替。仅显式标记[SYNTHETIC的源正文可发送，不将该标记当身份/源ACL。价格复核限定SGT2026-10-05，启动与每次非空调用均校验；以后先复核官方价格再更新，不静默沿用。key一次hidden TTY进内存，不写文件/浏览器/日志，默认fake不变；旧服务不热注入或读取其进程秘密。独立新8086 Drive OAuth进程用于真实模型验收。

预算SQLite新增进程内RLock/check_same_thread=False以支持Web worker；跨进程仍BEGIN IMMEDIATE保证预算预留。回滚provider/--model入口不影响四源reader，必须保留既有账本用于核销。G1/G2仍待批准。

## ADR-019 · 2026-10-05 · Model budget receipt linked to server request

为解决首轮live只能按单一reservation现场关联的证据缺口，增量model_calls表与reservation/query_id关联在同一预留事务落库；Engine传服务端UUID，provider不从Prompt取identity/request ID。validated usage与保守成本结算原子提交，失败状态固定enum，无原始vendor body/key/问题/资料正文。成功generation_completed审计事件保存同一receipt；失败通过query_id连接request_failed。dispatched只代表持久化发送意图：called=None，不冒充已收到供应商回复；settled/validated usage才called=True，空证据called=False且不建reservation。旧reservation保持unlinked，不能事后猜测添加query_id。本地账本不是独立签名或供应商发票。新增getpass warning-as-error，不能降级为终端明文输入。迁移不修改已有预算/额度，回滚Engine/provider接线仍保留table/既有支出。

## AUTH-011 · 2026-10-05 · unified eng_b reader preparation

用户明确“批准按推荐范围准备独立读者”，账号674544786@qq.com，保留CF/Jira既有eng_b；准备该邮箱Google免费注册/登录、仅比赛AI-Bang2 Slack普通reader成员、现有三合成Drive文件folder Reader共享。后续Drive drive.readonly（该新reader账号全Drive平台范围但程序三文件白名单）、Slack channels:read/channels:history/groups:read/groups:history+identify同试点scope；不接NTU/DM/bot/write/Billing/公开sharing或增模型预算。最终password/OTP/terms/OAuth由用户亲自操作，新收费或不同权限另确认。授权范围已获批，不代表reader账户、membership、native权限/API或完整四源验收已完成。具体候选与接口见UNIFIED_LIVE_PILOT.md。

## ADR-020 · 2026-10-05 · multi-source Drive PKCE

统一入口--source multi允许--oauth-client；先读public OAuth mapping构造无credential reader，再全部source actor/tenant验证，才读取private desktop client并按需hidden其他source；Drive不手工复制access token。客户端无效先于人工输入，Google拒绝不能返回partial bundle，全部native身份通过才bootstrap。load_oauth_reader单源接口保持，拆分prepare/complete共享实现，无扩scope/自动persona合并。example默认identity_mapping_reviewed=false；AUTH-011未完成native身份确认前不改为true。5新mock配置/CLI测试通过；此前新增测试缺续行SyntaxError已复现修复，单独OAuth HTTP测试在沙箱bind拒绝，完整许可本机回归248/248通过（60local/188mock）。本轮未调用真实平台/模型、不重启旧服务。

2026-10-05 AUTH-011 amendment: user confirmed kyle000909@gmail.com as eng_b Google/Drive identity, replacing QQ Google registration; existing Atlassian identity retained. Cloud test user saved and exact synthetic folder Viewer sharing read back; general access remains Restricted, notification unchecked. This does not establish API identity or grant. Slack still uses the specifically approved QQ email pending membership.

2026-10-05 Slack reader invitation: native UI returned Unable to send / Couldn’t invite for 674544786@qq.com; cause not established, no membership claimed. Drive reader process started on8087 (fake model), OAuth waiting user final grant, credentials not entered or copied. Private screenshot reader-slack-invite-failed.jpg.

2026-10-05 AUTH-003权限测试执行：仅在已批准合成folder移除eng_b Reader以验证同会话撤权，再恢复相同Viewer/Restricted范围，无公开share、正文编辑或新scope。原生Drive版本因权限分享从3至4变化但正文hash相同，按保守原生版本校验处理，不把权限引起的version变化记为新企业事实。

2026-10-05 AUTH-011 Slack amendment：用户明确批准eng_b Slack也用kyle000909@gmail.com，限AI-Bang2工作区和合成私有频道，原四项user只读scope+identify，不接NTU、不新增付款或写scope，最终terms/OAuth用户点击。QQ邀请失败原因未知，新Google邮箱邀请UI显示You’ve invited 1 person/Invited as a colleague/Expires in30days；仅邀请成功，尚未入组或授权。

2026-10-05 Slack reader OAuth准备：保留既有私有app原生install_redirect流程，未启用public distribution、未新增redirect或读取client/signing secret。用户既有Google登录用于主账号添加已批准的内部reader成员，随后仅Sign out切回reader，明确未选择leave workspace。只有最终Allow授予读权限，由用户操作；固定eng_b原生ID映射将在启动auth.test再次校验。参考Slack官方OAuth说明：https://docs.slack.dev/authentication/installing-with-oauth/。

2026-10-05 AUTH-011边界补充：普通Slack reader成员与只读OAuth批准不包括app Collaborator开发后台权限。平台在Allow后要求Collaborator，采用grant未知/token后台blocked记录，不默认新增权限。临时协作者候选仅kyle000909@gmail.com与app A0C6F96HFNX；其可管理app设置，因此另行征求明确授权，未批准前不执行。

2026-10-05 AUTH-012：用户对上一项明确候选回复“好的，可以”，批准kyle000909@gmail.com临时成为existing app A0C6F96HFNX Collaborator，token保存后移除。native UI候选及名单均确认U0C66B76TE3。平台明确可edit/submit/delete app、full member可管理collaborators；本次未修改scope/public distribution/付费/工作区admin。移除尚pending，不把临时developer访问视为业务资料可读证明。

2026-10-05 用户报告eng_b Slack token保存并离开密钥页；agent未读取秘密。按AUTH-012从已核对U0C66B76TE3自己的Collaborators页面Leave，native确认移除后Your Apps不再列出该app；未退出工作区/频道、未卸载业务OAuth grant。截图private/slack-reader-collaborator-removed.jpg。四源public配置均加载校验同tenant/actor，Drive映射kyle000909@gmail.com、SlackU0C66B76TE3与既有QQ Atlassian对应用户已确认persona；创建ignored0600 operator-bundle.json（mapping reviewed仅表示账号映射审查，非API验收）。下一步一次启动8088 multi+Drive PKCE+DeepSeek并逐source native identity强制核对。reader Slack API/统一live问答/撤权仍not_run；没有新模型调用。

2026-10-05 AUTH-013：用户明确“先做阶段性收尾，然后push和合并代码到main，我要睡觉了”，批准推送本开发分支及经验证的PR合并main；不扩大为部署、G1/G2、提交比赛或私有工具对话截图上传。保留队友未跟踪文件。

2026-10-05 ADR-020：修复网页用evidence数量推断模型调用的问题。将经过request_id/usage/state校验的既有回执随response保存，界面按显式called显示调用标识、token和保守费用估算；旧记录缺回执显示not recorded，不回填、不称vendor invoice。回执不新增授权，撤权历史整条隐藏。代价是旧进程未加载Engine新增代码时回执仍unknown；回滚可移除展示和response投影，账本/原有权限边界不变。

2026-10-05 ADR-021：旧generic配置/hidden错误无法区分输入失败，且有效邮箱随token失误被重复请求。引入固定受控reason enum和每字段最多3次本地重试；保留现有输入格式及安全TTY约束，不重试平台API、不缓存/persist秘密。原现场细分根因未记录，修复提供下一次可靠诊断，不声称已确认原用户输入。


2026-10-05 AUTH-014：用户明确回复“批准本机钥匙串保存与程序复用（推荐）”。批准本项目本机程序保存并复用已审核 eng_b 的 Confluence/Jira authorization（含邮箱）、Slack reader token、DeepSeek key、Google 已批准 drive.readonly 返回的 refresh token（若有），限现有 persona/native account/平台及模型预算。仅创建/读写 app-owned macOS Keychain 项；不读取用户已有「密码」条目、不写明文文件、不扩 scope/费用。不授权部署、G1/G2 或上传密钥。本项明确覆盖此前仅内存保存限制，默认 memory 模式仍保留。

2026-10-05 ADR-022：重复启动丢失全部人工输入造成操作负担；增加显式 --credential-store macos-keychain 与 make live，直接调用 macOS Security.framework Generic Password API，不经 shell 参数传密钥。按 source/tenant/actor/native account（Drive 为 client ID+email）隔离；源凭据格式通过即逐项保存，后续失败不要求已保存项重输，平台真实性仍由每次启动及请求的原生身份/权限检查决定。DeepSeek 构造校验后保存；Drive 固定 scope 的 offline OAuth 获得 refresh，核对原生账号后保存，重启刷新并再次核对身份；invalid_grant 才要求单独 Google 重授权，其他错误拒绝。--replace-credential 仅忽略并更新指定平台旧条目，不预先删除。拒绝/锁定钥匙串不降级明文。

钥匙串提供 OS 加密保存和系统访问提示，不是同机同账号恶意进程隔离或企业凭据服务；Python 内存不保证安全擦除。现有已下载 OAuth client JSON 仍按原批准保留为 ignored 0600 文件，本次不另写 token 文件。运行中 access token 到期仍 fail closed，可重启刷新；不承诺永久有效。回滚为 --credential-store memory，既有 app-owned 条目不会被自动删除，用户可用「钥匙串访问」按 AI-Bang2 pilot v1 / 平台删除。依据：[Apple Generic Password API](https://developer.apple.com/documentation/security/seckeychainfindgenericpassword(_:_:_:_:_:_:_:_:))、[Google native-app OAuth](https://developers.google.com/identity/protocols/oauth2/native-app)。实际四源 Keychain 复用/真实 Google refresh 尚 not_run。


2026-10-05 ADR-023：真实四源 eng_b 启动成功后，首个联合请求5b6b37e3e7074d62b95ee563333dbdb1读取8个对象、四源均allow，却在模型网络发送前失败（43.07秒，ledger无该query行/无费用）。实读DB确认Confluence C-01/C-02及Jira J-02正文使用原批准的完整 SYNTHETIC COMPETITION TEST DATA banner，旧DeepSeek guard仅接受方括号标记。保留旧标记路径，新增完整banner+按source匹配明确Fixture ID的窄兼容，不改正文/引用、scope/预算/授权断言；标题标记单独不放行。两个新增安全案例覆盖三个已种植版本及缺失/错源/错ID拒绝，268全回归通过。原文来自已批准比赛空间，非企业数据。证据live-unified/first-query-failure.json；失败记录保留，修复后真实重跑待用户只重启make live验证Keychain复用。


2026-10-05 ADR-024：已批准原有GET export端点尚无产品入口；新增Export answer按钮，每次调用后端重新鉴权后才生成下载，unknown/unavailable不创建Blob/文件，先清除旧显示。不使用预先生成下载链接或答案缓存。首次真实文件比对失败，发现JS parse/stringify舍入大整数Jira/Slack version；修复为解析结果仅校验访问与request ID、下载后端原始JSON envelope，Node byte-fidelity断言及实际下载逐字段与服务端持久记录匹配。合法下载副本之后不能撤回，UI注明这一边界。

403不直接等同session失效：额外检查既有/api/session，仍有效则保持身份并隐藏被拒绝资料；session也403时清除旧内容/preview/history ID并提示最新operator入口。默认不重启服务、保存新session或自动获取凭据。真实撤权后export不新增文件、旧citation拒绝并保留eng_b登录均实测，未因Chrome自动API导航blocked关闭安全设置。沿用原GET endpoints/权限契约，回滚只移除前端入口与错误提示；不削弱后台鉴权。


2026-10-05 ADR-025：统一真实问答53.37秒，原link_seed为每个没有links的候选完整读取原生对象，却没有关联可以展开。仅在links非空时执行这一专用于展开的检查；本次模型前、模型发送前、返回前以及采集当前权限检查不变，不缓存权限、不并行绕过原生鉴权。有links路径仍按原流程检查。mock计数5→4仅证明读取数量下降，真实耗时受网络影响，尚未重测。首次Slack安全测试以第5次读取模拟撤权，优化后注入落到模型之后；改为绑定实际model_dispatch第二候选，保留模型不调用和request_failed断言，原失败报告保留。回滚为恢复无条件link_seed检查；不涉及scope、预算或外部权限修改。


2026-10-05 ADR-025验证补充：使用可信本地git archive基准1ba796b及优化8d4ba6b两个临时operator，各自工作目录与SQLite隔离、端口8090/8091，fake model控制模型费用和延迟变量。程序复用AUTH-014自己保存的条目，stdin DEVNULL确保不依赖人工输入；Drive固定只读refresh与native身份核验实际通过。stdout只在内存提取reuse标记及一次性入口票据，不输出/保存ticket、OAuth网址或cookies，缺授权即停止。单样本53.209→40.116秒，不作稳定性能承诺。当前用户8088无重启/数据库混入假模型记录；测试结束仅停止自己进程。


2026-10-05 ADR-026：原文选择不够简洁回答跨源业务问题；采用显式opt-in综合模式，不将任意模型文本当已验证企业事实。生成输出严格claims/text/evidence_ids/supports契约，服务器匹配每个连续quote和当前授权证据；单独同模型prompt/call按全文逐结论判断支持关系，全部true才接受，未知/错误/范围缺失拒绝整答。两次请求共享已批准预算账本并分别预留/结算；review_dispatch重新检查全部selected当前原生权限与版本，任何撤权则第二调用不发，返回前再次检查。独立调用不是独立模型或信任域，同模型偏差仍可能共同漏检；精确quote仅证明出处，不证明语义。人工质量/G1仍必须进行。

代价是一次额外模型调用与一轮源检查，实际四源综合单题58.95秒，不能沿用fake-model40.12秒宣称综合性能。原文模式为默认，回滚选--answer-style excerpts，无需新scope/token/预算。首题三源7input未达四源探针要求，改变问题以真正询问Jira code fix状态后通过，未更改失败断言或补写通过。关键词检索覆盖仍为限制，不能据两題断言完整语义检索。模式专属安全contract/mock与真实合成证据分别记录。


2026-10-05 ADR-026安全验证补充：为避免向真实四源写入恶意资料，用授权本地fixture ACL及明确SYNTHETIC内容验证真实模型行为；固定eng_b、C-02可读，私有S-01不可读。复用AUTH-014保存的模型key及既有ledger，模型只收到当前fixture授权资料。此模式是fixture_source_live_model_synthesis，不能作为平台原生ACL/真实四源安全的替代。已检查确实有malicious input、只有固定模型endpoint、无tools和agent语义输出；模型安全单样本有效、额外无关但受支持结论记录为相关性缺口，不提高完整P-11/G1声明。


2026-10-05 ADR-027：API返回时权限允许不代表前端响应仍属于当前会话/视图。实际Node复现expiry后迟到preview重开旧正文；新增单调viewRevision及session对象引用检查，导航/注销/expiry使旧请求失效，成功或错误旧响应不改DOM/history_id/按钮状态或创建导出文件。业务权限仍由后端当前检查决定，前端token不是权限授予。请求已发送不能撤回模型处理/费用，逻辑丢弃不声称服务器取消。页面快照/合法已下载副本不能撤回。回滚去掉前端guard但会恢复已复现竞态，故不建议。

综合UI启动沿用既有只读授权/Keychain/USD20；8093独立进程入口只在内存并经0600Unix socket预备移交，但CUA的EPERM阻止读取。按工具限制停止自有进程，不改安全设置或把票据写明文文件；改为用户本人从正式终端打开新一次性入口。Makefile LIVE_PORT只是本机端口选择，默认8088与鉴权机制不变，不公开网络监听。


2026-10-05 ADR-028：真实8094综合UI回答fa3abd9a700a4520b479c65a255803be的4结论均有原文支持，但遗漏用户明确问到的运行保障；同模型v1逐句支持复核不足以证明问题覆盖。v2生成优先覆盖所有问题部分/合并重复结论，复核增加严格boolean question_covered；false、missing、unknown及非boolean整答拒绝。保持精确quote、全部原生授权阶段与原预算，既有claim_format不变，model名称v2区分运行版本。首轮v2真实复核output_rejected，原始verdict未捕获，具体拒绝原因未知；第二次实读输出多ID缺对应quote，模型前端契约拒绝且无review，不修补/臆造quote。补充生成提示显式要求ID列表等于supports对应ID、优先少量必要引用；保持服务器断言。失败记录保留，模型复核和coverage仍是同模型的可错判断，不是确定性语义保证。无生产自动付费重试；开发重测使用既有批准的合成源/账本。回滚v1会恢复已观察漏答，不建议；默认原文模式不变。

ADR-028验证补充：修正后隔离真实四源11checks通过，保障措施有C-01精确quote，模型覆盖判定true，agent对照本题所有请求部分。两次失败未删除或标通过；前三claim仍重复，模型判定不能替代人工质量/G1。用户服务不被自动终止；v1历史记录保持原model名称/回执，不回写成v2。


2026-10-05 ADR-029：8094新页面初始DOM为eng_b，但查询后session-ended；具体原因未能区分过期/重启/cookie覆盖，不记录为已确定归因。双本机HTTP服务器+真实共享CookieJar明确复现原session同名覆盖导致第一端口403。按绑定server_port选择aibang2_session_{port}，签入/认证/退出一致，只接收本端口cookie；旧session cookie不回退。保持随机token、server session/expiry、HttpOnly/SameSite/Host/Origin/CSRF及来源权限不变。Cookie名字防止意外冲突，并不能隔离同hostname恶意本机服务（各端口仍可能收到其他cookie），不是SSO/生产信任边界。依据[RFC6265 §8.5](https://www.rfc-editor.org/rfc/rfc6265#section-8.5)。5针对性HTTP测试及283回归通过；Chrome自动打开fixture8098被blocked，保留browser not_run，没有绕过保护。只停止自己的8098/8099，未改变Slack成员。回滚恢复同名cookie会复现端口覆盖；旧服务必须重启后用最新入口加载，不读取凭据或令失效session复活。


2026-10-05 具体综合撤权授权：用户明确批准C0C6R70SGG4私有合成频道/U0C66B76TE3（kyle000909@gmail.com）本次临时移除，验证8094 eng_b旧综合引用/history/export，然后恢复原访问；不改工作区成员、角色/token/scope、不新调模型。第一轮已执行并恢复Members2/同一UID；旧preview原生deny清除答案，history隐藏含Slack的综合supports/双回执，其他独立答案保持。由于拒绝旧引用会清除该旧导出按钮，额外第二轮旧导出测试被自动审批拒绝（认为上次只批准一个循环），需单独明确批准；Remove最终按钮尚未执行，原访问仍恢复，未绕过拒绝。

具体授权补充：用户单独批准第二轮同一member/channel的旧导出测试及恢复。已原生2→1→2，旧export返回unavailable、不建文件（0→0），旧正文/quotes/receipt清除而session保持。最终原生核对同一U0C66B76TE3、Members2，之后合法raw导出8146字节与存储答案逐字段一致。未改role/token/scope，未新调模型；审批拒绝未绕过。
# 2026-10-05 ADR-030: isolated lifecycle acceptance

2026-10-05 ADR-031 / AUTH-003执行：补齐既有合成Jira项目KAN的J-03，原生KAN-5/10014，In Progress，完整SYNTHETIC banner及Fixture ID；无新增成员、scope或费用。Maya作为虚构scenario owner在正文标记，native assignee明确Unassigned，不冒称真实账号。eng_b原生metadata及正文读取allow后，仅将该工单加入ignored本地白名单，保留旧配置备份；现有8094进程不重启，下一启动读新配置。DeepSeek guard只增加jira/J-03完整banner配对，错误source/缺banner仍拒绝，扩充原测试subtests（方法数仍283），无任意种植资料默认放行。真实综合一题覆盖全部工程要求事实及四源引用；双调用1856microUSD保守记账，同一USD20ledger。不是原eng_a/product_ops全矩阵或人G1，关键词检索/RAG质量仍待增强。

2026-10-05 AUTH-015：用户对具体候选回复“批准”，允许C-01（Confluence98564）临时改为fixture已定义runbook v2、验证后恢复原正文；允许在已批准Drive合成文件夹创建明确SYNTHETIC临时测试文件、加入本地只读白名单、验证后移至Drive废纸篓并检查旧引用/历史失效。不得删除原三文件、改变共享、增加scope/费用；发现第三方并发修改则停止恢复。本授权不代表G1/G2或发布批准。

AUTH-015执行：管理员UI操作CF正文与Drive临时文件回收，程序始终仅eng_b只读/已批准Keychain refresh，fake model无runtime费用；隔离SQLite与临时Drive白名单，不修改用户8094/bundle。CF原文恢复API严格相等，native1→2→3；Drive temporary native1eM_6RUZ8y130l9B0WKrSs3GkGu6rjbUZ移入回收站，原三文件保留、共享未操作。Chrome file URL权限blocked后没有扩展权限或旁路上传，由用户本人拖入。首个CF探针误取Evidence.native_id导致KeyError，保留audit失败事实并修正resource_id定位；初始脚本PYTHONPATH未设的启动失败发生在读取凭据/平台调用前。未改应用代码/有效安全断言；未测后台同步时延/HTTP导出/真实模型/人工G1，边界保持。

用户授权继续所有可推进工作，不等于新增外部写入、公开开放或人工G1/G2通过。采用独立内存fixture世界逐source/operation执行12组生命周期检查，不改变正在运行的8094、真实资料、钥匙串或模型账本。旧索引故意滞后，验证当前权限/版本独立保护模型、历史及引用；更新发布后核验新版本，撤权/删除不重建正文。结果明确local subset，导出仅共享backend projection，不冒称本次HTTP/browser验证。首次探针把用户question中的marker误当模型证据泄露，保留失败报告，修正为只查evidence；有效断言保留。另整理团队安全观看清单，人工批准继续not_run。回滚可删除独立runner/Makefile入口，不影响runtime。


2026-10-05 ADR-032：现实现按整篇16000字符budget跳过长文，不能检索后段事实。无新依赖/服务，改为本地固定2400Unicode字符/400重叠窗口；每资料最多3，总24证据/16000字符，短文<=4000保持旧ID；长引用resource@version#start:end只接受该版本规范窗口，locator.text_window记录单位/策略，正文为原文精确连续切片，不合并权限对象、不补写标题/标记。所有模型/复核/返回阶段仍按资料当前native权限与version检查，preview/history/export重新鉴权；content/ACL增量契约不变，窗口按已发布版本即时派生，无独立向量索引。小型通用英文aliases改善已知词汇变化，不宣称语义检索。代价：固定窗口可截句/重复，部分资料预算先后可能影响召回，仍全量本地扫描，不保证规模性能。DeepSeek synthetic-only严格检查未改：缺真实marker的晚段窗口拒绝调用，不能为了方便把源头标记复制进原文；真实长文模型另需可审查的来源边界实现及验收。回滚engine窗口入口即可恢复整篇模式；已存片段历史若回滚不可解析，安全拒绝，不迁移旧记录为伪原文。无平台写入/新收费/用户服务重启。


2026-10-05 ADR-033：依用户确认按验收缺口/依赖/交付风险排序，先补产品业务问答和审计候选，不因讨论RAG而无限扩展技术栈。复用AUTH-003/014已有eng_b四源只读/自己的Keychain与原USD20ledger做产品问答及无证据控制，无外部写入/新scope/凭据要求，不能据工程身份替代product_ops原生权限。新增opt-in验收runner，禁止覆盖现有live证据；实际harness漏改mode留下fake_model后缀，但model名/独立ledger/真实读者阶段明确是真实综合，保存原回答/hash链与实际执行源码，修复未来runnermode而不篡改历史或重复收费。离线import真实合成audit副本，以显式test auditor验证查询和CodeBuddy独立validator签名边界；临时同机privatekey自动删除，不将机制证明当生产独立保管或live审计认证。候选五场景矩阵与缺口集中维护，人工G1/G2继续not_run。


2026-10-05 干净归档首次重建失败事实：295测试中native_identity_failure安全stage案例mock Store(:memory:)却让main chmod磁盘路径，依赖本机已存在的confluence-web.sqlite，干净archive返回local_store而非期望native_identity。保留rebuild-candidate失败日志/报告；测试改用独立TemporaryDirectory中的真实SQLite，仍注入原native失败、保留server不serve/close一次/受控错误不含上游秘密全部断言，并实际检查文件0600。不改应用授权/失败分类、不预置本机凭据、不删除或跳过有效测试。需新commit干净archive重跑后才能宣称可重建。

干净候选修复验证：e9a55e6 archive实际295通过、5local场景/Node/fixture进程HTTP前后端通过，记录rebuild-fixed；只终止自有临时服务并清理自有临时目录。原失败证据保留不标通过。原source真实问答和后续本地重建模式分别列，不据HTTP smoke宣称browser/G1。当前未推送/合并，最终文档证据提交不改变被验证的应用/test代码。


2026-10-05 ADR-034：S-05 UI原来同页面并发查询只校验view，旧query/page响应可以覆盖新scope，Node先复现后修复。新增局部inquiryRevision，分页闭包持有该query的filters/as_of，旧response/error不能显示，next disabled防重复、错误可重试；backend audit role/scope/参数化查询不变。render audit事件区分candidate/authorized/model input/review/cited/stored/delivery，不把调用等同已读；所有资料用textContent无HTML执行。对unsafe JS整数显示查看后端/字符串evidence ID的提示，不伪精确或改原始记录。UI不验证独立签名，明确说明；Node模型DOM证据和Chrome blocked/visual not_run分别记，停止自有临时fixture不影响8094。回滚前端会恢复已复现scope混淆，不建议。未新增scope、账号、模型或费用。

2026-10-05 ADR-035 / AUTH-003执行：在既有比赛合成空间按fixture C-03新增557057，Restricted仅现有owner（不新增账号/权限，不修改C-01父页正文或访问）。只读验收实例显式仅557057/164283，复用AUTH-014 app-owned eng_b Keychain，用户配置和8094不改。受控本地stale synthetic索引来自已知owner UI文字，不冒称eng_b成功采集/真实旧授权历史；其保留时native refresh与preview拒绝，证明当前源权限与检索独立。第一次probe以fake generate次数当网络调用次数，实际负面空evidence也执行fake生成；保存失败/harness，改为断言负面空证据与唯一正面证据输入，13checks通过。未删安全断言或放宽runtime；无模型网络/费用。C-03 guard未加入DeepSeek允许集，因为本轮无授权把受限源发给模型。未测原contractor/fullpersona、统计时间边界/G1。新增验收脚本可删除回滚，不影响runtime；外部synthetic seed保留用于复测，删除另按恢复流程，不擅自操作。

2026-10-05 b541c02重建记录：第一次sandbox run因loopback bind EPERM产生23HTTP errors（297总），非应用断言问题。保留rebuild-native-restricted；经现有本地测试授权提权运行同一提交，setup/297tests/5fixture/2Node/HTTP smoke通过rebuild-native-restricted-approved。未删除有效测试、关闭安全设置或修改runtime；无源/模型调用。

2026-10-05 ADR-036：S-05原前置要求成功/部分授权/拒绝/失败，原captured-live stream未覆盖全部。增加独立fixture Engine请求和request-boundary事件ID oracle，不用inquiry过滤逻辑生成expected；引入page1之后真实新fixture请求验证as_of固定及scope/actor噪声。失败fake model明确注入并保留request_failed/无成功存储。既有CodeBuddy签名CLI复用，无伪造腾讯工具新增贡献；本机临时key删除，不冒称custody。验收输出拒绝覆盖已有目录，原runtime不改。团队单次观看流程集中在SAFETY_REVIEW，记录仍由实际观看产生，不因信任/自动结果标G1。新增runner/Makefile可单独删除回滚，无external权限/费用。

2026-10-06 ADR-037 / AUTH-003执行：用新建独立KAN-6合成工单验证内容更新，避免改已验证baseline KAN-4/KAN-5。仅owner UI写正文，程序只读eng_b既有授权；metadata-only exact key discovery后显式两ID whitelist，独立索引、无原bundle改动。Jira content fingerprint比较用相等/不等而非数字新旧；native/current history/preview保护与refresh证据分离。13checks通过、6guardtests；原源码/harness/hash/UTC timestamps保留，新加坡日期Oct6不回写audit。新临时工单留存Revision2，不删除或扩DeepSeek synthetic guard，不据新增fake模型测试说全live通过。

2026-10-06 独立产品读者接入候选：existing2918379149@qq.com Confluence-only只读scope/Oct20到期/token label及app-owned product_ops Keychain复用，见PRODUCT_READER_PILOT。AUTH-005/014仅eng_b不能推断新账号持久凭据已批准；具体确认已发送，未获答复不创建/读取新token或改平台权限。现有candidate映射须native current-user核验，不用eng_b冒充，C-01/C-03若实际allow即隔离失败。

2026-10-06 AUTH-016：用户对PRODUCT_READER_PILOT的具体确认回复“批准”。仅existing product_ops/2918379149@qq.com Confluence token，名称AI-Bang2 product_ops Confluence read-only pilot，Oct20到期，read:page:confluence+read:content-details:confluence；显式C-01/C-02/C-03合成白名单，不新增成员/业务写/admin scope/费用。同时批准confluence/aibang2-live-pilot/product_ops/已核验native account的app-owned本机Keychain保存复用，首次隐藏输入，禁止现有Passwords读取/明文存储；不扩Jira/Slack/Drive/DeepSeek账号。最终密钥创建/输入由用户完成，原生current-user核验后保存，错误身份不得persist/fallback。此授权不代表native验收或G1/G2完成。

2026-10-06 ADR-038：现CLI Keychain仅multi会迫使新获批Confluence产品读者重复输入。按AUTH-016最小扩到Confluence-only（其他single source仍拒绝），source loader保存新key前先native current-user核验，saved每启动同样核验，不读Passwords/不回退env或其他actor。单源Keychain数据库按actor/tenant/native account摘要分离并chmod0600，避免与旧confluence-web混用；multi/default memory行为保留。wrong source replacement拒绝。6新测试覆盖正确身份前后持久化、OS拒绝、错native不保存、saved无TTY和实际CLI重复启动/隔离；307全回归通过。浏览器已交接产品账号登录，未创建token/native权限验证，不能从mock通过推断live。回滚只去掉single CF opt-in会恢复重复输入需求，不迁移旧credential/DB或修改原8094。

### ADR-039 · Explicit new question after native product reader check (2026-10-06)

Evidence: browser security question immediately following product capability retained authorized C-02 through existing history_id dependency supplementation; an independent query correctly refused. Add New question action to clear history_id, composer and stale views, preserving session and explicit follow-up behavior. No authorization/model/retrieval relaxation; viewRevision discards delayed old answers. Node race checks cover dependency clearing and delayed response. Revert is limited to UI/button/tests; no schema/data migration or new fees/scopes.

### ADR-040 · Independent questions and no answer downloads (2026-10-06)

用户指出主界面独立问答外观与自动history_id依赖不一致，且无需求依据的下载扩大不可撤回副本范围，并明确批准纠正。选择独立问答：前端移除historyId/New question，HTTP拒绝history_id，Engine不查询旧run/补充依赖（旧本地harness参数仅兼容忽略）。删除Export answer/Blob生成/GET export路由，登录后直接请求返回404。保留历史、引用、逐模型阶段授权和原生撤权测试；旧导出断言替换为端点关闭断言，不再因测试需要提供下载。已合法保存的副本无法远程回收。覆盖ADR-024导出UI及ADR-039新问题按钮；如未来引入聊天或导出须作为明确产品变更，而非验收便利。无schema迁移/新scope/费用。运行中Python旧进程须重启；静态页面刷新只更新前端。

## AUTH-SEMANTIC-WORKSPACE-20261015-24-USD1

User approved LIVE_PLAN.md scope: existing four-source synthetic data read-only; three defaults and six paraphrases, false premise and existing conflict; independent automatic grant semantic-workspace-validation-20261015; max 24 DeepSeek calls and USD1 within original USD20 ledger. Preserve historical unknown; stop new unknown; no paid retries, human allowance, native writes, deployment or production restart. Freeze candidate and native oracle before calls.
