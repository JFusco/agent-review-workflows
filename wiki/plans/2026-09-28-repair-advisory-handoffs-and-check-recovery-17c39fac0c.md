---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows issue #12; .venv/bin/python -m unittest tests.test_review_cli (64 tests)"]
source_tool: "repository"
source: "/private/tmp/agent-review-issue-12-plan.md"
topics: ["implementation-review-evidence"]
digest: "17c39fac0cc2fdf8886a35890cfb1507a9b4ad9dc64f32323ec02bef49c6e5f7"
---

# Repair advisory handoffs and check recovery

1. Add a stage-specific advisory provider schema for new implementation `respond` and `reply` stages that exposes only finding ID, disposition, and rationale.
2. Normalize advisory assessments into the frozen canonical finding records before existing validation and artifact persistence, rejecting missing, duplicate, reordered, or unknown IDs.
3. Add a read-only `rerun-checks` operation that requires a fresh unchanged implementation target, preserves prior receipts, creates uniquely identified current receipts, increments the handoff revision, and safely reopens check-only unresolved finalization.
4. Add focused regression tests, update the implementation skill and CLI reference, and record the decision in the context wiki.
5. Run the full repository gate, deliver through issue 12 and its canonical pull request, merge after checks, then rerun the previously blocked implementation reviews with the installed updated skill.
