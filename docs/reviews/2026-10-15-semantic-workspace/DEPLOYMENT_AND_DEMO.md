# Candidate deployment, rollback and lifecycle demonstration

## Current versions

Local main baseline: `0d5be3096cfcbf09b267fe6b54853b1fac2e67af`. New work stays in `AI-Bang2-semantic-20261015` / `feat/semantic-workspace-20261015`.

On 2026-10-15 the existing local49161 health endpoint, using its configured Host `contextledger.hellokyleshi.com`, reported startup source `c161d77f8274edb5e3f336e15c980bf20ff3f9cbad9c3fe0bdd28f1ce3622c81`, loaded `2026-10-15T09:35:42.268926+00:00`, `confluence_drive_jira_slack_live_api_live_model_source_review`. This matches the earlier f2f0633 report; current process loading was checked, not inferred from local main. A bare localhost Host was correctly rejected403; no security settings changed.

Candidate uses sectioned-synthesis with a separate review, direct conclusions and per-part gaps, instead of the deployed source-review default. The UI is top navigation/three cards/collapsed passages/right drawer/mobile full panel. Runtime selection remains an operator setting; choosing the mode alone is not acceptance.

Current local code candidate: `2ef8d74`; latest real diagnostic runtime: `eb91828` (default partial failed generation field validation). Current human UI runtime: `fa88f2f` on55858, verified via the checked launcher; see LATEST_TRIAL.md. Current code includes separate gap explanation indices, mandatory independent per-part completeness verdicts and granular rejection diagnostics. Preserve v3 audit/index separately on rollback; older renderers/validators do not understand gap-bearing records.

Clean archive verification of2ef8d74: see candidate-partition-smoke.json for archive SHA256, startup fingerprint and asset hash match. Independent fixture/fake startup, health, top navigation/cards and graceful shutdown checked. No private runtime/credentials copied and no real calls made. Earlier11818ea artifact evidence remains historical in candidate-smoke.json.

## Preview

From the candidate worktree: `python3 -m scripts.reviewer_demo`. It prints a loopback URL using fixture sources and a fake extractive model. This checks navigation and fixture access, not the real generated answer protocol. For local protocol checks: `PYTHONPATH=tests python3 -m unittest test_sectioned_answer`. The existing human entry remains separately verified and is not automatically refreshed when worktree code changes. No old UI is substituted when the entry fails validation.

## Deployment (not authorized or executed)

1. Finish real quality and safety review; identify exact approved candidate commit and test modes.
2. Prepare immutable artifact and hash manifest; inspect differences from current49161. Preserve original main dirty evidence, private databases, existing account revisions, source mappings and budgets. No schema migration is required by this candidate.
3. Back up current startup configuration, executable pointer and databases using existing tools. Record current exact immutable release path and health fingerprint at deployment time.
4. On explicit approval, wait for current queries to finish, stop only the verified app process, switch its immutable release pointer and selected answer mode, restart on the same configured port/Host. Do not alter tunnel/DNS/accounts/source scope. Validate health, four-source readiness, login/role boundaries, permitted history/preview, and budget attribution. New model smoke only if separately covered by approved calls.
5. If checks fail, stop this app, restore previous release pointer and configuration, restart and compare original fingerprint. Do not restore stale source authorization or erase new audit/ledger events; preserve failed deployment logs.

This is a plan; no switch, service restart, public deployment, push/merge or competition submission has occurred.

## Repeatable update and revoke demo

Run `python3 -m scripts.scenario_lab` in an independent local process. It is a labelled synthetic/fake-model laboratory, separate from employee service and real platforms. Follow its fixed four-step sequence: initial answer → update fixture → verify updated answer/old access behavior → revoke fixture and verify history/preview denial. Restart the isolated in-memory lab to restore it. No source write or real model call is involved. See `docs/SCENARIO_LAB.md` for established commands and limitations.

For a native demonstration, first obtain separate approval identifying exact disposable object, owner/reader, field edit or membership removal, restore values and allowed time window. Capture original permission/version, run the ordinary question and preserve its request ID; perform only the approved change; measure source acknowledgment→discovery→index publication→first correct answer. Open prior citation and history to verify changed/revoked data is denied; restore only the exact approved grant and confirm. Never use a numeric fingerprint as chronological order. Do not reuse historical one-time update/revoke authority. Current candidate has not run this native procedure.
