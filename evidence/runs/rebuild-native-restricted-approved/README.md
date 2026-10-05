# Clean restricted-acceptance candidate

Commit b541c02, isolated git archive with no .runtime or .env. Setup, 297 Python tests, five fixture scenarios, both Node frontend checks and actual fixture HTTP assets/login/four-source query/exact preview passed. No native sources, model requests or credentials used. The runner stopped its own temporary HTTP service and cleaned its temporary directory.

The first attempt in ../rebuild-native-restricted had 23 HTTP bind EPERM errors under the sandbox. Those logs remain failed. The same commit was rerun with approved local loopback testing; no test or security settings were changed.

This establishes local rebuild/runtime behavior, not browser visual review, complete native personas or G1/G2.
