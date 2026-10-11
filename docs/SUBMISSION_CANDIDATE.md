# ContextLedger · submission candidate

Prepared 11 October 2026 from main b34a055 plus the current delivery branch. Current source-review v2 uses one DeepSeek Flash low-reasoning review with cap8192 as a bounded fallback after disabled-thinking reviews rejected or omitted authorized mitigation actions. Actual original Q1 now includes the current runbook measures and explicitly leaves latest ordering unknown; original Q2 and a pilot/GA scope question also returned supported source answers. These are single authorized agent HTTP observations, not browser/human acceptance or a stability estimate. All earlier failures, including an accepted review that omitted C01, remain recorded. G1/G2 and submission are not complete.

Current candidate constructs quotations covering every retrieved authorized passage in server code, then sends them to a single coverage/scope review. Unsupported claims and incomplete reviewed answers are blocked; failed source continuation remains labelled as failure. The server explicitly declines to infer latest ordering. This is a technical alternative to free-form synthesis; its current single successful first-question result is a reviewed source answer, not a free-form summary.

## Copy-ready project fields

**Title:** ContextLedger — The Internal Brain

**Short blurb (8 words):** Permission-aware enterprise answers with evidence and audit trails.

**Description:** Engineers handling an incident and product teams checking release readiness need context scattered across Confluence, Jira, Slack and Google Drive. ContextLedger brings these sources into an independent question workspace. Its value is a useful, verifiable answer with visible uncertainty, source versions and a record of how it was produced.

The prototype reads explicitly approved synthetic competition material through native source APIs. A verified server session selects the operator identity; collection credentials never grant an employee additional access. Local retrieval selects version-bound evidence, and current native access and content checks protect model dispatch, review, delivery, citation previews and saved answers. Missing or unknown access cannot grant permission. Incremental background discovery publishes completed source updates; it is polling with bounded operational checks, not a claim of continuously connected sources or a production freshness SLA.

The current DeepSeek Flash path reviews source quotations constructed by the server instead of freely rewriting facts or using a model to select passages. Code preserves every character of each retrieved authorized evidence window in bounded contiguous quotes. A single model call reviews support, relevance and complete question coverage after current source authorization. It must preserve proposal, approval and completion as different states and retain every requested supported part and critical qualification. True but unnecessary background can be removed only with explicit review confirmation that the remaining answer is independently complete; any retained source window remains whole so its trailing limitations are not dropped. Unsupported, uncertain or incomplete reviews block the answer. The server checks exact quote matches and authentic settled review usage, then rechecks current access and versions before delivery and History reads. No model generation call is claimed. A fixed server notice says that latest ordering is not inferred; it cannot supply a missing action or approval. Same-model review remains fallible and is not an independent security authority.

The previous free-form synthesis path remains available as a rollback. If a known-usage output is rejected, the trial may show an explicit answer-validation failure alongside unchanged source passages after final current-access/version checks. This evidence-only continuation is partial utility, not an accepted answer. Source or usage unknowns never use this continuation.

The interface shows elapsed time and recorded stage outcomes, classified failures, runtime and recent source checks, current-access citation previews, Recent summaries and explicit History retrieval. Refresh can reconnect to the current session's run without another model call. Expired sessions and server restarts have distinct limitations. Recent → Workspace restoration was confirmed in the actual Chrome trial: current-access checks restored the saved second answer without restarting elapsed time or submitting another question. This is browser engineering evidence, not team G1 approval. The product has independent questions, with no chat context inheritance or answer download.

Audit records preserve actor, question, per-resource decisions, model attempts and usage, citations and final answer. The real CodeBuddy contribution independently verifies audit hash chains and Ed25519 signed checkpoints. An unanchored chain and an unsigned tail remain explicitly untrusted; local key custody does not prove production resistance to a compromised host.

