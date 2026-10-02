---
topics: [plan-review-protocol, implementation-review-evidence]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/59']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/59'
---
# Remove obsolete review protocols

Issue #59 removes version-1 plan and implementation routing, advisory exchanges,
the older full-finding repair response, and the retired external coordinator
alias. Current runs use the frozen profile and the version-2 plan, evidence, and
repair-response contracts. An obsolete or incomplete saved run stops before
provider or writer dispatch; its artifacts remain available for inspection.
Operators start a new review from the current target and requirements instead
of editing old state or replaying a repair.

The CLI, response schema, skills, references, and regression fixtures were
updated together. The deterministic tests cover rejection before dispatch.
`pnpm run verify:ci` is the delivery gate; no provider trial is needed for this
protocol removal.
