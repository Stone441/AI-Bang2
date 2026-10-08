# 定向工程收尾 · 2026-10-08

基准main `2eabeb824e9d3ab8a5b17da391fc9246a4dfe426`（PR8已合并）；应用仍`cdbd62b`，分支`fix/targeted-closeout-20261008`，brain/scripts/tests/web无修改。v10显式low8192，原USD20预算不变。没有重复完整付费回归。

- **known05明确范围对照**：实际输入包含J03，回答PAY102 Done、PAY103 In Progress、GA未批准，三个精确引文，15.026秒、5179microUSD；fixture业务源＋live model，非native/browser。旧题、oracle和partial/J03输入遗漏保留；本对照不证明歧义是唯一原因。见`known05-control-final/`及`known05-review.json`。
- **统计细化**：原core24为21直接事实＋1纠正前提后有事实（business03）＋2纯空答；known12为3完整事实＋1部分＋1纠正前提后有事实（11）＋6纯空答＋1预期source unknown。原答案不改，不把无错误结论当作任务全成功。
- **AUTH026**：仅3新建＋4修正已全部消费。Jira KAN8/10017、Slack新root1791449350.384539及其修正reply1791449714.768099、Drive新文件1W_UZvPPeWyMQCX9tHFx1PlN_hK8HGu3I；Confluence只改AUTH024页1572865为silver/version2。未删/改ACL/旧业务资料，未重复AUTH024创建，新增模型费用0。
- **自动发现**：正常后台、最小60秒周期，无手动cycle。三创建＋Drive更新在持续worker中观察；Confluence version2也在原worker发布。原observer一次问答遇并发Jira内容变化停答并退出；只读恢复后另三问答遇Drive版本变化停答，随后四更新均有新值用于fake回答。失败保留：原审计341事件、恢复795事件，链有效仅本地，非独立防篡改。

| 操作 | 原生更新时间→完成发布(s) | 原生更新时间→观测到的成功fake回答(s) | 边界 |
|---|---:|---:|---|
| Jira创建 | 45.861 | 65.431 | 持续自动 |
| Slack创建 | 21.118 | 44.891 | 持续自动 |
| Drive创建 | 38.190 | 99.287 | 持续自动，问答观测较晚 |
| Confluence更新 | 8.910 | 446.349 | 原worker自动发布；失败/恢复后问答 |
| Jira更新 | 199.374 | 251.863 | worker重启恢复发布，非持续时延样本 |
| Slack修正reply | 200.206 | 244.375 | worker重启恢复发布，非持续时延样本 |
| Drive更新 | 45.340 | 69.372 | 恢复worker就绪后持续自动 |

时间起点为API报告的updated/version/message timestamp，并非精确源commit。UI观测JSON记录晚于UI确认，部分已发布，不能把其接近0的差值当成自动同步时延；以上使用原生时间与完成cycle。成功fake回答时点受记录及恢复影响，不宣称严格首成功延迟。完整数据和限制见`freshness-summary.json`，原生逐请求时间/周期/版本/审计及原失败均保留。fake仅证明新证据使用，不证明live synthesis最终silver语义优先。fake逐对象before_model/model_dispatch/before_dispatch已核；未运行live review_dispatch。

验证：`PYTHONPATH=. python3 evidence/runs/targeted-closeout-20261008/verify-freshness.py`，7操作/新值证据/三个fake授权阶段/两审计链/应用hash与无runtime diff通过。首次检查误要求fake具有live review阶段而断言失败，纠正为实际fake三阶段；未修改runtime gate。

原账本settled760885、accounted1085289、available18914711microUSD，pending1原324404保留。AUTH019及旧失败不变。剩余：多次持续自动样本与p95/max/失败率、完整四源native撤权/删除/故障矩阵、实际团队页面试用。新实例49161尚待具体授权，没有启动；8094/8100未动，产品browser拒绝不绕过，G1/G2未批准。本轮新分支未推送合并。

页面试用准备补充：`launch-page-trial.py`已完成本地限额验证（临时fixture账本，无native/model/端口/Keychain），具体命令、隔离目录、6尝试/结算停止阈值及人工首组操作见当前RUNBOOK。结算阈值为新请求admission控制，非在途硬费用上限。具体实例授权仍pending，脚本未执行、实际入口尚不存在。

AUTH027实际页面问答增量：第一题request e320cbdcc5c24d0a8b7cc48d799b4490在55.468s失败；usage prompt3991/completion8192，11028microUSD结算，generation输出拒绝，未到review。原始响应/finish_reason没有持久化，不能把达到cap直接归因为length。第二题明确payment-service request d34e5b0893164e6987701187d3a5fc95在18.411s停答，model_dispatch当前Drive新探针version6不一致，未调用模型/0新增费用；正常后台后来发布version7，正文hash和modifiedTime相同。Google[官方files契约](https://developers.google.com/workspace/drive/api/reference/rest/v3/files)说明version包含不可见服务器变化，确切变化原因未知；不以同正文绕过旧版本拒绝。两次实际任务均无支持答案，不能称页面/业务成功，fixture known05对照通过不替代native结果。失败/audit prefix保留，未自动retry/改配置/重启/放宽检查。当前结算增量11028，原pending1/324404保留；具体页面错误与团队反馈、引用/History实际操作仍待确认。

人工反馈与本轮结束（2026-10-08）：用户确认两题全部失败，此后没有进一步使用，引用/History后续任务未做；本次真实试用为failed，不是通过。用户观察到Ask Question后不显示已等待秒数、页面没有可感知的工作状态，持续等待且无法判断是否工作，产生焦虑；模型信息和四平台连接状态不够显性，页面过于简陋。仅记录这些问题，UX完善和失败后续处理待ChatGPT Chat给下一步指导，不修改实现/配置。已SIGINT结束本轮自建49161/PID8976，进程exit0且端口无监听，索引/原账本/失败保留，8094/8100未动。总2次人工问答尝试，1次模型调用/11028microUSD结算，原unknown324404保留；最终模式、反馈、审计链及预算见page-trial-final.json。当前定向收尾与真实试用/反馈收集完成；失败修复、UX及完整技术/业务验收均未关闭。
