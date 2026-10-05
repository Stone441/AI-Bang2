# Native Jira content-update acceptance

2026-10-06 Singapore (the raw UTC audit timestamps are 2026-10-05). Native Jira API / existing eng_b / fake model, isolated in-memory index. Owner UI created KAN-6 / 10015 in the already approved KAN synthetic project, then changed only its description from Revision 1 (amber) to Revision 2 (green). Both descriptions carry a full synthetic banner and unique fixture ID. Existing KAN-4/KAN-5 and permissions were untouched. No existing runtime whitelist or 8094 process was changed.

13 checks passed: initial native content, stale index preserved before refresh, old native fingerprint/preview/history-export projection denied, current source refreshed, new text/fingerprint/model evidence/preview correct, old marker absent, control KAN-4 unchanged, 23-event unsigned chain valid. Jira version is a content fingerprint, not a sequential revision counter; the observed number decreased and this is expected.

The runner reuses only the reviewed app-owned eng_b Jira Keychain item, performs GET requests, and waits between the two readonly phases. Only owner UI performs synthetic writes. No new key/scope or model API/cost. Screenshots are private/ignored; native-seed.json holds the paths and hashes, not the images.

Replay requires separately authorized UI preparation of KAN-6 as Revision 1, then Revision 2 after the runner says awaiting_source_update; the runner itself does not reset or edit the platform. Preserve this existing record by choosing a new output directory:

```sh
python3 -m scripts.native_jira_update_acceptance --live --output evidence/runs/native-jira-update-new
```

6 credential/output-guard tests passed, including 2 new Jira cases. No new full-suite count is claimed. This is not a background incremental worker/SLA, browser export download, real-model freshness, full platform/persona matrix, production independent audit custody, or human G1/G2 acceptance. The dedicated synthetic test issue remains Revision 2 for inspection, outside the application's standard allowlist.

Latest checkout full unittest execution also passed 301 tests; full-tests.log is the actual output. This is separate fixture/mock regression evidence, not a new clean archive or browser review.
