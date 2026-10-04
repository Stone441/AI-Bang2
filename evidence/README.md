# Evidence index

仅保存实际执行记录，fixture/fake 与 live 分开。

- 2026-10-04 DEV-02：`make test`，Python 3.14.7，3 tests passed（78 个权限组合另为 subtests）；`tests/test_contracts.py`。
- live API/model：not_run / blocked（未授权）。
- CodeBuddy/WorkBuddy：not_started，未调用、不声称贡献。敏感原始记录只放被忽略的 `tool-usage/private/`，不得默认上传。
- DEV-03/04：`make test` 18/18 通过（loopback 测试需环境允许本地 bind）；`node --check web/app.js` 通过。测试定义见 `tests/test_engine.py`、`tests/test_http.py`。首次沙箱运行 16 passed + 2 socket bind errors，未删除测试，授权重跑通过。
