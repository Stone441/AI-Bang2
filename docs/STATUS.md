# Current status

更新：2026-10-05（Asia/Singapore）。起始基准 `68e65c8` / main，仅文档。原未跟踪 `.DS_Store` / `Analysis&Planning/` 保留，Requirements 未改；README 仅追加运行说明。已完整阅读 AGENTS、PROJECT_START_HERE、docs/01–05，未采用旧 GPT Requirements。

**最新验证：96/96 测试通过（60 local synthetic + 36 mock HTTP），五场景仍为 passed_local_subset。Confluence operator query pilot 已接通共享引擎、索引、引用、历史与审计；用户提供真实 metadata-only API allow 结果，正文/问答/撤权及 live model 尚 not_run，前端仍 fixture。接续点见文末。**

**G0 仅本地完整开发已批准**；已批准专用四源空间的合成资料写入/测试权限调整，以及 DeepSeek 合成资料首轮等值 US$20 上限；真实空间、账号映射、凭据和预算控制尚未落实。G1/G2 未通过。原型已推送并通过 PR #1 合并至 main（81df3ef）；未部署、未调用真实知识平台/应用运行时模型。

## 已实现与验证

- 12 顶层对象 + 独立 Jira 安全评论，6 用户、78 权限组合；Confluence/Jira/Slack/Drive 各自 fixture policy。
- loopback 服务、opaque session/CSRF、英文 UI、四源关键词 + 授权一跳检索、fake extractive model、逐结论引用。
- 当前源授权在模型前和返回前检查；未知拒绝；四源撤权、旧历史/导出/引用保护。模型、HTTP 均有实际回归。
- 持久 fake source 与 SQLite 索引分离；对象级事务发布、创建/更新/删除、去重/乱序/重试、失败任务不被游标越过、重启恢复。请求触发处理，不宣称真实自动同步。
- 完整问答审计、逐资料决策、sent_to_model/cited/dispatch 区分、scope 查询与稳定分页；60 并发追加链测试。已接入离线 Ed25519 检查点 CLI；同机同账号仍不等于生产独立签名边界。
- `make test-report` 52/52 tests passed（32 原有 + 20 CodeBuddy）；另有 78 权限组合。`make verify` 五场景均 `passed_local_subset`，非完整 live 验收。首次 S-01 检索遗漏已复现、保留失败记录并修复。

原型 32 测试阶段已通过从提交导出的独立临时目录 `make setup` / `make test` / JS 语法检查；本轮签名集成验证为当前 checkout 的 52 测试回归。

证据：`evidence/runs/local-latest/tests.json`、`scenarios.json`、`audit.json`；包含运行时间、模式、基准 commit 与精确源码 SHA-256。验收映射见 ACCEPTANCE_STATUS。

## 能力边界与阻塞

| 项目 | 状态 |
|---|---|
| 四源 | fixture_only；live blocked（专用合成空间范围已批准，Slack/Jira/Confluence 已建立；Confluence Premium 试用至 2026-11-04、无付款方式，Drive/委托配置未完成） |
| 模型 | fake-extractive-v1；live not_run，无 embedding/reranker/compressor |
| 审计完整性 | partial；离线签名/篡改检测 verified local；独立 DB role / 加密 / 外部签名保管未实现 |
| 腾讯工具 | verified local：真实 CodeBuddy 实现 + 审查修正；20 新测试/全仓库 52 测试通过；7 截图及原生 conversation history 已本地保存，未上传 |
| 浏览器视觉 | blocked：IAB 不可用，Chrome localhost ERR_BLOCKED_BY_CLIENT；HTTP 集成通过不替代视觉检查 |
| 部署与人工 | local only；G1/G2 / 非作者质量与 ROI not_run |

## 精确接续点

1. DEV-09-CB 已完成：原始提交 `4165ee6`，集成提交 `8cd5088`，位于 `codex/dev-09-codebuddy-integration`；已通过 PR #2 合并至 main（71ad99b）。证据索引 `evidence/tool-usage/README.md`。后续推进密钥轮换、检查点生成节奏及独立保管；当前单公钥离线验证，不扩大 A-11 覆盖声明。
2. DEV-06：先完成 docs/LIVE_ONBOARDING.md 的注册交接。已生成本地 13 对象/6 身份 seed manifest，新增权限保留/禁止覆盖测试通过；没有平台写入。映射真实用户后才实施委托读取与撤权合同测试。
3. DEV-08/09：DeepSeek 首轮预算已批准；本地凭据配置、预算预留/故障记账和模型输出契约实现后才能调用，再做真实模型与语义支持评测；生产 DB/身份/HTTP 栈和独立审计边界仍需工程实现及运行验证。
4. 浏览器可访问后按 RUNBOOK 完成 UI/键盘/移动布局检查，并组织 G1 人工核验；完善候选材料，最后 G2。

本轮只交付本地候选，不宣称完整项目完成；没有承诺会话结束后继续运行。

2026-10-05 接入增量：Confluence `AIBANG2` 专用受限空间已建立（主页 131286），仅验证管理员可打开；独立身份访问/撤权、项目 seed 种植及 API 仍 not_run。等待队员测试邮箱映射，接续见 LIVE_ONBOARDING。

2026-10-05 身份增量：两个本人控制的测试邮箱已收到 Confluence 邀请，分别映射 eng_b/product_ops；后台 Invited。首次注册/登录待用户完成，native identity 只保存在 ignored 配置；真实 ACL not_run。

