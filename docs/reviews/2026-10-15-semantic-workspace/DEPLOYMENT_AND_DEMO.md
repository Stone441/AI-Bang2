# Candidate deployment, rollback and lifecycle demonstration

## Current versions

Local main baseline: `0d5be3096cfcbf09b267fe6b54853b1fac2e67af`. New work stays in `AI-Bang2-semantic-20261015` / `feat/semantic-workspace-20261015`.

On 2026-10-15 the existing local49161 health endpoint, using its configured Host `contextledger.hellokyleshi.com`, reported startup source `c161d77f8274edb5e3f336e15c980bf20ff3f9cbad9c3fe0bdd28f1ce3622c81`, loaded `2026-10-15T09:35:42.268926+00:00`, `confluence_drive_jira_slack_live_api_live_model_source_review`. This matches the earlier f2f0633 report; current process loading was checked, not inferred from local main. A bare localhost Host was correctly rejected403; no security settings changed.

Candidate uses sectioned-synthesis with a separate review, direct conclusions and per-part gaps, instead of the deployed source-review default. The UI is top navigation/three cards/collapsed passages/right drawer/mobile full panel. Runtime selection remains an operator setting; choosing the mode alone is not acceptance.

## Preview

From candidate worktree: `python3 -m scripts.reviewer_demo`. It prints a loopback URL; fake extractive model, no charges. Candidate user's existing preview51686 remains a prior startup snapshot, not automatically refreshed. Never silently restart a user test or production to hot-reload an edit.

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
