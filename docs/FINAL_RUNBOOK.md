# Final delivery runbook

2026-10-16 当前发布：869f407已上线 https://contextledger.hellokyleshi.com ，保持原source-review配置、账号及账本。最新结果以[发布报告](reviews/2026-10-16-release/REPORT.md)与[FINAL_HANDOFF](FINAL_HANDOFF.md)为准。下文是旧部署时间线，不是再次切换指令。

<details>
<summary>历史部署记录与命令</summary>

2026-10-15 主线集成说明：本轮收尾修复将作为下一轮开发基线合并main，后续继续完善前端、项目亮点、候选题问答与开发细节，不作正式封版。当前业务代码与10cc970一致；冲突题和四源题分别已有真实通过记录，JSON故障根因仍开放，线上仍独立运行f2f0633。[主线合并验证](reviews/2026-10-15-main-closeout-merge/REPORT.md)及[最新真实记录](reviews/2026-10-15-sectioned-live/json-investigation/REPORT.md)优先于下方历史说明。

2026-10-15 当前运行已切换到本地修复代码 `f2f0633`，同一公网入口；最新[真实验收与剩余缺陷](reviews/2026-10-15-closeout-live/REPORT.md)优先于下方历史状态。自动复验10次/USD0.011808，人工额度未占用、旧unknown保留。两项可选分题生成仍失败，不能宣称全部通过；未push/main合并或比赛提交。



Current closeout instructions (15 October): [candidate report and exact migration/switch boundary](reviews/2026-10-15-closeout/REPORT.md). Use an immutable code checkout with `--state-root <existing-project>` and an explicitly migrated `--attributed-grant human-team-closeout-20261015`. This reuses the approved original index, configuration, account registry and USD20 ledger; it does not copy or reset runtime state. Never automatically migrate on startup.

The selected human mode remains source-review / none8192 / structured / single / pooled4 / batch history / serial queries. Optional sectioned-synthesis is not the deployed default. Preserve the public-origin setting for the already approved hostname.

The following 13 October snapshots and commands are historical; current-state claims below do not override the closeout report.

Latest role update: all three accounts (engineer/product/partner) are active against the same approved real four-source connection, with additional server-side application ACLs. Their source identity remains eng_b. Current startup fingerprint: `b6f2ffbadef0bfbe28e02207c48980732b0b2364a74f896dcc23f92bbb61ac4c`; current log `.runtime/query-goal-20261013/application-role-final-service.log`. The launch command below is unchanged. Private role registry and policy files stay outside Git. Preserve the human USD1 state on every restart. The pre-role backups are `pre-application-roles-backup` and `pre-application-policy-guard-backup` under the private goal runtime. Old text below records earlier snapshots.

Current addendum (13 October): password-based engineering reviewer account and the approved human USD1 allowance are now active locally. See [REVIEWER_ACCESS](REVIEWER_ACCESS.md). The original frozen candidate and measurements below are historical; the updated manifest is [team-account validation](reviews/2026-10-13-team-access/VALIDATION.json). No public endpoint is active.

Current local launch (after the same ownership, idle and backup checks):

```bash
python3 -m scripts.performance_trial --source-transport pooled --source-concurrency 4 --reasoning-effort none --source-review-input structured --source-review-dispatch single --window-strategy structured --history-read-mode batch --query-concurrency serial --human-team-trial --reviewer-accounts .runtime/query-goal-20261013/reviewer-accounts.json
```

Current gate: `.runtime/query-goal-20261013/.runtime/human-team-admission.json`. Preserve it alongside the original goal file and shared ledger; restarting must not establish a new baseline. Private pre-update backups: `.runtime/query-goal-20261013/pre-team-account-backup/`. Current log: `.runtime/query-goal-20261013/team-account-service.log`. Password login replaces one-time operator links in this mode. Never restore an older ledger to recover budget. Reverting to the previous launcher also restores its exhausted attempt gate; that is not an appropriate way to reset allowance.


