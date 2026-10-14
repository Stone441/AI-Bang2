# ContextLedger — reviewer quick start

These are fictional demo people with individually configured access; job titles do not imply shared access for all employees.

## Try the application without external accounts

Install Python 3.11 or newer, clone the approved repository/version, and run from its root:

```sh
python3 -m scripts.reviewer_demo --accounts --open
```

On Windows, use `py -3` in place of `python3`. No additional Python packages, platform accounts or API keys are required. The terminal prints the local URL and the path to private login cards. Sign in as `engineer_blair`, `product_morgan`, or `partner_jordan` with its generated password. Keep the terminal running; Ctrl+C stops it. Accounts expire after seven days.

This is **synthetic data with a fake extractive model**, not a live-model quality or latency demonstration. The three accounts map to different server-enforced fixture identities. Ask the same incident question under each account and compare citations. Open a citation and Recent answers, then sign out before changing accounts.

## Real four-source / live-model demonstration

The team operates a separate approved live integration with Confluence, Jira, Slack and Google Drive, using synthetic demo materials. The live demo provides engineer, product and partner application accounts. They use the team’s approved native connection, intersected with server-enforced role resource lists; these are not three independent native employee accounts. Product can access selected capability/release/work-item/operations documents, while partner is limited to the explicitly shared capability page. The hosted team trial is available at https://contextledger.hellokyleshi.com while the owner’s Mac is online.

Obtain demo credentials privately from the team; reviewers do not need to configure the four source platforms. Shared role accounts identify the demo account, not the individual person using it. Individual accounts can be issued when per-reviewer history isolation is required.

The model may quote correct source passages without explicitly correcting an unsupported premise in the question. This disclosed competition-prototype limitation is accepted by the project owner. Measured response times and validation boundaries are in the [final handoff](FINAL_HANDOFF.md).

Never publish passwords, API keys, OAuth grants, local databases or private development conversations in the repository.
