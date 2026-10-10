# ContextLedger · submission candidate

Prepared 11 October 2026 from main b34a055 plus the current delivery branch. This is a reviewable candidate, not G1/G2 approval or a completed submission. Current runtime results are in [delivery evidence](../evidence/runs/delivery-20261011/); older evidence retains its original build and mode.

## Copy-ready project fields

**Title:** ContextLedger — The Internal Brain

**Short blurb (8 words):** Permission-aware enterprise answers with evidence and audit trails.

**Description:** Engineers handling an incident and product teams checking release readiness need context scattered across Confluence, Jira, Slack and Google Drive. ContextLedger brings these sources into an independent question workspace. Its value is a useful, verifiable answer with visible uncertainty, source versions and a record of how it was produced.

The prototype reads explicitly approved synthetic competition material through native source APIs. A verified server session selects the operator identity; collection credentials never grant an employee additional access. Local retrieval selects version-bound evidence, and current native access and content checks protect model dispatch, review, delivery, citation previews and saved answers. Missing or unknown access cannot grant permission. Incremental background discovery publishes completed source updates; it is polling with bounded operational checks, not a claim of continuously connected sources or a production freshness SLA.

DeepSeek Flash generates structured claims using supplied evidence only. The generation prompt preserves business object, approval/completion state, pilot versus GA, dates and applicable scope. The server checks evidence IDs and exact supporting quotes. A separate call to the same provider checks semantic support and question coverage. If a known-usage model output is rejected, the delivery instance may show an explicit synthesis failure alongside unchanged source passages after final current-access/version checks. This is evidence-only partial utility, not an accepted summary; source/usage unknowns never use this continuation. True but unnecessary background can be removed only when remaining conclusions retain every critical limitation and stand independently; unsupported or uncertain conclusions stop the answer. Same-model review remains fallible and is not an independent security authority.

The interface shows elapsed time and observed phases, classified failures, runtime and recent source checks, current-access citation previews, Recent summaries and explicit History retrieval. Refresh can reconnect to the current session's run without another model call. Expired sessions and server restarts have distinct limitations. The product has independent questions, with no chat context inheritance or answer download.

Audit records preserve actor, question, per-resource decisions, model attempts and usage, citations and final answer. The real CodeBuddy contribution independently verifies audit hash chains and Ed25519 signed checkpoints. An unanchored chain and an unsigned tail remain explicitly untrusted; local key custody does not prove production resistance to a compromised host.

Measured impact is reported as individual native request times, actual model usage/cost, current validation and observed limitations, not projected savings or a fabricated success percentage. The broad mitigation question has failed on previous builds and must be demonstrated on the current candidate before calling the core product complete. The test world is fictional; it is not Aspire internal data.

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
| Aspire live demo / architecture / source | Five scenes below, architecture and current repository | G1/G2 review; explicit push/merge and submission approval |

The 15 existing DEV09 artifacts were checked against their recorded hashes this round. Real contribution: original `4165ee6`, integration `8cd5088`; implementation and historical validation in [CodeBuddy delivery](CODEBUDDY_AUDIT_DELIVERY.md). No new CodeBuddy contribution is claimed.

## Start and use

Native team trial uses `打开试用页面.command` after this task's 49161 service and private entry are prepared. It checks the expected operator service; it does not submit a question. Entry tickets last ten minutes, sessions one hour. Refresh within a valid session resumes its run. If the session/entry has expired, obtain a fresh entry; restarting does not recover the old in-memory failure receipt. Successful stored answers remain subject to current History authorization/version checks.

Operator command: `python3 -m scripts.delivery_trial` for at most nine automated submissions, then normal stop of the owned idle process and `python3 -m scripts.delivery_trial --human` for the remaining three or more. Both modes share the new independent durable state and original USD20 ledger. Startup requires same-day `python3 -m scripts.model_readiness`, original native accounts/containers and available budget. Never reset trial state to regain attempts. The current script explicitly selects disabled thinking / 8192 / ranking none. Old low8192 configuration is retained in the historical launcher and b34a055.

For a no-provider-cost deterministic walkthrough: `make setup`, `make verify`, `python3 -m brain.server --demo --port 0`. This is fixture sources/fake extractive model with synthetic identity switching. Its printed loopback address is separate from the native 49161 instance. [Runbook](RUNBOOK.md) contains detailed existing procedures; dated claims below its current section are historical.

## Five-scene worked demonstration

