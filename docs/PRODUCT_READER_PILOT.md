# Independent product-reader pilot candidate

2026-10-06. Candidate only; new token/persistence are not approved. This does not mark product_ops native acceptance complete.

The existing third test account is 2918379149@qq.com. The local Confluence config contains a candidate product_ops native account mapping, but it must be checked against the token's actual current-user response before use. The existing eng_b token or identity must never be substituted.

## Concrete next authorization

Prepare one Confluence-only readonly token named `AI-Bang2 product_ops Confluence read-only pilot`, expires 2026-10-20, scopes `read:page:confluence` and `read:content-details:confluence`. The scope itself covers pages this account can read; application requests remain restricted to the synthetic lab/explicit C-01, C-02, C-03 IDs. Do not add memberships, broad page permissions, admin/write scope, paid resources or access to existing personal/enterprise documents.

The user completes credential creation and any security verification/terms. After one local hidden input, save/reuse only a new app-owned Mac Keychain item for `confluence / aibang2-live-pilot / product_ops / verified native account`. Do not read the user's existing Passwords entries or persist plaintext. This is outside AUTH-014's eng_b-only authorization and therefore needs explicit approval.

## Acceptance after approval

1. Verify the native account ID equals the reviewed product_ops mapping; mismatch stops, no fallback.
2. Read only the explicit approved synthetic targets under that identity. C-02 must allow. C-01/C-03 should deny under the intended native permissions; unexpected allow is a failed isolation case, not patched by a frontend role.
3. Query product release scope with a fake model; verify pilot-only/not GA/no invented date with actual evidence. Query incident/security data; verify no restricted text/title/path in answer/model evidence, and preview/history protection where applicable.
4. Keep operator config/SQLite independent; preserve eng_b and 8094. Record native decisions and developer checks as a Confluence-only product persona subset. Jira/Slack/Drive and native auditor remain separate prerequisites; no full four-source persona claim.

No token request, secret entry, new Keychain item, platform permission change or paid model call has been performed by this candidate document.
