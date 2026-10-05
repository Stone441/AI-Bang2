# Approved product-reader preparation — local verification

2026-10-06. AUTH-016 approves the specified Confluence-only product_ops token and app-owned Keychain persistence. Native credentials and permission acceptance remain not_run; no real product_ops Keychain item was created during these tests.

Single Confluence operator now supports explicit macos-keychain mode. A saved value is reused without TTY prompts; a newly entered value is checked against the actual native current-user account before saving. Wrong identity or OS denial stops without persistence/fallback. Other single-source Keychain modes remain unavailable. Its SQLite path is isolated by actor/tenant/native-account digest and actual file mode 0600.

32 targeted tests and 307 final full tests passed. An earlier test-package invocation failed to resolve a preexisting sibling import; the observed error is summarized in verification.json. Correct test discovery/PYTHONPATH was used without deleting any assertion. The intermediate 306-test run is retained separately; one additional real CLI/database-isolation test was added afterward and final full-tests-final.log is authoritative.

The dedicated ignored config and nonsecret example contain only product_ops and the three explicit synthetic Confluence pages. Existing multi-source configuration and 8094 are untouched. Browser is left at the user's login handoff; token final creation/security verification are user-operated. Startup command and the still-pending native acceptance are in docs/PRODUCT_READER_PILOT.md.

No native API, real Keychain secret, model request, paid resource, new platform grant or human acceptance was used in the tests. This is not native product persona verification or a newly validated clean archive/browser experience.