2026-10-05 原生配置增量：用户报告两测试账号注册完成；Confluence 空间两成员设 Viewer。首份 C-01 合成资料已发布（page 98564），原生 Restricted 名单仅管理种植者及 eng_b；核心原文已发布后核对。仅配置验证，普通用户允许/拒绝与撤权 not_run；等待独立用户会话。

2026-10-05 DEV-06-CF：实现白名单 Confluence delegated reader 与 operator-only probe，16 个模拟 HTTP/配置测试。完整 69 测试在允许 loopback 的环境通过；首次沙箱运行 4 项 HTTP bind 被阻止，未跳过断言。无真实 API 调用；尚未连接 Engine、OAuth/用户 session、索引/审计同步。精确接续见 CONFLUENCE_PILOT，先取得原生 space ID 与各用户最小委托凭据，再集中跑端到端撤权。

2026-10-05 C-02 已真实发布（page 164283），核心能力原文已读取核对。C-01/C-02 native ID 本地 manifest 已映射，页面配置不当作 live ACL 通过；剩余 C-03 和其他三源资料、委托及 runtime 接线继续待做。当前开发分支 codex/live-onboarding，无远端推送。

2026-10-05 DEV-08-BUDGET：持久化预算 reservation ledger 已实现，7 测试通过，覆盖跨连接预留、重启后未知消耗占用、禁止已发送请求退款、结算幂等、估计超支冻结和 US$20 上限。尚未接入模型 provider，因此不宣称运行时费用已受控或 live model 已启用。官方 DeepSeek API/pricing/JSON 文档本次读取 timeout；接口与计价须实际核对后再写适配。

本轮最终验证：make test-report 在获准 loopback 环境 76/76 passed（16 mock HTTP 合同 + 60 local synthetic），被测源码哈希逐项核对一致，证据 tests.json；live_api_called=false。已保存 C-02 真实发布截图，仍不以模拟合同/后台配置替代 live 全链路。

2026-10-05 DEV-06-CF-QUERY：新增独立操作员查询 pilot，复用 Engine/Store/Audit。逐次用户委托读取构建预过滤快照；dispatch 前、返回前、历史/引用重查；版本更新、删除、unknown 和撤权不能复用旧允许。14 个新增模拟测试；scoped token gateway 的固定 cloud UUID 验证另增加 1 测试。修复空证据历史也必须验证租户/身份。make test-report 91/91 passed（31 mock HTTP + 60 local synthetic），源码哈希一致；make verify S-01…05 passed_local_subset。没有真实 API/模型调用或新费用。

当前精确接续：浏览器 tab 996082519 为 eng_b 的 scoped API token 配置第一页；普通登录与额外邮箱 step-up 已由用户完成，并在管理页核对测试邮箱。尚未创建 token。自动审批拒绝填写具体 token 名称/有效期，要求行动时确认；已集中询问 `AI-Bang2 eng_b read-only pilot`、2026-10-20 到期、拟用 `read:content-details:confluence` / `read:page:confluence`。待具体批准后配置，由用户最终创建/保管凭据；不得使用管理员回退。native space ID 仍待核验。浏览器直开只读 API metadata 被 ERR_BLOCKED_BY_CLIENT 阻止，未绕过。真实前端身份/OAuth、四源联通、DeepSeek provider 与计价仍待完成；官方 DeepSeek 文档本轮再次 timeout，不凭旧模型名计价。

接续更新（覆盖上一段 token 配置状态）：用户已具体批准 AUTH-005，token 最终 Review 页已实测核对名称、2026-10-20 到期、两个 read scope，截图本地留存；最终 Create token 和保管交给用户。用户询问密码管理器位置，已给出 Mac Passwords 独立条目说明；尚未确认创建/保存，不读取可能正在显示密钥的弹窗。独立私有配置 `.runtime/confluence-pilot.json` 已准备（0600，仅 account ID/env reference，无凭据），native space ID 尚占位。新增 TTY 隐藏输入（拒绝 echo fallback）及白名单页面 metadata-only space discovery；5 新测试，全回归96/96，哈希核对一致。先前接线里程碑本地 commit `0a12481`，无远端推送。下一步用户保存 token 后，在本机终端运行 CONFLUENCE_PILOT 的 --discover-space --prompt-credential 命令，拿到实际 space_id 再配置正式读取；不将配置发现当端到端验收。

2026-10-05 凭据交接：用户回复“保存好了”，标记 token 已创建/保管（user_reported），未由程序读取或验证。不打开可能显示密钥的页面。私有配置 0600、两页面白名单已核对；下一步用户在本机真实 TTY 隐藏输入，运行 metadata-only discovery，将不含密钥/正文的结果 JSON 返回。收到实际结果前，live API 仍 not_run；不能把 token 保存等同 API 授权成功。

2026-10-05 首个 live API 结果（用户提供 CLI JSON）：eng_b / page 98564，current-user 与 metadata-only discovery 为 allow，space_id=131227，checked_at=2026-10-04T17:57:23.450014Z（新加坡 10-05 01:57），content_returned_to_probe=false，policy_version=0。原始结果及 user_supplied provenance 已存 evidence/runs/live-confluence/space-discovery-user-reported.json，不标 Codex 独立复跑或 live ACL 全通过。私有配置与模板 space_ids 已更新，credential-free 配置加载通过，无追加网络调用。下一步在用户 TTY 执行正式 query + --prompt-credential；完成后 Codex 可直接读本地 .runtime/confluence-query.sqlite 的回答/审计，无需贴长正文。仍需正文处理、查询、跨身份拒绝、撤权/历史/引用的真实验收。
