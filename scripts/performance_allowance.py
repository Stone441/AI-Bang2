"""AUTH036 goal-local admission; original USD20 ledger and old allowances retained.

Actual dispatched calls (including failed/unknown) count. Each new reservation
must fit the remaining goal cost ceiling at its conservative upper bound. No
automatic retry, cancellation, refund, or legacy state reset is provided.
"""
from contextvars import ContextVar
from scripts.delivery_trial import Admission
from brain.budget import BudgetLedger, TrialAdmissionPaused


class PerformanceAdmission(Admission):
    MAXIMUM = 60
    AUTOMATIC_LIMIT = 60
    COST_LIMIT = 500_000
    POLICY = 'AUTH036-query-goal-20261013'

    def __init__(self, query, ledger, state_path, *, plan_sha256):
        if not isinstance(plan_sha256, str) or len(plan_sha256) != 64:
            raise ValueError('Frozen goal plan required')
        self.plan_sha256 = plan_sha256
        self.active = ContextVar('performance_goal_active', default=False)
        self.baseline_model_calls = self.call_count(ledger)
        super().__init__(query, ledger, state_path)

    @staticmethod
    def call_count(ledger):
        with ledger.transaction():
            return ledger.db.execute(
                "SELECT COUNT(*) FROM reservations WHERE state IN ('dispatched','settled')"
            ).fetchone()[0]

    def load(self, prior):
        if (prior.get('authorization') != self.POLICY
                or prior.get('max_model_calls') != self.MAXIMUM
                or prior.get('settled_stop_threshold_micro_usd') != self.COST_LIMIT
                or prior.get('plan_sha256') != self.plan_sha256
                or type(prior.get('baseline_model_calls')) is not int):
            raise ValueError('Goal policy/plan cannot be reset or expanded')
        self.baseline_model_calls = prior['baseline_model_calls']
        super().load(prior)

    def state_extra(self):
        return {'authorization': self.POLICY, 'plan_sha256': self.plan_sha256,
                'baseline_model_calls': self.baseline_model_calls,
                'max_model_calls': self.MAXIMUM,
                'model_calls_used': self.call_count(self.ledger)-self.baseline_model_calls,
                'boundary': 'Goal-local 60 dispatched calls; conservative new reservation must fit USD0.50 goal ceiling. Shared ledger deltas are conservative if another operator runs. Legacy unknowns retained; new unknown stops.'}

    def additional_stop(self):
        return self.call_count(self.ledger)-self.baseline_model_calls >= self.MAXIMUM

    def update_public(self, body):
        super().update_public(body)
        if body.get('model_calls_used', 0) >= self.MAXIMUM:
            self.public.update(allowed=False, reason='model_call_limit')

    def __call__(self, *args, **kwargs):
        token = self.active.set(True)
        try:
            return super().__call__(*args, **kwargs)
        finally:
            self.active.reset(token)

    def reserve(self, upper_bound, **kwargs):
        # The query holds the persistent allowance lock across every model stage.
        # A second generation/review call must check the limit again, not merely
        # rely on a question count or the allowance snapshot at query entry.
        if not self.active.get():
            raise TrialAdmissionPaused('Model call requires goal admission')
        if type(upper_bound) is not int or upper_bound <= 0:
            raise ValueError('Positive reservation required')
        status = self.ledger.summary()
        new_spent = status['settled_micro_usd']-self.baseline['settled_micro_usd']
        if (status['blocked_for_review'] or self.pending_ids()-self.pending
                or self.additional_stop() or new_spent < 0
                or new_spent+upper_bound > self.COST_LIMIT):
            raise TrialAdmissionPaused('Goal call/cost/unknown limit reached')
        return self.ledger.reserve(upper_bound, **kwargs)


class GoalLedger(BudgetLedger):
    """Pass every existing ledger operation through, guarding new reservations."""
    def __init__(self, admission):
        if not isinstance(admission.ledger, BudgetLedger):
            raise ValueError('Original durable ledger required')
        self.admission = admission
        # Preserve the durable-ledger type contract used when a review model is
        # constructed lazily. Delegate bound methods to the SAME ledger, including
        # its timing wrappers; never open another DB or initialize/reset a budget.
        for name in ('transaction', 'dispatch', 'cancel_before_dispatch', 'settle',
                     'model_outcome', 'model_receipt', 'summary', 'freeze_for_review', 'close'):
            setattr(self, name, getattr(admission.ledger, name))

    def reserve(self, *args, **kwargs):
        return self.admission.reserve(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.admission.ledger, name)
