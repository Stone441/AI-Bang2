# 四路读取与 History 批量鉴权 · 2026-10-13

范围：AUTH036 本地可回退候选，原 provider / 合成容器 / 账号 / scope 不变，无新增依赖。初始模型8次、Goal新增结算USD0.040951、新unknown0，原unknown2保留。

## 为什么这样改

上一候选Q1/Q2三轮授权约11.648/12.249秒。每源并发2导致第三份Drive文件等待第二批；并发调度没有必要改变每个文件的身份→元数据→正文→读后元数据检查。新增显式并发4（默认仍1），HTTPS池匹配最大4条，每批全部join后才进入下一批，unknown包括429后不接纳新批，已经在途的同批请求可完成。四个来源总上限16个完整读取；这不是请求次数减少、ACL缓存、失败重试或延长超时。代理仍走原路由。

History原先逐条调用evidence，串行读取各来源。新增默认关闭的 `--history-read-mode batch`：验证服务端actor，先在本地检查每个证据ID的当前存储版本及合法窗口；按不可变资源去重，调用既有checks/check_many执行本次原生读取；全部allow且版本/active仍符合后才解析返回当前窗口、校验每条历史claim的精确引文。任一失败只返回原有generic unavailable，不泄露资料名称/数量。去重只在这次访问内，同一资源同一版本的多窗口共用本次读；第二次History重新读取，旧版本不能借当前权限通过。审计用原历史request_id关联本次history授权阶段，模型和历史答案原件不修改。默认serial便于回退。

## 验证依据与限制

四路并发测试：前四个都完成前不启动第五个、不提前更新共享authority；保留ContextVar和有序结果；unknown令第五个not-attempted；review/final阶段撤权、unknown、版本、删除仍拒绝。TLS测试同时占用四条连接时第五个等待超时且无第五次HTTP，释放后不泄漏连接。原两路断言保留。

History测试：serial/batch返回完整相同record，每次调用都复核完整集合；撤权、unknown、版本、删除、伪造窗口与引文返回generic unavailable；多个合法窗口仅一次本次资源读取，保留每段原文。原source-review历史撤权测试也在batch模式运行。

真实Drive探针仅读取原配置的三个文件，保留全部原生步骤，每轮均12 HTTP，内容逐字一致：two_cold5.788908s / four_cold1.969055s / four_warm1.994013s / two_warm3.643545s；实际峰值完整读取2/3/3/2。冷连接顺序和网络波动影响结果，小样本不能宣称p95或端到端问答改善。`scripts/performance_drive_concurrency_probe.py`只刷新原有OAuth grant并核验身份，不打开新consent、不保存token，不重试或覆盖既有结果。私有原件`.runtime/query-goal-20261013/drive-concurrency-probe-v1.json`。

真实History基线：现有Q2答案重新鉴权HTTP9.392120s，完整record与保存原件一致，模型调用及结算增量均0。新候选1.968095s，记录与同一原件完全相同，两次均25次原生HTTP；批量history授权wall1.964544s。模型调用及费用增量0。这不是重新回答问题、浏览器渲染或3秒问答证明。

Google原生接口仍可能返回限流错误，官方[Drive usage limits](https://developers.google.com/workspace/drive/api/guides/limits)分别说明配额和后端429限制。未把公布配额当本账号无限并发许可；保留现有源cooldown，本次仅有界少量只读对比。

回退：`--source-concurrency 2 --history-read-mode serial`，不用回滚账本/历史/授权。进一步回退网络层仍为legacy/1。当前剩余瓶颈包括三轮原生检查与低推理模型时间；此改动不宣称完成Goal。

最终完整本地578 tests / 25.844s / OK（history-four-full-local.log）；53相关1.107s通过。自有49161已在归属/空闲检查及pre-history-four-backup备份后加载4b63a5a7f7c5（pooled/4/covered/low8192/single/history batch）。原模型和实际调用数不变。新候选四源complete/current后执行History，不发送新问题。机器证据VALIDATION_FOUR_HISTORY.json，原始本地记录留在忽略目录。
