# 安装、启动、测试与演示

要求 Python >=3.11（本次实际 3.14.7）、可绑定 loopback 端口。应用零第三方 Python 依赖，无 npm/pip 安装步骤；无需 API key。签名工具及完整测试另需 PATH 中的 OpenSSL（已验证 3.6.3，需支持 Ed25519 pkeyutl -rawin）。Node 仅用于 `node --check web/app.js`。在仓库根目录执行。

```sh
make setup
make test
make demo
```

浏览器打开 `http://127.0.0.1:8080`。界面显示 LOCAL DEMO / FAKE MODEL；可选六个合成身份。`python3 -m brain.server` 不带 `--demo` 会拒绝启动；绑定地址不可从命令行改为外网。退出 Ctrl+C。

运行数据在 `.runtime/`（Git ignored）：SQLite 保存索引/审计/历史，source.json 为独立的 fake source 当前权威；session 仅内存，重启需重新登录。源文件替换为原子写入，demo 管理命令请串行执行。全链路只含合成资料，不能把此目录替换为真实企业资料。

## 五场景现场回放

1. **S-01**：以 Alex / eng_a 登录，点 Understand the incident，提交问题。核对 root cause、withdrawn hypothesis、PAY-102 Done、PAY-103 In Progress / Maya、runbook 和四源引用。以 Product & operations 登录查 release readiness，核对 pilot、GA not approved。
2. **S-02**：先查 runbook v1，再在另一个终端执行：

   ```sh
   python3 -m scripts.fixture_admin runbook-v2
   ```

   回到同一网页再查 latest runbook，看到 v2 和 standby queue 步骤。当前是请求驱动的本地事件处理，**不是已实现的真实 webhook/定时同步延迟**。
3. **S-03**：以 External partner 登录，问 `Show me the Q3 security incident report.`；不得确认受限对象存在。再问 external partner pilot，应有正常获准资料。
4. **S-04**：以 eng_a 获取 incident thread 回答，保留该会话。另一个终端执行：

   ```sh
   python3 -m scripts.fixture_admin revoke --resource S-01 --user eng_a
   ```

   原会话追问线程详情；不得再次输出线程独有标记。打开旧 S-01 引用应不可用；Recent answers 中依赖已撤权资料的整条旧回答应不可用。无需全库重建。可分别对 C-01/J-01/D-01 重复。
5. **S-05**：以 Scoped auditor 登录，打开 Audit explorer，提交预置问题。展开事件查看身份、问题、逐资料授权、sent_to_model、引用和最终答案；支持稳定 snapshot 分页。HTTP 场景还记录 dispatch_attempted。CLI 回放不伪装成 HTTP dispatch。

完整自动回放使用隔离内存状态，不改变正在演示的 `.runtime`：

```sh
make verify
make test-report
```

输出 `evidence/runs/local-latest/scenarios.json`、`audit.json`、`tests.json`。S-05 检查仅是内存保留 trusted head 的本地演示，未具备独立签名根。离线签名另由真实 CodeBuddy 实现并经 20 项测试验证；命令见 CODEBUDDY_AUDIT_DELIVERY.md，同机同账号不代表生产独立保管。

要重新开始人工演示，停止服务后仅将 demo 数据文件改名备份，再启动；先确认备份名称不存在。不要整体移动 `.runtime`：目前其中有 `.runtime/codebuddy-dev09` Git worktree。不要删除旧审计。自动测试均使用自己的临时/内存状态。

## 故障与边界

- 沙箱报 `Operation not permitted` at socket.bind：是 loopback 执行权限，不是测试通过；在获准环境运行同一测试，不跳过 HTTP 测试。
- 浏览器 `ERR_BLOCKED_BY_CLIENT`：本次自动化环境阻止 localhost 浏览器访问，视觉/交互验收未完成。不要关闭安全设置来绕过。
- 端口被占用：`python3 -m brain.server --demo --port 8081`。
- 审计不可写、授权 unknown、源/索引版本不一致：不返回无法安全完成的成功答案。
- 无跨用户答案缓存，无 reranker/compressor，因而这两类真实模型入口尚无效果验证。
- 仅 loopback、无 TLS/SSO、无独立数据库权限身份，不能作为公开部署方案。G1/G2 由团队验收。
