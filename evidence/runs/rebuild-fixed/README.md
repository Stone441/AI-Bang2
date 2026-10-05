# Clean committed-candidate rebuild

Validated application/test commit: `e9a55e6ff282af63c4090cc19ac2c41b4763581f`. A temporary git archive contained no `.runtime` or `.env`. Standard-library setup, all 295 unittest methods, five fixture worked examples and Node frontend security checks passed. Logs and `verification.json` are actual output.

A new ephemeral-port demo process served HTML/JS/CSS, accepted the explicitly labeled fixture login, answered with four fixture sources and returned an exact citation preview. Cookie/CSRF stayed only in memory. The process and temporary directory were removed; existing operator services were not stopped. This is HTTP smoke testing, not browser visual or native-platform/model acceptance.

Initial failure of commit `26dc4a9` is preserved in `../rebuild-candidate`: a test mocked an in-memory Store but relied on a leftover disk DB for chmod. The fix uses a real isolated temporary SQLite and retains all original native-error/listener/privacy assertions, plus verifies mode0600. No security assertion was skipped.

For a new candidate: `python3 -m scripts.rebuild_acceptance --ref HEAD --output evidence/runs/rebuild-<new-label>`. Existing evidence directories are protected from overwrite. Full tests require local loopback permissions and OpenSSL; Node is used for frontend test scripts. No pip/npm install, runtime credential or paid API is required for this validation.
