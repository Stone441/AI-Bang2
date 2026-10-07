# 从这里开始：AI-Bang2项目交接包

当前为已实现可运行原型；固定旧候选331bd28及证据保留。2026-10-07业务增强见[执行入口](docs/iterations/2026-10-07-business-validation/README.md)、[STATUS](docs/STATUS.md)与[DECISIONS](docs/DECISIONS.md)。下方初始Phase 0为历史交接，不代表当前空仓。


> 版本1.0｜2026-09-27｜适用：三人NTU团队、Aspire Internal Brain赛道。  
> 本包包含**7份工作文档 + 2份原文文字归档**。只创建了方案文件，没有替你们提交代码、修改GitHub、接入平台或运行产品测试。

## 1. 这个包解决什么

把原始手册与Kickoff中的官方信息、候选产品方案、技术边界、任务路线和验收规则分开，让Codex不必依靠某次聊天的记忆推进项目。

日常不需要回看PDF和录像。赛事事实查01；业务方向查02；实现查03；推进与工具分工查04；验收查05。原文归档只用于追溯。后续新邮件、群公告或赛道细则仍需补进01；本包不能代表尚未收到的信息。

| 文件 | 用途 | 首次必读者 |
|---|---|---|
| [PROJECT_START_HERE.md](PROJECT_START_HERE.md) | 导航、安装与首次Codex提示词 | 全员 |
| [AGENTS.md](AGENTS.md) | 根目录Agent指令、权限边界、读文档和执行规则 | 所有编码Agent |
| [docs/01_OFFICIAL_BRIEF.md](docs/01_OFFICIAL_BRIEF.md) | 官方要求汇编、100分表、时间冲突、材料/额度/条款、待澄清事项 | Codex及至少一名规则负责人 |
| [docs/02_PRODUCT_STRATEGY.md](docs/02_PRODUCT_STRATEGY.md) | 推荐产品、两类用户、差异化、范围、ROI、演示故事 | 全员、Codex |
| [docs/03_ARCHITECTURE.md](docs/03_ARCHITECTURE.md) | 信任边界、数据/授权/检索/更新/引用/审计与API契约 | Codex；成员重点审查关键取舍 |
| [docs/04_DELIVERY_PLAYBOOK.md](docs/04_DELIVERY_PLAYBOOK.md) | 阶段、DEV任务、三关口、Git协作、CodeBuddy/WorkBuddy可复制任务、提交核查 | 全员、Codex |
| [docs/05_ACCEPTANCE_TESTS.md](docs/05_ACCEPTANCE_TESTS.md) | 12个合成对象、六用户权限矩阵、五worked examples、51案例 | Codex、验收成员 |

追溯附件：[手册41页英文文本](docs/sources/HANDBOOK_TEXT_ARCHIVE.md)、[Kickoff完整转写](docs/sources/KICKOFF_TRANSCRIPT.md)。手册图像中的关键提交表和评分表已整合到01；纯视觉素材/二维码不在文字归档中复制。

## 2. 推荐方向与已知边界

暂用名**ContextLedger**，正式参赛题目为**The Internal Brain**。用同一份payment-service合成资料，展示工程师查事故/修复/runbook，以及产品/运营查功能支持/发布范围。四源共用一套授权、检索、证据和审计机制，不开发两个产品。

关键亮点：答案可以核对；资料更新后能跟上；源端撤权后，旧会话和缓存也不能继续提供受限信息；审计能精确还原，并可发现被检查点覆盖的日志篡改。

当前方案是可挑战的基线，不是固定不变的详细设计。Codex应以接口测试和业务验收收敛实现。是否获奖无法保证；不能把设计文件当成产品已具备这些能力的证据。

### 启动前最重要的事实

- 官方要求使用CodeBuddy或WorkBuddy至少一个，并有真实对话与至少三张过程截图；缺使用证明不评分。[01第8节]
- 10月16日提交，但时刻未知；入围公告10月20/23日有冲突；11月3日书面仍TBC。[01第2节]
- 四源真实数据/测试账号、mock接受范围、混用工具细则尚未确认。[01第12节]
- Kickoff提到产品/运营用户、半小时内可查询的期望、ROI；没有因此新增Notion必做项。[01第3–6节]
- WorkBuddy Projects只是现场预告10月初推出，不作为依赖；开发credits不等于运行时API预算。[01第7节；04第10节]

## 3. 放入仓库的方法

解压后，将**包内的`AGENTS.md`、`PROJECT_START_HERE.md`和`docs/`目录**合并到本地`AI-Bang2`仓库根目录，不要把整个包嵌套放入`Requirements`。

本包没有根`README.md`，不会主动替换现有README；也不包含现有Requirements里的另一份GPT生成方案。如本地后来已经出现同名AGENTS或docs文件，先比较合并，勿直接覆盖其他人的修改。

