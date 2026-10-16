# Demonstration guide

**[Watch the project demonstration (7m 32s)](https://youtu.be/BULowhVNfU8)** with English narration and captions. The video distinguishes a live question using native APIs and synthetic business data from controlled fixture scenarios.

## Entry and mode

Open **https://contextledger.hellokyleshi.com**, enter Workspace and select a shared demonstration identity. The hosted demonstration uses native source APIs, synthetic business data and reviewed model synthesis. It depends on the hosting Mac and current operator readiness.

If the website cannot be opened during evaluation, the hosting Mac may be asleep or offline, or its local service or tunnel may be stopped. Please [contact Team AI Bang2 (shuyi013@e.ntu.edu.sg)](mailto:shuyi013@e.ntu.edu.sg?subject=ContextLedger%20demo%20access) to arrange a test session. The [demonstration video](https://youtu.be/BULowhVNfU8) provides an alternative walkthrough.

For a credential-free reproduction, follow [Quick start](QUICKSTART.md). That mode and the separate scenario lab use fixtures and a fake model. Historical results remain historical even when reopening them checks access again.

## Five challenge scenarios

| Scenario | What to show | What to verify |
|---|---|---|
| Unified query | As Engineering, ask “Is PAY-102 complete, and can we offer payment-retry to all customers today?” | Distinguish code completion from pilot/GA approval; inspect each subquestion's quotes and source context. Model output can vary and must be checked. |
| Freshness | Open an authorized source preview and its source-update, indexing and check timestamps. In the fixture lab, publish the next controlled version and read again. | Separate native source timestamps from local indexing and permission-check times. A fixture mutation is not a new native latency measurement. |
| Permission denial | Use External Partner to ask for the restricted security incident report. | The response must not confirm restricted content or reveal its title, path or existence. Role labels alone do not prove all native employee permissions. |
| Dynamic revocation | In the isolated fixture lab, read the scenario, apply its fixed revoke action, then inspect the later answer and audit. | Revoked evidence must not continue through queries, history or previews. Do not change live platform permissions without a separate approved action. |
| Audit | As Audit reviewer, inspect a request from the allowed demonstration accounts and its resource decisions, model attempts, usage and outcome. | Scope remains restricted. Saved/attempted/delivered are different events; the UI does not certify external checkpoint custody. |

The fixture lab starts with `python3 -m scripts.scenario_lab`. It has its own in-memory data and fixed controls, separate from the hosted service. Its read, version-publication, revocation and audit steps provide a reproducible illustration without source writes or model charges.

## Evidence review

Expand exact supporting quotes, then open a source preview to verify the passage and version. Use Recent answers to reopen an existing result; that operation rechecks access but does not generate a new answer. An evidence-only or rejected result is not a successful synthesized answer, and a supported historical example does not establish general answer accuracy.

The [submission description](SUBMISSION.md) and [validation scope](VALIDATION.md) disclose remaining semantic and deployment limitations.
