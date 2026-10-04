# Evidence index

全部为合成数据，不含真实凭据/企业内容；没有上传外部证据。

- `runs/local-latest/tests.json`：unittest 实际结果、运行时间、Python 版本、被测 commit 和逐文件 SHA-256；含 HTTP、32 个测试方法、额外权限矩阵 subtests。
- `runs/local-latest/scenarios.json`：S-01…S-05 的实际输入/输出/引用/断言与部分覆盖边界。状态 passed_local_subset 不等于完整官方场景验收通过。
- `runs/local-latest/audit.json`：五场景执行的原始合成日志链，问答正文与每次授权保留。
- `runs/first-scenario-failure.json`：首次 S-01 失败，后续增加授权关联检索修复；不是预期内容充当实际输出。
- 本轮初期：DEV-02 3 tests；DEV-04 18 tests；增量扩展后 26、30，当前数字看 tests.json。
- 环境限制：首次沙箱 HTTP bind 失败，获准 loopback 执行后通过；IAB 不可用、Chrome localhost ERR_BLOCKED_BY_CLIENT，视觉验收 blocked。
- Live API/model：not_run / blocked；G1/G2：not_run。
- CodeBuddy/WorkBuddy：not_started。任务见 `docs/CODEBUDDY_TASK.md`。实际对话/截图只能来自真实工具，敏感原始记录放 ignored `tool-usage/private/`，未批准不上传。
