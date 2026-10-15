# Task 2 · durable grant attribution

Base: 94852c5. Scope: budget ledger, opt-in attributed allowance, conservative legacy label, new budget regressions. No live ledger, runtime, credentials, model/native calls, launch, restart, push or merge.

## Result and integration

`BudgetLedger.reserve(..., grant_id=...)` checks the grant cost, counted dispatched/settled calls, prepared call slots and original global USD20 ceiling in the same `BEGIN IMMEDIATE` transaction as inserting reservation + ownership. Immutable SQLite tables and update/delete rejection triggers retain policy, migration and reservation ownership. Settled rejected calls count; unresolved dispatched calls reserve their entire global upper bound. Existing APIs and legacy allowance JSON remain unchanged. Legacy allowances are explicitly conservative global-delta accounting; the new mode must be selected deliberately.

Prepare an explicit migration using the actual existing human allowance JSON, without changing that file:

```python
import hashlib, json
from scripts.attributed_allowance import (
    migration_plan, apply_migration, AttributedAdmission, AttributedGoalLedger,
)
prior = json.loads(existing_state_path.read_text())
plan = migration_plan(
    original_ledger, 'human-team-trial-20261013', prior,
    external_reservations={
        # Only exact settled reservation IDs supported by reviewed evidence:
        # exact_id: {'owner': 'team-live17', 'evidence_sha256': evidence_digest},
    },
)
# Save and review this complete plan before authorizing its runtime application.
# Digest must be the exact reviewed plan bytes, not a newly generated substitute.
apply_migration(original_ledger, plan, expected_plan_sha256=reviewed_digest)
gate = AttributedAdmission(
    engine.query, original_ledger, 'human-team-trial-20261013',
    policy=prior['authorization'],
    cost_limit=prior['settled_stop_threshold_micro_usd'],
    max_calls=prior['max_model_calls'],
)
engine.model.ledger = AttributedGoalLedger(gate)
engine.query = gate
```

Lazy review-model constructors receive the same `BudgetLedger` adapter contract, connection and original receipt/summary methods through `GoalLedger`. Existing timing wrappers remain on the underlying ledger. `gate.public_status()` reports grant-local current costs/counts and unknowns directly from the durable database. A goal and human trial can use separate migrated grant IDs.

## Migration boundary and rulings

The exact original prior state is embedded in canonical JSON alongside a complete reservation snapshot, explicit external reservation evidence hashes, frozen historical cost/call deltas, and historical unknown IDs. Applying a plan re-computes all fields and rejects any intervening reservation change, edited frozen totals, mismatched reviewed digest, existing conflicting grant, or policy expansion. Old reservations and source state are never rewritten. Existing blocked global budget stays blocked.

Ruling: Historical global increments without exact external attribution remain conservatively charged to this grant. Explicit reviewed external IDs can be excluded only if settled, not among original pending IDs, and accompanied by a separate owner label and immutable evidence SHA256. Evidence contents and truth require operator review; the module validates identity, shape, snapshot and arithmetic, not the business authenticity of supplied evidence. The plan digest is the final checked input. Cost if wrong: unresolved external costs can conservatively consume the historical grant, or erroneous explicit evidence could misattribute old spend; no automatic inference from questions, timestamps or model data occurs.

Ruling: A new historical unknown remains a permanent migration stop with the original global reservation intact; it cannot be accepted as a new baseline or implicitly refunded. A migration with this condition is reviewable but not usable for further calls. Exact reconciliation must happen before generating/applying a usable migration; applied immutable grants cannot be reset. The original baseline unknown IDs (including the two old unknowns when present in real state) stay reserved globally and are excluded from new-grant unknown stops. No actual historical IDs or costs were guessed in this task.

Ruling: This opt-in gate conservatively serializes unresolved model reservations within a grant: a second reservation pauses while another is prepared/dispatched. Different grants remain independent except for the shared global ceiling/freeze. Cost if wrong: an attributed high-concurrency launcher requires a separate reviewed known-in-flight extension; this adapter currently supports the sequential human launcher. Existing concurrent mode remains explicitly legacy conservative and was not silently changed.

## Validation

- `task2-legacy-reproduction-red.log`: existing legacy API reproduces the attribution bug (one external call incorrectly consumes first grant's call count).
- `task2-red.log`: new regression suite created first, initially fails because opt-in module does not exist.
- `task2-targeted.log`: budget suite including 10 new meaningful cases: 17 passed.
- `task2-allowance.log`: 18 existing allowance/concurrency tests passed.
- `task2-delivery.log`: 13 existing delivery admission tests passed.
- `task2-full.log`: 729 tests passed in 52.815s after combined task2/task3 working-tree validation. This is not native/model/browser/human acceptance.

No historical cost is removed from the global USD20 ledger. No old unknown is settled/cancelled. No actual runtime migration has been performed.
