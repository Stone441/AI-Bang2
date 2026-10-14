# ContextLedger · final demonstration script

13 October demo account update: engineer, product and partner are server-authenticated application personas. Their explicit resource policies are intersected with the team connection's current native permissions. All three can use the live-source demo; this does not demonstrate three independent native employee identities. The live model and original permission/version checks remain unchanged. See [reviewer access](REVIEWER_ACCESS.md).

Prepared 13 October 2026; actual final team viewing not yet run. This script uses the selected structured source-review configuration. [Older demo records](reviews/2026-10-13-final-delivery/prior-DEMO_CANDIDATE.md) are historical evidence, not current acceptance.

## Operator setup

1. Use only the owned local 49161 instance. Before any update, verify listener ownership and idle status, back up persistent SQLite state/admission/configuration, and retain the original budget ledger and pending reservations. Do not touch 8094/8100.
2. The selected startup command is below. It requires existing approved saved credentials and current model readiness; do not run a second instance against a live listener. The selected instance was backed up, restarted and verified on 13 October; original private usage and audit state were retained. Disaster recovery from restored databases was not exercised.

```bash
python3 -m scripts.performance_trial --source-transport pooled --source-concurrency 4 --reasoning-effort none --source-review-input structured --source-review-dispatch single --window-strategy structured --history-read-mode batch --query-concurrency serial
```

3. Wait for all four sources to be complete/current, then use `打开试用页面.command` to obtain the existing private local entry. Do not paste tickets, credentials or private runtime files into submission materials.
4. Use final viewing allocation from [CLOSEOUT_PLAN](reviews/2026-10-13-final-delivery/CLOSEOUT_PLAN.json). Questions below each consume a model call when dispatched; preview/History do not. No automatic retries.
5. If browser automation remains blocked, a team member performs the same normal user steps. Do not use another automation route to bypass a tool denial. Record that browser validation remains pending until it actually happens.

## Seven-minute presentation

| Time | Exact narration and action | Evidence boundary |
|---|---|---|
| 0:00–0:40 | “An engineer needs the incident mitigation. A product colleague needs to know what can be offered today. Their evidence is spread across four systems. ContextLedger answers independent questions with current access checks and traceable sources.” Show cover and workspace. | State that all demonstration business data is synthetic. |
| 0:40–1:50 | Ask: “What is the latest approved mitigation for the payment incident?” Say: “The answer must retain the supported timeout-budget inspection and approved failover procedure. It must also acknowledge when the sources cannot establish the globally latest ordering.” Open a supporting citation. | Show the actual answer and elapsed time; never replace a failed answer with an overlay. |
| 1:50–2:50 | Ask: “For payment-service, which code fix is complete, which preventive work remains in progress, and is general customer release approved?” Say: “PAY-102 being Done and PAY-103 being In Progress answer different questions. A controlled pilot does not authorize general availability.” | Check the actual source scope and status; do not imply any general release date. |
| 2:50–3:30 | Open Recent/History and a citation, then refresh/reopen the workspace. Say: “Saved answers are checked against current access and versions. Refresh does not silently purchase another answer.” | Record actual behavior. A new login may not recover in-memory run progress; stored answers remain in authorized History. |
| 3:30–4:20 | Show clearly dated S-02 update and S-04 revocation evidence, then the labelled deterministic fixture walkthrough if useful. Say: “This replay shows why content updates and permission changes are separate. We retain the original mode and version of each result.” | No current source writes are authorized. Historical native replay and fixture/fake model are not a new live revocation test. |
| 4:20–4:50 | Show S-03 fixture identity contrast. Say: “A denied question must not expose the existence or title of a restricted document. Model instructions cannot create access.” | Label fixture identities; do not claim the full native persona matrix passed. |
| 4:50–5:40 | Show S-05 scoped audit and the genuine CodeBuddy contribution. Say: “The audit can reconstruct the request. CodeBuddy implemented an independent verifier for hash chains and signed checkpoints. Unsigned records and local key custody are disclosed limitations.” | Genuine screenshots/history only. A valid local chain is not independently tamper-proof. |
| 5:40–6:30 | Show architecture. Say: “We preserved source structure, reduced model work to one evidence review, reused connections and bounded native concurrency. Our six baseline single queries completed in about six and a half to ten seconds over HTTP. The final Q1/Q2 checks took 13.26 and 9.60 seconds; the queued three-request group completed in up to 28.64 seconds.” | Do not call HTTP timing browser timing, or claim 3 seconds/production SLA. |
| 6:30–7:00 | “The result is a synthetic enterprise prototype with inspectable evidence and explicit failure boundaries. The next production steps are broader source support, enterprise identity and independently managed audit custody.” End with limitations and questions. | No fabricated customer adoption or ROI. |

## Final team viewing record

Record viewer, date, exact candidate fingerprint and mode. For Q1/Q2 note missing or incorrect facts, understandable wording, citation usefulness and complete-render elapsed time. Check first login, queue visibility, History/preview, refresh/reopen and one controlled local failure/recovery. Observe security scenes with their actual evidence modes. G1/G2 require explicit human decisions and remain open.

Do not repeatedly ask all questions merely to obtain a cleaner recording. A failed run is evidence to diagnose, not footage to relabel as success. The optional video must use real screen content, remain 5–8 minutes and be checked for playback before it is called complete.
