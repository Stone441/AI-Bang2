# ADR093 · 结构窗口候选 structured-v2

2026-10-13，AUTH036；基准1649e30，增量未提交。whole-v1冻结原件及失败结果保留。

## 原因与实现

whole-v1的business_16虽然包含正确worker-pool结论，却连带显示固定2400字符窗口中的无关归档；600字符均分还会切断单词。新候选只改变证据组织与逐字引文分段，不改模型提示词、provider、8192上限、语义支持/覆盖拒绝或权限路径。

默认fixed保持旧行为；显式structured对超过4000字符的文档按标题、完整行/段落、列表及表格切分，保留列表/表格相邻说明和限定词引导的后续段落。超大不可分块保持完整，受既有16000字符总预算约束，不截去未知尾部。短文档保持全文。新段落的模型别名仍由服务端映射，模型不能生成事实或URL；最终保留的段落必须逐字重构。

窗口ID使用`resource@version#s1:start:end`，定位携带原文标题层级及精确Unicode偏移。旧`#start:end`仍按原固定规则解析，因此旧History/引用不重写；伪造或非规范窗口拒绝。每次预览和History仍检查当前权限、版本和删除。单review出口仅增加精确模型代码类白名单，构造后/review/final授权保持。

600字符引文优先在完整行、句末或空白处分段，保留全部字节；只有不可分长token才可能按字符截分。结构解析不是语义解析，无法独立证明任意文档限定语都已召回；模型的支持/覆盖判断仍须与业务oracle分开。

## 验证与限制

- 22结构/原引用/History/撤权/unknown/构造后及模型后变化测试通过。首次测试把BV-16的worker事实误归BV-11，纠正测试事实后保留初始失败日志；未改真实fixture。
- 完整本地607项通过，26.238秒；验收运行器更新后另4项通过，包含同账本结算与新unknown停止。不是611项不同测试。
- 独立CANDIDATE_STRUCTURED_V2.json固定代码hash、原PLAN、题集及运行配置。旧v1清单不覆盖；v2是已经看过的开发案例，非盲测。
- v2固定12案例机械事实检查通过，10次live model；另外两项无资料/无权正确不调用。Agent逐条读答案确认business_16归档混入/断句已修复，business_03仍直接呈现withdrawn/accepted原文，未用解释句明确纠正问题的rejected前提；该措辞限制保留，不替代真人验收。
- 以上fixture来源是模拟，不证明native权限性能或浏览器显示。浏览器工具已返回ERR_BLOCKED_BY_CLIENT，不绕过。

## 运行与回退

本任务49161备份到私有`pre-structured-backup`后加载，原账本、Goal admission、历史库及旧unknown保留。启用`--source-review-input structured --window-strategy structured`，其他pooled/4/none/single/history batch不变。回退`--source-review-input whole --window-strategy fixed`，不恢复或清空账本/历史；旧结构引用由兼容解析器继续验证。原8094/8100未操作。

原生验收驱动另存本文目录，执行前记录自身SHA256及候选hash。冷组是每题新服务进程的首次查询，后台同步保持正常，不能声称平台/模型缓存或每条连接都冷。热组及两组三并发分别记录HTTP完成时间；不冒称浏览器渲染时间或可靠p95。
