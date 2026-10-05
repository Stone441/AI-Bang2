# Native restricted-document acceptance

2026-10-05. Confluence native API, existing eng_b mapping, fake model, controlled stale synthetic index. This is a subset of S-03, not the contractor persona/full matrix or G1.

The owner published C-03 / 557057 in the approved AI-Bang2 Synthetic Lab, as a child of C-01. Native Share shows Restricted with only the existing owner listed. No existing page or member permission changed. The private screenshot and its hash are indexed in native-seed.json; it is not uploaded or CodeBuddy evidence.

The existing eng_b Keychain item was reused without input or modification. Native identity returned 200, C-03 metadata returned 404, and C-02 metadata/body returned 200. No restricted body request was made. Runtime access remained readonly. The two-page allowlist was isolated in the test instance; the user's bundle/8094 process was unchanged.

13 recorded checks passed: native deny and allowed control; negative answer empty; no restricted title/native ID/canary in the response or model evidence; both queries refresh native denial; stale index deliberately retained; preview denied with native audit; only the positive fake-model invocation has evidence; the 16-event unsigned chain is valid. Local stale text was copied from the explicitly synthetic owner UI seed, not retrieved under eng_b or presented as historical ingestion proof.

The first run at ../native-restricted remains failed. Its probe incorrectly expected one fake-model invocation; FakeExtractiveModel also receives empty evidence for a negative query. The corrected probe verifies that empty invocation and the sole positive evidence-bearing invocation. No security assertion was removed; actual model network calls are zero. Both executed harness snapshots and their source hashes are preserved.

Command (explicit approved live opt-in, refuses an existing output directory):

```sh
python3 -m scripts.native_restricted_acceptance --live --output evidence/runs/native-restricted-new
```

Four guard tests passed, including no-live and evidence-preservation checks before Keychain/network access. Full 295-test runtime regression remains the prior clean candidate result; no new full-suite claim is made here. This does not establish timing side-channel resistance, live-model quality, browser denial, other native personas, or independent audit key custody.
