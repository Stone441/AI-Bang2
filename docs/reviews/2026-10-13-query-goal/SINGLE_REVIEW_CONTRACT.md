# 单审查出口候选契约 · 2026-10-13

状态：已实现 opt-in；默认 legacy。50 项相关测试、564 项完整本地测试通过；审计链断言改为检查 valid 字段后，22 项专项再次通过。native Q1 已验：完整 selected 仅 before_model / review_dispatch / before_dispatch 三轮（另关联种子检查），低推理原文审查成功，HTTP 54.732s。三轮授权合计约 11.648s，模型 41.133s；不以此宣称三秒或稳定收益。

适用范围仅为服务端代码明确列出的三个 source-review 模型类（原版、compact、covered），不根据模型输出或浏览器参数选择。旧 synthesis / reviewed-excerpts 双调用路径不适用。

原路径：候选 before_model → selected model_dispatch → 本地原文分段 → review_dispatch → 唯一模型调用 → before_dispatch。
候选路径：候选 before_model → 本地原文分段 → selected review_dispatch → 唯一模型调用 → before_dispatch。

等价依据：source-review 的 source_claims 只对已授权 Evidence 作本地逐字构造和校验，不调用模型、业务源或预算 reserve。实际唯一外部模型出口仍在 review_dispatch 对全部 selected 的当前权限/版本检查之后。保留较晚的检查，覆盖构造期间变化；没有复用前一阶段 allow，没有把检查移至构造之前。最终交付、历史、预览的检查保持。审计如实记录实际阶段，不伪造被省去的 model_dispatch 授权记录。

必须验证：同一 fake transport 的 payload、claims、费用与最终正文完全一致；单次路径完整 selected 集合在 review 前后均复核；构造期及 review 后 deny/unknown/version/deleted 全部拒绝；构造期失败无模型调用/无 reservation；review 后失败保留已结算费用且无答案提交；History 撤权仍生效；未指定开关保持四轮，双调用不能启用本开关。任何非列出模型类必须在调用前拒绝。native API 的波动与时间收益须另测，不能由减少一次函数调用推导达标。

局限：本改动本身不解决模型覆盖失败；不能消除 before_model、review_dispatch、before_dispatch 这三轮原生读，也不能证明完整答案 3 秒。

首轮单阶段测试有 4 个测试设置错误：在 before_model 返回后注入版本/删除，选材阶段会先排除该记录；剩余模拟答案随后因没有 responsive claim 而 ModelOutputRejected。修正测试明确检查任何实际模型输入不含该旧记录，而非错误要求一定在模型前以 PermissionError 退出。deny/unknown 仍要求零模型；原有构造期四类变更仍全部要求零调用。首次日志保留。
