# Current status

更新：2026-10-04（Asia/Singapore）。首次盘点基准 `68e65c8`，起始 main，仅文档；原未跟踪 `.DS_Store` / `Analysis&Planning/` 保留，Requirements 和原 README 未覆盖。已完整阅读 AGENTS、PROJECT_START_HERE、docs/01–05；未采用旧 GPT Requirements。

G0 本地完整开发已批准；外部接入/模型/预算待定；G1/G2 未通过。

## Verified

DEV-00 仓库与环境盘点；DEV-02 合成 fixture/SourceAdapter/用户权限契约。
`make test`：3 tests pass；包括 13 × 6 权限矩阵子断言。模式 fixture_fake_model（当前无模型调用）。不是 51 项验收通过。Python 3.14.7 / Node 22.23.2，无第三方 runtime 依赖。

## Next

DEV-03/04：loopback 服务、服务端 session、检索/当前源权限、fake extractive model、引用、持久审计与 UI；随后同步/撤权与五场景回放。

四源 live blocked；模型 live not_run；腾讯工具贡献 not_started。无可调用腾讯工具连接，PATH 未找到 CLI。独立签名校验器预留 CodeBuddy。

## 纵向链路更新

DEV-03/04 本地闭环 verified：英文静态前端 + loopback HTTP、opaque session/CSRF、四源 fixture 检索、模型前及返回前权限复核、严格摘录 fake model、引用/历史/导出保护、持久审计与 scoped query。`make test` 18/18 通过，含真实 loopback HTTP（沙箱内绑定初次失败；授权执行后通过）。`node --check web/app.js` 通过。未启用 reranker/compressor/答案缓存；浏览器视觉核对待运行。

当前 hash-chain 没有独立签名 checkpoint；SQLite authorizer/trigger 仅为逻辑演示，A-02/A-03/A-04 不完整。增量和五场景记录下一步。
