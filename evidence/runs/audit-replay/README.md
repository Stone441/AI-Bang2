# Audit reconstruction and signed-boundary replay

Run `python3 -m scripts.audit_replay_acceptance`. This imports a copy of the actual synthetic live product pilot audit into an in-memory store, performs the supported natural-language inquiry under an explicit local test auditor, and checks stable pagination against concrete event IDs. The normal reader is denied audit access. `inquiry.json` includes the query filters, actual events and oracle.

`verification.json` records seven actual executions of the existing CodeBuddy-contributed independent verifier. Full checkpoint rejects body modification, middle deletion, covered-tail deletion and internally recomputed replacement; original verifies. Prefix checkpoint identifies the unsigned tail and accepts its removal, honestly demonstrating that boundary. Original events were hash-compared unchanged.

The signer used a disposable same-machine Ed25519 key generated in an ignored temporary runtime directory; the private key was deleted when the run ended. Only test public key and checkpoints are retained. This is NOT independent operational key custody, native auditor authentication, production database-role isolation or the complete S-05 mixed success/deny/failure oracle. No source API or model calls. The verifier contribution remains attributed to its actual CodeBuddy history, not to this new Codex runner.
