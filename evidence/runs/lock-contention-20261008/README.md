# DEV-PERF-01 · 最终本地交付

基准main a3a0060；原应用80b9ffc；任务分支fix/lock-contention-20261008。最终应用cdbd62b339f8a85f726514c49dad668bb4016322，中间应用514831d原证据保留。未推送、合并、部署或重启8094/8100。

锁争用先以慢来源复现（before.log，两断言失败），再实施锁外采集与pilot→store短临界区原子发布；baseline状态防旧结果覆盖、停止不发布、失效fail closed。阶段内四source有界并发，来源内串行，所有结果由请求线程有序记审计；未省略身份/频道/父线程/正文/版本，也未跨阶段复用allow。共享source cooldown尊重429 numeric Retry-After，不自动retry；此前已接纳读取可完成，非跨进程/平台全局限流。

## 同条件 native CLI 比较

固定相同两题、eng_b、synthesis-v10、low/8192、stored sampling=0（low时请求实际省略temperature），model60s/native30s。后台从query前至preview后保持运行。两题分别13/15原证据窗口ID与text字节一致。

| 指标（秒） | Slack旧→最终 | 产品旧→最终 |
|---|---:|---:|
| query返回 | 78.287→40.083 | 97.225→49.034 |
| 授权wall | 69.052→34.363 | 75.009→35.017 |
| generation最终 | 4.197 | 10.827 |
| review最终 | 1.478 | 3.131 |
| 单引用 | 27.166→1.656 | 25.540→1.052 |
| 引用锁等待 | 25.522→0.000057 | 24.955→0.001621 |

原/最终Slack引用slack:C0C6R70SGG4/1791364699.192759@56399498513313818；产品引用confluence:164283@1。仅中间514831d选Drive引用，不混入最终matched比较。按source/phase/endpoint调用数及累计HTTP在[performance-cdbd62b.json](performance-cdbd62b.json)；并发累计72.176/78.146秒不能与wall相加。单次实测不是p95/SLA；查询30–40秒团队目标未全达，主要剩余为保留的原生授权wall与模型时间。

## 最终配置回归

原24开发题：21正确事实范围、3合理澄清/无证据；已知12题：3完整正确、1部分覆盖、7合理澄清/无证据、1预期来源unknown停答。known05遗漏原意PAY103 In Progress，保留为partial；known12预期Drive unknown、零模型调用。两组零错误弃答/错误结论/非预期运行失败。本次非盲测、非质量全通过。native两题正确完整。逐题见[semantic-review-cdbd62b.json](semantic-review-cdbd62b.json)，完整输入/输出/诊断分别在core24-cooldown-final、known12-cooldown-final、native-cooldown-final；结构/配置/hash/quote/四阶段权限/审计链核验见[structural-cdbd62b.json](structural-cdbd62b.json)。本地未签名链不等于独立custody或防篡改证明。

421 clean git archive测试、两Node前端、五fixture场景、fixture HTTP smoke通过：[clean-cdbd62b/verification.json](clean-cdbd62b/verification.json)。确定性慢同步/引用/真实本地HTTP、query并发、版本/撤权unknown/乱序/停止恢复/审计预算、四来源并发与冷却断言在对应测试及原始日志。真实HTTP为本地mock来源；产品浏览器saved denial保持blocked，不能称浏览器性能。

## 自动发现子集

用户AUTH024明确批准一次单页创建及测量。owner UI仅创建既有space131227下页1572865，继承C01限制未改。正文只含批准的synthetic copper测试说明；没有编辑/删除旧资料或再授权限。独立只读CLI先完成初始同步，之后正常60秒minimum cycle/1秒wake，没有手动run_once、没有paid model或HTTP服务。

UI确认07:39:48.459835Z，下一Confluence cycle开始07:40:19.234504Z，durable publication完成07:40:24.058942Z，首fake回答07:40:45.584411Z。确认→cycle30.775秒、→发布观察35.601秒、→回答57.124秒；listing累计0.748秒、该cycle4.824秒。源metadata07:39:30.241Z→发布53.818秒。UI确认晚于源metadata，两者均非精确server commit；cycle_start也非逐次listing开始时间。fake输出确实引用copper新页，同时echo其他eligible证据，不能作为语义质量证明。117事件本地链valid。仅Confluence create子集，不重写旧十二行历史、不宣称完整四源生命周期或SLA。见[native-freshness/summary.json](native-freshness/summary.json)及[发布截图](native-freshness/published-owner-ui.jpg)。本次AUTH024已消费。

## 预算、复现与限制

最终三流64有效usage回执/105121microUSD；本轮含中间验证结算202522microUSD（USD0.202522）。原USD20账本settled755706/accounted1080110/available18919890，原unknown reservation324404、pending1保留，无新missing usage。[budget-final-cdbd62b.json](budget-final-cdbd62b.json)按回执统计，不把共享并发snapshot差额当单流成本。

复现命令与加载hash分别保存在各verification.json，离线结构复核：`PYTHONPATH=. python3 evidence/runs/lock-contention-20261008/verify-captures.py`。native freshness observer命令：`PYTHONPATH=tests:. python3 evidence/runs/lock-contention-20261008/capture-native-freshness.py`；目录已存在且一次授权已消费，不能再次运行/种植。失败before/import/初始回归与全部中间流保留，不改expected、不降低阈值。SQLite运行数据库留本机，不进入Git；原ZIP/队员文件保持。

AUTH019两项原延期、ADR040、embedding/chat/export/review策略、浏览器blocked、G1/G2及真人业务/ROI/录屏/提交边界保持。下一可独立处理known05召回/范围完整性和剩余query耗时；不是本轮继续加场景或追加配置实验的授权。
