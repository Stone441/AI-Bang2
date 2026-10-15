# Embedding experiment decision · in progress

现有 baseline 12 资源、三题及六条新改写（作者可见，非盲测）× 三身份，共27次实际 Engine/fake model检索留档。工程/产品原题及改写未缺必要证据；外协不要求其无权工单。所有题仍有大量主题相关而不直接支持目标事实的证据，因此这不证明精确率或最终语义质量。

本轮环境只读探测：当前 Python 无 sentence_transformers、transformers、torch、onnxruntime。尚未下载本地 embedding 模型；没有新 embedding provider、模型数据外传或新费用授权。未用 fake embedding 代替真实语义实验。

当前选择：不纳入默认候选。理由是已有九问法未显示必要证据漏召回，且真实 embedding 对照条件未齐；不是断言 embedding 无价值。未知表达/更大干扰集、真实答案质量与分阶段时延仍需测量，现有样本不支持 p95/SLA。

投入上限：两小时本地可行性与测量准备。不因 embedding 阻塞综合回答/UI。若后续发现明确未知表达漏召回，再准备具体模型、下载体积/内存/费用/出境边界与授权。任何方案绑定 resource/version/security scope；保留精确ID与原权限/删除/撤权/模型前检查，不新增独立向量数据库。
