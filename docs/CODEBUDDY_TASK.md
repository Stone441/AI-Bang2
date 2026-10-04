# DEV-09-CB · 可直接转交 CodeBuddy

状态：未执行；没有任何腾讯工具贡献证明。当前未发现已授权 callable tool/CLI，由团队在实际 CodeBuddy 入口运行。

基准 commit：`889773c`。独立分支 `codebuddy/dev-09-audit-verifier`，独立工作目录；建议团队从该 commit 建立 worktree，不在 Codex 当前工作区编辑。后续契约变更须先与集成人核对。

允许新建/修改：`tools/audit_verifier/**`、`tests/codebuddy/**`、`docs/CODEBUDDY_AUDIT_DELIVERY.md`。
禁止修改：`brain/**`、`web/**`、`fixtures/**`、现有 tests、AGENTS、01–05、任何凭据和旧材料。

复制以下提示词，并显式附加列出的输入：

```text
你在真实 CodeBuddy 中承担 AI-Bang2 的 DEV-09-CB。先读 AGENTS.md，
docs/03_ARCHITECTURE.md 第10节、docs/05_ACCEPTANCE_TESTS.md A组、
docs/CONTRACTS.md 和 brain/audit.py、brain/store.py。

在你的独立分支/目录实现离线审计签名检查点生成器和独立 CLI 验证器。
输入是 Audit.export() 的 JSON 数组；规范化编码/哈希必须兼容现有 v1。
必须使用成熟密码库或系统 OpenSSL，不自己设计签名算法。
签名私钥通过本地文件路径输入，不写入仓库/输出/截图；验证器只需公钥。
检查点至少绑定 schema_version、through_seq、head_hash、timestamp。
验证器必须显式接受独立保留的可信 checkpoint 和公钥路径，不能从被校验
日志内部自动接受新的信任根。报告锚定范围及未覆盖尾部。

实现并实际运行：原链成功；正文改动、中间删除、已签名覆盖尾部删除、
整链重算替换、错误公钥、错误签名、缺检查点均失败或明确不可信。
未覆盖尾部必须单列，不能笼统输出全部可信。
仅允许修改任务指定路径。需要新第三方依赖时先提出，优先现有标准库
和已安装 OpenSSL。不得调用真实数据、外部业务写 API、收费资源或上传证据。

交付实现、测试、命令、环境、真实运行结果和限制；注明同机同账号的签名
仍不能抵御整个账号被攻陷。不要宣称完成生产独立安全边界。
保留真实对话记录、至少3张过程截图（理解契约、实现/调试、运行验证），
以及最终 commit/diff。不要伪造输出，失败先复现，再修复。
```

验收：A-03/A-04/A-11 的签名与校验部分；A-02 真实数据库角色另行实施。
团队保留证据到 `evidence/tool-usage/private/`（Git ignored），建立工具版本、入口、操作者、时间、原记录路径、截图路径、commit 清单。不得默认推送或上传对话。完成后告诉 Codex 工作目录与 commit，由 Codex review/test/integrate。
