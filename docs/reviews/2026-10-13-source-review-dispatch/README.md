# Source-review 派发契约审查

日期：2026-10-13（Asia/Singapore） · 任务：DEV-SR-CONTRACT-01。

基准：`1649e301959b7eea7303fdda9ba0ee58a578d19e`；独立分支 `review/source-review-contract-20261013`。用户在架构诊断之后明确同意进行本地契约审查、计时设计及保留三份首题反例。本轮仅增加审查材料和测试；没有修改 brain/scripts/web、真实账本、原始证据、凭据或业务来源，没有模型调用、服务重启、推送、合并或发布。

## 审查结论

四轮检查确实出现在单次 source-review 路径中；但检查不能仅按名称或调用数认定重复。`model_dispatch` 之后还会构造原文 claims；构造期间的撤权、unknown、版本变化、删除，当前由 `review_dispatch` 阻断。模型返回期间的变化由 `before_dispatch` 阻断。新增测试在真实构造函数和模拟 transport 的边界注入变化，证明这两个位置承担独立安全职责。

**当前结论：保持全部检查。相邻检查合并仍为未实现、未验证的优化候选，不能宣称可安全删除某轮或已节省 7–8 秒。**

| 检查 | 当前职责 | 本轮证据 / 后续条件 |
|---|---|---|
| before_model | 当前原生权限与内容检查，决定哪些候选可以进入证据集合 | 保留；本轮不改候选、预算、关联扩展 |
| model_dispatch | 在完整 selected 集合形成后再次复核，包括资料版本与 active | 保留；这是通用路径中 generation 前检查，单审查路径随后仍有本地构造 |
| review_dispatch | 引用构造后、唯一 review 派发前核对完整 selected 集合 | 新增构造期 deny/unknown/version/deleted 四类阻断；无模型请求、无 reservation |
| before_dispatch | 模型返回与解析后、保存与交付前复核完整 selected 集合 | 新增 review 后四类变化阻断；无 committed answer，已发生 usage 保留 |
| History / preview | 当前访问、原文窗口及版本重新校验 | 已有 source-review / synthesis 相关测试本轮通过；未改变入口 |

代码位置：`brain/engine.py` 的 `_query`、`authorize_selected`、`authorize_model_stage`；`brain/synthesis.py` 的 `DeepSeekReviewAllSourcesModel.generate_with_authorization`；`brain/deepseek.py` 的 `generate`。

### 能进一步研究的优化

可以研究针对 `reviewed_source_v1` 的专用派发组织：原文构造和输入准备完成之后，由一个实际 review 出口统一实施完整集合检查。后续必须证明构造期间变更仍阻断、出口失败仍保留审计、真实 usage/unknown 不被重置、旧双调用路径保持各阶段鉴权，而且实际输入版本与被检查对象严格一致。不能以改名、共享上一次 allow、缩小证据集合或把检查移到构造前实现合并。

即使实现这种组织，也不能声称跨四个平台存在原子授权快照。现有 reader 与模型 transport 间还有 payload 构造、预算预留及事件记录；当前试验没有覆盖这一整个时间区间的所有外部变更。计时设计将标出检查结束到实际发送的间隔，不伪造原子保证。

## 历史质量反例

原始文件不复制、不改写；[COUNTEREXAMPLES.json](COUNTEREXAMPLES.json) 记录三组 response/result/audit 的路径及 SHA256。测试读取实际文件并核对 hash，随后按当前原文构造器和 parser 离线重放。测试结果只证明本地结构与历史记录可复现，不证明当前 native 权限或新模型质量。

| 历史运行 | C01 输入与结果 | 本轮离线重放 |
|---|---|---|
| v1 / 6cc1cb6b | index2 已送审；supported=true、responsive=false；coverage=false；evidence_only | parser 拒绝；失败延续仍不计答案成功 |
| v2 disabled / 6338c118 | 同一 C01 已送审；responsive=false；coverage=true；accepted 但漏措施 | parser 确实接受，并排除 C01；继续标为业务失败 |
| v2 low / 18a99f38 | C01 被保留，措施与未知顺序有依据 | parser 保留 C01；与 disabled 的 Evidence 对象完整一致；仅一次成功 |

前两种失败不能通过提高 parser 测试通过率被抹去。误接受是现契约依赖模型完整性布尔判断的能力限制；本轮没有增加题目特定的运行时规则、改提示词或更换模型。

## 已有耗时证据与限制

| 2026-10-11 保存的运行 | 请求开始→派发 | 派发→usage | usage→答案提交 | HTTP 总耗时 |
|---|---:|---:|---:|---:|
| low 原首题 | 27.304s | 31.273s | 7.532s | 66.140s |
| low 原第二题 | 24.147s | 9.000s | 7.190s | 40.371s |
| low 范围题 | 21.971s | 15.480s | 6.694s | 44.174s |

表中为事件时间戳区间；HTTP 计时边界稍宽，差值不是丢失的模型耗时。并行检查的 audit 事件在 join 后按顺序写入；不能将相邻 audit 写入间隔视为单资料的 HTTP 耗时。三题四轮中，Drive 的原生 `checked_at` 均最后完成；只定位到这些样本的来源关键链路，不能归因到具体 HTTP 请求或推广为 SLA。

已有 `scripts/validation_timing.py` 提供 Measurements、来源 transport 分类、lock_wait 和 ContextVar；本轮发现并复用其设计，不称计时工具尚不存在。实际 trial/server 尚未在本轮接入新增 spans。完整方案见 [TIMING_DESIGN.md](TIMING_DESIGN.md)。

## 实际验证

1. `python3 -m unittest discover -s tests -p test_source_review_dispatch_contract.py -v`：5 tests，0.039s，全部通过。
2. `PYTHONPATH=tests:. python3 -m unittest test_source_review_dispatch_contract test_source_review test_model_stages test_parallel_authorization test_validation_timing test_synthesis -v`：56 tests，1.358s，全部通过。

两轮分别是首次专项检查和相关兼容/安全回归；后者含前者，不相加成 61 个独立测试。新文件的两个变更边界 test 各有四个 subtests；不是八个已运行 native 案例。测试使用 fixture、模拟 transport、临时 SQLite 及本地 HTTP，不访问原生来源或模型。无新增依赖；未重复全套485或付费质量题集。

本轮 verified：契约审查、5项新增测试、三份固定反例完整性与离线重放、56项相关回归。not_run：真实性能提升、检查合并、trial计时接入、当前服务版本/live模型、浏览器与G1/G2。机器结果与文件指纹见 [VALIDATION.json](VALIDATION.json)。

下一项可推进任务：按照计时设计，为操作员诊断入口添加受限、可关闭的单请求 spans；先用模拟时钟、受控并发和故障验证不改变 dispatch/ledger/lock 语义，再决定是否接入实际 trial。不要直接恢复付费测试或删除检查。
