"""AUTH036 loopback goal launcher. Legacy state and ledger are not reset.

Uses the original private answer/index database, with a separate goal admission.
Run after verified idle ownership/backups. Missing stored credentials stop with
stdin unavailable; no plaintext credential fallback or model call on startup.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import sys
import tempfile

from scripts.performance_allowance import PerformanceAdmission, GoalLedger

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT/'.runtime/query-goal-20261013'
PLAN = ROOT/'docs/reviews/2026-10-13-query-goal/PLAN.json'


def write_private(path, value):
    fd, temporary = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as output:
            output.write(value)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def private_directory(path):
    if path.is_symlink():
        raise ValueError('Private path must not be a symlink')
    path.mkdir(mode=0o700, exist_ok=True)
    if path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o777 != 0o700:
        raise ValueError('Owned private directory required')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reasoning-effort', choices=['none', 'low'], default='low')
    parser.add_argument('--source-transport', choices=['legacy', 'pooled'], default='legacy')
    parser.add_argument('--source-concurrency', type=int, choices=[1, 2, 4], default=1)
    parser.add_argument('--source-review-input', choices=['legacy','compact','covered','whole','structured','explained'], default='legacy')
    parser.add_argument('--source-review-dispatch', choices=['legacy','single'], default='legacy')
    parser.add_argument('--window-strategy', choices=['fixed','structured'], default='fixed')
    parser.add_argument('--history-read-mode', choices=['serial','batch'], default='serial')
    parser.add_argument('--query-concurrency', choices=['serial','isolated3'], default='serial')
    parser.add_argument('--human-team-trial', action='store_true', help='Explicit USD1 human-only allowance; no automated acceptance')
    parser.add_argument('--reviewer-accounts', type=Path, help='Private password-account registry; opt-in shared synthetic reviewer identity')
    parser.add_argument('--reviewer-public-origin', help='Exact HTTPS origin behind a local reverse proxy; does not bind publicly')
    args = parser.parse_args(argv)
    if (args.reviewer_accounts or args.reviewer_public_origin) and not args.human_team_trial:
        parser.error('Reviewer mode requires explicit human trial allowance')
    if args.reviewer_public_origin and not args.reviewer_accounts:
        parser.error('Public origin requires reviewer accounts')
    if args.human_team_trial and args.query_concurrency != 'serial':
        parser.error('Human team trial requires the selected serial configuration')
    if args.reviewer_accounts:
        args.reviewer_accounts = args.reviewer_accounts.resolve()
    if args.source_concurrency > 1 and args.source_transport != 'pooled':
        parser.error('Source concurrency above one requires the bounded pooled transport')
    for path in (PRIVATE, PRIVATE/'.runtime'):
        private_directory(path)
    runtime = PRIVATE/'.runtime'
    original_index = ROOT/'.runtime/delivery-trial-20261011/.runtime/multi-auth017-web.sqlite'
    for name, target in (('deepseek-budget.sqlite', ROOT/'.runtime/deepseek-budget.sqlite'),
                         ('multi-auth017-web.sqlite', original_index)):
        if target.is_symlink() or not target.is_file() or target.stat().st_uid != os.getuid():
            raise ValueError('Original owned state required')
        alias = runtime/name
        if not alias.exists():
            alias.symlink_to(target)
        if not alias.is_symlink() or alias.resolve() != target:
            raise ValueError('Existing state mapping cannot be changed')
    plan = json.loads(PLAN.read_text())
    if plan['authorization'] != PerformanceAdmission.POLICY:
        raise ValueError('Frozen goal authorization required')
    plan_hash = hashlib.sha256(PLAN.read_bytes()).hexdigest()
    from brain import operator_web
    from brain import drive_oauth
    from brain.confluence import SourceUnavailable
    def no_new_consent(*args, **kwargs):
        raise SourceUnavailable('Existing authorization required')
    # Refresh an existing grant only; never launch consent or ask for new scope.
    drive_oauth.authorize = no_new_consent
    rollbacks = []
    original_app = operator_web.OperatorApp
    if args.source_transport == 'pooled':
        class PooledApp(original_app):
            def __init__(self, *positional, **keyword):
                super().__init__(*positional, **keyword)
                from brain.http_pool import install
                rollbacks.append(install(self.world.readers, maximum=max(2, args.source_concurrency)))
                self.world.read_concurrency = args.source_concurrency
        operator_web.OperatorApp = PooledApp
    original_create = operator_web.create_server
    def create(app, port):
        server = original_create(app, port, public_origin=args.reviewer_public_origin)
        serve = server.serve_forever
        def renew(_signal, _frame):
            current = server.application
            if current is None or current.auth_kind != 'operator':
                return
            try:
                ticket = current.renew_bootstrap_ticket()
                write_private(PRIVATE/'bootstrap-token', ticket)
                write_private(ROOT/'.runtime/page-failure-ux-logs/human-bootstrap-token', ticket)
            except OSError:
                print('Entry renewal unavailable; existing service retained.', flush=True)
        signal.signal(signal.SIGUSR1, renew)
        def guarded_serve(*positional, **keyword):
            current = server.application
            current.engine.query_expansion = 'none'
            current.engine.evidence_on_model_rejection = True
            query=current.engine.query;gate_type=PerformanceAdmission;ledger_type=GoalLedger
            if args.query_concurrency=='isolated3':
                from brain.isolated_query import IsolatedQueries
                from scripts.concurrent_allowance import ConcurrentPerformanceAdmission,ConcurrentGoalLedger
                current.isolated_queries=IsolatedQueries(current.engine)
                query=current.isolated_queries.query
                gate_type=ConcurrentPerformanceAdmission;ledger_type=ConcurrentGoalLedger
            if args.human_team_trial:
                from scripts.team_trial_allowance import TeamTrialAdmission
                gate = TeamTrialAdmission(query, current.engine.model.ledger,
                    runtime/'human-team-admission.json',
                    previous_state_path=runtime/'goal-admission.json', human=True)
            else:
                gate = gate_type(query, current.engine.model.ledger,
                            runtime/'goal-admission.json', plan_sha256=plan_hash)
            if args.query_concurrency=='isolated3':rollbacks.append(gate.close)
            current.engine.model.ledger = ledger_type(gate)
            current.engine.query = gate
            if args.reviewer_accounts:
                from brain.reviewer_access import ReviewerApp
                server.application = ReviewerApp(current, args.reviewer_accounts.resolve())
            control = json.dumps({'pid': os.getpid(), 'port': port,
                                  'public_origin': args.reviewer_public_origin,
                                  'runtime_version': operator_web.runtime_version()}, indent=2)+'\n'
            write_private(PRIVATE/'entry-server.json', control)
            write_private(PRIVATE/'runtime-configuration.json', json.dumps({
                'source_transport': args.source_transport,
                'source_concurrency': args.source_concurrency,
                'reasoning_effort': args.reasoning_effort,
                'source_review_input': args.source_review_input,
                'source_review_dispatch': args.source_review_dispatch,
                'history_read_mode': args.history_read_mode,
                'window_strategy': args.window_strategy,
                'query_concurrency': args.query_concurrency,
                'plan_sha256': plan_hash,
                'admission_policy': gate.POLICY,
                'human_team_trial': args.human_team_trial,
                'reviewer_mode': bool(args.reviewer_accounts),
                'reviewer_public_origin': args.reviewer_public_origin,
                'proxy_behavior': 'original urllib route; no direct proxy bypass',
            }, indent=2)+'\n')
            # Preserve the user's established local entry helper and file modes.
            write_private(ROOT/'.runtime/delivery-trial-20261011/entry-server.json', control)
            return serve(*positional, **keyword)
        server.serve_forever = guarded_serve
        return server
    operator_web.create_server = create
    os.chdir(PRIVATE)
    try:
        return operator_web.main(['--source', 'multi', '--config', str(ROOT/'.runtime/operator-bundle.json'),
            '--actor', 'eng_b', '--oauth-client', str(ROOT/'.runtime/drive-oauth-client.json'),
            '--port', '49161', '--live', '--model', 'deepseek', '--credential-store', 'macos-keychain',
            '--answer-style', 'source-review', '--reasoning-effort', args.reasoning_effort,
            '--source-review-input', args.source_review_input,
            '--source-review-dispatch', args.source_review_dispatch,
            '--history-read-mode', args.history_read_mode,
            '--window-strategy', args.window_strategy,
            '--output-tokens', '8192', '--discovery-auth017', '--timing-dir', str(PRIVATE/'timings')])
    finally:
        for rollback in reversed(rollbacks):
            rollback()
        operator_web.OperatorApp = original_app


if __name__ == '__main__':
    class SafeOutput:
        def write(self, value):
            if '#ticket=' in value:
                ticket = re.search(r'#ticket=([A-Za-z0-9_-]+)', value).group(1)
                write_private(PRIVATE/'bootstrap-token', ticket)
                write_private(ROOT/'.runtime/page-failure-ux-logs/human-bootstrap-token', ticket)
                value = 'One-time entry prepared privately; use the established local entry.\n'
            return sys.__stdout__.write(value)
        def flush(self):
            return sys.__stdout__.flush()
    sys.stdout = SafeOutput()
    raise SystemExit(main())
