# AI-Bang2

## Try it / 组员与评委快速体验

Requires Python 3.11+. From the repository root, run:

```sh
python3 -m scripts.reviewer_demo --accounts --open
```

Windows: use `py -3` instead of `python3`. This opens a local **synthetic-data / fake-model** demo: no platform accounts, API keys, dependency installation or model charges. It does not reproduce the live model's answer quality or latency. Keep the terminal open; press Ctrl+C to stop.

[中文接入说明与评审安排](docs/REVIEWER_ACCESS.md) · [English reviewer quick start](docs/REVIEWER_QUICKSTART.md) · [当前最终交接](docs/FINAL_HANDOFF.md)

Real four-source / live-model team trial: **https://contextledger.hellokyleshi.com**. Request a demo account privately from the team; no local setup is required. The service is hosted on the project owner’s Mac and depends on that computer staying online. It uses approved synthetic materials in real Confluence, Jira, Slack and Drive, with per-account application permissions intersected with the team connection’s native access. Never commit credentials or login cards.


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
