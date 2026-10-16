# 提交收尾报告 · 2026-10-16

本地提交准备已完成；按用户要求结束诊断和付费试验循环。冻结源码 **2b79036cdd620f6810758a9951bc1675499882b3**，后续本次提交只更新收尾记录。完整语义目标未完成，赛事尚未提交。

## 交付包

本机目录：`artifacts/submission-20261016/`（Git 忽略，不含在远程仓库中）。

- `ContextLedger-source-2b79036.zip`：冻结 Git 源码归档，4190 个归档条目，含测试与原始项目资料。
- `CodeBuddy-proof-private.zip`：15 份真实原件及 manifest，含 conversation-history.zip、7 张截图、原始补丁及对话文本。所有原件 SHA256 与原 manifest 一致；保留原文件，证明包权限0600。尚未上传，团队上传前检查隐私。
- `Submission-description.md`：英文标题、8词简介、完整描述及限制。
- `Cover.png`：1600×900、16:9封面；`Architecture.svg`：架构及信任边界。
- `Demo-walkthrough.md`：演示流程；没有冒充已录制视频。
- `MANIFEST.json`：文件大小、SHA256、验证事实。仓库副本见 [PACKAGE_MANIFEST.json](PACKAGE_MANIFEST.json)。

## 实际验证

从上述源码ZIP解压后运行 `python3 -m unittest discover -s tests`：**800 项通过，54.847秒，退出码0**。这是离线测试，不是800次真实模型验收。日志存在 SQLite 连接未关闭的 ResourceWarning；未影响本轮测试结果，未声称零警告。

源码与证明包 ZIP CRC 通过；源码无 `.runtime`、`.git`、私有证明目录、SQLite或.env文件。常见密钥模式扫描无命中，仅为启发式扫描，不替代完整隐私检查。架构SVG XML解析通过，本轮未进行视觉渲染验收。

`candidate_entry.py --control .runtime/human-latest-20261016/entry.json --check` 成功核对人工试用 **fa88f2f** 的进程、后端指纹和静态文件；未发问题、未消耗人工额度、未切换服务。

## 保留的限制

最新隔离引文模式已知对照2/2通过，但11题全流程首题引文审查拒绝，其余10题未运行（3调用/USD0.001872，已关闭）。没有被拒草稿，不推测拒绝正确性。实验模式未切入人工试用。不能声称完整语义验收、生产SLA或完整员工原生权限集成通过。

原主目录改动保留；没有推送、合并、外部上传或赛事提交。自动grant不复用，旧unknown与人工额度保持原状。

## 最后提交动作

1. 团队使用已准备材料完成最终观看及内容签核，接受文案中明确披露的限制（G1/G2不由自动测试代签）。
2. 将冻结源码经正常PR流程发布至提交所填GitHub仓库；远端旧main不能冒充本候选。使用准备好的文案、封面和真实工具证明上传，并完成赛事提交。

无需再开展模型诊断。可选视频未制作；本机试用URL不能当作公网演示URL。
