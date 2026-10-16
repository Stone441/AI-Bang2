# Review schema candidate live acceptance

## 2026-10-16 审查格式候选真实验收：独立核验未通过

用户明确批准后执行冻结候选dd99b3b，独立grant semantic-review-schema-20261016（24调用/USD1上限），原四源合成资料只读。默认部分题仅一次：HTTP200/11.394秒，2调用/USD0.003260估算，无新unknown、人工额度未变，原2个pending保留。生成及模型审查accepted；PAY-102 Done、PAY-103 In Progress和日期insufficient均正确。

独立业务核验失败：第2条claim额外说明两工单来自“final payment-service postmortem”，唯一引文为“Follow-ups: PAY-102 and PAY-103.”。完整源文档含此背景，因此不称其凭空编造；但所选引文未支持完整的final/payment-service/postmortem限定，且该背景并非回答状态/日期所必需。模型将其判为supported/responsive并不替代独立验收。保留全部3条claim与5条引文检查，未删除有问题的claim制造通过。

评估门收到fail后结束，剩余10题not_run，无重试/后续grant/切换。运行进程正常退出0，CLOSED记录2调用。本人历史/引用200、跨用户403、三普通角色audit403；137事件本地链有效，无独立签名证明。浏览器本轮not_run，现用试用页不变。

互不重叠阶段：鉴权/源检查8.248秒，生成传输2.050秒，审查传输1.042秒，检索（排除嵌套鉴权）0.014秒，其他0.038秒。单样本不支持p95/SLA。

结果改变下一步判断：该次分题格式、完整审查schema及requested-value分类已通过，但完整引用支持及审查语义可靠性仍有缺口；不能再把问题单纯归因于JSON结构。后续修复应针对实际语义反例，不能放宽规则、直接丢弃claim、无限重复付费或把模型accepted当作通过。详见review-schema-live-results.json。Goal未完成。
