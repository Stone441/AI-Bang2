# DEV-09-CB 交付：审计签名检查点与独立验证器

状态：实现完成，测试全部真实运行通过（结果见下）。由 CodeBuddy 在独立 worktree
`.runtime/codebuddy-dev09`、分支 `codebuddy/dev-09-audit-verifier` 实现；基准
commit `81df3ef`。未提交、未推送，diff 留待集成人审查。

## 修改范围（仅任务允许路径）

| 路径 | 内容 |
|---|---|
| `tools/audit_verifier/chain.py` | 独立重算 v1 规范化 hash 链；**不导入 `brain.*`**，按 `docs/CONTRACTS.md` v1 契约独立实现 |
| `tools/audit_verifier/crypto.py` | Ed25519 签名/验签，全部委托系统 OpenSSL CLI（`pkeyutl -sign/-verify ... -rawin -in <file>`），不自研密码算法；消息与签名经 `tempfile.TemporaryDirectory` 临时文件交换。**密钥类型强制**：`pkeyutl` 会按密钥类型自动选算法，故任何签名/验签前先用 `openssl pkey -pubout -outform DER` 导出 SPKI 并比对 Ed25519 固定 OID（`1.3.101.112`，DER `302a300506032b6570032100`，44 字节），RSA/EC 等非 Ed25519 密钥被显式拒绝（`UnsupportedKeyError`），仅做常量比对，不实现密码算法 |
| `tools/audit_verifier/checkpoint.py` | 检查点生成器 CLI；私钥仅由 openssl 从指定路径读取，不显示、不复制、不写入输出 |
| `tools/audit_verifier/verify.py` | 独立验证器 CLI；checkpoint 与公钥必须由外部独立保留的副本显式提供，绝不从被校验日志内接受新信任根 |
| `tests/codebuddy/test_audit_verifier.py` | unittest（仓库无 pytest，未新增依赖）；密钥由 openssl 在 `TemporaryDirectory` 生成，不显示、不提交 |
| `docs/CODEBUDDY_AUDIT_DELIVERY.md` | 本文档 |

未修改：`brain/**`、`web/**`、`fixtures/**`、既有 tests、AGENTS、docs 01–05、CONTRACTS、任何凭据。

## 契约要点（与现有 v1 逐字节兼容）

- 规范化：`json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))`
- 事件 hash：`SHA256(b'ContextLedger.audit.v1\0' + canonical(事件不含 hash))`，genesis `previous_hash` 为 64 个 '0'，`seq` 从 1 连续
- 兼容性由 `HashContractCompatibility.test_independent_recomputation_matches_brain_v1` 断言：验证器独立实现的 `event_hash`/`canonical` 与 `brain/audit.py`、`brain/store.py` 对真实 `Audit.export()` 输出逐事件一致
- 检查点签名的消息为 `canonical(checkpoint)`，checkpoint 绑定 `schema_version, stream_id, through_seq, head_hash, timestamp`

## 命令

```bash
# 生成密钥对（一次性，私钥由集成方在仓库外保留；测试中仅在 TemporaryDirectory）
openssl genpkey -algorithm ed25519 -out priv.pem
openssl pkey -in priv.pem -pubout -out pub.pem

# 导出链并生成签名检查点（示例：覆盖前 6 条）
python3 -c "import json;from brain.store import Store;from brain.audit import Audit;\
s=Store();a=Audit(s);\
[a.append('request_started','eng_a','r%d'%i,{'query':'q%d'%i}) for i in range(6)];\
json.dump(a.export(),open('events.json','w'))"
python3 tools/audit_verifier/checkpoint.py --events events.json \
    --private-key priv.pem --through-seq 6 --out checkpoint.json

# 独立验证（checkpoint.json 与 pub.pem 使用独立保留的可信副本）
python3 tools/audit_verifier/verify.py --events events.json \
    --checkpoint checkpoint.json --public-key pub.pem
# 无检查点：本地链，显式 untrusted（exit 2）
python3 tools/audit_verifier/verify.py --events events.json
```

退出码：`0` 签名锚定段验证通过（未覆盖尾部单列，不视为可信）；`1` 验证失败
（坏签名/错公钥/stream 不符/锚定段或尾部篡改）；`2` 无锚点，明确不可信。

Ed25519 使用 `openssl pkeyutl -sign/-verify -rawin -in <临时文件>`（不用
stdin，不用 `dgst -sha256`），符合 OpenSSL 3.6 `pkeyutl` 手册对一次性算法的要求；以上命令均在测试和端到端运行中真实执行。

## 真实运行结果

