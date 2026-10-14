# 完整段落选择契约候选 · 2026-10-13

状态：已实现并冻结v1；原生三题事实通过，12开发案例机械事实通过，整体质量尚未验收。AUTH036，沿用原DeepSeek provider和预算，无新增出口。

当前source-review已经由程序逐字构造所有claim，模型仍返回逐claim的supported/responsive和两个覆盖布尔值。原Q1 none误删措施或拒绝，low又用6631推理tokens。新候选改变任务接口：服务器先证明每个来源全文都由精确连续claim构成，再让模型选择完整段落别名，返回selection_safe与question_covered两个严格布尔；不生成事实文本、引文或URL。selection_safe包含原支持审查的实体/属性/适用范围/限定/反证和过滤后独立可读义务；question_covered保持请求所有可支持部分，未知状态必须由同主题证据明确保留，顺序未知仍由原notice承认。此变化不将逐字相同当作语义覆盖证明。

输出仅 `{selected:["P0",...],selection_safe:true,question_covered:true}`。严格字段集合、别名映射、唯一性、两个true、非空选择、必要措施段落集合；任何拒绝不修复、不补造模型结果、不自动重试。别名由本次授权Evidence生成，最终证据ID和URL仍由服务端映射。完整段落不能裁掉尾部限定或表格列。旧模型解析器/有效断言不改；历史反例继续保留。

安全边界与single-dispatch一致：本地构造后对完整selected当前权限/版本复核，再进行唯一模型调用；最终交付和History/预览继续鉴权。新增类必须进入服务端精确类型白名单，不接受模型自称能力。默认legacy，显式whole才启用。

验证先证明全文构造/未知别名/不完整或unsafe/遗漏必要措施/构造期和review后变化/账本/History正确，再消耗一次原Q1诊断调用。只有业务核对通过才扩至Q2/SCOPE；若失败，不立即叠加同类提示词重跑。模型布尔只是运行过滤器，冻结业务oracle及后续多案例验收仍是质量依据，不冒充独立语义证明。


## 实际结果与限制

583项完整本地25.842s通过；其后加入冻结验收运行器，13项相关测试0.191s通过，包含真实本地GoalLedger/model类构造、原账本结算、新unknown保留reservation并停止第二题。此13项与583重叠，不相加为总数。

同一组合pooled/4/whole/none8192/single/history batch：Q1 HTTP8.841760s（模型1.083367s，1962输入/35输出tokens），Q2 7.553300s（模型0.956537s），SCOPE6.387779s（模型0.719199s）。Q1六段文本与上一low候选完全一致，保留实际措施与未知最新顺序；Q2四段保留Done/In Progress/pilot-GA，去除多余readiness段；SCOPE保留pilot、GA未批准及发布日期未知。这三次不是p95、浏览器或3秒达标证明。

冻结文件CANDIDATE_WHOLE_V1.json保留代码/输入/配置/题目hash，运行器每题前再次校验，不修改原PLAN。service9d26fabd2fa7已加载包含验收运行器的同业务实现；之前诊断servicecc8f520391dd保留。12个已知作者开发案例完成，10次实际模型调用、两例无证据/受限0调用。模型案例完整本地时间0.616–0.913s，不包括原生API。机械oracle通过只说明固定事实和权限探针，主Agent逐条读最终答案另保留semantic-review.json。

复核发现business_16实际根因正确，但返回了冗长无关archive和断句窗口；business_03保留withdrawn/accepted事实但没有自然语言明确纠正rejected前提。这些限制不能因机械通过被抹去，最终质量状态仍incomplete。冻结v1保留，不继续付费重复同一已知缺陷。下一候选如改变结构切块，应使用新标识，并保持v1为已见开发对照，不声称盲测。

浏览器工具本轮createBrowserTab访问127.0.0.1:49161返回net::ERR_BLOCKED_BY_CLIENT，未尝试其他路由绕过；前端提交到完整渲染验收blocked。native最终冷/热/三并发未运行；G1/G2未替代。

截至本轮Goal21次模型，新增账本结算USD0.046237，新unknown0、旧2保留。最终fixture额度已用10实际调用，原预留24尚余14；native最终12未用。这里只记录实际分配，不改变总60/USD0.50授权上限。回退whole输入到covered或legacy需要显式加载对应已记录配置；不会回退账本、计数或历史。
