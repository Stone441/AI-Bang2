# Candidate closure preparation · 2026-10-08

基准main为4b93d52（PR #5已合并；实现对应0bc90ae）。本目录目前仅保存当日真实价格复核、readiness与封版验证runner的本地检查，封版闭环仍in_progress。

- business_holdout支持可信low/4096和相应预算预检查；原12题保持原字节，后续结果必须称已知问题回归，不能称新盲测。
- native runner分开查询返回、native HTTP、授权、generation/review及单个引用preview；授权时间包含native HTTP，不可相加。后台发现使用独立phase。未执行新native测量，旧133/146秒包含全部preview，不能沿用作纯query时间。
- 本地400项完整回归（含2项timing测试）及另外2项holdout guard通过，前端语法/两个Node检查通过；12题fake runner执行通过，不证明语义质量。
- 原AUTH021三阶段证据与AUTH019延期保持；时间线整合、最终版本已知12题live回归和native测量仍待完成。browser blocked，G1/G2 not_run。

Git交付不证明8094/8100加载新版；未重启任何服务、未新增模型调用/费用。
