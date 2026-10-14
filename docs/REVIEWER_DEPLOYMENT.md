# 真实四源评审入口：部署准备与发布步骤

**当前状态：2026-10-13 已上线 https://contextledger.hellokyleshi.com 。用户明确委托代理完成检查，作为本次 G1 真人观看要求的例外；未宣称真人观看或 G2 通过。下方“尚未上线/待G1”为此前准备记录，最新结果见 [托管验收](reviews/2026-10-13-hosted-demo/README.md)。**

最新确认：作品名 ContextLedger，拟用 `contextledger.hellokyleshi.com`，由用户电脑持续托管，供组员通过账号登录测试真实四源。尚未上线；原有权限边界不变。

2026-10-13。代码与本机演示准备；**未部署、未开放公网、未新增云费用**。本页不是已上线证明。

## 2026-10-13 本机托管准备结果

- 用户批准本机持续托管、组员远程试用真实四源；名称最终为 ContextLedger。
- Cloudflare 域名账户已实际登录；域名 Active / Free。
- cloudflared 2026.10.0 已在 `.runtime/contextledger-host/` 下载并核对官方发布 SHA256，没有系统级安装。
- 专用隧道 `contextledger-hackathon-2026` 已创建；`contextledger.hellokyleshi.com` 的 CNAME 已添加。未修改个人主页。
- 私有 ingress 配置仅将该 hostname 路由到 `127.0.0.1:49161`，其余请求 404；配置校验通过。
- 隧道未运行，应用仍为本地模式，尚未开放公网。等待 AGENTS.md 要求的 G1 人工安全验收；不能将域名解析成功当作服务上线。
- 新增本机入口兼容 HTTPS 域名，6 项入口测试和 9 项账号 HTTP 测试通过；含确切 Host/Origin、Secure Cookie、跨账号历史/引用拒绝等。无真实模型问答调用。

### 上线前人工查看

在现有本地入口分别使用 Blair 和 Jordan 账号：

1. Blair 查询工程事故问题，查看回答与引用原文；记下该条回答。允许使用现有人工预算。
2. 退出后用 Jordan 登录，询问同一问题，确认不会出现 Blair 的受限工程资料；Recent answers 不显示 Blair 的历史。
3. 在 Jordan 会话下尝试打开 Blair 的引用或历史请求，确认拒绝访问，而非显示原文。退出后也不能继续访问受保护内容。

如已实际看过以上场景，可直接反馈实际结果；未看过则按步骤操作。当前自动 HTTP 测试不代替真人观看，未获得结果前不启动隧道。

### 待 G1 后执行的切换

确认本机无在途请求，备份原账本和数据库，仅重启当前归属明确的 49161 服务。在原 performance_trial 启动参数末尾增加 `--reviewer-public-origin https://contextledger.hellokyleshi.com`，保留现有账号、预算、模型与源连接。核验本地带确切 Host 的登录/状态，再运行：

```sh
.runtime/contextledger-host/cloudflared tunnel --config .runtime/contextledger-host/tunnel.json run contextledger-hackathon-2026
```

完成公网 HTTPS 登录、四源状态、跨账号拒绝和安全 Cookie 验证，再交付可分享网址。最终使用受管理进程运行，并准备停止入口；本页当前不声称已完成该步骤。隧道凭据保存在本机 `~/.cloudflared/`，不可提交 Git。现有 USD1 人工额度用于组员人工试用，不用于自动付费测试。

## 已选设计

评委浏览器 → HTTPS 反向代理 → 仅绑定 loopback 的账号登录应用 → 原有权限/版本校验与真实四源读取 → 原有模型及审计。固定账号密码映射到服务器允许的身份。工程、产品和外部协作方应用角色已接入同一获批真实四源连接，并施加不同应用白名单。该方案经用户明确批准，不代表三个源平台员工身份。多人共享某个角色账号时，其历史和审计归属同一演示账号。

## 可审阅的技术配置

已实现的启动器选项：

- `--human-team-trial`：本机新批准的人工 USD 1 额度；不供自动验收使用。
- `--reviewer-accounts <私密JSON绝对路径>`：启用账号登录。密码只保存 scrypt 哈希，角色必须已在运行时各源中映射；错误映射阻止启动。
- `--reviewer-public-origin https://<实际评审域名>`：仅允许该 Host/Origin，并设置 Secure Cookie；仍仅绑定 127.0.0.1。此选项本身不会发布服务。

本机完整运行命令见 [FINAL_RUNBOOK](FINAL_RUNBOOK.md)。此启动器仍依赖本机 Keychain 和既有持久状态，不能把命令直接复制到空白 Linux VM 就宣称云端部署完成。

若最终选用同机 TLS 反向代理，可审阅配置草案如下；需换成获批的真实域名，当前未安装或运行代理：

```caddyfile
review.example.org {
    reverse_proxy 127.0.0.1:49161
}
```

Caddy 官方说明支持此反向代理语法，并可在满足域名解析和网络可达条件时自动管理 HTTPS。默认不启用代理重试，本应用也不自动重试付费问答。参考：[reverse_proxy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)、[Automatic HTTPS](https://caddyserver.com/docs/automatic-https)。模板尚未在本机 Caddy 实例中验证。

## 发布前必须落实的事项

1. 确定团队所有的服务器和域名，以及云费用/上线期限。当前 USD 1 授权只针对本机人工模型试用，不等于云服务器购买或公开试用预算。
2. 若迁移到云服务器，先准备适用该主机的密钥存储和已有 OAuth 授权配置方式；不能复制本机 Keychain 或通过 Git 提交凭据。建立持久账本和备份，迁移前后使用量必须连续，不能重置原未知预留。现阶段不声称 Linux 凭据迁移已实现。
3. 只开放获批合成容器和明确演示角色，分别核验原生身份。采用已批准的应用角色与团队原生权限交集；审核各角色资源白名单及真实源撤权效果，不将其写成独立原生员工权限验证。
4. 在确定域名的环境下完成 G1：错误登录、跨账号历史/引用拒绝、正常四源问答、源撤权、预算暂停、账号撤销与会话失效；记录实际浏览器结果。现有本地 HTTP/DOM 测试不能替代公网环境验收。
5. 最终确认公开范围、访问期限和托管费用后发布；把私密登录卡片通过批准的渠道单独发给评委，GitHub 不含密码。当前未获发送消息授权，未向任何人发送。
6. 活动结束后撤销评委账号、关闭公网入口；保留审计和账本，按团队批准规则处理其保留期。单机多进程部署尚未验收；当前按一个应用进程串行处理问答，不宣称生产级高可用。

## 腾讯产品要求

用户提供的 10 月 9 日群聊称 ADP/TRTC 可选，开发阶段使用 WorkBuddy/CodeBuddy 是最低要求；同一晚也强调腾讯云产品为强制要求。赛事官方页面把 CodeBuddy、WorkBuddy、Miora 列为腾讯云 AI 产品：[赛事页](https://tch.tencentcloud.com/contest/44)。现有真实 CodeBuddy 开发证据仍是提交依据。

据此暂不迁移 ADP/TRTC，也不假定必须购买腾讯云服务器。最后一句强制要求的精确适用范围应向主办方核对；以下问题已准备，尚未发送：

> We have used CodeBuddy substantively during development and retained the required evidence. Does this satisfy the mandatory Tencent Cloud product requirement, without additional ADP/TRTC integration or Tencent Cloud hosting?

三个培训短链接本次工具无法打开，没有据此确认免费额度、模型可用性或账号权益。
