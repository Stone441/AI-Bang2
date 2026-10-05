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

这是LOCAL OPERATOR / LIVE API / FAKE MODEL试点，不是员工SSO/OAuth。只有白名单合成Confluence页面，不发收费模型请求；源授权在查询、模型前、返回前及history/export/preview仍重查。默认不带`--live`不读凭据/联网。代码已mock HTTP验证，C-01真实网页问答已记录，引用/历史获用户确认；不是完整Confluence权限矩阵或G1通过。

Jira只读诊断/问答命令、原生ID配置与权限缺口见 [JIRA_PILOT.md](JIRA_PILOT.md)，不能复用Confluence token或将模板中的占位ID当真实ID。


操作员启动故障（2026-10-05修复）：先预留loopback端口，再隐藏输入凭据；服务只在native identity验证后开始处理HTTP。`[port_in_use]`表示监听端口已有服务，不请求凭据、不调用平台；保留已有服务或在命令末追加`--port 8082`（不要擅自kill占用者）。其他安全诊断分为configuration_or_hidden_input、local_store、native_identity、runtime；不会打印异常原文、token或上游body。身份未知仍停止，不能靠诊断降低授权要求。


### Jira operator web（一次启动输入，进程内复用）

已批准 Jira 凭据、核验 native IDs 并配置 `.runtime/jira-pilot.json` 后：

```sh
python3 -m brain.operator_web --source jira --config .runtime/jira-pilot.json --actor eng_b --port 8083 --live
```

启动时隐藏输入实际 eng_b 邮箱与密码管理器 Jira token 一次，打开输出的一次性入口链接（不要截图/分享 ticket）。同一运行进程中，网页 query/history/citation 不再请求输入 API 凭据，但每次仍重查源身份及当前权限。不是将授权结果缓存成永久 allow。DB 独立为 `.runtime/jira-web.sqlite`；Ctrl+C 停止后内存凭据消失，下次启动需重新输入。默认不读取系统密码应用，不保存 token 文件。保留已有 Confluence 服务，不 kill 端口占用者。网页是操作员 pilot/fake model，不是 SSO 或 live LLM。

可问 `What is the status of the payment-service retry configuration fix, and does completion approve general customer release?`，点击引用及 Recent answers；实际结果由 DB 验证，不能把 mock 测试当 live 问答通过。

前端安全视图回归：`node tests/frontend_operator_security.js`（需Node，独立于标准库Python运行时）与 `node --check web/app.js`。验证导航/preview拒绝/待返回query/history请求清除旧视图。页面跨视图不复用旧答案；请用Recent answers重新鉴权访问。前端静态文件修正可直接刷新当前网页，session仍有效，无需重启或重新输入API凭据。


### Slack operator pilot

见 [SLACK_PILOT.md](SLACK_PILOT.md)。一次隐藏输入 USER OAuth token，不需要邮箱；配置 native IDs 后可使用 `--source slack --actor eng_a --port 8084`。既有app已由用户授权并保存token，真实root/reply问答、引用与历史已核验；频道撤权仍待独立reader。不要直接运行含占位ID的模板，当前结果仅live API + fake model。


### Drive operator preparation

见 [DRIVE_PILOT.md](DRIVE_PILOT.md)，本地mock已接同一Engine/网页入口，首版personal Drive UTF-8 text/plain；真实scope、OAuth、原生IDs/种植尚未批准配置。准备的`--source drive --port8085`命令不可用占位模板直接当live启动。

### Unified multi-source operator

`--source multi` supports two to four reviewed source configurations under one tenant and one operator actor. Copy `config/operator-bundle.example.json` into ignored `.runtime/operator-bundle.json`; include only approved/configured sources. Paths are relative to the bundle. Keep the example review flag false until each source account is verified as belonging to the intended operator persona, then set `identity_mapping_reviewed` to true. This local flag records a trusted configuration review; it does not verify ownership or grant source rights. Do not rename existing eng_a/eng_b mappings merely to make a bundle load.

```sh
python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --port 8086 --live
```

The loader validates all configurations and matching tenants before prompting for any missing credential. Approved environment references can supply already-configured credentials; otherwise each source asks once using its existing hidden-input helper. Every configured native identity is checked before the browser bootstrap is issued. Each later read still checks current source rights. The local database is `.runtime/multi-web.sqlite`; no secret is stored in it or sent to the browser. Keep existing single-source processes running. Do not extract their in-memory tokens or reuse an identity mapping that belongs to another persona.

