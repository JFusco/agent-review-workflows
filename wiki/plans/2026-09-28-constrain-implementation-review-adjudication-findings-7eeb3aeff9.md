---
status: "implemented"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/14; tests/test_review_cli.py; skills/review-implementation/SKILL.md"]
source_tool: "repository"
source: "/private/tmp/agent-review-adjudication-plan.md"
topics: ["implementation-review-evidence"]
digest: "7eeb3aeff96274506072fcf26dc4d9bca1b99df1405f7d8963be3494b46b6dc2"
---

# Constrain implementation-review adjudication findings

## Objective

Prevent the coordinator adjudication stage from introducing or redefining reviewer-owned findings while preserving authoritative dispositions.

## Steps

1. Extend the current implementation decision-schema boundary from `respond` and `reply` to `adjudicate`.
2. Accept only every existing finding ID in canonical order with a disposition and rationale.
3. Restore immutable definition and verification fields before ordinary validation and persistence.
4. Add regression coverage across all three decision stages and update the skill, CLI reference, README, and wiki contract.
5. Run skill validation and `pnpm run verify:ci`, then retry the rejected real adjudications.

## Boundaries

- Preserve independent review and recheck as the only stages that may introduce findings.
- Preserve the coordinator as the only authoritative disposition owner.
- Add no fallback model, compatibility path, recursive delegation, or new workflow stage.
