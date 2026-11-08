---
topics: [review-agent-profiles]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/100']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/100'
---

# Recover a check-blocked independent recheck

The Opus implementer review confirmed its source repair but recorded BLOCKED
because required hook tests timed out. Passing check recovery only reopened
finalization, leaving this recheck unresolved. Repeating repair or starting a
new review would waste work and discard the existing chain as the active path.

New version-3 rechecks pause before provider dispatch while required checks fail,
avoiding a review call that cannot complete verification. Passing recovery
restores ready for the first independent assessment.

For already unresolved rechecks, `rerun-checks` now restores version-3 `recheck/ready` when complete, current
failed receipts become passing and every finding is rejected or accepted with
PASSED/BLOCKED verification, including at least one BLOCKED finding. A fresh
independent recheck must still verify the findings against the new receipts.
The helper never infers semantic correctness from passing commands.

The target, scoped files, frozen profile and commands, finding definitions and
verification, and repair count stay unchanged. Previous receipts remain on disk
and in the recovery artifact; handoff revision advances to reject stale responses.
Failed/unverified findings, new gaps, missing/stale prior receipts, previously
passing checks, and legacy version-2 runs retain the unresolved result. Recovery
never retries the writer or adds a repair pass.

Deterministic temporary-repository tests reproduce failed checks, BLOCKED recheck,
failed recovery, passing recovery, fresh independent verification and local
completion with one repair. Guard cases cover substantive/new gaps, stale or
missing receipts, legacy runs and repeat recovery. No live provider trial is
needed for this state-transition fix. The CLI recovery procedure owns usage.
