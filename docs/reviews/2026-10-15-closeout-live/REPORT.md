# Authorized switch and bounded live acceptance · 2026-10-15

**The owned service has been switched and the authorized trial completed. This is not an all-scenarios quality pass:** two optional sectioned-synthesis cases still fail generation validation. No paid answer was retried. Source-review remains the deployed default.

## Version and deployment

The user explicitly approved the prepared human grant migration, same-host 49161 switch, exact three-demo-account auditor scope, and a separate maximum of 12 DeepSeek calls / USD0.50. The older 36-call authorization was not combined with this allowance.

- Native/model trial candidate: `498239ea54a09a45c9e90ed0ef57c524428b84d5`, immutable release, startup source `77f7fbbe7a2ff4a553988267bfe815ba0eabcde74c88a3d2ee7463ce35084442`.
- Final deployed code: `f2f0633e524ea266b2ea8f23187dd2c716399a3a`. Its only runtime change after that trial is the public-static-navigation gate fix; it does not change models, prompts, retrieval, source authorization or accounting. Startup source `c161d77f8274edb5e3f336e15c980bf20ff3f9cbad9c3fe0bdd28f1ce3622c81`, loaded at `2026-10-15T09:35:42.268926+00:00`.
- Same existing hostname: https://contextledger.hellokyleshi.com . Existing Cloudflare Tunnel retained. No new service, DNS, scope, source write or cloud purchase.
- Backup through SQLite backup API plus exact private config/state copies, integrity checks and manifest preceded the switch. Original PID/listener, absence of active connections, idle admission locks and exact prepared config hashes were checked.
- LaunchAgent runs the immutable release directory with explicit original `--state-root`; fixed code/UI and original durable state are separate. No hot reload claim.

The original `main` checkout remains at 5727300 with its prior dirty evidence intact. Fixes and reports are committed locally on `fix/systematic-closeout-20261015`; no push, protected-main merge or competition submission was performed.

## Accounting, old unknowns and identity

The exact reviewed human migration plan was applied without changing the original human JSON bytes. Seventeen earlier team-live settlements were excluded only from the human grant using their exact original receipt IDs and evidence digest; all original global charges remain. Human historical settlement is **3,213 micro-USD / 8 calls**, unchanged throughout this automatic trial. The two original dispatched unknown reservations, totaling 648,808 micro-USD, remain. No baseline or ledger was reset.

Separate grant `closeout-live-20261015-12`: **10 actual calls / USD0.011808 conservative settlement**, against 12 calls / USD0.50. New unknown **0**. Global ledger settled 1,345,936 micro-USD; accounted including the two old reservations 1,994,744 micro-USD, within the original USD20 ceiling. These are conservative internal estimates and validated usage receipts, not a supplier invoice. The remaining allowance was not spent on repeated failed answers.

The new optional `closeout_auditor` has no native source identity and cannot query knowledge. It is restricted to exact existing revisions of the three approved fictional application accounts and payment-service. Existing employee passwords/revisions were copied unchanged into a separate private candidate registry; no original account registry was overwritten. Its new login card remains local at `.runtime/closeout-20261015/auditor-login-card.txt`, outside Git. Do not send or upload it without separate authorization.

## Actual checks and semantic review

All cases used the existing approved real four-source synthetic data and a separate loopback HTTP service with an isolated index/audit store. The same approved shared budget ledger was used through the independent grant. Source readiness was checked before each question. No source was modified. Author-written expected answers were frozen before execution; the judgments below are Agent comparisons against actual source text, not human or blind evaluation.

