"""Opt-in durable grant admission; legacy JSON admissions remain conservative.

Migrate a reviewed legacy state using migration_plan/apply_migration first.
No runtime migration, new allowance, implicit baseline reset, or retry occurs.
"""
from contextvars import ContextVar
from brain.budget import TrialAdmissionPaused
from brain.budget_attribution import initialize, status, migration_plan, apply_migration
from scripts.performance_allowance import GoalLedger


class AttributedAdmission:
    def __init__(self, query, ledger, grant_id, *, policy, cost_limit, max_calls):
        initialize(ledger)
        self.query, self.ledger, self.grant_id = query, ledger, grant_id
        self.active = ContextVar('attributed_grant_active', default=False)
        with ledger.transaction(): value = status(ledger.db, grant_id)
        if (value['policy'], value['cost_limit'], value['max_calls']) != (policy, cost_limit, max_calls):
            raise ValueError('Grant policy cannot be reset or expanded')

    def public_status(self):
        with self.ledger.transaction():
            value = status(self.ledger.db, self.grant_id)
            blocked = self.ledger.db.execute('SELECT blocked FROM budget WHERE id=1').fetchone()[0]
            globally_unavailable = blocked or self.ledger._used() >= self.ledger.limit
        reason = ('usage_unconfirmed' if value['unknown'] else
                  'global_budget_unavailable' if globally_unavailable else
                  'cost_limit' if value['accounted'] >= value['cost_limit'] else
                  'model_call_limit' if value['max_calls'] is not None and value['calls'] >= value['max_calls'] else None)
        return dict(allowed=reason is None, reason=reason, human_unlimited=value['max_calls'] is None,
                    model_calls_used=value['calls'], attempts_used=None, attempts_limit=None, attempts_remaining=None,
                    settled_usd=value['settled']/1_000_000, settlement_limit_usd=value['cost_limit']/1_000_000,
                    settlement_remaining_usd=max(0,value['cost_limit']-value['accounted'])/1_000_000)

    def __call__(self, *args, **kwargs):
        if not self.public_status()['allowed']: raise TrialAdmissionPaused('Grant paused')
        token = self.active.set(True)
        try: return self.query(*args, **kwargs)
        finally: self.active.reset(token)

    def reserve(self, upper_bound, **kwargs):
        if not self.active.get(): raise TrialAdmissionPaused('Model call requires grant admission')
        if 'grant_id' in kwargs: raise ValueError('Grant ownership is server selected')
        return self.ledger.reserve(upper_bound, grant_id=self.grant_id, **kwargs)

    def _owned(self, reservation):
        with self.ledger.transaction():
            row = self.ledger.db.execute('SELECT grant_id FROM reservation_grants WHERE reservation_id=?', (reservation,)).fetchone()
        if row != (self.grant_id,): raise TrialAdmissionPaused('Reservation belongs to another grant')

    def dispatch(self, reservation, **kwargs):
        if not self.active.get(): raise TrialAdmissionPaused('Dispatch requires grant admission')
        self._owned(reservation)
        def check_dispatch(db):
            value = status(db, self.grant_id)
            blocked = db.execute('SELECT blocked FROM budget WHERE id=1').fetchone()[0]
            if (blocked or set(value['unknown'])-{reservation}
                    or value['accounted'] > value['cost_limit']
                    or value['max_calls'] is not None and value['calls']+value['prepared'] > value['max_calls']):
                raise TrialAdmissionPaused('Grant dispatch paused')
            if kwargs.get('admission_check') is not None:
                kwargs['admission_check'](db)
        return self.ledger.dispatch(reservation, admission_check=check_dispatch)

    def settle(self, reservation, *args, **kwargs):
        self._owned(reservation)
        return self.ledger.settle(reservation, *args, **kwargs)

    def cancel_before_dispatch(self, reservation):
        self._owned(reservation)
        return self.ledger.cancel_before_dispatch(reservation)

    def model_outcome(self, reservation, outcome):
        self._owned(reservation)
        return self.ledger.model_outcome(reservation, outcome)


class AttributedGoalLedger(GoalLedger):
    def __init__(self, admission):
        if not isinstance(admission, AttributedAdmission): raise ValueError('Attributed admission required')
        super().__init__(admission)
        for name in ('dispatch','settle','cancel_before_dispatch','model_outcome'):
            setattr(self, name, getattr(admission, name))
