# Full isolated synthesis acceptance result

## 2026-10-16 完整v4验收：首题引文审查拒绝，按规则关闭

用户批准最多66调用/USD1后建立新独立semantic-isolated-full-20261016 grant，冻结5ff40c6。原默认部分题一次HTTP200，15.548秒；生成格式有效，claim_index0的隔离引文审查true，claim_index1明确quote_supported=false/quote_review_unsupported。没有进入全文审查，产品返回evidence_only、claims为空；其余10题not_run。进程正常退出0，grant已关闭，无重试。

3次调用（生成+2次单claim审查），USD0.001872账本估算，无新unknown、人工额度未变，原USD20账本及旧pending保留。鉴权11.273秒、生成传输2.304秒、两次引文审查传输合计1.888秒、检索排除鉴权0.018秒、其他0.062秒，单样本无SLA/p95结论。native history/citation/audit角色检查见isolated-full-live-results.json；浏览器本轮not_run。

实际证据只证明新增隔离审查在真实生成流程中触发并阻止草稿展示，不证明第2条结论一定错误：拒绝草稿未保存，不能还原其精确结论/引文，也不能仅凭210输入token等相似性断言是先前的postmortem出处问题。不得把模型false当作独立真值或将该题记为通过。完整11题质量目标仍未达标，现用试用页未切换。

下一步应先补足隔离、默认关闭的诊断证据：在明确的合成诊断范围内绑定实际claim/quote与当前原文版本，使人工能判断是真拦截还是误拒；不应在缺少失败内容时继续猜测修改提示或自动发起付费重测。历史结果、关闭grant和全局账本不得改写。