| Case / mode | Actual calls / conservative USD | Actual result |
|---|---:|---|
| Incident cause and withdrawn cache hypothesis / source-review | 1 / 0.000843 | Accepted; Slack withdrawal and Drive final retry/timeout cause present. 13.913s |
| Done fix, protective work, release approval / source-review | 1 / 0.000794 | Accepted; PAY-102 Done, PAY-103 In Progress, no inference of release approval. 9.220s |
| Chinese assumed GA release / sectioned | 2 / 0.002910 | Accepted; explicitly corrects GA premise, pilot only, no confirmed date. 23.547s |
| Missing synthetic project revenue / source-review | 1 / 0.001105 | Review rejects coverage. Zero claims, explicit failed-answer/insufficiency wording, evidence gallery only. Presentation repaired; not a validated answer. 23.088s |
| Same missing revenue / sectioned | 2 / 0.002886 | Accepted with one genuinely insufficient part and zero claims; no invented revenue/nonexistence conclusion. 28.076s |
| Same-scope SG-GATE conflict / sectioned | 1 / 0.001230 | Generation rejected: `answer_part_assignment`. No review call or draft displayed. **Quality failure.** 11.167s |
| Four current probe values / sectioned | 1 / 0.001872 | Generation rejected: `claim`. Authorized current raw evidence from all four expected objects contains amber; no validated per-part answer. **Quality failure.** 19.891s |
| Partner question claiming admin authority / source-review | 1 / 0.000168 | Only authorized C-02 capability evidence; coverage rejects and zero answer claims. Scope protection passed; requested engineering answer not delivered. 3.637s |

The latest Drive native version observed was 11 (earlier trial reported 10), with current amber content; no cause for that external version change is inferred. Jira/Slack fingerprints are compared for identity/change, not numeric ordering. The table's timings are complete HTTP returns, not browser render time, p95 or SLA.

Five initial submissions were **zero-call** failures: the isolated driver mistakenly used source-review-only `single` dispatch for sectioned synthesis, then immediately encountered the existing request cooldown. These original failures were retained. The driver was corrected to use each mode's valid dispatch configuration and pacing; only those uncharged questions were subsequently executed. None of the charged successes or failures was repeated. An initial deployment-check tuple-unpacking error was also a zero-model diagnostic; it did not alter accounts or budget.

Real HTTP history/preview checks returned own-history 200 / own-preview 200, cross-account history 403 / preview 403, and ordinary-account audit denial 403. After the final switch, engineer/product/partner/auditor logins were 200 with Secure cookies; auditor scoped events returned 200, auditor knowledge query 403, and all four sources were complete/current. The scoped online audit was exercised using actual saved requests; this is distinct from signing an offline export and not proof of human reading or independent checkpoint custody.

## Public browser and regression

Automated command-line HTTPS requests were blocked by Cloudflare 1010/403. No Cloudflare policy, browser warning or security setting was bypassed or disabled.

Actual Chrome navigation separately found an application bug: its overbroad cross-site gate also denied anonymous public HTML. It was reproduced with explicit cross-site request headers. The fix allows only the three immutable anonymous GET assets, still after exact Host validation; every API and every POST retains Origin/fetch-site/session/CSRF protections. Independent review found no permission regression. Red, green and full logs are retained here.

The repaired deployed page was opened in Chrome and visibly reached **LIVE API DEMO**, with the actual username/password login form and application-role boundary text. Thus the public login page and its initial health/API boot were observed. Authenticated browser question/history/audit interaction and human G1/G2 were not performed and are not replaced by HTTP or DOM checks.

Post-navigation full local regression: **758 Python tests / 53.851s / OK**. The preceding core candidate had 757 Python, 14 DOM suites, 25 offline groups and the real fixture HTTP wrapper passing. The navigation-only change additionally passed its new header test and the original nine HTTP tests. Native/model results belong to 498239e; the final static-navigation change was validated locally and in the actual deployed browser without extra model calls.

## Remaining defects and next action

P1 remains for optional sectioned conflict/four-value generation. The new bounded diagnostic distinguishes assignment from claim failure, but the full rejected draft was deliberately not saved; exact bad indices/claim fields cannot be reconstructed. Preserve these request/audit/receipt hashes, then improve bounded field diagnostics and add faithful offline regressions before proposing any narrowly justified paid revalidation. Do not loosen quote, part mapping, review or authorization gates and do not automatically spend remaining calls to seek a successful answer.

Default source-review missing-information behavior is now a clear safe failure rather than a large irrelevant prose dump; it remains a quality limitation. The accepted application-role scope is retained. Four-source independent employee identities, three untested native revocation paths, generation-time native revoke, long-duration stability, semantic malicious-source injection resistance, independent checkpoint custody and human acceptance remain distinct limits.

Raw answers, questions, receipts, native resources, audit databases, scripts and backups remain private under the evidence root listed in `EVIDENCE_MANIFEST.json`; only non-secret summary/hash indexes are committed. Existing CodeBuddy proof originals were not recreated or uploaded.
