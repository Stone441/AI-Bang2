# Public demo UI and security review — 2026-10-16

Baseline: 84b23dd. Scope: existing public demo, UI cleanup, bounded application hardening. No new paid model calls, cloud resources or source permissions.

## Changes

- Source names use Confluence, Jira, Slack and Google Drive. Runtime source details are collapsed; the scenario retains one visible source overview.
- Answers prioritize the question and per-part conclusions. Exact quotes and source buttons expand together; the reference inventory is collapsed for supported answers, open for evidence-only/empty answers. Every qualification, insufficient-evidence notice and source-access check remains.
- Normal synthesis-method notes use muted text; genuine gaps/errors retain notice treatment.
- Examples appear immediately above the input. Selecting one fills and focuses the input, positions the form, and never submits.
- Introduction and all workspace views include © 2026 Team AI Bang2. All rights reserved.

## Security findings and mitigations

1. Anonymous/unknown routes could call source refresh before authentication. Removed the global pre-auth refresh; only authenticated known evidence/history/audit routes refresh, and query retains its existing authorization path.
2. HTTP connections previously created unbounded threads. Added 32 active connection slots and a 16-connection listen backlog; saturation closes excess connections before allocating threads. Existing 10-second idle I/O and 5-second body deadlines and 12 KB body limit remain. These are resource bounds, not comprehensive slow-client/DDoS protection.
3. Password login now has a global 30-attempt/60-second rolling limit before expensive authentication. IP headers are not trusted. Session capacity is 128 with expired-session/run cleanup; at most four query requests can be active or waiting. Existing model cost/admission protections remain. Public shared accounts still permit strangers to consume the shared allowance and view authorized shared history by the owner's explicit decision.
4. Added Permissions-Policy and HTTPS HSTS, and removed Python version disclosure. Existing CSP, HttpOnly/Secure/SameSite cookies, Host/Origin/CSRF checks, textContent rendering, allowlisted source links and immutable static file allowlist remain.

## Host boundary and residual risk

Observed: app listener is 127.0.0.1:49161; both app and tunnel are per-user LaunchAgents with umask 077. Public demo credential file and tunnel configuration have mode 0600. The app runs as the everyday macOS user, without a VM/container/dedicated OS account boundary. No route for arbitrary filesystem download, command execution or uploads was found in this scoped code inspection; this is not proof of no vulnerabilities.

Cloudflare Tunnel is an ingress proxy, not host-process isolation. If a future application/dependency vulnerability enables code execution, it may access files and credentials available to the process user. Publishing the URL increases discoverability; hiding it is not an access-control strategy. Public demo credentials are not secrets and cannot serve as an abuse barrier.

Recommendation before prolonged public operation: move the demo and its narrowly scoped synthetic-data credentials to a dedicated hosted VM or isolated account/VM with no personal home-directory mounts or personal secrets; retain the same domain and tunnel. This review does not create paid infrastructure or claim that personal assets are isolated. Cloudflare account-specific WAF/rate-limit rules were not inspected or changed. No public load test, penetration-test certification or incident-forensics claim.

Primary references: [Python HTTP server limitations](https://docs.python.org/3.14/library/http.server.html), [Cloudflare Tunnel routing](https://developers.cloudflare.com/tunnel/concepts/routing/), [Google Drive official naming](https://support.google.com/drive/answer/2424384).

## Validation

- 38 HTTP-related local synthetic tests passed, including 5 new hardening cases: anonymous/unknown no-refresh, rate-limit/recovery, session capacity/expiry, connection saturation/recovery, headers/query queue.
- 10 reviewer-access and 32 sectioned-answer Python tests passed. All 15 standalone frontend tests passed; the HTTP lifecycle script passed through its Python server wrapper. An initial direct invocation of that script lacked its required URL; the wrapper result is authoritative. The runtime UI test still expected the removed raw budget copy from the earlier approved design, so it now asserts a hidden healthy state and a visible unavailable state with submission disabled. Rendering tests preserve exact quotes, scoped gaps, revoked-answer cleanup and citation actions.
- Local Chrome confirmed the single source row and collapsed runtime details. Additional visual/deployment checks are recorded separately after release.
- No paid model call, source mutation, new account permission or live attack/load test.

Local Chrome also verified example-before-input order, click-to-fill/focus/scroll without submission and the copyright footer.

Clean archive 44c7621: 806 Python tests ran in 57.882 s; 805 passed and the static-snapshot fixture failed because it only supplied the original three assets, omitting the three subsequently added logos. The fixture now supplies all six allowlisted assets; the immutable loaded-JavaScript assertion is unchanged. The corrected case passed separately. All 15 standalone frontend tests passed in the clean archive. Existing test ResourceWarnings were observed; this is not a leak-free certification. Candidate diff scan found no common credential patterns or known public-demo passwords.

Tunnel configuration was read without printing credentials: one public hostname maps to loopback port 49161, followed by a catch-all HTTP 404. It does not expose arbitrary host ports or filesystem paths through that configuration.
