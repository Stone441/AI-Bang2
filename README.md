# AI-Bang2


## ContextLedger · local synthetic prototype

Tencent Cloud AI CAN DO IT Hackathon / Aspire **The Internal Brain**.
The original project documents remain under `docs/01–05`. Implementation status: [STATUS](docs/STATUS.md).

```sh
make setup                 # Python >= 3.11, standard library only
make test                  # includes real loopback HTTP integration tests
make demo                  # http://127.0.0.1:8080 — explicit synthetic mode
make verify                # execute five scenario subsets and write evidence
make test-report           # machine-readable actual test report
```

No runtime credentials, outbound model requests, or paid services are used. Select one of six synthetic identities in the local UI. Answers are dynamic source excerpts from an explicitly **fake extractive model**, not live LLM synthesis. Four fixture adapters are not four live integrations.

[Run and demo guide](docs/RUNBOOK.md) · [Actual architecture](docs/IMPLEMENTED_ARCHITECTURE.md) · [CodeBuddy task](docs/CODEBUDDY_TASK.md) · [Acceptance coverage](docs/ACCEPTANCE_STATUS.md)

Do not expose this server publicly. Production authentication, live source permissions, runtime models, independent signed audit checkpoints and G1/G2 remain incomplete. No remote push or deployment has been performed.
