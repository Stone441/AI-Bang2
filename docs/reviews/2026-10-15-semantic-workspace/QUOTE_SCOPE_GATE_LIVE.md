# Quote-scope gate live result

## 2026-10-16 修正执行器后的真实引文对照：负例漏检

明确批准后，以冻结3f17ec6执行新独立semantic-quote-gate-fixed-20261016 grant。第一项short_quote_scope一次HTTP200，8.575秒，1次审查调用，USD0.000782账本估算，无新unknown、人工额度未变；原USD20账本和旧pending保留。

模型返回合法无重复字段JSON，三个reasoning标志和part verdict全部true，claim verdict明确supported=true、responsive=true，审查被接受。负例只有“Follow-ups: PAY-102 and PAY-103.”短引文，却声称来自final payment-service postmortem；模型仍从完整原文补足所选引文未包含的限定。相同出处问题使该结论本身responsive，本次失败明确在引用支持粒度，不依赖上一轮“无关背景”的判定。

独立核验fail后立即关闭，正例及原11题全部not_run，无重试。诊断适配器没有将结论作为用户答案展示。此结果证明本次提示修订没有排除已知漏检；不证明模型永远不能判断，也不代表其他题失败。下一步不能继续仅追加相似提示并要求付费循环；需要可验证地隔离“引用蕴含”与“全文覆盖/冲突”的不同审查输入，评估调用成本及对跨源综合的影响，或明确保留当前质量限制。不能用确定性关键词匹配代替语义支持、移除原文冲突检查或删除有效验收断言。

证据quote-scope-gate-live-results.json，当前运行试用页未切换。Goal未完成。
