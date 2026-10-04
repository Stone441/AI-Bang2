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

Confluence 只读 API pilot 的配置、诊断及共享 Engine 查询命令见 [CONFLUENCE_PILOT.md](CONFLUENCE_PILOT.md)。独立操作员入口已接通本地索引/检索/引用/审计，Confluence API操作员查询/撤权已实际运行；新网页入口已通过mock源+真实loopback HTTP测试，真实网页运行待用户完成。以上demo命令仍fixture。

- 沙箱报 `Operation not permitted` at socket.bind：是 loopback 执行权限，不是测试通过；在获准环境运行同一测试，不跳过 HTTP 测试。
- 浏览器 `ERR_BLOCKED_BY_CLIENT`：本次自动化环境阻止 localhost 浏览器访问，视觉/交互验收未完成。不要关闭安全设置来绕过。
- 端口被占用：`python3 -m brain.server --demo --port 8081`。
- 审计不可写、授权 unknown、源/索引版本不一致：不返回无法安全完成的成功答案。
- 无跨用户答案缓存，无 reranker/compressor，因而这两类真实模型入口尚无效果验证。
- 仅 loopback、无 TLS/SSO、无独立数据库权限身份，不能作为公开部署方案。G1/G2 由团队验收。


## Confluence 操作员网页（已批准eng_b只读token）

```sh
python3 -m brain.operator_web --config .runtime/confluence-pilot.json --actor eng_b --live
```

在真实TTY隐藏输入邮箱和token（不保存），打开终端输出的一次性本机链接。链接10分钟有效，消费后不能复用；它是会话入口凭据，不要截图/分享。启动时服务端核对token的native account ID；浏览器仅获opaque cookie/CSRF，不能选择用户或role。问 `Show the payment-service runbook`，核对引用、Recent answers。DB在ignored `.runtime/confluence-web.sqlite`，退出Ctrl+C；不要与8081已有服务冲突，可用`--port 8082`。

这是LOCAL OPERATOR / LIVE API / FAKE MODEL试点，不是员工SSO/OAuth。只有白名单合成Confluence页面，不发收费模型请求；源授权在查询、模型前、返回前及history/export/preview仍重查。默认不带`--live`不读凭据/联网。代码已mock HTTP验证；实际浏览器视觉/真实网页验收仍not_run，自动浏览器被环境阻挡。

Jira只读诊断/问答命令、原生ID配置与权限缺口见 [JIRA_PILOT.md](JIRA_PILOT.md)，不能复用Confluence token或将模板中的占位ID当真实ID。


操作员启动故障（2026-10-05修复）：先预留loopback端口，再隐藏输入凭据；服务只在native identity验证后开始处理HTTP。`[port_in_use]`表示监听端口已有服务，不请求凭据、不调用平台；保留已有服务或在命令末追加`--port 8082`（不要擅自kill占用者）。其他安全诊断分为configuration_or_hidden_input、local_store、native_identity、runtime；不会打印异常原文、token或上游body。身份未知仍停止，不能靠诊断降低授权要求。


### Jira operator web（一次启动输入，进程内复用）

已批准 Jira 凭据、核验 native IDs 并配置 `.runtime/jira-pilot.json` 后：

```sh
python3 -m brain.operator_web --source jira --config .runtime/jira-pilot.json --actor eng_b --port 8083 --live
```

启动时隐藏输入实际 eng_b 邮箱与密码管理器 Jira token 一次，打开输出的一次性入口链接（不要截图/分享 ticket）。同一运行进程中，网页 query/history/citation 不再请求输入 API 凭据，但每次仍重查源身份及当前权限。不是将授权结果缓存成永久 allow。DB 独立为 `.runtime/jira-web.sqlite`；Ctrl+C 停止后内存凭据消失，下次启动需重新输入。默认不读取系统密码应用，不保存 token 文件。保留已有 Confluence 服务，不 kill 端口占用者。网页是操作员 pilot/fake model，不是 SSO 或 live LLM。

可问 `What is the status of the payment-service retry configuration fix, and does completion approve general customer release?`，点击引用及 Recent answers；实际结果由 DB 验证，不能把 mock 测试当 live 问答通过。