Measured impact is reported as individual native request times, actual model usage/cost, current validation and observed limitations, not projected savings or a fabricated success percentage. The broad mitigation question failed on previous builds; the current low-review candidate returned the runbook actions in one actual request (66.14s). This does not establish repeatability or team acceptance. The test world is fictional; it is not Aspire internal data.

## Official checklist and existing artifacts

| Item | Candidate / source | Remaining human action |
|---|---|---|
| SUB-01/02 title and <10-word blurb | Fields above | Approve wording |
| SUB-03 description, prompts, impact | Description above; [actual architecture](IMPLEMENTED_ARCHITECTURE.md), [synthesis prompts](../brain/synthesis.py) | Review claims against current result |
| SUB-04 real conversation history | [DEV09 manifest](../evidence/tool-usage/dev09-manifest.json), local `evidence/tool-usage/private/dev09-20261004/conversation-history.zip` | Review private content and authorize submission upload |
| SUB-05 16:9 cover | [existing PNG, 1600×900](../assets/submission/contextledger-cover.png), [SVG](../assets/submission/contextledger-cover.svg) | Approve cover; official recommended pixels are 380×216 |
| SUB-06 optional 5–8 minute video | Script below | Record actual UI and verify playable final video |
| SUB-07 ≥3 genuine screenshots | Existing DEV09 01-task-start, 04-code-writing, 07-final-validation PNGs; manifest contains seven screenshots | Select/redact actual screenshots; never reconstruct tool use |
| SUB-08 optional live URL | Loopback demo for team only | Public deployment is not authorized |
| Aspire live demo / architecture / source | Five scenes below, [standalone architecture SVG](../assets/submission/contextledger-architecture.svg) and current repository | G1/G2 review; explicit push/merge and submission approval |

The 15 existing DEV09 artifacts were checked against their recorded hashes this round. Real contribution: original `4165ee6`, integration `8cd5088`; implementation and historical validation in [CodeBuddy delivery](CODEBUDDY_AUDIT_DELIVERY.md). No new CodeBuddy contribution is claimed.

## Start and use

Native team trial uses `打开试用页面.command` after this task's 49161 service and private entry are prepared. It verifies the owned 49161 listener and runtime fingerprint, then explicitly renews a private one-time entry on this Mac when double-clicked; it does not submit a question or restart the service. Entry tickets last ten minutes, sessions one hour. Refresh within a valid session resumes its run. If the entry has expired or was used, double-click again for a fresh entry. If the session has expired, a fresh login does not restore its in-memory run; restarting does not recover the old in-memory failure receipt. Successful stored answers remain subject to current History authorization/version checks.

The current human trial is already running. For an authorized update of an owned idle instance, preserve task state first and use `python3 -m scripts.delivery_trial --human --human-open --answer-style source-review --review-reasoning-effort low`. Do not start another listener or interrupt a human request. Startup requires same-day `python3 -m scripts.model_readiness`, the original native accounts/containers and available budget. The independent durable admission state and original USD20 ledger survive restart. Original admission is exhausted at12/12 with17 model calls and remains unchanged. AUTH034 explicitly removes human submission and total call count limits. The new human-open state inherits AUTH033 counters and its original USD0.10 new-settlement stop baseline, currently USD0.024688 newly settled and9 submissions/8 calls recorded; new unknown usage still stops admission. No automatic questions. Never reset state to regain attempts. The current trial uses low reasoning only for its single review / 8192 / ranking none. Disabled thinking was tried first and remains the launcher default and explicit rollback by omitting `--review-reasoning-effort low`; it is not the current trial configuration. `--answer-style reviewed-excerpts` retains the earlier failed selector candidate; `--answer-style synthesis` selects the older synthesis rollback; omitting this option also defaults to that older path. Original low8192 configuration remains in the historical launcher and b34a055.

For a no-provider-cost deterministic walkthrough: `make setup`, then `python3 -m brain.server --demo --port 0`. This is fixture sources/fake extractive model with synthetic identity switching. Its printed loopback address is separate from the native 49161 instance. [Runbook](RUNBOOK.md) contains detailed existing procedures; dated claims below its current section are historical.

