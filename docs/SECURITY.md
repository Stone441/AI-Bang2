# Security model and deployment limits

ContextLedger is a synthetic-data prototype. Its access checks are implemented in application code; this document describes that boundary and its remaining limits.

## Access and data handling

The server obtains identity from a verified session. Application policy narrows the connected source identity's permissions; collection access alone is not presented as independent employee authorization. Native identity, permission and content-version checks guard evidence before model dispatch and final delivery. Unknown access fails closed. Saved answers, previews and linked evidence are checked again; current readability does not automatically authorize every old version.

Source titles, paths or existence are not released as a substitute for a denied answer. Source links are mapped and allowlisted on the backend. Retrieved text is untrusted input and cannot grant identity, broaden access or turn an audit query into arbitrary SQL. Ordinary users and audit reviewers retain different scopes.

The live demonstration contains fictional payment-service data in explicitly scoped test containers. Runtime source adapters are read-only. Source seeding, permission changes and lifecycle exercises are separate administrative actions, not features of the employee query API.

## HTTP and operating boundary

The demo uses constrained request bodies and deadlines, bounded connection/session/query capacity, login throttling, Host/Origin/CSRF checks, a fixed static-file allowlist and text-based rendering. HTTPS deployment enables Secure/HttpOnly/SameSite cookies and relevant response policies. These controls are not a penetration-test or DDoS-resistance certification.

The existing hosted demo runs on a team member's Mac under that user's normal operating-system account. Cloudflare Tunnel provides ingress routing, **not host-process isolation**. A code-execution vulnerability could reach files and credentials available to the process account. Longer public operation should use an isolated account or dedicated host with narrowly scoped synthetic-data credentials and no personal home-directory access; that migration is not implemented here.

Shared demo credentials are intentionally available on the sign-in page. They are not an abuse barrier. Visitors share the synthetic histories and model allowance, and the configured auditor can inspect the three demonstration identities. Do not enter personal or confidential information.

## Model and budget boundary

The model cannot authorize sources or return trusted URLs. Exact-quote and structural checks reject malformed support, and a separate model review assesses semantic coverage. Review may still be wrong. Full semantic reliability and prompt-injection immunity are not claimed.

Live model calls require approved data and budget. The implementation reserves usage, records receipts and preserves uncertain consumption for review. Existing automatic trial allowances must not be reused as permission for another paid run. The configured model rates and their reference date support local cost estimates; that date does not expire access or stop the service. Actual provider charges may differ from these estimates.

## Audit boundary

Audit records preserve identity, question, evidence, resource authorization and final outcome. Model preparation, dispatch, usage and storage are distinct events. Queries are parameterized and scope restricted.

The independent CodeBuddy verifier checks canonical hashes and Ed25519 checkpoints supplied with a trusted public key. It detects changes within signed coverage; events after that checkpoint remain unanchored. Checkpoint rollback/freshness, independent custody, stream identity and complete host-account compromise require additional production controls. A valid local chain is not proof of an independently secured audit service.

Credentials, private keys, account registries, runtime databases and raw development conversations are excluded from the repository. The native CodeBuddy history and genuine screenshots are separate submission attachments requiring reviewed disclosure.