Four-source HTTP integration and one-source revocation are mock-verified. The current live Slack eng_a and Confluence/Jira eng_b configurations are not a reviewed same-persona bundle. Real unified integration, Drive OAuth, SSO, live model and G1 remain pending; no restart/input is requested for this new feature yet.

### Drive Google desktop consent (no manual token copy)

After the approved Google desktop client and exact synthetic files are configured:

```sh
python3 -m brain.operator_web --source drive --config .runtime/drive-oauth-pilot.json --oauth-client .runtime/drive-oauth-client.json --actor eng_a --port 8085 --live
```

The downloaded desktop client JSON is private, ignored by Git and must be owned by the local user with mode 0600, not a symlink. Use `config/drive-oauth-pilot.example.json` as the configuration shape; all placeholders are deliberately invalid. Review the Google client ID, operator email and exact file→parent IDs. The server reserves 8085 before consent; leave other source processes running. It prints a Google authorization URL with one-use state and S256 challenge. Open it and complete only the approved Drive read-only consent yourself. Do not share the authorization URL, callback code, client JSON or bootstrap ticket. The callback listener is loopback-only and waits up to 10 minutes.

The program exchanges the one-use code, checks the exact granted scope and native Google account metadata, then serves the same operator UI. It does not ask for email/token input. Tokens are in process memory; no refresh is persisted or used, so expiration fails closed and a later start requires browser consent again. The callback page says received before native account verification: only successful operator startup confirms that verification passed. This is not employee SSO, and Drive native read/revocation acceptance remains separate.

OAuth callback成功页是临时页面：看到Google authorization received后不要reload。账号检查通过后临时listener关闭，旧callback URL重载可出现ERR_CONNECTION_REFUSED；这不等于Drive服务退出。使用终端后续8085应用入口即可，不发送ticket/code。若Chrome拦截agent自动打开localhost（ERR_BLOCKED_BY_CLIENT），由用户在应用入口地址栏Enter，不关闭安全设置、不重复Google授权。health显示drive_live_api_fake_model/operator才确认正式服务启动；应用查询仍单独验收。

### Approved DeepSeek pilot (price reviewed 2026-10-05 Singapore)

Keep the existing port 8085 process. In a new local VS Code terminal:

```sh
python3 -m brain.operator_web --source drive --config .runtime/drive-oauth-pilot.json --oauth-client .runtime/drive-oauth-client.json --actor eng_a --port 8086 --live --model deepseek
```

Complete the existing Google read-only consent through the terminal URL, then enter the DeepSeek API key at the hidden prompt. Do not paste the key or bootstrap URL into chat. Open the application link after startup. Google callback is temporary: do not reload it. Subsequent questions reuse credentials held in this process. Default commands without `--model deepseek` remain fake-model pilots. No live model call occurs during startup.

Only explicitly marked synthetic evidence is sent. The model selects evidence; the server renders original excerpts. Free-form synthesis is not enabled. `.runtime/deepseek-budget.sqlite` is the shared USD20 ledger across all operators: never delete, reset, replace or change working directories to bypass pending charges. Peak/cache-miss accounting is conservative, not a billing invoice. Unknown consumption keeps its full reservation. Price review expires at the end of the reviewed Singapore date; future startup or nonempty model use stops until prices are reviewed again. Existing fake services continue running. Real DeepSeek results remain not_run until actual call/output/ledger/audit are inspected.

Actual first DeepSeek checkpoint: [live-drive-query.json](../evidence/runs/deepseek/live-drive-query.json), native Drive + real model selection, query/preview/history verified. Original fake commands and comprehensive live acceptance are separate. Keep port8086 running; no further key input is required during its lifetime.

Model usage receipts: new answers expose validated token counts and a conservative USD cost estimate under “Model usage receipt”. This is not the vendor invoice. Older answers without a receipt say “MODEL CALL NOT RECORDED”; do not infer a live call or zero usage from their evidence list. Native/history/export authorization still gates the entire record. Static UI updates require refresh; already running Python processes do not load changed Engine code automatically.

Atlassian hidden input: enter the mapped Atlassian email only, then paste only the scoped token value from the password field. Nothing appears while typing/pasting. Invalid input retries just that field (at most3 attempts): `credential_email_invalid`, `credential_token_empty`, `credential_token_multiline`, `credential_token_too_long`; `credential_secure_tty_required`, `credential_hidden_input_unavailable`, `credential_input_ended` stop without echo fallback. These local diagnostics do not indicate whether a token is valid on the platform. Share only the fixed error code for troubleshooting, never entered values.