## Five-scene worked demonstration

| Scene | What to show and say | Evidence mode and honest boundary |
|---|---|---|
| S-01 unified query | Ask unchanged Q1: “What is the latest approved mitigation for the payment incident?” Show supported approved measures and scoped unknown ordering. If synthesis blocks, preserve the failure banner and inspect the current runbook source excerpt; do not describe this evidence-only result as a successful summary. Ask unchanged Q2: “For payment-service, which code fix is complete, which preventive work remains in progress, and is general customer release approved?” Show Done/In Progress and pilot/GA distinction; open current citations. | Current low-review Q1 contains runbook actions and unknown-order notice; Q2 and pilot/GA scope accepted once each. These are agent HTTP results, not current browser/真人 acceptance. Historical Q1 failures remain. eng_b is an engineering reader, not a product_ops impersonation. |
| S-02 freshness | Use existing saved creation/update records, show old version, publication and new version timestamps. Open the saved fixture content-update case in `evidence/runs/lifecycle-local/results.json`: compare `prior_answer`, `old_history_export_projection`, `old_preview`, `sync` and `after_sync_answer`. This is a CLI-produced replay; the web page has no source-update control. | Native four-source history: [targeted closeout](../evidence/runs/targeted-closeout-20261008/); some results used restart/fake recovery, not continuous freshness. This round authorizes no source edits. |
| S-03 no access | In fixture mode choose contractor; ask for the security incident report and show generic refusal without confirming existence, title or hidden count. Contrast an allowed product question. Show historical native C-03 deny evidence separately. | Fixture role contrast; native historical [restricted evidence](../evidence/runs/native-restricted-fixed/). Full native persona matrix remains incomplete. |
| S-04 revocation | Replay existing native same-session Slack removal/restore evidence with old citation/History unavailable; open the saved fixture revoke case in `evidence/runs/lifecycle-local/results.json` and show old History/preview denial and the subsequent answer. This is a CLI-produced replay, not a page control. | [Native historical revocation](../evidence/runs/synthesis-native-revocation/); no new native revocation authorized. A replay must be labelled historical, fixture demonstration must be labelled fake. |
| S-05 audit | Open scoped Audit explorer in fixture mode, find the demonstrated question and show candidate → allowed/denied → model attempt/usage → final answer. Show the actual saved verifier outcomes in `evidence/runs/audit-mixed/verification.json`. If executing a fresh CLI audit demo, use `make verify-audit-mixed AUDIT_OUTPUT=.runtime/team-review-NEW` with a new directory; it uses fixture sources and a fake model and preserves existing records. Never treat prepared output as a command just executed. | [Mixed audit walkthrough](SAFETY_REVIEW.md), [independent verifier](CODEBUDDY_AUDIT_DELIVERY.md). Local test auditor/key custody; no production independent custody claim. |

## Evidence to show, without score inheritance

The material package includes the five fixture scene snapshots, the fixture lifecycle report and the mixed-audit verifier report, each retaining its recorded commit, mode and limitations. They are saved replay evidence, not new page observations or reviewed-excerpt answer-quality results. The full source archive is a companion for linked historical records and implementation.

