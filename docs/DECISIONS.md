# Decisions / ADR

## 2026-10-04 · AUTH-001 · approved local scope

用户本次明确授权本仓库内本地、可逆、无新增费用的完整开发、测试、独立分支和小步提交，范围不再限于 Phase 0。G0 **仅本地开发部分获批**；四源真实账号/数据/scope、运行时模型、费用及数据出口待定。G1/G2 未通过。凭据存在不代表可用。无远端推送、公开部署或业务系统写入授权。

## ADR-001 · local implementation baseline

盘点基准 `68e65c8`：只有文档，Python 3.14.7 / Node 22.23.2；未发现 Docker、uv、FastAPI、pytest 等依赖。先用 Python 标准库、SQLite 和同源原生 Web UI 构建可重现本地闭环，避免安装/云资源依赖。Python unittest 实测安全边界；SQLite 事务维护版本与日志顺序。关键词检索先建立确定性基线，语义检索/真实模型效果仍待实现与授权。

代价：stdlib HTTP 服务仅允许 loopback 合成演示，不可作为生产部署；SQLite 不具备 PostgreSQL 独立数据库写角色隔离，A-02 不能因此通过。后续公开部署前迁移受支持 Web 框架、生产身份和数据库角色。迁移保留 SourceAdapter、Evidence、Model 接口和回归测试；不得放宽安全要求。

## ADR-002 · Tencent task reservation

当前工具注册表无 CodeBuddy/WorkBuddy 调用工具，PATH 未发现 CLI；不扫描/使用凭据、不调用收费开发入口。预留 DEV-09-CB：独立签名审计检查点及验证器（`tools/audit_verifier/`、`tests/codebuddy/`），由真实 CodeBuddy 实现；Codex 完成日志契约和基础 hash-chain，持续推进同步主线。选择此任务替代原 DEV-05，是为了在人工接力前不阻塞动态更新与五场景本地开发。签名与独立信任根未交付前 A-03/A-04 仅可报告局部链检查，不能标全通过。

## ADR-003 · source-linked retrieval and durable demo authority

自然语言 S-01 回放首次遗漏 PAY-103，证据保存在 first-scenario-failure.json。保留原 oracle，增加最多一跳、逐 seed 和目标授权的链接扩展；固定候选/字符预算。没有按题目硬编码业务答案。来源权威独立持久化到 `.runtime/source.json`，每次授权检查重新读取，避免生成期间的磁盘撤权只在下一 HTTP 请求才可见。源事件处理是 request-driven demo 模式，未实现真实 webhook/后台定时同步。

## ADR-004 · honest audit scope and acceptance

审计范围先在参数化 SQL 按获准 actor 过滤，再按精确 source/resource_scope 定位请求并返回其生命周期；因此可还原问题和最终回答，而不只看到孤立资源事件。自然语言仅支持文档模板，模糊/任意 SQL 拒绝。签名检查点由真实 CodeBuddy 独占实现；在此之前 S-05 只能标 passed_local_subset，A-02/03/04 的完整验收不通过。浏览器工具 localhost 被 ERR_BLOCKED_BY_CLIENT 阻挡，视觉验收不伪造。
