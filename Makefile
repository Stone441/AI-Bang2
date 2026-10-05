.PHONY: test demo verify setup live live-synthesis
setup:
	python3 -c "import sqlite3; import sys; assert sys.version_info >= (3, 11); print('Standard-library runtime ready')"
test:
	python3 -m unittest discover -s tests -v
demo:
	python3 -m brain.server --demo
verify:
	python3 -m scripts.evaluate
live:
	python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port 8088 --live --model deepseek --credential-store macos-keychain
live-synthesis:
	python3 -m brain.operator_web --source multi --config .runtime/operator-bundle.json --actor eng_b --oauth-client .runtime/drive-oauth-client.json --port 8088 --live --model deepseek --credential-store macos-keychain --answer-style synthesis
test-report:
	python3 -m scripts.test_report
