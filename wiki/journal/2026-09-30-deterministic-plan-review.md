---
topics: [plan-review-protocol]
plans: [2026-09-30-deterministic-efficient-plan-review-aacda16d5f.md]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/33']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/33'
---
# Deterministic plan review

Issue [#33](https://github.com/JFusco/agent-review-workflows/issues/33) implements
the approved [plan](../plans/2026-09-30-deterministic-efficient-plan-review-aacda16d5f.md)
for efficient review with deterministic handoffs. New plan runs retain independent
Opus review and Astra completeness assessment, combine adjudication and
refinement, and recheck every refined document. The helper completes successful
reviews without an additional model call.

The response schema exposes only the fields each stage owns. The helper assigns
new finding IDs, validates exact assessment coverage, and carries immutable
definitions and earlier records forward. Accepted artifacts retain both submitted
output and normalized canonical findings. Final-plan rendering uses the accepted
snapshot so later draft changes cannot alter a completed result.

The bound remains two refinement attempts. User decisions pause explicitly, and
incomplete second rechecks end unresolved. Legacy runs keep their recorded
contracts; implementation protocols and model defaults are unchanged. No review
workflow gains implementation, publication, merge, or deployment authority.

Eighteen new deterministic fixture tests cover the changed contract, transitions,
recovery, freshness, permissions, and compatibility. Existing single-stage tests
also cover new-plan dispatch. The delivery gate is `pnpm run verify:ci`; these are
local fixtures, not live-provider or model-quality evidence. The durable decisions
are recorded in [Plan review protocol](../topics/plan-review-protocol.md).
