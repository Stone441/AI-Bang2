# ADR094 · 并发前置保护与剩余实施边界

2026-10-13；AUTH036，基准1649e30，本地未提交。当前运行实例继续使用冻结structured-v2；本次修改未加载，不继承原生性能结果。

## 实测和代码对应关系

v2两组三并发最慢26.922/24.905秒；后续查询在request_lock处等待最高18.024秒。当前有三层整查询串行保护：HTTP request_lock（与pilot.lock相同）、store.lock、Goal admission的进程锁/文件锁。只改HTTP锁不能得到完整并发。

这些锁目前还保护共享authority.resources、按actor存储的snapshot、discovery发布与版本恢复、SQLite连接以及Goal计数/费用检查。模型reviewer是每次新建，但这不意味着整个Engine具备请求隔离。单查询仍有5.820–8.911秒原生授权wall，解除排队不会单独解决3秒目标。

## 本次实际实现

`DelegatedAuthority.state_lock`与`pilot.lock`使用同一个RLock；保留原HTTP整查询锁与预算gate。check_many在此锁下取得独立的资源/动态映射副本，完成既有原生检查后，再在同一状态锁下比较当前发布与发起读取时的版本、正文、定位、tenant和active状态。

若期间状态改变，返回unknown/concurrent-authority-change，不接纳旧allow、不覆盖新版本、不复活删除对象。若仅相同资料被更新了观测时间，沿用最新观测字段。默认串行行为不变，没有跨请求/跨阶段复用allow，没有新增API、模型、账号、scope或外部写入。

这只是防止迟到响应覆盖状态的前置保护；不能据此移除外层锁。已撤权后再恢复等ABA变化、reader映射切换、同actor两次prepare覆盖、最终授权到持久化之间的发布变化，仍需要后续请求状态/发布代次设计。

## 可执行证据

- `tests/test_authority_publication_race.py`：直接调用check_many且故意不持外层查询锁，以两个线程和事件控制晚到响应；native transport为mock。覆盖新版本、删除、条目移除、同版本正文变化、tenant变化、嵌套locator变化，以及相同资料观测更新。
- 在进程内恢复原无条件回写逻辑的负对照，2个测试产生7个预期失败；保留`authority-race-negative-control.log`。没有改源文件、运行实例或真实平台。
- 新保护下2项通过，`authority-race-local.log`。
- 完整611项通过，26.878秒，`authority-race-full-local.log`；日志末尾模拟runner打印的failed属于既有预期输出，unittest结果为OK。
- 原生、live model、浏览器性能增益均未测；Goal仍43调用/USD0.056704新增结算，new unknown为0，旧2项保留。

## 下一步实施顺序

1. 请求范围的只读候选快照、actor与读者映射；查询不能将另一个请求的中间状态当作自己的当前授权。后台发布保留短锁及单调代次。
2. Goal admission改为短临界区的调用/费用保守预留，区分仍在执行的已知reservation与崩溃/失联后的unknown；同时证明60调用与USD0.50、原USD20上限在竞争下不能超支。不可只把整个gate锁移除。
3. 每次模型出口和最终返回维持当前权限检查，已授权的原文映射与发布代次比较；原始审计、History/preview、旧双调用路径与单次版本恢复全部保留。
4. 本地用三线程固定竞态覆盖跨用户/同用户多session、重复提交409、版本/删除/撤权、后台发布、预算临界和进程异常。证明后才考虑有界并发开关及更新实例。

最终native原配额12次已经使用。当前不追加收费重复；新实现形成后再给出剩余17次总额度内明确、有诊断目的的分配方案，不能将新候选当成v2已验收。