### Approved one-command four-source startup (AUTH-014)

在仓库根目录的新 VS Code 终端只运行：

```sh
make live
```

使用已审核 eng_b 的 ignored bundle，8088，真实四源及 DeepSeek，显式 opt-in 本机钥匙串保存。首次仍需逐项隐藏输入 Confluence/Jira 邮箱与各自 token、Slack reader token，完成 Google 只读浏览器授权，再隐藏输入 DeepSeek key。程序不读取你在「密码」应用里已有的条目；创建自己的钥匙串条目。已保存项在后续启动复用，后续步骤失败也不丢失前面的已保存项。操作系统可能要求解锁或允许钥匙串访问。不要关闭安全设置，不发送密钥/完整入口链接。

Google refresh 只在原生账号核对成功后保存；以后重启自动换 access token，scope 固定 drive.readonly。撤销/过期可能需要只重新完成 Google 授权；运行中的 access token 到期仍拒绝访问，可重启。源 token 的格式校验不等于平台授权通过：启动仍核对全部原生账号，每次问答/引用/历史仍核对当前权限。DeepSeek 价格日期及 USD20 账本限制不变。

如只有某枚凭据错误，复制下列命令，将最后的平台选择为 confluence、jira、slack、drive 或 deepseek，只重新输入该项：

```sh
python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port 8088 --live --model deepseek --credential-store macos-keychain --replace-credential slack
```

默认未指定 credential-store 的旧命令依然仅内存保存。钥匙串拒绝读取时停止，不回退明文。只读平台与模型真实集成另行验收；本次合成钥匙串 smoke 和 mock refresh 不代表统一四源 live 已通过。


答案和Recent answers中的Export answer会重新检查所有依赖的当前权限，再下载服务端原始JSON envelope（history数组，保留大整数版本号）。已撤权的答案不下载文件。下载副本离开系统后不能被撤回；演示中只导出合成资料。刷新页面即可加载前端更新，无需重启服务/重填凭据。Session失效时提示打开运行终端最新的一次性入口；资料403而session仍有效时只拒绝对应访问，不要求重登录。

### Opt-in grounded synthesis (synthetic pilot)

Default `make live` retains source-excerpt selection. Use `make live-synthesis` for the reviewed mode, or add
`--answer-style synthesis` to the reviewed multi-source command:

```sh
python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port 8088 --live --model deepseek --credential-store macos-keychain --answer-style synthesis
```

Do not start a second process on an occupied port. Keep the current service or
stop it yourself before selecting this mode; app-owned Keychain reuse avoids
re-entering saved credentials. Native account verification still runs. Existing
source scopes and the same `.runtime/deepseek-budget.sqlite` USD20 ceiling apply.
Do not change the working directory to create another budget ledger.

Ask `What is approved for the payment-service pilot, what remains blocked, and what incident safeguards must be in place?`.
The answer displays a concise conclusion per claim, citation buttons, expandable
exact supporting quotes, and separate generation/review usage receipts. History
and raw export preserve grounding and both receipts; current access is checked
again. The review reads full authorized evidence after another native check.

Review is a fallible quality filter: exact quotes prove source provenance, not
semantic correctness. Human acceptance must check scope, negation, contradictions
and whether conclusions actually follow and answer every requested part. The v2
review requires explicit boolean `question_covered: true` as well as support for
all claims; this remains a fallible model judgment. Missing quote/citation, unknown or
negative review, changed access/version and incomplete output reject the answer;
no automatic paid retry or silent fallback occurs. Fake-model mode does not
simulate passing synthesis review. Complete five-scenario live acceptance and
G1/G2 remain separate from local/mock results.


To preserve an existing8088 service while opening another reviewed synthesis operator, use `make live-synthesis LIVE_PORT=8094` from repository root. The same budget ledger is used, with no scope change; native identities are verified again. Open the new terminal one-use link yourself and keep it out of chat/screenshots. `LIVE_PORT` defaults to8088; existing listeners are never killed automatically.

Frontend navigation/expiry/sign-out invalidate prior requests. A late answer/quote/history/export does not repopulate the newer view or create a file; this does not undo an already-dispatched model call or recover a downloaded copy.
