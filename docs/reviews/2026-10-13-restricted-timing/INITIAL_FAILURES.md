# 本轮初始失败记录（保留事实，不视为最终通过）

以下为当前会话工具stdout的摘要，不是复造原始完整终端日志。最终日志另存，没有覆盖初始整合日志。

1. `PYTHONPATH=tests:. python3 -m unittest test_restricted_timing -v`：9 tests / 0.556s，1 failure。enabled late-change契约的构造期四类subtest均报告 `PermissionError not raised`。计时install已在instance捕获实际source_claims，而旧注入patch的是class方法；改为patch当前instance，仍在原文构造后注入同样变更，断言不变。复验该安全契约通过。
2. `PYTHONPATH=tests:. python3 -m unittest test_restricted_timing test_source_review_dispatch_contract -v`：14 tests / 0.629s，1 error。fixture HTTP测试读取诊断时 `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`。直接写最终json让读者看到未完成内容；改为pending完整写入、原子发布，并让HTTP测试使用保存完成Event同步，不增加业务等待或删断言。随后14 tests / 0.624s通过。
3. `PYTHONPATH=tests:. python3 -m unittest test_restricted_timing -v`：10 tests / 0.593s，1 failure。新增timeout测试错误期待state为usage_unknown，actual为dispatched。读取现有BudgetLedger/model_receipt与既有timeout测试确认实际契约：state=dispatched、outcome=usage_unavailable、called=None、pending_requests=1；按真实契约增加这些具体断言，不改账本实现或减少预留。
4. 首次全回归：500 tests / 23.863s，1 error。`ObservedLock` only提供context-manager协议，计时层直接调用acquire导致AttributeError。完整输出见full-local-regression.log。修复保持原__enter__/__exit__，定向18和最终502通过。
