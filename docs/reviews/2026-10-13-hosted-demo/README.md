# ContextLedger 本机托管验收 — 2026-10-13

用户授权在本机持续托管，后明确要求代理代为确认安全场景。本次按该直接指示记录为代理验收例外，不宣称真人观看 G1 或 G2 最终提交通过。

- 地址：https://contextledger.hellokyleshi.com
- 专用 Cloudflare 隧道、独立子域名；后台应用仍只监听 loopback。
- 三个人物账号公网 HTTPS 登录、Secure/HttpOnly/SameSite Cookie、错误 Origin 拒绝通过。
- Blair 本地真实问答 8.84 秒；公网最终问答 8.855 秒，accepted，含 Confluence/Jira/Slack/Drive 四源证据。
- Jordan 本地 3.12 秒，仅返回白名单能力页；综合失败时 evidence_only，不能称为综合质量通过。跨账号历史/引用均403，Recent隔离、退出后拒绝通过。
- 最初测试将 Jordan 预期错误地写成“零证据”，实际已批准能力页可读；原失败报告私下保留，随后按精确白名单逐字检查已有结果，未重跑模型。
- 发现 Drive 仅启动时刷新 token，运行约一小时后失效。新增同一只读grant自动续期，账号不符/刷新失败拒绝；37项Drive测试通过，完整666项40.861秒通过。真实长期跨一小时运行尚未观察，续期边界/并发/失效由单测覆盖。
- 本轮三次真实问答（本地两次、公网一次），不循环重试。人工额度现余额 USD0.997920；此前用户消耗保留，旧unknown两笔不变。
- 浏览器工具打开公网域名 ERR_BLOCKED_BY_CLIENT，未绕过；网页视觉及真人操作未验。以上为真实HTTPS和API证据。
- 两个用户级LaunchAgent负责应用/隧道，60秒重启节流；caffeinate -i仅随应用运行防空闲休眠。登录macOS后启动；不能承诺合盖、关机、断网时可用。
- 新增启动在线试用.command / 停止在线试用.command。停止保留账本、审计、账号；不发送账号给他人。凭据/日志在本机私有目录，不入Git。
