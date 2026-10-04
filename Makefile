.PHONY: test demo verify setup
setup:
	python3 -c "import sqlite3; import sys; assert sys.version_info >= (3, 11); print('Standard-library runtime ready')"
test:
	python3 -m unittest discover -s tests -v
demo:
	python3 -m brain.server --demo
verify:
	python3 -m scripts.evaluate
