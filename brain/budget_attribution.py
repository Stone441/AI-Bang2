"""Immutable grant ownership layered on the original global budget ledger."""
import hashlib
import json
import re
from brain.budget import TrialAdmissionPaused


def initialize(ledger):
    with ledger.transaction():
        ledger.db.execute('CREATE TABLE IF NOT EXISTS allowance_grants (id TEXT PRIMARY KEY, policy TEXT NOT NULL, cost_limit INTEGER NOT NULL, max_calls INTEGER, frozen_cost INTEGER NOT NULL, frozen_calls INTEGER NOT NULL, frozen_unknown TEXT NOT NULL, migration TEXT NOT NULL)')
        ledger.db.execute('CREATE TABLE IF NOT EXISTS reservation_grants (reservation_id TEXT PRIMARY KEY REFERENCES reservations(id), grant_id TEXT NOT NULL REFERENCES allowance_grants(id))')
        for table in ('allowance_grants', 'reservation_grants'):
            for operation in ('UPDATE', 'DELETE'):
                ledger.db.execute(f"CREATE TRIGGER IF NOT EXISTS {table}_{operation.lower()} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT, 'Immutable grant attribution'); END")


def status(db, grant):
    row = db.execute('SELECT policy,cost_limit,max_calls,frozen_cost,frozen_calls,frozen_unknown FROM allowance_grants WHERE id=?', (grant,)).fetchone()
    if row is None: raise ValueError('Explicit checked migration required')
    rows = db.execute('SELECT r.id,r.state,r.reserved,r.actual FROM reservations r JOIN reservation_grants g ON g.reservation_id=r.id WHERE g.grant_id=?', (grant,)).fetchall()
    return dict(policy=row[0], cost_limit=row[1], max_calls=row[2],
                settled=row[3]+sum(r[3] for r in rows if r[1]=='settled'),
                accounted=row[3]+sum(r[3] if r[1]=='settled' else 0 if r[1]=='cancelled' else r[2] for r in rows),
                calls=row[4]+sum(r[1] in ('dispatched','settled') for r in rows),
                prepared=sum(r[1]=='prepared' for r in rows),
                unknown=json.loads(row[5])+[r[0] for r in rows if r[1] in ('prepared','dispatched')])


def check(db, grant, upper):
    value = status(db, grant)
    if (value['unknown'] or value['accounted']+upper > value['cost_limit']
            or value['max_calls'] is not None and value['calls']+value['prepared']+1 > value['max_calls']):
        raise TrialAdmissionPaused('Grant call/cost/unknown limit reached')


def snapshot(db):
    return db.execute('SELECT id,reserved,state,actual FROM reservations ORDER BY id').fetchall()


def migration_plan(ledger, grant_id, prior, *, external_reservations=None):
    """Return reviewable JSON, never mutate allowance or reservations.

    Exact external IDs require an explicit owning grant and immutable evidence hash.
    Without these, all historical global increments are conservatively frozen.
    The original state (including its baseline) is retained verbatim in the plan.
    """
    external = external_reservations or {}
    if not isinstance(grant_id, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,120}', grant_id):
        raise ValueError('Stable grant ID required')
    policy = prior.get('authorization')
    cost = prior.get('settled_stop_threshold_micro_usd')
    calls = prior.get('max_model_calls')
    baseline_calls = prior.get('baseline_model_calls')
    baseline_cost = prior.get('baseline', {}).get('settled_micro_usd')
    pending = prior.get('original_pending_ids')
    if (not isinstance(policy, str) or not policy or type(cost) is not int or not 0 < cost <= ledger.limit
            or calls is not None and (type(calls) is not int or calls <= 0)
            or type(baseline_calls) is not int or baseline_calls < 0
            or type(baseline_cost) is not int or baseline_cost < 0
            or not isinstance(pending, list) or any(not isinstance(x, str) for x in pending)):
        raise ValueError('Existing immutable authorization and baseline required')
    with ledger.transaction(): rows = snapshot(ledger.db)
    by_id = {r[0]: r for r in rows}
    for rid, evidence in external.items():
        if (rid not in by_id or rid in pending or by_id[rid][2] != 'settled'
                or not isinstance(evidence, dict) or set(evidence) != {'owner','evidence_sha256'}
                or not isinstance(evidence['owner'], str) or not evidence['owner'] or evidence['owner'] == grant_id
                or not re.fullmatch(r'[0-9a-f]{64}', evidence.get('evidence_sha256', ''))):
            raise ValueError('Exact settled external reservation and evidence required')
    frozen_cost = sum(r[3] for r in rows if r[2]=='settled')-baseline_cost-sum(by_id[r][3] for r in external)
    frozen_calls = sum(r[2] in ('dispatched','settled') for r in rows)-baseline_calls-len(external)
    unknown = sorted(r[0] for r in rows if r[2] in ('prepared','dispatched') and r[0] not in pending)
    if frozen_cost < 0 or frozen_calls < 0 or not set(pending) <= set(by_id):
        raise ValueError('Historical baseline/exclusions require reconciliation')
    # New historical unknowns remain a permanent migration stop, with their
    # original global reservations intact. They cannot become a fresh baseline.
    body = dict(version=1, grant_id=grant_id, prior=prior, reservations=rows,
                external_reservations=external, frozen_cost=frozen_cost,
                frozen_calls=frozen_calls, frozen_unknown=unknown,
                boundary='Conservative historical increments frozen; only explicitly evidenced external reservations excluded. No refund or new authorization.')
    return json.dumps(body, sort_keys=True, separators=(',', ':'))


def apply_migration(ledger, plan, *, expected_plan_sha256):
    if hashlib.sha256(plan.encode()).hexdigest() != expected_plan_sha256:
        raise ValueError('Reviewed migration plan digest required')
    body = json.loads(plan)
    initialize(ledger)
    with ledger.transaction():
        # Recompute all fields, so a hand-edited cost/count cannot silently refund.
        # Use a small transaction-free view for the already locked snapshot.
        current = snapshot(ledger.db)
        if json.loads(json.dumps(current)) != body['reservations']:
            raise ValueError('Ledger changed; regenerate and review migration plan')
        class View:
            limit = ledger.limit
            db = ledger.db
            def transaction(self):
                from contextlib import nullcontext
                return nullcontext()
        rebuilt = migration_plan(View(), body['grant_id'], body['prior'], external_reservations=body['external_reservations'])
        if rebuilt != plan: raise ValueError('Invalid migration plan')
        prior = body['prior']
        values = (body['grant_id'], prior['authorization'], prior['settled_stop_threshold_micro_usd'],
                  prior['max_model_calls'], body['frozen_cost'], body['frozen_calls'],
                  json.dumps(body['frozen_unknown']), plan)
        existing = ledger.db.execute('SELECT * FROM allowance_grants WHERE id=?', (body['grant_id'],)).fetchone()
        if existing is not None:
            if tuple(existing) != values: raise ValueError('Grant cannot be reset or expanded')
            return
        ledger.db.execute('INSERT INTO allowance_grants VALUES(?,?,?,?,?,?,?,?)', values)