| Scene | What to show and say | Evidence mode and honest boundary |
|---|---|---|
| S-01 unified query | Ask unchanged Q1: “What is the latest approved mitigation for the payment incident?” Show supported approved measures and scoped unknown ordering. If synthesis blocks, preserve the failure banner and inspect the current runbook source excerpt; do not describe this evidence-only result as a successful summary. Ask unchanged Q2: “For payment-service, which code fix is complete, which preventive work remains in progress, and is general customer release approved?” Show Done/In Progress and pilot/GA distinction; open current citations. | Current candidate native + live model needs actual results. Historical Q1 failures remain. eng_b is an engineering reader, not a product_ops impersonation. |
| S-02 freshness | Use existing saved creation/update records, show old version, publication and new version timestamps. In an isolated fixture demonstration update the runbook using the existing fixture admin procedure; old preview/History refuse stale versions, new query uses new content. | Native four-source history: [targeted closeout](../evidence/runs/targeted-closeout-20261008/); some results used restart/fake recovery, not continuous freshness. This round authorizes no source edits. |
| S-03 no access | In fixture mode choose contractor; ask for the security incident report and show generic refusal without confirming existence, title or hidden count. Contrast an allowed product question. Show historical native C-03 deny evidence separately. | Fixture role contrast; native historical [restricted evidence](../evidence/runs/native-restricted-fixed/). Full native persona matrix remains incomplete. |
| S-04 revocation | Replay existing native same-session Slack removal/restore evidence with old citation/History unavailable; in isolated fixture use existing revocation walkthrough and show subsequent query does not reuse old access. | [Native historical revocation](../evidence/runs/synthesis-native-revocation/); no new native revocation authorized. A replay must be labelled historical, fixture demonstration must be labelled fake. |
| S-05 audit | Open scoped Audit explorer in fixture mode, find the demonstrated question and show candidate → allowed/denied → model attempt/usage → final answer. Run existing CodeBuddy verifier against a prepared signed copy; show an altered copy rejected and unsigned tail explicitly labelled. | [Mixed audit walkthrough](SAFETY_REVIEW.md), [independent verifier](CODEBUDDY_AUDIT_DELIVERY.md). Local test auditor/key custody; no production independent custody claim. |

## Seven-minute video script (English UI/narration)

| Time | Narration and shot | Recording requirement |
|---|---|---|
| 0:00–0:40 | “At three in the morning, an engineer needs the incident context. A product colleague needs to know what can be offered today. Both need evidence they are allowed to read.” Cover → workspace. | Show synthetic-data and runtime labels. |
| 0:40–2:25 | “This question stands on its own. The workspace reports actual elapsed time and observed phases, then releases only validated claims.” Ask original Q1; explain approved actions and chronology limitation. Ask original Q2; open citations. | Record actual current outcomes. Keep failures visible; label any waiting-time edit. No fake answer overlay. |
| 2:25–3:10 | “Refreshing reconnects to the same run; it does not buy another answer. Recent lists our questions; History checks current access before retrieving a saved answer.” Demonstrate wait/refresh, saved answer and preview. | Reserve current human submissions; after completed question use read-only History/preview. |
| 3:10–4:25 | “Source content and access change separately. This labelled replay shows update and revocation protection.” Show S-02/S-04 existing native records; switch to clearly labelled fixture for deterministic lifecycle walkthrough. | No external source writes this round; disclose history and fixture/fake mode on screen. |
| 4:25–5:00 | “A denied question does not reveal whether a restricted report exists.” S-03 fixture role contrast. | Do not reveal private report titles as application output. |
| 5:00–5:50 | “Audit reconstructs identity, source decisions, calls and the final answer. CodeBuddy built the independent checkpoint verifier.” S-05 audit and tamper-copy result. | Use actual command result and genuine CodeBuddy screenshots, not recreated evidence. |
| 5:50–6:35 | Architecture diagram: session → local retrieval → native checks → generation → native checks/review → final checks → answer/history; audit alongside. Explain same-model review limitations and readonly boundary. | Use current architecture; distinguish polling from continuous connection. |
| 6:35–7:00 | “Our working prototype is synthetic and loopback only. These are the remaining quality and human acceptance limits. We measure useful grounded answers, time and cost before claiming impact.” End on actual result/limit card. | Team verifies final playable 5–8 minute video, then G2 approves materials. |

## Remaining decisions, grouped

1. Team observes current core answers, refresh, preview/History and safety walkthrough, recording real G1 judgement.
2. Team records the video and reviews private CodeBuddy conversation/screenshots for submission disclosure.
3. Team approves final wording/version under G2 and explicitly authorizes push/merge and contest submission. Public deployment is a separate decision.

Unsupported formats (Google Docs/OCR/all attachments/DM), full native persona/child-resource coverage, stable freshness statistics, SSO and independent production audit custody remain limitations. They do not silently become completed claims or block preparation of the rest of this candidate.
