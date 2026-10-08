# Native freshness: one specific source write awaiting approval

Scope: create exactly one page in the existing AUTH-017 Confluence space `131227`, using the already approved owner management UI. The product and CLI remain eng_b read-only; no new OAuth scope, account, model charge, service restart, or change to 8094/8100. AUTH-021's completed one-time seed/change sequence is not reused.

Title: `[SYNTHETIC] PERF-20261008 automatic discovery probe`

Exact body:

```text
[SYNTHETIC]
PERF-20261008 automatic discovery probe.
This local hackathon test page says the approved probe value is copper.
It contains no customer or employee data and establishes no business release approval.
```

Measurement: before creation, start an isolated CLI background reader with the fixed `cdbd62b` code and original AUTH-017 mappings; obtain baseline complete publication. Record owner creation confirmation as an observation time (not exact server commit), the new page's native created/version metadata, automatic listing start, durable publication and first fake-model answer containing the new value. Use the original 60-second successful-cycle minimum and 1-second polling wakeup. Do not manually force discovery, stop polling for query timing, write via product credentials, update/delete existing pages, or claim an SLA. All mode labels remain native_api/fake_model.

Only this creation is requested. No subsequent edits or deletion are authorized by this proposal. Retain this uniquely titled synthetic page; any cleanup requires separate approval.

Current status: `not_run_requires_specific_source_write_approval`. Offline automatic poll evidence exists in `freshness-mock.json`; it is not native timing. This proposal does not authorize execution.
