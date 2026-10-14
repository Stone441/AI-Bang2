# 受限本地计时实现 · DEV-SR-TIMING-02

日期：2026-10-13（Asia/Singapore）。独立分支 `feat/restricted-timing-20261013`，基准 `1649e301959b7eea7303fdda9ba0ee58a578d19e`，保留前一轮未提交审查材料。用户明确同意在本地实现受限计时并验证。没有新依赖、真实来源访问、模型费用、试用实例重启或外部写入。

## 当前成果

`brain/timing.py` 提供默认关闭的请求局部 collector，复用现有 Measurements / TimedNativeTransport。CLI 仅在操作员启动时显式指定 `--timing-dir` 安装；浏览器、prompt、请求字段不能开启。`brain.operator_web` 与 `scripts.delivery_trial` 均支持该参数，本轮只运行了 `--help`，没有运行真实启动命令。

| 计时层 | 当前记录 | 如何解释 |
|---|---|---|
| 请求 | query、preview、history、独立背景source cycle | HTTP query通过身份检查后、锁等待前开始；已begin的query绑定真实request_id，接纳前停止和其他操作使用独立随机诊断ID |
| 锁 | request_lock / store.lock 的wait与held | 保留原context-manager协议、对象、获取顺序、嵌套与异常退出；不是删锁或缩小范围 |
| 检索 | delegated prepare及本地预过滤/BM25/关联扩展父跨度 | 关联扩展可能包含嵌套原生检查，不能相加为总wall；窗口最终选择未单列跨度 |
| 授权 | before_model、model_dispatch、review_dispatch、before_dispatch、link_seed | 原函数完整调用；span不授予权限、不裁剪集合、不缓存allow |
| 来源 | 四个并行source_lane及固定类别native_http | lane有原阶段和parent；来源内仍串行；native HTTP按实际delegate get/media测量 |
| 引用 | source_claims | 原文构造期间的变化仍由review_dispatch阻断 |
| 模型 | messages/JSON序列化、实际_send、parse_output | 模型transport独立于ledger、parse；数据不进入模型输入，不增加调用 |
| 持久化 | reserve/dispatch/settle/model_outcome、save_run | 不改账本、回执或审计；未知消耗依旧保留预留 |

单请求最多512 spans（本地API可设1–4096）；达到上限标 `incomplete`，仍继续所有业务检查。ContextVar通过既有copy_context传至来源线程；join和审计顺序保持。无有效request Context的调用不记录，避免误归到上一问题。AUTH017背景cycle显式分开记录；本轮没有为全部内部后台锁增加跨度。

没有添加 `api/timing`、UI统计、文件下载或外部 tracing。原审计schema和答案字段不变。时间只证明本地观测，不证明授权原子性、业务覆盖或用户已读。

## 隐私、文件与故障

- 只存固定类别、来源名、原授权阶段、随机ID、局部parent关系、monotonic offset/duration及固定outcome；未知endpoint映射other。
- 不存URL、参数、headers、token、ticket、用户名、问题、资料标题/原文、模型输出或推理、供应商ID与异常文本。
- 目录必须当前用户拥有、0700且无symlink组件；已有公共目录拒绝，不自动chmod。保存时使用已打开目录fd、独占生成文件名、0600写入。
- 先写 `.pending`，关闭后以不覆盖既有文件的原子hardlink发布 `.json`，最后移除pending。读者只读完成的json。进程崩溃可能留下pending；本轮不自动清理或删除历史文件，不宣称fsync/独立防篡改。
- clock/sink失败只影响诊断，不重试模型、不替换业务异常、不修改预算。诊断写入在请求处理scope退出时完成，可能晚于客户端收到HTTP正文；读取方须等待对应文件完成，不能把暂时没有日志当0耗时。
- 计时目录是私有本地操作员资料；即使无正文，来源时序也不适合未经审阅公开。不要将实际诊断加入Git、提交包或产品接口。

## 使用与回退

在今后经授权的实际启动中，为原有完整启动命令追加：

```text
--timing-dir <owned-private-directory>
```

父目录必须已存在；该叶目录可由collector以0700创建。使用绝对路径；delivery_trial会在切换cwd之前固定相对路径。省略参数即关闭collector。当前服务没有重启，本轮没有生成实际49161/native/model计时。旧价格检查、实例归属、原账本、原admission与来源启动检查仍适用；该参数不是新的付费或重启许可。

检查json时分别报告request_wall、每阶段authorization wall、每条source_lane和各HTTP类别。嵌套与并行时长不相加；worker累计秒是工作量。HTTP root的ok只表示响应状态，不把evidence_only或review accepted推断为业务正确。跨度缺失标not_recorded；incomplete日志不能用于精确全阶段归因。

回退：受控启动时省略 `--timing-dir`。没有改provider、参数、retrieval、权限判定、审计断言、预算阈值或锁。代码自身不产生真实性能提升；检查合并仍未实现。

## 实际验证与失败保留

`tests/test_restricted_timing.py` 新增12项测试：模拟时钟与嵌套、类别隐私、权限文件/拒绝symlink、原子读取、span上限、clock/sink故障、取消/锁释放及原__exit__抑制语义、模拟四lane并发/Context、独立背景cycle、开关前后真实mock输入/审计/费用一致、模拟timeout unknown预留一致、构造期和review后八类变化阻断，以及fixture HTTP query ID / preview / History /无计时接口。

- 新计时专项最终12项，0.596s，通过：[final-timing-tests.log](final-timing-tests.log)。
- 锁兼容修复定向18项（当时计时10项＋缓存查询8项），1.167s，通过：[targeted-after-lock-fix.log](targeted-after-lock-fix.log)。不相加为独立样本数。
- 最终整合502项，23.710s，通过：[full-local-regression-final.log](full-local-regression-final.log)。含前轮5项契约及本轮12项计时；含fixture/mock和本地HTTP/Node子过程，不证明浏览器、native或live模型。
- 首轮整合500项、23.863s、1 error，原件保留：[full-local-regression.log](full-local-regression.log)。故障是ObservedLock没有acquire，修复后沿用原context-manager协议并增加抑制异常语义测试。
- 三次早期专项失败原因与实际输出摘要见 [INITIAL_FAILURES.md](INITIAL_FAILURES.md)。整合日志内故意mock失败stdout/price提示仍保留，不删除以制造全通过外观。

前轮三份首题的9份response/result/audit SHA256仍吻合。`test_source_review_dispatch_contract.py` 仅把故障注入从class方法改为正在执行的instance方法，使计时包装后仍在真实构造边界注入；没有修改原assertion/原始证据/parser或授权规则。此前VALIDATION.json是前轮文件指纹快照，本轮改动按新指纹记录，不静默刷新历史文件。

本轮not_run：真实试用加载、native来源性能、live模型、节省时间、浏览器、人类G1/G2、推送/合并/发布。没有重跑付费题集。

下一项可推进工作：本地读取诊断json生成阶段与lane摘要，以不相加并发wall为验收；实际性能诊断则等待具体试用实例更新和调用范围授权，不能把模拟记录当真实测量。
