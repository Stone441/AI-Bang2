# Unified live pilot checkpoint

2026-10-05 updated checkpoint. Unified eng_b four-source live query, citations,
history and Slack reader revocation are verified subsets. Grounded synthesis is
opt-in and has one successful four-source live query; full scenario/ACL acceptance
is pending. The local operator is not employee SSO.

| Source | Current actual unified reader | Remaining boundary |
| --- | --- | --- |
| Confluence | eng_b, secondary email | Already delegated; retain current native identity |
| Jira | eng_b, secondary email | Already delegated; retain current native identity |
| Slack | eng_b, kyle000909@gmail.com | Own native identity/OAuth; private member revocation verified subset, full ACL matrix pending |
| Drive | eng_b, kyle000909@gmail.com, Reader | Native identity/refresh verified; full inherited permission matrix pending |

Do not rename eng_a's existing Slack/Drive delegation to eng_b or borrow owner
access. The reviewed reader preparation uses existing Atlassian email
`674544786@qq.com` and existing Google/Drive/Slack account `kyle000909@gmail.com`.
The user explicitly confirmed this account substitution on 2026-10-05. Join only
AI-Bang2 Slack, and share only the approved synthetic Drive folder as Reader.
This enables actual removal of the reader while owner seeding access remains.
These additional memberships and synthetic-folder sharing were explicitly approved; future changes outside that scope still require approval.
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
python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port 8088 --live --model deepseek
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

2026-10-05 native setup: Google reported no account for the QQ email; user chose the existing kyle000909@gmail.com instead. Cloud Audience now shows two test users, and the synthetic folder sharing readback shows this account as Viewer with general access Restricted. Reader API identity, OAuth grant and revocation remain not_run.

2026-10-05 Slack account substitution explicitly approved; invitation to kyle000909@gmail.com succeeded in native UI. Acceptance, member ID, private-channel membership and OAuth still pending. Drive reader query/revocation subset is now verified (reader-query-and-revocation.json); permission restored as Viewer/Restricted by UI readback.

Port allocation update:8087 is occupied by the running independent Drive reader; keep it running and use8088 for the eventual unified operator. The unified manifest must reference `.runtime/drive-oauth-reader.json` for eng_b, not the eng_a owner config `.runtime/drive-oauth-pilot.json`. Slack reader config can be prepared only after its real user ID is verified. No new live operator should be started from the example with unreviewed identity mapping.

2026-10-05 launch preparation: reader Slack UI identity/private membership verified; user reports its OAuth token saved. Temporary app Collaborator was removed via native self-Leave. `.runtime/operator-bundle.json` now references the actual eng_b configs, with reviewed public actor/tenant mapping. The command above is ready for local hidden-input startup; this does not claim Slack API binding or unified live execution. Startup independently rejects any native credential mismatch before issuing an application ticket. Keep8085/8086/8087 running; enter each required credential once into the fresh8088 process, then reuse it throughout query/revocation checks.


## Current simplified startup · AUTH-014

Use `make live` from the repository root. The user approved app-owned macOS Keychain persistence for the reviewed eng_b mapping and existing model budget. First input saves each source independently; later launches reuse saved credentials, with native identity and current permission checks unchanged. Drive offline consent uses the same exact read-only scope; native-account verification precedes refresh-token storage. Existing Passwords entries are never read. See RUNBOOK for replacement of one invalid credential. Actual unified startup and real refresh reuse are verified subsets in evidence/runs/linkless-optimization/live-latency.json; local/mock tests and the synthetic native Keychain smoke remain separate evidence.


Current opt-in synthesis: `make live-synthesis` from repository root, preserving the existing USD20 ledger and saved reader credentials. Stop the current8088 process yourself before reusing that port. Exact quotes, separate same-model review and a fresh `review_dispatch` native authorization check apply; model review is fallible. See RUNBOOK and evidence/runs/synthesis/live-query.json. Historical preparation notes above describe earlier checkpoints and must not be interpreted as the latest acceptance status.
