# Local setup and verification

## Requirements

- Python 3.11 or newer; the application uses the Python standard library.
- Node.js for standalone frontend tests and the Python-wrapped frontend HTTP test.
- OpenSSL with Ed25519 support for checkpoint tests; local HTTPS tests also use its CLI.

No package installation is needed for the credential-free demo. The current full test suite was exercised on macOS; live credential storage and several operator utilities use macOS Keychain or POSIX APIs, so full Windows parity is not claimed.

## Start the local demo

From the repository root:

```sh
python3 -m scripts.reviewer_demo --accounts --open
```

The server binds loopback on an available port. The terminal prints its URL and the generated private login-card path under `.runtime/reviewer-demo/`. Choose an account from those cards and sign in. Ctrl+C stops the server; generated data remains local and is ignored by Git.

The local demo uses synthetic data and a fake extractive model. It demonstrates application interaction and access boundaries, not live-model synthesis quality. To use a fixture identity selector instead of password accounts, omit `--accounts`.

## Run checks

```sh
python3 -m unittest discover -s tests
python3 -m scripts.competition_check --output .runtime/validation/rehearsal
```

The first command runs the full Python suite, including real loopback HTTP tests and the frontend HTTP lifecycle wrapper. The second runs the five-scenario fixture rehearsal and focused source, permission, UI and audit checks. Choose a fresh output directory on each run; existing results are not overwritten.

Standalone frontend suites can also be run with `node tests/frontend_reviewer_login.js` or the corresponding `frontend_*.js` file. `frontend_http_lifecycle.js` requires a running test server and is normally invoked by its Python test wrapper.

## Explore the fixture lab

```sh
python3 -m scripts.scenario_lab
```

Open the printed loopback URL. Fixed controls demonstrate read → publish a new version → revoke → inspect audit, using a separate in-memory synthetic world and fake model. They do not mutate connected platforms. Ctrl+C stops the lab.

## Native integrations

`config/*.example.json` contains placeholder schemas for the four source readers and a multi-source bundle. Keep reviewed settings and credentials under the ignored `.runtime/` directory. Example flags and a policy identifier are not authorization to access a source or spend money.

`python3 -m brain.operator_web --help` describes native operator options. Native mode requires explicit resource allowlists, verified identity mappings, existing source credentials and a separately approved model budget. The hosted demo's private account registry, OAuth client and budget database are intentionally not bundled. Do not start it by copying a personal deployment command from a historical record.

[Security model](SECURITY.md) · [Validation scope](VALIDATION.md) · [Demonstration guide](DEMO.md)
