# Local retrieval windows evidence

Run `make verify-retrieval` to reproduce five authored cases. `results.json` records actual evidence, exact offsets, request IDs, source hashes and an unsigned audit-chain check. Fixture sources and fake model only; no external API, model or credential use.

The unknown-vocabulary case intentionally has no result. The entity-fallback case matches Orion alone, not the meaning of its other words. These examples are not a held-out semantic benchmark.

Ten additional unittest methods cover late content, exact preview, stale versions/deletion/revocation, same-history protection, restricted neighboring resources, forged offsets, unknown authority, dispatch-time changes and the unchanged synthetic marker guard. Full results are in `../local-latest/tests.json`; scenario and lifecycle records remain separately labeled local subsets.

Initial targeted commands failed because unittest module invocation omitted the tests import path, then because the sandbox denied a loopback bind. `initial-test-errors.json` records those failures; unchanged HTTP assertions passed during the explicitly authorized local regression.
