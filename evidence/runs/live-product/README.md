# Live product question · operator subset

`answer.json` and `audit.json` are actual four-source synthetic pilot / DeepSeek synthesis results for eng_b. `verification.json` contains automated fact probes, exact quote validation, per-stage authorization and independent original-budget ledger joins; `semantic-review.json` is the developer’s review, not a human gate. The model received four sources; the four answer claims cite Confluence/Jira/Drive.

Two accepted model calls cost 1,529 micro-USD by conservative accounting, not a supplier invoice. `unsupported-answer.json` is an actual no-evidence response and has no model call/ledger charge. That unique-token sample does not establish arbitrary missing-information correctness.

The source files are approved synthetic documents; no platform writes, new scope or new credentials occurred. The current reader has engineering access, so this is not the independent product_ops permission scenario. User service 8094 was untouched.

The exact executed runner is retained as `executed-harness.py.txt`; the current script adds an evidence overwrite guard and fixes future mode labels. To run another approved sample use `python3 -m scripts.live_product_acceptance --live --output <new-local-evidence-directory>` with the existing reviewed configuration, app-owned Keychain credentials and original budget DB. No automatic live execution via make/test/demo.

Mode-label discrepancy: the executed runner left Engine.mode with a fake_model suffix after replacing the model. Actual model name, linked accepted supplier calls and receipts prove this was live synthesis. Raw evidence is preserved; `mode-label-discrepancy.json` explains the issue, and the current runner sets the mode correctly. This is not a live rerun of the metadata fix.