环境：macOS（darwin），Python 3.14.7，OpenSSL 3.6.3（Library 3.6.3）。
基准 commit `81df3ef`，工作区除本任务三个路径外无改动。

- `python3 -m unittest discover -s tests/codebuddy -v`：
  **Ran 20 tests — OK**（含真实 openssl 子进程调用）
- `python3 -m unittest discover -s tests`（全仓库）：
  **Ran 52 tests — OK**（32 项既有 + 20 项新增，无回归）
- 端到端 CLI 真实运行：`checkpoint.py` exit 0（through_seq=6，
  head_hash `aa8b385e…a937c9`）；`verify.py` 全锚定 exit 0，verdict
  `anchored_valid`；无检查点 exit 2，verdict `untrusted_no_anchor`

测试场景与验收映射（均为真实运行）：

| 场景 | 结果 | 关联 |
|---|---|---|
| 原链 + 正确签名检查点 | exit 0，`anchored_valid` | A-03/A-04 正向 |
| 锚定段正文改动 | exit 1，`anchored_chain_invalid`（chain_mismatch） | A-03 |
| 中间删除（全覆盖检查点） | exit 1，`covered_events_missing` | A-03 |
| 中间删除（部分覆盖检查点） | exit 1，`chain_mismatch` at seq 3 | A-03 |
| 删除已签名覆盖的尾部 | exit 1，`covered_events_missing`（签名仍验签通过，删除被序号锚定发现） | A-04 |
| 整链重算替换 | exit 1，`anchored_head_mismatch`（链自洽但与签名 head 不符） | A-04 |
| 错误公钥 | exit 1，`signature_invalid` | A-04 |
| 损坏签名 | exit 1，`signature_invalid` | A-04 |
| 缺检查点 | exit 2，`untrusted_no_anchor`，明示整链替换不可检测 | A-04/A-11 |
| 未覆盖尾部 | exit 0 但尾部单列（from_seq/to_seq/count/note），verdict `anchored_valid_tail_unanchored` | A-11 |
| 尾部篡改 | exit 1，`tail_chain_invalid`（锚定段仍 valid，仅尾部失败） | A-11 |
| stream_id 不符 | exit 1，`stream_id_mismatch`；外部期望匹配同一检查点则通过 | A-11 |
| 生成器拒绝坏链 | 非零退出，不产出检查点文件 | 健壮性 |
| RSA/EC 私钥签名（生成器） | 非零退出，stderr 明示 "not an Ed25519 key"，不产出检查点 | 密钥类型强制 |
| RSA/EC 公钥验签 | exit 1，verdict `non_ed25519_key`，`signature.verified=false` | 密钥类型强制 |
| 事件 `seq`/`schema_version` 为 JSON `true`（含攻击者重算的合法 hash） | `schema_mismatch`/`chain_mismatch` 拒绝（`True == 1` 不被接受） | 输入严格性 |
| checkpoint `through_seq` 为 JSON `true` | exit 1，verdict `invalid_checkpoint_through_seq` | 输入严格性 |

## 边界与限制（不宣称的部分）

- **同机同账号**：签名私钥、检查点、日志若由同一账号控制，无法抵御该账号被
  全面攻陷；本实现是逻辑演示，不是生产独立安全边界。
- **stream_id 未内生于事件**：v1 事件没有 stream_id 字段；验证器仅将 stream
  身份作为外部期望参数对检查点校验（默认 `audit-main`，可
  `--expected-stream-id` 指定），不能宣称已证明防跨链移植。
- **未覆盖尾部**：`through_seq` 之后的事件不受签名保护，尾部内的替换/截断
  不可由该检查点检测；报告始终单列尾部，不输出笼统"全部可信"。
- 验证基于解析后 JSON 重算规范化 hash，检测内容篡改，不检测同一逻辑内容的
  非规范化重序列化。
- 整数类型严格性：`seq`、`schema_version`、`through_seq` 均要求真整数，
  JSON `true`（Python `bool`，且 `True == 1`）被显式拒绝。
- A-02（真实数据库角色分离）不在本任务范围，另行实施。

## 集成人须知

- 审查 diff：`git -C .runtime/codebuddy-dev09 diff` / `git status`（相对基准
  `81df3ef`，仅上述三个路径）。
- 生产化保留策略：checkpoint 生成节奏（如每 N 条或每批次）、检查点与公钥的
  独立保管位置、密钥轮换流程（当前验证器绑定单一公钥，轮换需外部决策）。
- 工具使用证据（对话记录、≥3 张截图：契约确认、实现/调试、运行验证）由团队
  保存到 `evidence/tool-usage/private/`（Git ignored）；本对话不包含私钥内容。
