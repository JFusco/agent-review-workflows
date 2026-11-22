---
status: "implemented"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/107", "tests/test_plan_protocol.py"]
source_tool: "codex"
source: "GitHub issue JFusco/agent-review-workflows#107"
topics: ["plan-review-protocol"]
digest: "b30b53f4074841561005d37c62080ad42a7fc2fb81b3dae43a9a489c8637c9ac"
---

# Catch plan review gaps before recheck

- Ask the coordinator to trace each material refinement through its owning component, affected callers and interfaces, applicable repository constraints, and verification before returning the plan.
- Provide a unified diff from the last accepted plan snapshot to the current plan snapshot during independent recheck. Keep the complete current plan, verify both snapshots against the ledger, and retain the existing two-refinement budget.
- Require new findings to identify a concrete consequence. Put optional preferences in review notes and preserve actionable findings at every severity.
- Cover both refinements, a material final-recheck finding, stale snapshots, and supplemental diff bounds in deterministic tests. Replay the recorded late-finding cases locally and run repository verification.
