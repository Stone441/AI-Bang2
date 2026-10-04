# Unified live pilot checkpoint

2026-10-05. Current single-source native queries are verified subsets; unified
four-source live execution is not_run. The local operator is not employee SSO.

| Source | Current actual operator | Unified-reader gap |
| --- | --- | --- |
| Confluence | eng_b, secondary email | Already delegated; retain current native identity |
| Jira | eng_b, secondary email | Already delegated; retain current native identity |
| Slack | eng_a, primary Google account | Separate ordinary reader membership and its own OAuth grant |
| Drive | eng_a, primary Google account, file owner | Separate Google reader and Reader sharing on the three synthetic files |

Do not rename eng_a's existing Slack/Drive delegation to eng_b or borrow owner
access. Suggested genuine reader is the existing eng_b email
`674544786@qq.com`: use a Google account associated with that email, join only
AI-Bang2 Slack, and share only the approved synthetic Drive folder as Reader.
This enables actual removal of the reader while owner seeding access remains.
These additional registrations, memberships and sharing require explicit approval.
Google/Slack final credentials and terms remain user-operated.

Requested eventual read scopes are the existing pilot scopes: Drive
`drive.readonly` (platform-wide for that new Google reader account; application
limited to three synthetic file IDs); Slack `channels:read`, `channels:history`,
`groups:read`, `groups:history` and basic `identify` (application limited to the
existing synthetic thread). No NTU workspace, DMs, bot, message/file write,
billing, public sharing or model budget increase.

## Ready local interface

Use `config/operator-bundle-oauth.example.json` as a template. Its
`identity_mapping_reviewed: false` is deliberate and cannot be bypassed to get a
demo running. All referenced sources must map the same confirmed actor and tenant.
Drive reference is the OAuth pilot configuration, not a manual access-token file.

After identities and native read permissions are reviewed, a fresh loopback
operator can start with:

```sh
python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port 8087 --live --model deepseek
```

Complete config and tenant validation precede private client loading and manual
prompts. Each non-Drive secret is entered once if absent; Drive uses fixed-scope
PKCE Google consent. Every native identity must pass before a browser bootstrap
ticket exists. Existing source services remain running; their memory is never
read to obtain credentials. This command is **not ready for live execution** until
the real reader setup and identity mapping are approved and checked.

Acceptance: unified engineering/operations questions, same-session source
revocation, no revoked evidence entering the model, history/export/citation
protection, retained index, and other authorized sources remaining usable.
Mocks, native owner queries and a signed local chain do not replace this matrix.

AUTH-011 update: user approved the exact reader preparation on 2026-10-05. Native account, membership, sharing and consent are pending; identity mapping remains unreviewed until actually checked. Local full regression248/248; 5 new bundle OAuth contract tests.
