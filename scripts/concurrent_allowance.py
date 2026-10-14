"""Opt-in short-lock AUTH036 gate. Used only by the explicit isolated3 trial launcher option.

One owning process, concurrent admitted threads; the original ledger and goal
state remain authoritative. An OS lease excludes a second concurrent gate.
Unfinished reservations are known only while their owning query is alive in
this process; restart or query exit makes them unknown, never refundable.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import fcntl
import json
import os
from pathlib import Path
import uuid

from brain.budget import TrialAdmissionPaused
from scripts.performance_allowance import PerformanceAdmission, GoalLedger


class ConcurrentPerformanceAdmission(PerformanceAdmission):
    def __init__(self, query, ledger, state_path, *, plan_sha256):
        self._owners={}
        self._queries=set()
        self._query_token=ContextVar('concurrent_goal_query',default=None)
        self._closed=False
        path=Path(state_path).with_suffix('.owner.lock')
        self._lease=os.open(path,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:
            info=os.fstat(self._lease)
            if info.st_uid!=os.getuid() or info.st_mode & 0o777 != 0o600:
                raise ValueError('Private owned lease required')
            fcntl.flock(self._lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
            super().__init__(query,ledger,state_path,plan_sha256=plan_sha256)
            with self._critical():pass  # Reclassify abandoned work on restart.
        except BaseException:
            os.close(self._lease);self._closed=True
            raise

    @contextmanager
    def _critical(self):
        with self.lock:
            if self._closed:raise TrialAdmissionPaused('Admission owner closed')
            with self.path.with_suffix('.lock').open('a') as lock:
                os.chmod(lock.fileno(),0o600)
                fcntl.flock(lock,fcntl.LOCK_EX)
                self.load(json.loads(self.path.read_text()))
                try:yield
                finally:self.save()

    def state_extra(self):
        result=super().state_extra()
        pending=self.pending_ids()-self.pending
        result.update(new_unknown_reservations=sorted(pending-set(self._owners)),
                      known_in_flight_reservations=sorted(pending & set(self._owners)),
                      concurrent_admission=True)
        return result

    def _check(self, db, *, upper=0, slots=0):
        rows=db.execute('SELECT id,reserved,state,actual FROM reservations').fetchall()
        pending={r[0] for r in rows if r[2] in ('prepared','dispatched')}
        unknown=pending-self.pending-set(self._owners)
        actual_calls=sum(r[2] in ('dispatched','settled') for r in rows)-self.baseline_model_calls
        prepared=sum(r[2]=='prepared' and r[0] not in self.pending for r in rows)
        spent=sum(r[3] for r in rows if r[2]=='settled')-self.baseline['settled_micro_usd']
        outstanding=sum(r[1] for r in rows if r[0] in pending-self.pending)
        blocked=db.execute('SELECT blocked FROM budget WHERE id=1').fetchone()[0]
        if (unknown or blocked or actual_calls<0 or spent<0
                or actual_calls+prepared+slots>self.MAXIMUM
                or spent+outstanding+upper>self.COST_LIMIT):
            raise TrialAdmissionPaused('Goal call/cost/unknown limit reached')

    def _owned(self, reservation):
        token=self._query_token.get()
        if token not in self._queries or self._owners.get(reservation)!=token:
            raise TrialAdmissionPaused('Reservation requires its admitted query')

    def __call__(self, *args, **kwargs):
        token=uuid.uuid4().hex
        with self._critical():
            with self.ledger.transaction():self._check(self.ledger.db)
            if self.attempts>=self.MAXIMUM or self.additional_stop():
                raise TrialAdmissionPaused('Goal attempt or call limit reached')
            self.attempts+=1;self._queries.add(token)
        context=self._query_token.set(token)
        try:return self.query(*args,**kwargs)
        finally:
            self._query_token.reset(context)
            with self._critical():
                self._owners={rid:owner for rid,owner in self._owners.items() if owner!=token}
                self._queries.remove(token)

    def reserve(self, upper_bound, **kwargs):
        with self._critical():
            token=self._query_token.get()
            if token not in self._queries:
                raise TrialAdmissionPaused('Model call requires goal admission')
            reservation=self.ledger.reserve(upper_bound,**kwargs,
                admission_check=lambda db:self._check(db,upper=upper_bound,slots=1))
            self._owners[reservation]=token
            return reservation

    def dispatch(self, reservation):
        with self._critical():
            self._owned(reservation)
            self.ledger.dispatch(reservation,admission_check=self._check)

    def settle(self, reservation, actual, **kwargs):
        with self._critical():
            self._owned(reservation)
            # In-flight receipts still settle after another call becomes unknown.
            return self.ledger.settle(reservation,actual,**kwargs)

    def cancel_before_dispatch(self, reservation):
        with self._critical():
            self._owned(reservation)
            self.ledger.cancel_before_dispatch(reservation)
            self._owners.pop(reservation)

    def model_outcome(self, reservation, outcome):
        with self._critical():
            self._owned(reservation)
            self.ledger.model_outcome(reservation,outcome)
            self._owners.pop(reservation)

    def close(self):
        with self.lock:
            if self._queries:raise RuntimeError('Cannot close active admission')
            if not self._closed:
                os.close(self._lease);self._closed=True


class ConcurrentGoalLedger(GoalLedger):
    def __init__(self, admission):
        if not isinstance(admission,ConcurrentPerformanceAdmission):
            raise ValueError('Concurrent admission required')
        super().__init__(admission)
        for name in ('dispatch','settle','cancel_before_dispatch','model_outcome'):
            setattr(self,name,getattr(admission,name))
