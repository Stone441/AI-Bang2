"""Run the five-scene offline rehearsal; never uses platform credentials or paid models."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from brain.contracts import now
from scripts.build_metadata import revision, dirty

ROOT = Path(__file__).resolve().parents[1]


def run(output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)  # Preserve every previous rehearsal, including failures.
    report = {'started_at': now(), 'commit': revision(), 'worktree_dirty': dirty(),
              'python': platform.python_version(), 'mode': 'fixture_and_mock_http_fake_model',
              'live_api': 'not_run', 'live_model': 'not_run', 'human_review': 'not_run', 'checks': []}
    checks = [
        ('five-scenarios', [sys.executable, '-c',
            'import sys; from pathlib import Path; from scripts.evaluate import run; run(Path(sys.argv[1]))', str(output/'scenarios')]),
        ('four-source-lifecycle', [sys.executable, '-c',
            'import sys; from pathlib import Path; from scripts.lifecycle_acceptance import run; sys.exit(not run(Path(sys.argv[1])))', str(output/'lifecycle')]),
        ('continuous-sources', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_continuous_sources.py']),
        ('freshness-status', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_source_freshness_status.py']),
        ('version-recovery', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_page_failure_ux.py']),
        ('application-permissions', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_application_roles.py']),
        ('account-isolation', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_reviewer_access.py']),
        ('answer-presentation', ['node', 'tests/frontend_answer_sections.js']),
        ('sectioned-answer-contract', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_sectioned_answer.py']),
        ('retrieval-challenges', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_retrieval_challenges.py']),
        ('answer-challenges', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_answer_challenges.py']),
        ('sectioned-answer-display', ['node', 'tests/frontend_sectioned_answer.js']),
        ('freshness-display', ['node', 'tests/frontend_source_freshness.js']),
        ('audit-presentation', ['node', 'tests/frontend_audit_requests.js']),
        ('scenario-lab-contract', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_scenario_lab.py']),
        ('scenario-lab-display', ['node', 'tests/frontend_scenario_lab.js']),
        ('security-challenges', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_security_challenges.py']),
        ('audit-timeline', ['node', 'tests/frontend_audit_timeline.js']),
        ('signed-audit', [sys.executable, '-m', 'scripts.audit_mixed_acceptance', '--output', str(output/'signed-audit')]),
        ('http-body-deadline', [sys.executable,'-m','unittest','discover','-s','tests','-p','test_request_body.py']),
        ('budget-attribution', [sys.executable,'-m','unittest','discover','-s','tests','-p','test_budget_attribution.py']),
        ('grant-migration', [sys.executable,'-m','unittest','discover','-s','tests','-p','test_grant_migration.py']),
        ('application-audit-http', [sys.executable,'-m','unittest','discover','-s','tests','-p','test_application_audit_http.py']),
        ('release-static-snapshot', [sys.executable,'-m','unittest','discover','-s','tests','-p','test_static_snapshot.py']),
        ('closeout-readiness-ui', ['node','tests/frontend_closeout.js']),
    ]
    report['source_hashes'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for folder in ('brain', 'web', 'scripts', 'tests', 'tools', 'fixtures')
        for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    def save():
        (output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    save()
    for name, command in checks:
        started = time.monotonic()
        with (output/(name+'.log')).open('w') as log:
            try:
                result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=180)
                code = result.returncode
            except (OSError, subprocess.TimeoutExpired) as error:
                log.write(type(error).__name__+': '+str(error)+'\n');code = None
        check = {'name': name, 'status': 'passed' if code == 0 else 'failed', 'exit_code': code,
                 'elapsed_seconds': round(time.monotonic()-started, 3), 'log': name+'.log'}
        report['checks'].append(check);save()
        print(name+': '+check['status'], flush=True)
    report['successful'] = all(c['status']=='passed' for c in report['checks'])
    report['finished_at'] = now()
    report['limitations'] = [
        'Mock API timing does not establish native freshness or a latency SLA.',
        'Application roles do not prove independent employee identities on four platforms.',
        'Local signed audit rehearsal does not establish independent key/checkpoint custody.',
        'DOM tests are not a browser or human usability review.']
    save()
    return report['successful']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory; existing evidence is never overwritten')
    args = parser.parse_args()
    raise SystemExit(not run(args.output))
