# ContextLedger · submission text

13 October demo account update: engineer, product and partner are server-authenticated application personas. Their explicit resource policies are intersected with the team connection's current native permissions. All three can use the live-source demo; this does not demonstrate three independent native employee identities. The live model and original permission/version checks remain unchanged. See [reviewer access](REVIEWER_ACCESS.md).

Updated 13 October 2026. Local submission draft, not uploaded or team-approved. Final delivery work is tracked in [the closeout checklist](reviews/2026-10-13-final-delivery/README.md). The previous description and its dated results are preserved in [the prior snapshot](reviews/2026-10-13-final-delivery/prior-SUBMISSION_CANDIDATE.md).

## Copy-ready fields

**Project title:** ContextLedger — The Internal Brain

**Short blurb (8 words):** Permission-aware enterprise answers with evidence and audit trails.

**Project description:**

Engineers investigating an incident and product teams checking release readiness need answers scattered across Confluence, Jira, Slack and Google Drive. ContextLedger brings these sources into one independent-question workspace, with evidence that users can inspect and an audit record of how each answer was produced. The competition prototype uses fictional payment-service material, not Aspire internal data.

The engineering question asks which mitigation is supported by current evidence. The product question distinguishes completed code, preventive work still in progress and the approval boundary between a controlled pilot and general availability. These distinctions matter: a completed Jira issue is not permission to promise a general release, and an old proposal is not necessarily the current approved action. The interface exposes citations and uncertainty rather than hiding those distinctions.

A server-verified session supplies identity. Local permission prefiltering narrows retrieval, then native source APIs check current access, content and versions before evidence reaches the model and before the answer is delivered. Collection credentials do not grant employee access. Unknown access cannot pass. Citation previews and saved answers receive current checks too; a saved answer is not a permanent permission grant. Incremental background discovery publishes completed source updates, retaining source-specific identities and mappings.

Retrieval combines lexical ranking, explicit source relationships and structure-preserving evidence windows. Headings, lists, tables and nearby qualifications remain attached where supported by the window rules. Short documents can remain whole. The selected model path is DeepSeek Flash with disabled reasoning and one review call. Its prompt asks the model to select evidence passage aliases and report selection safety and question coverage through a strict JSON contract. The server reconstructs selected passages from exact source text, splits long quotations at readable boundaries, validates IDs and quotes, and applies a bounded required-action coverage check. The model cannot invent citation URLs or confer permissions. This produces reviewed source answers; it is not a claim of unrestricted free-form synthesis or a universal semantic correctness guarantee.

The implementation uses Python, SQLite, native read-only source adapters and a browser workspace. Bounded connection reuse and up to four native reads per source reduce repeated network overhead. The selected delivery configuration serializes independent queries while allowing native reads within a query to overlap. Experimental request isolation is not part of the selected delivery configuration. Model admission retains durable usage receipts, conservative cost reservations and a stop on new unknown usage. There are no automatic paid retries.

Audit records retain identity, question, per-resource decisions, evidence, model attempts and usage, and final answers. CodeBuddy made a real implementation contribution: an independent hash-chain and Ed25519 checkpoint verifier. It distinguishes anchored records from unsigned tails. A local hash chain without an independently held checkpoint does not prove resistance to a compromised host.

Measured results for the frozen structured-v2 baseline include six single-query native HTTP answers in 6.48–9.90 seconds and two three-request groups with slowest responses of 26.92 and 24.91 seconds. All twelve native answers passed the fixed business-fact checks. These are small, authored-case observations, not browser-render measurements, blind accuracy estimates or a production SLA. Earlier failures remain recorded. Explicit correction of a false premise remains a wording limitation: the passages distinguish withdrawn and accepted states, but may leave that distinction for the reader to interpret. A four-call attempt at automatic premise labels was rejected after semantic failures. The project owner accepted this disclosed limitation for the competition prototype on 13 October; it remains unfixed. The three-second goal was not achieved; final delivery now prioritizes correctness, usable waiting behavior and recovery. The selected final build subsequently returned Q1/Q2 in 13.26/9.60 seconds and a queued three-request group in 9.14/22.11/28.64 seconds, retaining the required core facts. Browser acceptance, human benefit and final team sign-off are separate, unfinished checks.

The prototype demonstrates a practical way to make enterprise answers inspectable while preserving current source access. Production SSO, independent audit-key custody, arbitrary document formats, all attachments and direct messages, and broad native permission-matrix coverage remain outside demonstrated scope. No quantified ROI or real-customer adoption is claimed.

## Submission artifacts and disclosure

| Requirement | Prepared artifact | Boundary |
|---|---|---|
| SUB-01/02 | Title and 8-word blurb above | Team final wording approval pending |
| SUB-03 | Description above; [implemented architecture](IMPLEMENTED_ARCHITECTURE.md); prompts in `brain/synthesis.py` | Selected source frozen; final human wording approval pending |
| SUB-04 | [DEV09 manifest](../evidence/tool-usage/dev09-manifest.json); private conversation-history.zip | Genuine local evidence, upload not authorized |
| SUB-05 | [Cover PNG](../assets/submission/contextledger-cover.png), 1600×900; [SVG](../assets/submission/contextledger-cover.svg) | Exact 16:9; official recommended 380×216 differs slightly in ratio |
| SUB-07 | DEV09 genuine screenshots 01-task-start, 04-code-writing, 07-final-validation | All 15 original artifacts verified against hashes on 13 October; human disclosure review pending |
| Aspire architecture/source/demo | [Architecture SVG](../assets/submission/contextledger-architecture.svg), repository, [demo script](DEMO_CANDIDATE.md) | Diagram refreshed and visually checked; source frozen; no push/merge/submission |
| Optional video | Seven-minute narration in demo script | No new video is represented as recorded |
| Optional public link | None | Loopback is not a public deployment |

The official checklist is [01 section 8](01_OFFICIAL_BRIEF.md). Submission date in provided materials is 16 October; cutoff time and some access/format details remain unspecified. This draft does not change official requirements or authorize disclosure.
