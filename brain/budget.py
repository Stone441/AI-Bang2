"""Durable pilot spending reservations, integer micro-USD, no credentials.

Accounting is conservative, not a provider-side billing cap. A dispatched request
with unknown consumption retains its entire reservation until reconciled.
"""
import sqlite3
import uuid
import threading
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
        self.db.execute('CREATE TABLE IF NOT EXISTS budget (id INTEGER PRIMARY KEY CHECK(id=1), ceiling INTEGER NOT NULL, blocked INTEGER NOT NULL DEFAULT 0)')
        self.db.execute('CREATE TABLE IF NOT EXISTS reservations (id TEXT PRIMARY KEY, reserved INTEGER NOT NULL, state TEXT NOT NULL, actual INTEGER)')
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

    def reserve(self, upper_bound):
        if type(upper_bound) is not int or upper_bound <= 0:
            raise ValueError('Positive integer upper bound required')
        with self.transaction():
            if self.db.execute('SELECT blocked FROM budget WHERE id=1').fetchone()[0] or self._used() + upper_bound > self.limit:
                raise BudgetExceeded('Pilot budget unavailable')
            request_id = uuid.uuid4().hex
            self.db.execute('INSERT INTO reservations VALUES(?,?,?,NULL)', (request_id, upper_bound, 'prepared'))
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

    def settle(self, request_id, actual):
        if type(actual) is not int or actual < 0:
            raise ValueError('Nonnegative integer actual cost required')
        exceeded = False
        with self.transaction():
            row = self.db.execute('SELECT reserved,state,actual FROM reservations WHERE id=?', (request_id,)).fetchone()
            if not row or row[1] not in ('dispatched', 'settled'):
                raise ValueError('No dispatched request to settle')
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
