# Confluence delegated read pilot

2026-10-05：代码与模拟 HTTP 合同测试；真实 API `not_run`。这不是已接入产品的 SourceAdapter，也不改变 LOCAL DEMO / FAKE MODEL 模式。

## 边界

`ConfluenceReader` 接受服务端确定的 Actor 映射，按对应凭据调用 `GET /wiki/rest/api/user/current`，核对 native account ID 后才获取白名单页面。不会回退到管理员或共享采集账号。CLI 的 `--actor` 仅用于本地操作员诊断，不能复用为前端登录机制。

仅允许明确指定 HTTPS Atlassian 站点、page ID 和 native space ID。先读取页面 metadata，确认对应空间及 current 状态，再由同一凭据读取 storage 正文；版本变化、异常/缺字段/不支持的宏均停止。403/404 为 deny，401/429/网络或未知响应为 unknown，不输出正文、标题或上游错误。不缓存允许结论；旧版本请求必须与当前版本相同。HTTP 不跟随重定向，有超时、响应类型及大小限制。页面 URL 由后端构造。

没有实现：用户 OAuth 登录、同步 worker、完整宏/附件/子资源、索引入库和 Engine 连接、审计事件接线、源端撤权传播延迟测量。平台在请求之间仍可变化；接入 Engine 后必须在模型 dispatch 和答案/历史/引用返回前重查。模块返回的 `policy_version=0` 表示平台未提供 ACL revision，不把内容版本当权限版本。

## 配置与执行

先复制 `config/confluence-pilot.example.json` 到 ignored `.runtime/confluence-pilot.json`，填入实际核验的 native space ID 和独立测试用户 account ID。真实身份映射已保存在 ignored `.runtime/live-identities.json`；模板不包含邮箱或凭据。授权 header 从对应 `AIBANG2_CONFLUENCE_*` 环境变量读取，不保存到 JSON。当前没有申请/创建 token 或 OAuth scope，不读取其他项目凭据；凭据接入方式须另行落实最小授权。不要把密码/API key 发到聊天、命令历史或 Git。

先检查没有 live flag 的默认阻止路径：

```sh
python3 -m scripts.confluence_probe --config .runtime/confluence-pilot.json --actor eng_b --page 98564
```

预期 `mode=not_run`，退出码 2，不发网络请求。配置与授权准备后才执行：

```sh
python3 -m scripts.confluence_probe --config .runtime/confluence-pilot.json --actor eng_b --page 98564 --live
```

输出只有 decision、时间、method、版本和是否读取到内容，不输出内容、标题或凭据。allow 退出 0；deny/unknown 退出 1；配置不足退出 2。allow 仅证明此次读取，不代表全链路安全验收。将来真实撤权验收集中在已接通问答链路中执行，不逐页让团队人工检查。

## 已核对的官方接口

- [Get page by ID](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)：对应页面和空间的读取权限；storage body-format。
- [Current user](https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-users/#api-user-current-get)：当前凭据对应 accountId。
- [Authentication](https://developer.atlassian.com/cloud/confluence/basic-auth-for-rest-apis/)：API 身份认证方式。生产用户授权方案仍优先委托 OAuth，不因支持 Basic 而默认申请全权限 token。
