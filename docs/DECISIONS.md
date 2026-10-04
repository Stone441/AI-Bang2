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


## 2026-10-04 · AUTH-002 · CodeBuddy execution and local evidence

用户明确授权 Codex 直接操作已安装的 VS Code CodeBuddy、必要时安装官方 CLI、协助过程截图。已验证插件 4.12.38765564 可用，因此采用真实插件入口，无需新增 CLI。允许将本项目开发任务与代码交给该工具使用现有开发额度；不将此扩展为应用 runtime 费用/真实业务数据授权，不自动充值。截图与对话证据只保存在 ignored 本地目录，不自动上传。

CodeBuddy worktree 基于已合并的 81df3ef，避免从旧基准遗漏最新任务包；v1 hash 契约不变。Codex 仅进行任务下发、命令审查、测试和后续集成，签名验证器代码由 CodeBuddy 实际生成，分别记录来源。未自动合并或推送本轮分支。

## ADR-005 · 2026-10-04 · 真实 CodeBuddy 审计签名集成

CodeBuddy 插件在隔离 worktree 实现 DEV-09-CB；原提交 `4165ee6`，Codex 审查后 cherry-pick 为 `8cd5088`。使用系统 OpenSSL Ed25519，无新增 Python 依赖或应用运行时费用。Codex 指出初版密钥算法与 bool/int 验证问题，由 CodeBuddy 修正并增加测试；Codex 独立复跑 20 新测试、全仓库 52 测试通过。签名只证明 trusted checkpoint 覆盖的规范化事件，未覆盖尾部、检查点回滚/新鲜度、v1 跨流身份、同账号全面失陷和密钥轮换未被此实现解决。回滚可单独 revert 集成提交，不改变问答链路。真实截图/对话留本地 ignored evidence；未上传/提交比赛。

## 2026-10-05 · AUTH-003 · synthetic live sources and DeepSeek pilot

用户“可以，按你说的来”批准上一轮明确提案：建立比赛专用 Confluence/Jira/Slack/Drive 测试空间，仅写入合成资料，允许在这些空间调整测试身份权限；不接入 NTU 课程 Slack 或既有个人资料。站点/文件白名单和真实账号映射仍需落实。注册验证码、条款接受和授权确认由用户完成。平台采用可用免费/试用方案，不授权收费续订。

DeepSeek 直连首轮总预算上限等值 US$20，仅处理合成资料，不自动充值；OpenRouter 仅备用，未批准额外调用。密钥通过本地忽略配置提供，不能发到聊天或提交 Git。配置存在不等于 live 验收完成；预算控制与输出校验完成后才开启调用。G0 部分授权扩大，不标整体通过；G1/G2 仍待人工验收。

## 2026-10-05 · AUTH-004 · Confluence trial agreement

用户在展示具体 Customer Agreement、隐私政策与 30 天 Premium 试用后明确回复“同意接受”，已点击 Try now 并验证开通。仅授权免费试用，不授权付费续订。账单显示 2026-11-04 到期、Payment info None，且提示未补付款方式将停用；不能把通用自动降级说明当成本账户保证。到期前人工检查并选择 Free，避免演示中断。截图仅本地 ignored 保存，API/ACL live 验收仍 not_run。

## ADR-006 · 2026-10-05 · 委托读取与集中端到端验收

根据用户明确反馈，停止逐页人工平台权限点验，保留一次接通问答链路后的真实撤权/同会话/引用历史验收。实现首个只读 Confluence pilot：凭据身份用 current user accountId 实测比对，不回退到管理员；页面与空间 ID 白名单，metadata/body 双读取一致性，无允许缓存。平台不提供 ACL revision 时 policy_version=0，不能替代真实 ACL 版本。仅支持普通合成 storage 文本；宏/附件拒绝使用，避免忽略子资源权限。暂不接入原 FixtureWorld/Engine，以免假身份及 fixture 模式掩盖真实模型/权限差异；下一步显式 live authority 与服务端 session 接线。配置只保存 env reference，CLI actor 是操作员诊断参数，非产品身份。真实 scope/token 创建仍未执行。回滚可单独移除 reader/probe，不影响 fixture 应用。

## ADR-007 · 2026-10-05 · 未知模型消耗保留预算

预算使用 integer micro-USD（总上限 20,000,000），SQLite BEGIN IMMEDIATE 串行预留。网络发送前持久化 dispatched；超时/进程崩溃不自动退款，未知用量继续占用全部预留。只可取消未发送请求。真实费用结算超过预留时先记录实际值，再冻结后续发送并报错，不能把超支隐藏为成功。账本不控制供应商账户其他调用；需固定模型价格/token 上界与官方计价后接入 provider，未接入时不声称预算保证。
