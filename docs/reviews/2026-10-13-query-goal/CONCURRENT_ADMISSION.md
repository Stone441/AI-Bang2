# ADR095 · AUTH036并发预算门控

2026-10-13；本地未提交，尚未接入49161启动器。原PerformanceAdmission和冻结structured-v2继续运行，未重置或迁移生产账本。

## 实现与边界

新增`ConcurrentPerformanceAdmission`和`ConcurrentGoalLedger`，复用原Goal状态格式、计划hash、原预算SQLite以及旧unknown基线。网络/查询函数在文件锁外运行，只有接纳、预留、派发、结算和结果记账持短临界区。

BudgetLedger.reserve/dispatch增加默认不启用的服务端admission_check回调；检查在同一个BEGIN IMMEDIATE事务内执行，检查和新增预留/派发之间不存在另一个SQLite写者插入的窗口。原全局USD20账本限制仍独立执行；不改原调用方行为。

每次新增预留同时检查：实际已派发/结算调用数＋新prepared名额＋本次名额≤60；新增已结算费用＋新未结算预留上界＋本次上界≤USD0.50。原unknown保留且继续占原共享账本额度。新未知用量阻止新接纳、预留和prepared派发；已经派发的请求仍允许结算真实回执。没有自动重试、退款或取消。

OS独占owner lease限制同一Goal只有一个并发门控进程，内部支持多个线程。reservation只属于创建它的请求上下文，其他请求不能替它派发、取消、结算。仍在执行且属于本进程活跃请求的reservation可以明确识别；请求退出后未完成的预留、进程崩溃后遗留的预留都转为unknown。持久化的known-in-flight列表仅为诊断，重启不把它当作仍存活证明。

## 实际验证

7项专项通过（0.180秒），包含：

- 三线程全部到达模型派发后的屏障，证明门控没有持锁包住整次模拟模型调用；3次独立结算，无新unknown。
- 59次历史调用时争夺最后一个名额；已花USD0.40时同时申请两个USD0.075上界；第二项预留均被拒绝。
- 某调用产生unknown后，另一prepared调用不能派发，另一个已派发请求仍能结算；未派发预留不伪装为实际模型调用。
- 第二门控owner、未接纳调用、跨请求操作及运行中关闭被拒绝。
- 真正子进程在派发后os._exit：OS释放lease，新进程保留123 microUSD预留并停止新调用；不是仅模拟一个异常返回。
- 原模型类/逐次reviewer/预算类型契约集成通过，使用fake transport，原同一SQLite记录费用与回执。

完整618项通过（26.223秒），日志`concurrent-admission-full-local.log`。该日志末尾既有mock runner打印failed不改变unittest OK。专项日志`concurrent-admission-integration.log`。

## 未完成与接续

本次未改变HTTP request/store整查询锁，未提供线上并发或3秒性能证明。下一步按CONCURRENCY_SAFETY实现请求范围的authority/候选/reader映射隔离及发布代次检查，再将短锁门控与有界并发统一接线；不得只删除外层锁。原串行门控仍可回退，切换前须停妥自有实例并保留全部持久状态；未完成预留不可通过切换重置。

当前真实Goal仍43次模型、USD0.056704新增结算、新unknown0；原最终native12次额度已用。本轮0真实模型、0native业务读取、0新增费用，无外部写入/发布/推送/合并。
