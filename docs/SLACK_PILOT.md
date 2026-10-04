# Slack read-only pilot

## Actual state — 2026-10-05

AUTH-008 approves the competition workspace `T0C6FQ246TF`, synthetic allowlisted messages and four user scopes. Earlier installation retries returned creation-rate and incomplete-install messages. After Chrome was updated, the actual app list showed four same-name apps: `A0C6F96HFNX`, `A0C6R6B4V7E`, `A0C6MAR8FUJ`, `A0C6G6EN3SR`. Failed installation did not mean creation failed. Do not create further duplicates or delete these without separate approval.

Selected existing app `A0C6F96HFNX`: OAuth settings verified no bot scopes and the four approved user scopes. The native review also displayed basic identity `identify` and application privacy/terms. The user explicitly confirmed final Allow (user_confirmed); the agent did not click Allow or inspect the post-authorization token. Await user secret storage and leaving the token page before checking non-secret installation state. Native API/query/ACL remain not_run.

The manifest contains user scopes `channels:read`, `channels:history`, `groups:read`, `groups:history`; no bot, write, DM or files scopes. The platform grant covers channels the authorizing user can read; the application further restricts workspace, channel types and exact message IDs. This does not connect the NTU workspace. The user completes final grant and secret storage. Manually revoke the pilot token by 2026-10-20; no paid plan or new terms are approved here.

## Trust boundary

`brain/slack.py` verifies `auth.test` user and team before every read, rejects bot credentials, verifies current `conversations.info`, then retrieves one allowlisted message using `conversations.history` or one allowlisted reply using `conversations.replies`. A reply must name an earlier allowlisted root. There is no search, source write, administrator fallback or positive permission cache. These reads join the same delegated Engine as Confluence/Jira; final model dispatch and history/citation/export also recheck current access and exact content fingerprint.

Private channels require current membership; removal prevents fetching message content. **Leaving a public channel does not revoke a user's public-channel access**: Slack user tokens can read public channels without membership. Native revocation acceptance must use a private synthetic channel, a genuinely restricted identity or token revocation. Do not implement a fake public-channel ACL to demonstrate success.

Missing or malformed metadata, token expiration, missing scopes, rate limiting and network failures produce unknown and no usable content. Native access denial/deleted exact message produces deny. No adjacent message may substitute for an unavailable timestamp. Shared/Slack Connect channels, DM, files, attachments, bot/subtype messages and unsupported rich blocks are rejected. Plain rich-text fallback must match the actual message text. Edits use a full content hash and derived snapshot version, not a native monotonic version; old answer/evidence access requires an unchanged snapshot. Background sync, pagination, OAuth refresh and full Slack object coverage are not implemented.

## Native configuration and startup

After installation, verify the personal workspace URL, authorizing native user ID, synthetic channel ID/type and exact message timestamps through the native UI. Preserve timestamps as strings. `config/slack-pilot.example.json` intentionally has invalid placeholders; do not start it as live configuration. Replace only verified mappings in ignored `.runtime/slack-pilot.json`, set file permission `0600`, and leave secrets out of it. `eng_a` is a local actor mapping, not a client-selectable privilege or the Atlassian eng_b identity.

Once those prerequisites are verified:

```sh
python3 -m brain.operator_web --source slack --config .runtime/slack-pilot.json --actor eng_a --port 8084 --live
```

Startup asks for the Slack **USER OAuth token once**, with hidden TTY input, and verifies native identity before serving. It does not ask for an email. Credentials remain only in process memory; the one-use bootstrap link creates the existing loopback operator session. Browser requests never receive the token. Subsequent queries reuse the credential while repeating source checks. Restarting requires re-entry. Do not send the token, screenshot it or store it in Git. This operator pilot is not employee OAuth/SSO. The runtime database is `.runtime/slack-web.sqlite`; the model remains `fake-extractive-v1`.

## Validation

```sh
PYTHONPATH=tests python3 -m unittest test_slack test_slack_operator
make test-report
node tests/frontend_operator_security.js
```

The 22 Slack tests use mock source HTTP, including real local operator HTTP sessions, private-channel revocation, deletion/edit, exact reply matching, credential reuse, malformed/shared objects and Slack/Jira combined evidence. They do not call Slack. Live acceptance still needs an actual root/reply read, native private-channel permission removal, same-session query/history/citation/export checks and restoration. Record actual native errors rather than treating unknown as proven revoke.

Official method contracts: [auth.test](https://docs.slack.dev/reference/methods/auth.test/), [conversations.info](https://docs.slack.dev/reference/methods/conversations.info/), [conversations.history](https://docs.slack.dev/reference/methods/conversations.history/), [conversations.replies](https://docs.slack.dev/reference/methods/conversations.replies/), [conversation object](https://docs.slack.dev/reference/objects/conversation-object/). Rate policies depend on app classification; no measured live quota or creation cooldown duration has been established. Runtime 429 remains fail-closed.


Native setup update: user confirmed token stored and page closed. Competition private channel `C0C6R70SGG4` now contains synthetic root `1791142152.858189` and reply `1791142180.560339`; rendered sender/profile verified primary native user `U0C6QPLBZPW`. Non-secret exact config is `.runtime/slack-pilot.json` (0600). UI seed is recorded separately from API acceptance in `evidence/runs/live-slack/native-seed.json`. Only one member; native channel-removal acceptance still needs a separate reader identity. Ready for one hidden-token operator startup, not yet live query verified.

Root web subset verified: request `1ad44120a721453b91153d15d5ad1cea`, real native root allow, preview/history clicked, 9 DB checks and unsigned chain valid. Reply returned unknown and never entered model; complete thread remains unverified. New reader diagnostics are fixed codes only. Reply now requests up to2 messages and permits only the exact target plus its allowlisted parent; missing/duplicate/extra timestamps do not pass. This is a candidate compatibility fix with2 additional mock tests;199 full regression passed. Existing service must restart before native diagnosis/retest. No new scopes or credential access are needed.
