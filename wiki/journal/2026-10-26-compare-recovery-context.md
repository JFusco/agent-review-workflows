---
topics: [review-suite-evaluation, review-agent-profiles]
issues: ['https://github.com/JFusco/agent-review-workflows/issues/73']
---
# Recovery context in run comparisons

[Issue #73](https://github.com/JFusco/agent-review-workflows/issues/73): an
independent review of the deterministic-mechanics merge found that
`compare-runs` reported only primary profiles as context. Two runs where one
switched to a recorded fallback model, re-prompted after a contract rejection,
or raised its timeout looked like identical contexts; the switch was visible
only inside per-call records.

Run evidence now carries `agent_fallbacks`, `agent_selections`,
`fallback_history`, `response_corrections`, `timeout_history`, and `timeout`,
reported empty when an older run predates them. Each appears in
`context_differences` when the runs disagree. Comparability still depends only
on original requirements and target, and collection stays read-only.

A fixture regression in `tests/test_mechanics.py` compares a fallback-selected
run with its primary-only copy and checks historical defaults; no provider was
invoked. See the [suite-eval procedure](../../references/suite-eval.md).