| Evidence | Recorded result | Claim boundary |
|---|---|---|
| Prior native synthesis Q2 | Complete factual answers at 26.45s and 26.00s | Older synthesis builds; current verbatim-source candidate still needs its own result |
| Pre-candidate native Q1 diagnostic | 21.54s; synthesis rejected; source continuation only | Failure retained; not a successful mitigation answer |
| Reviewed-source candidate Q1 | Two original-question submissions omitted C01; coverage review blocked both | Failed; source continuation is not a successful answer |
| Current local integration | 485 tests in25.091s after failure-restoration fix; related Node checks passed | Offline/mock; first full-run failure retained separately |
| Original delivery allowance | 12 submissions, 17 model calls, USD0.016143 conservative new settlement | Exhausted and retained; not a provider invoice |
| Current preserved AUTH033 cost baseline | 9 submissions/8 calls; USD0.024688 new settlement, no new unknown | USD0.10/newunknown stop retained; no reset |
| Source-review v2 / disabled | Review accepted but omitted C01 operational actions | Business failure, not a successful Q1 |
| Current low-review Q1 | Runbook timeout-budget check and approved failover procedure; ordering not inferred; 66.14s | One genuine result, no repeatability claim; [result](../evidence/runs/first-question-diagnostic-20261011/low-result.json) |
| Current low-review Q2 / scope | Done/In Progress/pilot versus GA;40.37s /44.17s | One result each, not broad quality acceptance |
| Current Q1 History / C01 preview | Current access/version checks passed and exact content retained | Native HTTP; no browser or human inference |
| Recent → Workspace | Earlier actual Chrome restored saved Q2 with timer hidden and Ask enabled; new failed-run precedence fixed locally | Post-restart Chrome reload blocked; no bypass, not G1 |
| Human benefit | Not measured | No time-saved or business ROI claim |

## Seven-minute video script (English UI/narration)

| Time | Narration and shot | Recording requirement |
|---|---|---|
| 0:00–0:40 | “At three in the morning, an engineer needs the incident context. A product colleague needs to know what can be offered today. Both need evidence they are allowed to read.” Cover → workspace. | Show synthetic-data and runtime labels. |
| 0:40–2:25 | “This question stands on its own. The workspace reports actual elapsed time and recorded stage outcomes, then releases reviewed source passages only if validation succeeds.” Ask original Q1; explain approved actions and chronology limitation. Ask original Q2; open citations. | Record actual current outcomes. Keep failures visible; label any waiting-time edit. No fake answer overlay. |
| 2:25–3:10 | “Refreshing reconnects to the same run; it does not buy another answer. Recent lists our questions; History checks current access before retrieving a saved answer.” Demonstrate wait/refresh, saved answer and preview. | Reserve current human submissions; after completed question use read-only History/preview. |
| 3:10–4:25 | “Source content and access change separately. This labelled replay shows update and revocation protection.” Show S-02/S-04 existing native records; switch to clearly labelled fixture for deterministic lifecycle walkthrough. | No external source writes this round; disclose history and fixture/fake mode on screen. |
| 4:25–5:00 | “A denied question does not reveal whether a restricted report exists.” S-03 fixture role contrast. | Do not reveal private report titles as application output. |
| 5:00–5:50 | “Audit reconstructs identity, source decisions, calls and the final answer. CodeBuddy built the independent checkpoint verifier.” S-05 audit and tamper-copy result. | Use actual command result and genuine CodeBuddy screenshots, not recreated evidence. |
| 5:50–6:35 | Architecture diagram: session → local retrieval → native checks → code-constructed source quotes → native checks/review → final checks → answer/history; audit alongside. Explain same-model review limitations and readonly boundary. | Use current architecture; distinguish polling from continuous connection. |
| 6:35–7:00 | “Our working prototype is synthetic and loopback only. These are the remaining quality and human acceptance limits. We measure useful grounded answers, time and cost before claiming impact.” End on actual result/limit card. | Team verifies final playable 5–8 minute video, then G2 approves materials. |

## Remaining decisions, grouped

1. Team observes current core answers, refresh, preview/History and safety walkthrough, recording real G1 judgement.
2. Team records the video and reviews private CodeBuddy conversation/screenshots for submission disclosure.
3. Team approves final wording/version under G2 and explicitly authorizes push/merge and contest submission. Public deployment is a separate decision.

Unsupported formats (Google Docs/OCR/all attachments/DM), full native persona/child-resource coverage, stable freshness statistics, SSO and independent production audit custody remain limitations. They do not silently become completed claims or block preparation of the rest of this candidate.
