# Confluence delegated read pilot

2026-10-05：委托读取已通过独立 operator pilot 接到共享 Engine / Store / Audit；36 个模拟 HTTP 合同测试。用户提供首个 metadata-only live API allow，native space ID `131227` 已配置；正文/问答/撤权仍 `not_run`。未接到浏览器登录，不改变 LOCAL DEMO / FAKE MODEL 模式。

## 边界

`ConfluenceReader` 接受服务端确定的 Actor 映射，按对应凭据调用 `GET /wiki/rest/api/user/current`，核对 native account ID 后才获取白名单页面。不会回退到管理员或共享采集账号。CLI 的 `--actor` 仅用于本地操作员诊断，不能复用为前端登录机制。

仅允许明确指定 HTTPS Atlassian 站点、page ID 和 native space ID。先读取页面 metadata，确认对应空间及 current 状态，再由同一凭据读取 storage 正文；版本变化、异常/缺字段/不支持的宏均停止。403/404 为 deny，401/429/网络或未知响应为 unknown，不输出正文、标题或上游错误。不缓存允许结论；旧版本请求必须与当前版本相同。HTTP 不跟随重定向，有超时、响应类型及大小限制。页面 URL 由后端构造。

operator pilot 每次查询清空该用户的本地允许快照，再读取两份白名单页面；只有对应用户此次获准的内容参与关键词检索。逐对象写入单独 SQLite 索引，并记录当前读取决策。已接入模型 dispatch 前、返回前及历史/引用访问重查。源端撤权、删除、429/未知不能复用索引中的允许结论；内容版本变化拒绝旧回答。仍存在多次 HTTP 请求之间的源端并发窗口，不宣称原子 ACL 事务。模块返回的 `policy_version=0` 表示平台未提供 ACL revision，不把内容版本当权限版本。

没有实现：用户 OAuth/SSO 登录、前端 live 路由、同步 worker、完整宏/附件/子资源、源端撤权传播延迟测量与真实模型。CLI actor 是本机操作员选择的映射，不能当作已验证员工登录。默认关闭网络；共享 fixture HTTP 应用仍仅使用 fake source。

## 配置与执行

先复制 `config/confluence-pilot.example.json` 到 ignored `.runtime/confluence-pilot.json`，填入实际核验的 native space ID 和独立测试用户 account ID。真实身份映射已保存在 ignored `.runtime/live-identities.json`；模板不包含邮箱或凭据。授权 header 从对应 `AIBANG2_CONFLUENCE_*` 环境变量读取，不保存到 JSON。当前没有申请/创建 token 或 OAuth scope，不读取其他项目凭据；凭据接入方式须另行落实最小授权。不要把密码/API key 发到聊天、命令历史或 Git。

scoped API token 使用配置中的 cloud_id，经固定 `https://api.atlassian.com/ex/confluence/{cloudId}` 调用；页面引用仍返回原站点。已核对 current-user 所需 granular scope 为 `read:content-details:confluence`，页面读取为 `read:page:confluence`，不是凭印象选择 `read:user:confluence`。实际 token 管理 UI 的可选 scope 及请求成功仍待核验，不申请 write/admin 权限。

本轮已实际核对两个 scope 在 eng_b token UI 可选；用户批准名称 `AI-Bang2 eng_b read-only pilot` 与 2026-10-20 到期，最终创建/保管由用户操作；配置探针成功不代表正文或查询已成功。提供 `--prompt-credential`：只在真实 TTY 隐藏输入邮箱/token，内存组装 Basic header，不存文件/环境变量/命令历史；无隐藏输入能力则拒绝，不回退到 echo。可用密码管理器保管原始 token，不能覆盖实际账号登录密码。

native space ID 不明时可先执行 metadata-only 配置诊断：

```sh
python3 -m scripts.confluence_probe --config .runtime/confluence-pilot.json --actor eng_b --page 98564 --discover-space --prompt-credential --live
```

该模式只验证当前凭据身份并请求白名单页面 metadata，输出 native space ID，不读取 storage 正文、入库或回答问题。discovery-only reader 不允许内容读取；不能把发现空间的结果当成查询或撤权验收。将实际成功输出的 space_id 填入私有配置 space_ids 后才执行正式读取。若账户/scope/API gateway 不匹配，明确 deny/unknown，不使用管理员回退。

先检查没有 live flag 的默认阻止路径：

```sh
python3 -m scripts.confluence_probe --config .runtime/confluence-pilot.json --actor eng_b --page 98564
```

预期 `mode=not_run`，退出码 2，不发网络请求。配置与授权准备后才执行：

```sh
python3 -m scripts.confluence_probe --config .runtime/confluence-pilot.json --actor eng_b --page 98564 --live
```

输出只有 decision、时间、method、版本和是否读取到内容，不输出内容、标题或凭据。allow 退出 0；deny/unknown 退出 1；配置不足退出 2。allow 仅证明此次读取，不代表全链路安全验收。将来真实撤权验收集中在已接通问答链路中执行，不逐页让团队人工检查。

完成本地授权配置后，可运行完整查询 pilot（stdout 包含此次获准的合成正文与引用，审计/历史仅存 ignored `.runtime`）：

```sh
python3 -m scripts.confluence_query --config .runtime/confluence-pilot.json --actor eng_b --question "Show the payment-service runbook" --live
```

输出模式 `confluence_live_api_fake_model`，模型为本地 extractive，不调用收费模型。`--history-id` 支持在同一逻辑会话追问，重新检查所有依赖。没有 `--live` 时不加载凭据/创建数据库/联网。其他用户无权页面的正文、标题、路径不进入响应或模型。撤权与内容更新后的历史/引用 API 由 `ConfluenceQueryPilot.history/evidence` 验证，尚无 live HTTP 端点。重启后保留索引也必须重新委托读取，不由持久库授予权限。

也可追加 `--prompt-credential` 用隐藏输入执行查询，不要求持久保存凭据到仓库。

## 已核对的官方接口

- [Get page by ID](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)：对应页面和空间的读取权限；storage body-format。
- [Current user](https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-users/#api-user-current-get)：当前凭据对应 accountId。
- [Authentication](https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/)：API 身份认证方式。生产用户授权方案仍优先委托 OAuth，不因支持 Basic 而默认申请全权限 token。
- [Scoped API tokens](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)：scoped token 的 API gateway、有效期与安全验证流程。
