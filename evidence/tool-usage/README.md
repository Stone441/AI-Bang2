# Real CodeBuddy contribution · DEV-09-CB

2026-10-04 Asia/Singapore。操作者：Codex 按 Kyle 明确授权操作 VS Code 原生界面。
工具：Tencent CodeBuddy 插件 4.12.38765564，Craft / Auto；没有模拟调用，没有另装 CLI。

- 基准 `81df3ef`，隔离 worktree `.runtime/codebuddy-dev09`，分支 `codebuddy/dev-09-audit-verifier`。
- CodeBuddy 实际编写：`tools/audit_verifier/`、`tests/codebuddy/`、`docs/CODEBUDDY_AUDIT_DELIVERY.md`。原始本地提交 `4165ee6`；Codex 审查并集成为 `8cd5088`。
- Codex 贡献：任务拆分、命令审查、Ed25519 命令纠正、密钥算法/类型检查审查建议、独立复跑、集成与证据整理。没有把 Codex 编写的实现归给 CodeBuddy。
- CodeBuddy 初版测试曾发生初始化错误和删除事件的 verdict 断言错误；原始记录保留了失败及修复。没有移除拒绝篡改的断言；增加了部分覆盖的删除测试。
- 独立验证：`python3 -m unittest discover -s tests/codebuddy -v`，20/20 passed；集成后 `make test-report`，52/52 passed，含 HTTP 测试。实际 JSON 见 `../runs/local-latest/tests.json`，含代码 SHA-256 和时间。
- 测试使用合成 Audit.export() 和临时测试密钥；OpenSSL 签名/验签是真实运行，业务源和回答模型仍为 fixture/fake。不代表生产独立签名根或完整 A-11 密钥轮换已验收。

## 私有原始证据

以下文件实际存在于 `private/dev09-20261004/`，Git ignored，未上传。`dev09-manifest.json` 只记录本地文件名、长度和 SHA-256，不含原始对话或截图。

| 文件 | 实际内容 |
|---|---|
| `01-task-start.png` | 在真实 CodeBuddy 提交任务 |
| `02-contract-plan.png` | CodeBuddy 读取契约后的方案 |
| `03-implementation-review.png` | 实现阶段界面 |
| `04-code-writing.png` | 实际写入代码过程 |
| `05-tests-debugging.png` | 真实测试失败与修复 |
| `06-initial-validation.png` | 初版交付/验证，尚未完成安全审查 |
| `07-final-validation.png` | 审查修正后的最终测试交付 |
| `conversation-history.zip` | 通过 CodeBuddy History → Export 原生导出的完整会话；已校验 ZIP 和内含 JSON 可读 |
| `01-*.ax.txt` … `06-*.ax.txt` | 阶段界面的原始可访问性文本快照，用于补充核对，不能替代原生对话导出 |
| `codebuddy-original.patch` | 原始提交完整补丁 |

原始截图没有重绘或拼接。开发 credits 与应用 runtime 预算分离；未购买资源或新订阅。证据公开、上传比赛仍需团队审批和脱敏检查。


2026-10-05 Slack onboarding：只读 manifest 审核与用户最终点击限流截图仅存 `private/onboarding-20261005/slack-app-readonly-review.jpg` / `slack-app-rate-limit.jpg`。无密钥截图，非 CodeBuddy 贡献。非敏感状态索引 `../runs/live-slack/installation-blocked.json`；安装/OAuth/API 尚未通过，截图不默认上传。
