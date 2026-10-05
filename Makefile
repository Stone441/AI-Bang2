.PHONY: test demo verify verify-lifecycle verify-retrieval verify-audit-mixed setup live live-synthesis
LIVE_PORT ?= 8088
AUDIT_OUTPUT ?= .runtime/audit-mixed-review
setup:
	python3 -c "import sqlite3; import sys; assert sys.version_info >= (3, 11); print('Standard-library runtime ready')"
test:
	python3 -m unittest discover -s tests -v
demo:
	python3 -m brain.server --demo
verify:
	python3 -m scripts.evaluate
verify-lifecycle:
	python3 -m scripts.lifecycle_acceptance
live:
	python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port $(LIVE_PORT) --live --model deepseek --credential-store macos-keychain
live-synthesis:
	python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port $(LIVE_PORT) --live --model deepseek --credential-store macos-keychain --answer-style synthesis
test-report:
	python3 -m scripts.test_report

verify-retrieval:
	python3 -m scripts.retrieval_acceptance

verify-audit-mixed:
	python3 -m scripts.audit_mixed_acceptance --output $(AUDIT_OUTPUT)
