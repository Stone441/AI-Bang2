# Independent product-reader pilot candidate

2026-10-06. AUTH-016 approved the specified Confluence token and app-owned product_ops Keychain reuse. Native account login is verified in the API token manager; the final token review shows the exact approved name, expiry and two scopes. The user reports token creation and Passwords storage complete; secure input, app-owned Keychain reuse and native current-user validation have now passed. The Confluence-only product subset has passed 16 native/fake checks and browser positive/negative evidence checks; it does not complete the four-source persona matrix.

The existing third test account is 2918379149@qq.com. The local Confluence config contains a candidate product_ops native account mapping, but it must be checked against the token's actual current-user response before use. The existing eng_b token or identity must never be substituted.

## Concrete next authorization

Prepare one Confluence-only readonly token named `AI-Bang2 product_ops Confluence read-only pilot`, expires 2026-10-20, scopes `read:page:confluence` and `read:content-details:confluence`. The scope itself covers pages this account can read; application requests remain restricted to the synthetic lab/explicit C-01, C-02, C-03 IDs. Do not add memberships, broad page permissions, admin/write scope, paid resources or access to existing personal/enterprise documents.

The user completes credential creation and any security verification/terms. After one local hidden input, save/reuse only a new app-owned Mac Keychain item for `confluence / aibang2-live-pilot / product_ops / verified native account`. Do not read the user's existing Passwords entries or persist plaintext. This is outside AUTH-014's eng_b-only authorization; AUTH-016 now explicitly approves this limited extension.

## Acceptance after approval

1. Verify the native account ID equals the reviewed product_ops mapping; mismatch stops, no fallback.
2. Read only the explicit approved synthetic targets under that identity. C-02 must allow. C-01/C-03 should deny under the intended native permissions; unexpected allow is a failed isolation case, not patched by a frontend role.
3. Query product release scope with a fake model; verify pilot-only/not GA/no invented date with actual evidence. Query incident/security data; verify no restricted text/title/path in answer/model evidence, and preview/history protection where applicable.
4. Keep operator config/SQLite independent; preserve eng_b and 8094. Record native decisions and developer checks as a Confluence-only product persona subset. Jira/Slack/Drive and native auditor remain separate prerequisites; no full four-source persona claim.

The token form has been prepared through the final review, with a private nonsecret screenshot at evidence/tool-usage/private/product-reader-20261006/token-review.png. The user reports completing creation and local Passwords storage. The agent has not inspected the secret. App-owned Keychain persistence/reuse and native identity validation are now verified; no page permission change or paid model call has been performed.

## Prepared startup (fake model only)

The isolated `.runtime/confluence-product.json` configuration contains only product_ops and the three explicit synthetic pages. The reviewed candidate native account ID still requires actual current-user validation; mismatch stops before saving the credential. The existing four-source bundle is unchanged.

After token preparation, run in VS Code's secure terminal:

```sh
python3 -m brain.operator_web --source confluence --config .runtime/confluence-product.json --actor product_ops --port 8100 --live --model fake --credential-store macos-keychain
```

First launch asks for email and token through hidden input, verifies the native identity, then saves the new app-owned item. Later launches reuse it. SQLite is separated by a digest of actor/tenant/native account, instead of sharing the old confluence-web.sqlite. Open the new one-time link privately; do not send it or any key to chat. This command does not request a product_ops DeepSeek credential or call a paid model.

## Actual result

See evidence/runs/native-product-reader: 16 native API/fake checks, C-01/C-03 denied without body fetch, C-02 allowed, restricted stale preview denied. 8100 browser answer, preview, history and standalone security refusal verified. New question clears prior answer dependencies; existing follow-up semantics remain for continued questions. No paid model calls or changes to platform page permissions. Remaining: native product Jira/Slack/Drive and auditor/contractor identities, complete human acceptance.
