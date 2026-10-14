# 派发与来源计时设计（未接入运行时）

日期：2026-10-13 · 状态：设计完成，实现 / native 测量 not_run。

目标是区分来源请求、阶段 wall、锁等待及模型响应；数据不参与授权判断、模型输入或答案内容。复用 `scripts/validation_timing.py` 的 Measurements / TimedNativeTransport 与原有 ContextVar 传播；不创建第二套 tracing 服务，不上传数据、不引入依赖。

## Span 契约

以下为拟议本地诊断数据，不是新增产品 API、公共 audit schema 或已存在的事件。

| 字段 | 语义 / 约束 |
|---|---|
| request_id | 已有随机请求标识；用于本地受限关联，不附带用户名、问题或来源对象 ID |
| span_id / parent_span_id | 请求内局部整数；标识包含关系，不用于权限 |
| operation | 固定枚举：query、preview、history、background_discovery |
| category | 固定枚举：request_wall、lock_wait、lock_held、retrieval、authorization、source_lane、native_http、source_claims、model_input、model_transport、model_output、ledger、commit |
| authorization_phase | 既有 before_model / model_dispatch / review_dispatch / before_dispatch / preview 等白名单；无阶段则 null |
| source | confluence / jira / slack / drive / deepseek / local 白名单 |
| endpoint | 已有 transport 的固定类别；如 file_metadata、file_body、about；新类别需白名单，未知映射 other |
| start_offset_seconds / duration_seconds | time.monotonic 的请求内相对值；不保存 monotonic 绝对值，不依赖跨线程系统时间差 |
| outcome | 固定枚举：ok、deny、unknown、version_changed、cancelled、unavailable；不保存原始异常文本 |

禁止记录：URL、query值、headers、token、ticket、模型key、问题、资料标题/正文、自由文本模型理由、供应商 response ID。原有证据/audit继续承担内容与身份还原，不把内容复制造进计时日志。

诊断只保存到任务所有的私有本地目录（目录0700 / 文件0600），默认不加入产品页面、Git或提交包。诊断读取遵循现有身份和审计范围；来源耗时/对象数量也可能泄露受限存在，不因为省略正文就开放给所有 session。全局预过滤统计不输出；候选统计只基于当前允许集合。失败时不输出受限对象元数据。

## 插入点与安全职责

| 插入点 | 记录什么 | 不能改变什么 |
|---|---|---|
| server 接纳及 request_lock / store.lock | request开始、各原锁 wait / held；原顺序、嵌套分别记录 | 不更换锁、不改变作用域；重复提交接纳规则不变 |
| Engine.prepare / retrieval | 来源完整性门槛、预过滤、排序、窗口构造 wall | 不额外读取源、不缓存 allow、不扩大可用资料 |
| Engine.checks | 每个授权阶段的父 span | 仍检查完整集合，unknown不放行 |
| DelegatedAuthority.check_many | 最多四个 source_lane span；context通过 copy_context传播 | 来源内串行、join后权限更新与审计顺序不变 |
| native transport.get / media | 固定endpoint请求 span，包括异常 finally | 请求参数、重试、429冷却、返回值完全透传 |
| source_claims | 本地连续引用构造 wall | 不删资料、不截断限定条件 |
| model provider | 序列化/input验证、预算预留、transport._send、usage结算、输出parse分别计时 | 不插入额外请求、不改usage/unknown和回执；计时异常不能触发retry |
| before_dispatch / Store.save_run | 最终检查和答案commit | 不提前响应、不绕过当前权限版本 |

若插入点无法得到唯一 request Context，应标为未关联的背景诊断，不归到某个用户问题；不得继续使用默认 background_discovery 标签冒充真实操作。后台出版等待单独记录，不与请求内来源网络累计混为一谈。

## 时间解释

- request_wall 是请求端到端观测；锁等待在开始业务函数前测量，否则现有 request_started 时间会漏掉排队。
- authorization wall 是整个阶段 elapsed；source_lane 是来源串行链路 elapsed；native_http 是请求 elapsed。它们互相包含，不能相加。
- 四来源并行时，报告每lane和阶段 wall。累计 HTTP worker秒只代表总工作量，不能作为用户等待时间。
- lock_wait 与 lock_held 分开；嵌套锁held也不能相加为request wall。
- 模型attempt→usage是响应、验证及结算区间。新transport span才隔离真正 `_send` wall；不能将现有event区间写成纯推理耗时。
- 按序列化完成、最后授权完成、实际transport开始分别标点，显示检查到实际发送的间隔。指标不是原子授权证明。
- 成功、来源故障、模型拒绝、预算停止分别报告；缺 span 标 not_recorded，不填0。不能从三个样本计算生产p95或SLA。

## 本地验收设计

1. 模拟monotonic时钟，验证offset/包含关系、异常finally与时钟恢复；不以真实机器毫秒阈值判定通过。
2. 四来源以threading.Event受控并发，验证phase/request Context传播；按来源保留串行，wall不错误加总并行请求。
3. transport注入包含敏感URL/token/原文的异常，检查计时结果只有白名单；返回和异常与原delegate一致。
4. lock异常、cancel和来源unknown场景验证原锁仍释放、所有未完成跨度正确终止、不死锁。
5. 复用本轮构造期 / 模型后四类变更、旧双调用、preview/History与预算unknown测试；比较计时开关前后实际输入、审计安全事件、调用数和持久状态。
6. 设置有界span数量：达到上限只标诊断incomplete，不截断授权检查、不改变请求结果；计时失败不得覆盖业务错误或unknown账本。

这些为下一任务的验收标准，未在本轮冒称实现或通过。真实试用接入须核实例归属、当前版本、已授权操作及状态保存；本轮无重启或付费测量。
