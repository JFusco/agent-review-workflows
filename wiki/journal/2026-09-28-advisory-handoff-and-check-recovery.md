---
topics: [implementation-review-evidence]
plans: [2026-09-28-repair-advisory-handoffs-and-check-recovery-17c39fac0c.md]
issue: 'https://github.com/jfusco/agent-review-workflows/issues/12'
issues: ['https://github.com/jfusco/agent-review-workflows/issues/12']
---

# 2026-09-28 — Advisory handoff and check recovery

Implemented the protocol correction tracked by
[JFusco/agent-review-workflows issue #12](https://github.com/JFusco/agent-review-workflows/issues/12)
after seven real implementation reviews repeatedly stopped at the advisory Sol
response boundary.

Current implementation `respond` and `reply` calls now receive a stage-specific
provider schema containing only each existing finding ID, a recommended
disposition, and rationale. The schema fixes the exact ID set and item count;
the helper separately enforces canonical ordering, then restores the immutable
severity, location, evidence, correction, acceptance check, and verification
fields before normal validation and artifact persistence. The accepted ledger
and response artifacts therefore retain complete canonical findings without
requiring an advisory model to reproduce immutable prose.

The CLI also adds `rerun-checks` for transient check-environment failures. It
requires the complete target inventory and fingerprint to remain unchanged and
refuses repair or other non-recoverable states. Each rerun increments the
handoff revision, writes attempt-qualified check IDs, retains earlier receipt
files, and records both prior and current receipts in an immutable artifact. A
passing rerun reopens only a finalization that was unresolved solely because of
checks; it does not clear unrelated blocked or unresolved states.

The focused Python suite passes 64 cases, including advisory omission,
duplication, reordering, unknown IDs, attempted definition changes, canonical
artifact restoration, stale handoff rejection, receipt preservation, check-only
finalization recovery, target drift, and repair-stage rejection. The public
skill and CLI reference describe the new deterministic boundaries. No model,
effort, permission, writer, scope, verification, merge, publication, or bounded
pass policy changed.