放置后建议结构：

```text
AI-Bang2/
├── README.md                       # 原有文件，保留
├── Requirements/                   # 原有材料，保留
├── PROJECT_START_HERE.md            # 新增
├── AGENTS.md                       # 新增
└── docs/
    ├── 01_OFFICIAL_BRIEF.md
    ├── 02_PRODUCT_STRATEGY.md
    ├── 03_ARCHITECTURE.md
    ├── 04_DELIVERY_PLAYBOOK.md
    ├── 05_ACCEPTANCE_TESTS.md
    └── sources/
        ├── HANDBOOK_TEXT_ARCHIVE.md
        └── KICKOFF_TRANSCRIPT.md
```

Codex对AGENTS.md有项目指令读取机制，但不能假设它自动读完所有链接或永远记住全文；首次明确要求读取。其他工具显式附加相关文件，并核对读取范围。[外部技术资料见03 T11/T12]

由你们自行确认差异并提交Git。本次没有向远端写入，也没有更改仓库权限。

## 4. 第一条发给Codex的提示词

在VS Code中打开**仓库根目录**，新建Codex会话，发送：

```text
请接管AI-Bang2的项目推进。我们是三名NTU成员，参加腾讯AI CAN DO IT
Hackathon的Aspire Internal Brain赛道。你主导架构细化、编码、测试和集成；
我们负责业务判断、必要授权、安全验收和最终提交。

先读根AGENTS.md、PROJECT_START_HERE.md，然后完整阅读docs/01至05。
内容较长可分段，但未读部分不要猜；常规情况下不读sources归档，
也不要采用Requirements里之前GPT生成的另一份方案作为需求依据。

接着检查真实仓库、当前分支、未提交改动与开发环境。不要覆盖队友工作。
区分官方要求、候选设计、已有实现与未验证状态。

现在执行Phase 0：
1. 评估这套方案的关键可行性，优先验证四源权限检查与接入条件，
   不做大段复述；提出必要的最小修正及理由。
2. 根据真实情况创建docs/STATUS.md、BACKLOG.md、DECISIONS.md，
   排好DEV任务依赖、验收ID和CodeBuddy/WorkBuddy的实质任务。
3. 在本地开始可逆、无外部写入及无新增费用的准备工作：
   数据/接口契约、12对象合成真值与基础测试规划。
4. 集中列出需要我们决定的最多三组事项：账号及权限、模型预算、范围/规则。
   可从现有文件或只读检查解决的问题先自己解决，不逐项反问。

G0批准前不自行接入真实敏感数据、申请scope、创建收费资源或公开部署。
缺凭据时用明确标记的fixture/fake provider推进不依赖凭据的部分，
不要把模拟效果写成真实集成已完成。

完成Phase 0后，汇报已验证的事实、阻塞项、最小下一步和G0待决事项。
G0通过后按里程碑连续推进常规工作，阶段更新状态与实际测试结果。
```

这条提示词避免两个极端：没有了解场景就立刻铺代码，或只输出宏大的计划、每步都等人催促。

## 5. 后续日常启动提示词

```text
先读AGENTS.md及最新STATUS/BACKLOG/DECISIONS，检查当前分支和改动。
按已批准范围继续下一个可推进的DEV任务，只补读相关设计与测试章节。
完成实现、实际验证和状态更新；遇到安全、费用、外部写入或发布边界时停在该步骤。
其他不依赖此决定的任务可以继续。不要重复整套方案，也不要伪造未运行的结果。
```

给CodeBuddy/WorkBuddy的具体任务在04第7–8节，可直接复制。不要让两个编码Agent同时编辑同一个工作目录中的相同文件；共享代码用分支/PR，共享事实用仓库文档，而不是共享账号。

## 6. 三个人最少需要亲自做什么

一人负责官方澄清、材料与腾讯工具证明；一人负责源账号、权限和数据边界；一人负责端到端产品与业务验收。可兼任、轮换，不按专业强制分配。

每个阶段亲自看关键场景运行，尤其同一账号撤权后的追问。测试由Agent跑，人仍要判断测试是否真的验证了业务问题。对外声明、费用、真实数据接入和最终提交不能仅靠Agent自行决定。

## 7. 初始状态与维护

本包创建时仅只读查看了GitHub根目录列表，看到`README.md`及`Requirements/`；没有递归审计仓库，也不能据此判断每位成员本地未提交代码。Codex接管时须重新盘点。

本包没有应用源代码、运行环境、live连接器或已通过的性能报告。首次任务不是“继续已经完成的RAG”，而是从真实仓库状态建立起点。

版本1.0只覆盖本次上传的手册和Kickoff转写。后续官方答复只更新01及其变更记录；产品决定更新02/03和ADR；推进状态写STATUS，不在每份文档重复。源归档保持不变以便追溯。
