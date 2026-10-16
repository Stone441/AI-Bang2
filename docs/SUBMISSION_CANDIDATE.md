# ContextLedger · submission fields · 16 October 2026

Submission-ready wording for the team's final review. Source release and runtime boundaries: [FINAL_HANDOFF](FINAL_HANDOFF.md). This is a prototype with disclosed limitations, not a claim that the full semantic acceptance goal passed.

**Project title:** ContextLedger — The Internal Brain

**Short blurb (8 words):** Permission-aware enterprise answers with evidence and audit trails.

**Project description:**

Engineers investigating incidents and product colleagues checking release readiness often need information scattered across Confluence, Jira, Slack and Google Drive. ContextLedger brings those sources into an evidence-first workspace: ask a business question, inspect its supporting passages and versions, and trace how access was checked. Our prototype uses fictional payment-service materials in dedicated test containers, not Aspire internal data.

The interface provides three business entry points: release readiness, delivery planning and customer impact. Answers can distinguish supported facts from missing information, while source previews preserve context. Top navigation, saved-answer access and a responsive evidence drawer support review without turning each question into an implicit conversation.

Python read-only adapters feed a versioned SQLite index. Local lexical/BM25 retrieval, exact windows and a bounded bilingual glossary select evidence. Server-verified sessions and application policy narrow access; native permission and version checks run before model input and final delivery. Unknown permission does not pass. Saved answers and source previews are checked again. Shared collection credentials are not represented as independent employee identities.

Prompts ask DeepSeek Flash to organize supported conclusions by subquestion, quote exact passages and preserve scope, uncertainty, false premises and unresolved conflicts. Strict output validation and a separate full-source review reject unsupported drafts. An experimental additional path reviews each claim using only its selected quotations, then retains the full-source review. In a real two-case diagnostic it rejected an incomplete quote and accepted the complete quote. Its subsequent end-to-end acceptance run stopped on the first question when another claim was rejected; the remaining ten questions were not run. Reliable semantic synthesis across the full test set is therefore not claimed.

Audit records retain identity, question, resource decisions, evidence, model receipts and final outcome. CodeBuddy made a documented implementation contribution to an offline hash-chain and Ed25519 checkpoint verifier. Local verification is not independently managed production audit custody. An isolated fixture lab demonstrates content updates, version invalidation, revocation and audit inspection without modifying live sources.

The frozen application code passed 800 offline Python tests in an independent clean working directory; historical reports retain their original versions and failures. These are implementation tests, not an answer-accuracy score. Four native source integrations and scoped access checks have live evidence; failure records remain visible. No production SSO, comprehensive employee permission matrix, prompt-injection immunity, stable latency SLA, customer adoption or quantified ROI is claimed. Embeddings were not added: a small 27-case lexical retrieval study did not demonstrate a necessary-evidence gap, and no genuine embedding comparison was completed.

The result is an inspectable enterprise-knowledge prototype with explicit trust boundaries, useful source access and a reproducible record of both progress and remaining limitations.

## Upload references

- Cover: [1600×900 PNG](../assets/submission/contextledger-cover.png), exact16:9.
- Architecture: [SVG](../assets/submission/contextledger-architecture.svg), including trust boundaries and experimental path.
- Source: reconciled local source ZIP identified in [final reconciliation](reviews/2026-10-16-final-check/REPORT.md). Existing repository: https://github.com/Stone441/AI-Bang2 . Latest candidate commits are **not yet published there**.
- Genuine CodeBuddy proof: all15 originals were found in the main working directory and SHA256-verified on16October; a private local upload bundle is prepared. It includes conversation history and7 genuine process screenshots. It is not uploaded or included in the source ZIP.
- Demo: [version-aware walkthrough](reviews/2026-10-16-final-check/DEMO.md). Existing user trial remains its frozen delivered UX; the experimental backend is not silently enabled.
- Optional5–8 minute video: not produced. Do not enter an invented video URL.
- External/public URL: only use a verified existing service after team review; local127.0.0.1 is not an external demo link.

Official source remains [01 section8](01_OFFICIAL_BRIEF.md). Final team sign-off and external source publication/upload/submission remain separate from preparing these materials.
