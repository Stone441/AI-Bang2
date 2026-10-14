"""Explicit 13 October human trial grant: no count cap, USD1 new settlement.

Separate immutable baseline; original goal state and durable ledger are retained.
Only the interactive local trial launcher selects this policy. Automated
acceptance launchers must continue using their original goal allowance.
"""
from contextvars import ContextVar
import hashlib
import json
from pathlib import Path

from scripts.delivery_trial import Admission
from scripts.performance_allowance import PerformanceAdmission


class TeamTrialAdmission(PerformanceAdmission):
    MAXIMUM = None
    AUTOMATIC_LIMIT = None
    COST_LIMIT = 1_000_000
    POLICY = '2026-10-13-human-team-trial-usd1'

    def __init__(self, query, ledger, state_path, *, previous_state_path, human=False):
        if not human:
            raise ValueError('Team allowance requires explicit human trial mode')
        previous = Path(previous_state_path)
        prior_bytes = previous.read_bytes()
        prior = json.loads(prior_bytes)
        if (prior.get('authorization') != PerformanceAdmission.POLICY
                or prior.get('max_model_calls') != 60
                or prior.get('settled_stop_threshold_micro_usd') != 500_000
                or prior.get('new_unknown_reservations')
                or type(prior.get('baseline_model_calls')) is not int):
            raise ValueError('Original goal authorization and known usage required')
        self.previous_sha256 = hashlib.sha256(prior_bytes).hexdigest()
        self.active = ContextVar('human_team_trial_active', default=False)
        self.baseline_model_calls = self.call_count(ledger)
        # Never absorb a new unknown into the new policy's accepted baseline.
        with ledger.transaction():
            pending = {r[0] for r in ledger.db.execute(
                "SELECT id FROM reservations WHERE state IN ('prepared','dispatched')")}
        if pending - set(prior['original_pending_ids']) or ledger.summary()['blocked_for_review']:
            raise ValueError('Unconfirmed usage must be resolved before team trial')
        Admission.__init__(self, query, ledger, state_path, human=True)

    def load(self, prior):
        if (prior.get('authorization') != self.POLICY
                or prior.get('max_model_calls') is not None
                or prior.get('settled_stop_threshold_micro_usd') != self.COST_LIMIT
                or prior.get('previous_goal_sha256') != self.previous_sha256
                or type(prior.get('baseline_model_calls')) is not int):
            raise ValueError('Human allowance cannot be reset or expanded')
        self.baseline_model_calls = prior['baseline_model_calls']
        Admission.load(self, prior)

    def state_extra(self):
        return {'authorization': self.POLICY,
                'previous_goal_sha256': self.previous_sha256,
                'baseline_model_calls': self.baseline_model_calls,
                'max_model_calls': None,
                'model_calls_used': self.call_count(self.ledger)-self.baseline_model_calls,
                'boundary': 'Human trial only, no count limit. USD1 new settlement plus conservative reservations; original shared ledger and unknowns preserved. No automated acceptance runs.'}

    def additional_stop(self):
        return False

    def update_public(self, body):
        Admission.update_public(self, body)
        spent = body['current']['settled_micro_usd']-body['baseline']['settled_micro_usd']
        self.public.update(human_unlimited=True,
                           settled_usd=spent/1_000_000,
                           settlement_limit_usd=self.COST_LIMIT/1_000_000,
                           settlement_remaining_usd=max(0, self.COST_LIMIT-spent)/1_000_000)
