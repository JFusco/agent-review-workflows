---
issues: ['https://github.com/JFusco/agent-review-workflows/issues/47', 'https://github.com/JFusco/agent-review-workflows/issues/62', 'https://github.com/JFusco/agent-review-workflows/issues/73']
---
# Review-suite evaluation

The opt-in `review-suite-eval` skill compares two saved runs in the invoking
conversation. Identical original requirements and targets are the prerequisite
for a comparative conclusion. Profile, recorded recovery, instructions, and
check-command differences provide context. Existing call, ledger, finding, and check
artifacts provide observable outcomes and costs; missing measurements remain
unavailable. Quality judgments require explicit maintainer expectations.

The `compare-runs` command collects recorded inputs without altering runs,
calling providers/GitHub, or executing project commands. Its procedure is maintained in
[suite-eval.md](../../references/suite-eval.md).

Issue #62 separates recorded launch attempts from accepted CLI, external,
deterministic, operator, fixture, and unclassified events. Provider and check
process durations retain measured coverage; missing values remain unavailable.
Individual Claude/Codex usage records preserve source/accounting scope without
cross-call token/cost totals, cumulative deltas, or inferred billed savings.
Historical unsupported protocols can be inspected without migration. Any changed
input path set or bytes forces UNKNOWN; optional telemetry gaps alone do not
invalidate exact original-input comparability. Semantic quality still requires
explicit maintainer expectations.

[Issue #73](https://github.com/JFusco/agent-review-workflows/issues/73) adds
recorded recovery context: frozen fallbacks, selections, fallback history,
response corrections, and timeout changes appear as context differences, empty
for older runs, without changing input comparability. See the
[journal entry](../journal/2026-10-26-compare-recovery-context.md).
