"""Durable pilot spending reservations, integer micro-USD, no credentials.

Accounting is conservative, not a provider-side billing cap. A dispatched request
with unknown consumption retains its entire reservation until reconciled.
"""
import sqlite3
import uuid
import threading
import re
from contextlib import contextmanager


class BudgetExceeded(Exception):
    pass


class BudgetLedger:
    APPROVED_MAX = 20_000_000  # AUTH-003: USD 20 equivalent pilot ceiling.

    def __init__(self, path, limit=APPROVED_MAX):
        if type(limit) is not int or not 0 < limit <= self.APPROVED_MAX:
            raise ValueError('Pilot limit must be within approved USD 20 ceiling')
        self.lock = threading.RLock()
        self.db = sqlite3.connect(path, timeout=10, isolation_level=None, check_same_thread=False)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY CHECK(id=1), ceiling INTEGER NOT NULL, blocked INTEGER NOT NULL DEFAULT 0)')
        self.db.execute('CREATE TABLE IF NOT EXISTS reservations (id TEXT PRIMARY KEY, reserved INTEGER NOT NULL, state TEXT NOT NULL, actual INTEGER)')
        self.db.execute('CREATE TABLE IF NOT EXISTS model_calls (reservation_id TEXT PRIMARY KEY REFERENCES reservations(id), query_id TEXT NOT NULL, model TEXT NOT NULL, prompt_tokens INTEGER, completion_tokens INTEGER, total_tokens INTEGER, outcome TEXT NOT NULL)')
        with self.transaction():
            row = self.db.execute('SELECT ceiling FROM budget WHERE id=1').fetchone()
            if row and row[0] != limit:
                raise ValueError('Existing ledger ceiling cannot be silently changed')
            self.db.execute('INSERT OR IGNORE INTO budget(id,ceiling) VALUES(1,?)', (limit,))
        self.limit = limit

    @contextmanager
    def transaction(self):
        with self.lock:
            self.db.execute('BEGIN IMMEDIATE')
            try:
                yield
                self.db.execute('COMMIT')
            except BaseException:
                self.db.execute('ROLLBACK')
                raise

    def _used(self):
        return self.db.execute("SELECT COALESCE(SUM(CASE WHEN state='settled' THEN actual WHEN state='cancelled' THEN 0 ELSE reserved END),0) FROM reservations").fetchone()[0]

    def reserve(self, upper_bound, *, query_id=None, model=None):
        if type(upper_bound) is not int or upper_bound <= 0:
            raise ValueError('Positive integer upper bound required')
        if ((query_id is None) != (model is None) or
                (query_id is not None and (not isinstance(query_id, str)
                 or not re.fullmatch(r'[0-9a-f]{32}', query_id)
                 or not isinstance(model, str) or not re.fullmatch(r'[a-z0-9-]{1,80}', model)))):
            raise ValueError('Server request ID and model required together')
        with self.transaction():
            if self.db.execute('SELECT blocked FROM budget WHERE id=1').fetchone()[0] or self._used() + upper_bound > self.limit:
                raise BudgetExceeded('Pilot budget unavailable')
            request_id = uuid.uuid4().hex
            self.db.execute('INSERT INTO reservations VALUES(?,?,?,NULL)', (request_id, upper_bound, 'prepared'))
            if query_id is not None:
                self.db.execute('INSERT INTO model_calls VALUES(?,?,?,NULL,NULL,NULL,?)',
                                (request_id, query_id, model, 'pending'))
        return request_id

    def dispatch(self, request_id):
        with self.transaction():
            row = self.db.execute('SELECT state FROM reservations WHERE id=?', (request_id,)).fetchone()
            if not row or row[0] != 'prepared':
                raise ValueError('Request cannot be dispatched')
            # Persist BEFORE network dispatch. A process crash here is conservative.
            self.db.execute("UPDATE reservations SET state='dispatched' WHERE id=?", (request_id,))

    def cancel_before_dispatch(self, request_id):
        with self.transaction():
            row = self.db.execute('SELECT state FROM reservations WHERE id=?', (request_id,)).fetchone()
            if not row or row[0] != 'prepared':
                raise ValueError('Dispatched consumption cannot be released')
            self.db.execute("UPDATE reservations SET state='cancelled' WHERE id=?", (request_id,))

    def settle(self, request_id, actual, *, usage=None):
        if type(actual) is not int or actual < 0:
            raise ValueError('Nonnegative integer actual cost required')
        if usage is not None and (not isinstance(usage, dict)
                or set(usage) != {'prompt_tokens','completion_tokens','total_tokens'}
                or any(type(v) is not int or v < 0 for v in usage.values())
                or usage['total_tokens'] != usage['prompt_tokens'] + usage['completion_tokens']):
            raise ValueError('Validated token usage required')
        exceeded = False
        with self.transaction():
            row = self.db.execute('SELECT reserved,state,actual FROM reservations WHERE id=?', (request_id,)).fetchone()
            if not row or row[1] not in ('dispatched', 'settled'):
                raise ValueError('No dispatched request to settle')
            if usage is not None:
                call = self.db.execute('SELECT prompt_tokens,completion_tokens,total_tokens FROM model_calls WHERE reservation_id=?', (request_id,)).fetchone()
                if not call: raise ValueError('No linked model call')
                counts = tuple(usage[k] for k in ('prompt_tokens','completion_tokens','total_tokens'))
                if call[0] is not None and tuple(call) != counts:
                    raise ValueError('Conflicting token reconciliation')
                self.db.execute('UPDATE model_calls SET prompt_tokens=?,completion_tokens=?,total_tokens=? WHERE reservation_id=?', (*counts, request_id))
            if row[1] == 'settled':
                if row[2] != actual: raise ValueError('Conflicting reconciliation')
                return
            self.db.execute("UPDATE reservations SET state='settled',actual=? WHERE id=?", (actual, request_id))
            exceeded = actual > row[0] or self._used() > self.limit
            if exceeded:
                self.db.execute('UPDATE budget SET blocked=1 WHERE id=1')
        if exceeded:
            # Keep the real charge durable even when the estimation contract failed.
            raise BudgetExceeded('Actual charge exceeded reservation; review billing')

    def model_outcome(self, reservation_id, outcome):
        if outcome not in ('accepted','output_rejected','usage_unavailable','usage_exceeded'):
            raise ValueError('Unsupported model outcome')
        with self.transaction():
            row = self.db.execute('SELECT c.outcome,r.state FROM model_calls c JOIN reservations r ON r.id=c.reservation_id WHERE reservation_id=?', (reservation_id,)).fetchone()
            expected_state = 'settled' if outcome in ('accepted','output_rejected') else 'dispatched'
            if not row or row[0] not in ('pending', outcome) or row[1] != expected_state:
                raise ValueError('Conflicting model outcome')
            self.db.execute('UPDATE model_calls SET outcome=? WHERE reservation_id=?', (outcome, reservation_id))

    def model_receipt(self, reservation_id):
        with self.lock:
            cursor = self.db.execute('SELECT c.query_id,c.model,c.prompt_tokens,c.completion_tokens,c.total_tokens,c.outcome,r.id AS reservation_id,r.reserved AS reserved_micro_usd,r.state,r.actual AS accounted_upper_micro_usd FROM model_calls c JOIN reservations r ON r.id=c.reservation_id WHERE r.id=?', (reservation_id,))
            row = cursor.fetchone()
            if not row: return None
            receipt = dict(zip((d[0] for d in cursor.description), row))
        return dict(receipt, called=True if receipt['state']=='settled' else None if receipt['state']=='dispatched' else False,
                    dispatch_recorded=receipt['state'] in ('dispatched','settled'),
                    accounting_basis='conservative peak/cache-miss upper estimate; not vendor invoice')

    def summary(self):
        with self.transaction():
            used = self._used()
            spent = self.db.execute("SELECT COALESCE(SUM(actual),0) FROM reservations WHERE state='settled'").fetchone()[0]
            pending = self.db.execute("SELECT COUNT(*) FROM reservations WHERE state IN ('prepared','dispatched')").fetchone()[0]
            blocked = bool(self.db.execute('SELECT blocked FROM budget WHERE id=1').fetchone()[0])
        return {'ceiling_micro_usd': self.limit, 'accounted_micro_usd': used,
                'settled_micro_usd': spent, 'available_micro_usd': max(0, self.limit - used),
                'pending_requests': pending, 'blocked_for_review': blocked}

    def freeze_for_review(self):
        """Keep reservations intact when the provider exceeds its token contract."""
        with self.transaction():
            self.db.execute('UPDATE budget SET blocked=1 WHERE id=1')

    def close(self):
        self.db.close()
