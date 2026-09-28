---
status: "implemented"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/17; tests/test_review_cli.py; scripts/review_cli.py"]
source_tool: "repository"
source: "/private/tmp/agent-review-adjudication-discovery-plan.md"
topics: ["implementation-review-evidence"]
digest: "a85c7cc5ea65ca3e35558691bb4d0d4ee9ea628113a8286113d13ca47862fa29"
---

# Preserve in-scope adjudication discoveries

## Objective

Allow the coordinator to retain newly established, in-scope gaps during adjudication without weakening advisory immutability, finding identity, repair scope, or independent verification.

## Steps

1. Keep `respond` and `reply` on the existing ID-only advisory schema and canonical restoration path.
2. Restore the full adjudication finding schema while preserving every existing finding and its immutable definition and verification state.
3. Permit only sequential new adjudication IDs with scoped locations, `UNVERIFIED` status, and no verification receipts.
4. Route accepted additions through the existing repair and independent recheck stages.
5. Add focused regression coverage and update the skill, CLI reference, README, and wiki contract.

## Boundaries

- Preserve pinned roles and model settings.
- Preserve one scoped writer and the two-pass limit.
- Do not allow advisory stages to introduce or mutate findings.
