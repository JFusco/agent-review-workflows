---
topics: [implementation-review-evidence]
plans: [2026-09-28-constrain-implementation-review-adjudication-findings-7eeb3aeff9.md]
---
# Constrain adjudication findings

Issue [#14](https://github.com/JFusco/agent-review-workflows/issues/14) records a failure found by rerunning real implementation reviews after the advisory-response repair. Context Wiki, Design Passport, and QA Operations each completed implementer and reviewer assessments, but Astra adjudication returned an additional finding. The existing deterministic guard rejected all three handoffs with `Only independent review/recheck may introduce new findings.`, so no invalid state was persisted.

Implementation `respond`, `reply`, and `adjudicate` now share one constrained decision contract: every existing ID exactly once in canonical order, with only disposition and rationale supplied by the model. The helper restores immutable definitions and verification fields before validation. Advisory stages remain non-authoritative; normalized adjudication still applies the coordinator's authoritative decisions.

Regression coverage exercises all three stages and rejects omissions, duplicates, reordering, unknown IDs, and injected definition fields. The Python unit suite and skill validator passed before full repository verification.

Affected durable topic: [implementation review evidence](../topics/implementation-review-evidence.md).