Selected version: [FINAL_CANDIDATE](reviews/2026-10-13-final-delivery/FINAL_CANDIDATE.json). This supersedes older trial startup instructions. Runtime source fingerprint begins `09f67454ef93`; the full fingerprint and every code/UI hash are in the manifest. Human G1/G2 are pending.

## Reproduce without credentials or provider charges

Python 3.11+ and SQLite are required; the final local regression used Python 3.14.7. Runtime is standard-library Python; frontend checks additionally use an existing Node installation. No package installation is needed.

```bash
make setup
python3 -m unittest discover -s tests
python3 -m brain.server --demo --port 0
```

Use the loopback address printed by the final command. This is fixture data, synthetic identities and a fake extractive model. It reproduces the application workflow and permission demonstrations, not native integration, the live source reviewer or live timing. `make live` is a historical generic launcher, not the selected final configuration.

## Existing approved native trial on this Mac

Double-click `打开试用页面.command` while the owned 49161 service is running. The entry is private, single-use and time-limited. The helper renews login only; it does not restart the service or submit a question. A valid session may recover its run after refresh; successful answers are stored and remain subject to current History checks. A server restart loses in-memory sessions/progress, so obtain a new entry after restart.

The selected launch command, from the repository root, is:

```bash
python3 -m scripts.performance_trial --source-transport pooled --source-concurrency 4 --reasoning-effort none --source-review-input structured --source-review-dispatch single --window-strategy structured --history-read-mode batch --query-concurrency serial
```

This requires the existing approved source bundle, app-owned Mac Keychain credentials, Drive OAuth grant, shared budget ledger and original goal admission state. These private inputs are intentionally absent from a source package. A clean checkout is not automatically authorized for native access. No new consent, scope or provider is granted by this runbook.

Wait until all four sources show complete/current before submitting. Queries queue serially; native reads within a query can overlap. Queued questions remain visible to their own sessions. Do not promise parallel model responses or a 10-second SLA.

## Restart and recovery

1. Verify `scripts.local_entry.renew(ROOT, check_only=True)` succeeds. It checks the exact loopback operator, startup fingerprint and PID/listener ownership. Never stop 8094/8100 or an unidentified process.
2. Confirm no active query, no new unknown usage and no unaccounted model reservation. Acquire the existing goal-admission lock without waiting before changing the owned service.
3. Use SQLite's backup API for the current index and budget; privately copy goal admission, configuration and instance control. The completed pre-update backup is `.runtime/query-goal-20261013/pre-final-delivery-backup/`, with hashes and integrity checks. It contains private state and must not be submitted.
4. Send SIGINT only to the verified owned idle PID. Confirm the process and 49161 listener have exited before launching the command above. If an observation tool times out, inspect that same process; do not start a duplicate.
5. Verify health fingerprint against the final manifest, wait for four complete/current sources, and renew the private entry. Keep all original usage, audit and unknown reservations.

If startup fails, diagnose the preserved log `.runtime/query-goal-20261013/final-delivery-service.log`. Do not reset the admission state, replay paid questions, silently change provider or restore an older budget over newer usage. A stale source can legitimately prevent a query until current access is confirmed.

For a later code regression, restore code/UI from the final source archive into a separate directory, verify its manifest, and use the same retained authorized private state only after reviewing path mappings. Do not overwrite teammate work. Historical v2 hash manifests alone are not a complete executable rollback archive. Database backups are disaster-recovery evidence, not a way to refund or erase newer actions.

## Final team action

Follow [DEMO_CANDIDATE](DEMO_CANDIDATE.md) once. Record exact version, visible correctness, full-page elapsed time, citation/History, queue, refresh/reopen and failure recovery. The previous browser tool refusal remains unbypassed; HTTP and DOM evidence do not count as human/browser acceptance. Review the explicitly limited premise wording before signing G2. Source publication, private tool-proof disclosure, external access and contest submission still require separate approval.

</details>
