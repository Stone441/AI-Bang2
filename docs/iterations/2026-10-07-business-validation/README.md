# AI-Bang2：业务能力增强交接入口

编制日期：2026-10-07。研究快照日期：2026-10-06。

本包只新增3份Markdown，不包含产品代码，也不覆盖AGENTS、docs/01–05、状态、数据或旧审查。它把上一轮公开研究交给本地Codex，在真实当前分支上增量合入项目。

## 文件与阅读顺序

1. 先读当前仓库适用的AGENTS及最新DECISIONS/STATUS/BACKLOG，核对实际HEAD。
2. [研究原稿](../../research/2026-10-06_ASPIRE_RESEARCH_ACTION_PLAN.md)：研究依据、公开来源、假设和建议，保持原字节。
3. [EXECUTION_BRIEF.md](EXECUTION_BRIEF.md)：把研究映射到现有文档和DEV-BV任务；不维护第二套实时进度。

研究原稿SHA-256：`15fc2c59734f198b7fdfff0ad2cb4035b433c4d0032b4f25c7e0bfec15658607`。

本文和执行说明是本次新增的交接组织，不是对Aspire公开事实的新一轮独立核验。原稿引用的动态产品/接口/价格，在用于实际配置或对外声明时应按原来源核对。

## 导入方法

将ZIP放在本地AI-Bang2根目录。由Codex检查包清单和路径再导入，拒绝越界路径/符号链接，已有相同文件跳过，不同先比较。不能替换整个docs目录。ZIP不加入Git，不扫描其他下载文件，不执行包外文件。

解压后的目标：

```text
docs/
  research/
    2026-10-06_ASPIRE_RESEARCH_ACTION_PLAN.md
  iterations/
    2026-10-07-business-validation/
      README.md
      EXECUTION_BRIEF.md
```

若浏览器自动解压，可直接使用这个docs子目录，但仍逐文件合并，不替换既有docs。确切路径找不到时询问位置，不扫描无关文件。

## 怎样成为项目的当前要求

不要只存一个附件让Agent“自行记住”。执行说明第3节要求把采纳的业务选择写入02/DECISIONS、技术选择写入03、验收写入05、任务和结果写入BACKLOG/STATUS/ACCEPTANCE_STATUS；入口只放短链接。01仅维护赛事官方事实。

不为每份文件重新抄整套内容；先写必要增量，结果发生后再更新运行和演示材料。保留旧决定被后续覆盖的记录。研究不可变，执行状态只在既有状态文件维护。较早的另一份研究可以保留，不采用互相冲突的数据预算。

## 当前授权的含义

读取、整理文件不等于批准所有研究建议。用户发送下面启动词时，明确采用本轮业务方向并延续既有本地可逆开发；外部写入、提供商/费用、权限、服务重启、推送合并、公开发布和比赛提交仍按实际AUTH。AUTH-019延期不会被自动撤销。

当前远端main落后于用户报告的本地候选；本包编制时仅重新只读核对远端，没有修改GitHub、用户电脑或运行进程。不要先pull/强推来“对齐”。本地小步提交不等于已上传GitHub；远端写入需相应授权。

## 可直接使用的Goal目标

下方为拟由用户发送的任务指令；不能因为它存在文件中就预填为已经获得授权。

```text
/goal 按AI-Bang2_Business_Iteration_Pack.zip中的增量执行说明，完成本轮业务能力增强，形成有实际质量、四源变化和审计证据的统一候选；不以整理文件或生成计划结束。

先读取当前AGENTS，检查目录、分支、HEAD和未提交改动。从仓库根目录读取这个指定ZIP，校验清单/路径后仅新增包内3份Markdown；同名相同跳过，不同先比较，ZIP不入Git，不覆盖整份docs或队友工作。找不到确切文件只问位置，不扫描其他下载资料，不先pull/reset。

读docs/iterations/2026-10-07-business-validation/README.md和EXECUTION_BRIEF.md，以及其中链接的完整研究。按说明将采纳内容增量写入现有02–05、DECISIONS、BACKLOG及入口；01仍只记录官方事实。以当前本地实现和最新AUTH为准，已完成修复不重做，不回退331bd28。

我采纳本轮业务强化方向，并授权在已有边界内继续本地可逆开发与验证。保留ADR-040、AUTH-019、原预算和已批准数据范围；新权限、收费/提供商、外部写入、服务重启、推送合并、公开部署及比赛提交另按具体授权，不由本消息一并批准。

先完成短接线，再实际运行代表性业务问题的当前实现基线，随后连续推进DEV-BV-02至06中可执行任务。研究中的数量是预算、embedding是对比候选，不机械补组件。按需用一个只读审查子Agent，保护保留题，不伪装独立人审。阶段汇报只是通知；一个外部动作阻塞时继续其他工作。

完成须有实际实现/对比和对应模式证据，剩余失败、获批延期、unsupported、blocked与人工验收分列。不能把核心缺口全标blocked后称完成。遇到真实授权/执行/预算阻塞或无进展时保存准确接续点。G1/G2不自动批准。现在开始，不停在阅读、计划或“等我说继续”。
```

建议继续当前已经掌握仓库的session；如开新session，也从这些文件及最新状态接手，不重复旧ZIP或整段聊天。不要让两个session同时编辑同一工作目录。

## 工具说明的官方参考

- Codex Goal是线程内的持续目标，不是项目文件的替代：[Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)。
- 长指令放文件，由短Goal引用：[Developer commands](https://learn.chatgpt.com/docs/developer-commands)。
- 项目长期规则与读取路径：[AGENTS.md](https://developers.openai.com/codex/guides/agents-md)。

2026-10-07查阅。这里只说明交接用法，不要求更换模型、客户端或调整安全配置。
