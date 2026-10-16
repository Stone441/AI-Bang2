# ContextLedger — The Internal Brain

**Team:** AI Bang2

**Track:** FinTech / Aspire

**Short blurb:** Permission-aware enterprise answers with evidence and audit trails.

## Project description

Engineers investigating incidents and product colleagues checking release readiness often need information scattered across Confluence, Jira, Slack and Google Drive. ContextLedger brings those sources into an evidence-first workspace: ask a business question, inspect its supporting passages and versions, and trace how access was checked. The prototype uses fictional payment-service materials in dedicated test containers, not Aspire internal data.

Three business entry points cover release readiness, delivery planning and customer impact. Answers organize supported conclusions and missing information by subquestion. Exact quotes, source previews and versions help users check the basis of a decision; saved answers are reauthorized rather than treated as an implicit conversation.

Read-only Python adapters feed a versioned SQLite index. Bounded lexical/BM25 retrieval and a bilingual glossary select exact evidence windows. Server-verified sessions and application policy narrow access; native permission and version checks run before model input and final delivery. Unknown permission cannot pass. Shared collection credentials are not represented as independent employee identities.

Runtime prompts ask DeepSeek Flash to preserve scope, uncertainty, false premises and unresolved conflicts, and to support conclusions with exact quotations. Strict output checks and a separate model review assess the draft. Review can fail or miss errors, and full semantic acceptance has not passed. An additional isolated-quotation experiment is not enabled in the hosted demonstration.

Audit records retain identity, question, resource decisions, evidence, model receipts and outcome. Tencent CodeBuddy implemented the independent offline audit-chain and Ed25519 checkpoint verifier, with twenty component tests and traceable original commits. Its local checkpoint custody is not independently operated production audit storage. An isolated fixture lab demonstrates version updates, revocation and audit inspection without modifying live sources.

Automated tests exercise application, authorization and UI contracts; their counts are not semantic accuracy scores. Four native integrations have bounded live evidence, with synthetic roles and explicit resource scopes. No production SSO, complete employee ACL matrix, stable latency SLA, prompt-injection immunity or customer ROI is claimed. The intended impact is less time finding and verifying answers; a controlled task-time and decision-quality study remains future work.

The result is an inspectable enterprise-knowledge prototype with explicit trust boundaries, useful source access and reproducible verification.

## Reviewer resources

- [Project demonstration video (7m 32s, English narration and captions)](https://youtu.be/BULowhVNfU8)
- [Hosted demonstration](https://contextledger.hellokyleshi.com)
- [Complete source repository](https://github.com/Stone441/AI-Bang2)
- [Cover image, 1600×900](../assets/submission/contextledger-cover.png)
- [Architecture PNG](../assets/submission/contextledger-architecture.png) · [SVG](../assets/submission/contextledger-architecture.svg) · [Trust boundaries and tradeoffs](IMPLEMENTED_ARCHITECTURE.md)
- [Five-scenario demonstration guide](DEMO.md)
- [CodeBuddy contribution](CODEBUDDY_CONTRIBUTION.md)
- [Validation and limitations](VALIDATION.md)

**Availability:** The hosted demo runs on a team member's Mac and may be unavailable while that computer is asleep or offline. If the website cannot be opened during evaluation, [contact Team AI Bang2 (shuyi013@e.ntu.edu.sg)](mailto:shuyi013@e.ntu.edu.sg?subject=ContextLedger%20demo%20access) to arrange access, or watch the video above.

The original CodeBuddy conversation and at least three genuine development screenshots are separate competition attachments retained locally for reviewed disclosure. The video distinguishes a live question using native APIs and synthetic business data from controlled fixture scenarios. This document does not attest that a competition form has been submitted.
