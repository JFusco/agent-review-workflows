---
topics: [review-agent-profiles]
issue: 'https://github.com/jfusco/agent-review-workflows/issues/64'
issues: ['https://github.com/jfusco/agent-review-workflows/issues/64']
---
# Longer review calls and recorded fallback models

[Issue #64](https://github.com/JFusco/agent-review-workflows/issues/64) responds to
reviews taking around 15 minutes and stopping on unavailable models or usage
limits. New runs now allow 30 minutes per call/check and retain the existing
1–3600-second override.

Read-only reviewer and coordinator roles freeze bounded ordered fallback
candidates alongside the primary profile. Classified capacity failures retain
their call evidence and select a fresh session using the canonical packet.
Selections persist through subsequent stages and recovery, with visible history.
The default reviewer can move from Claude to Codex; a host reviewer-only call
pauses before dispatching Codex so the caller can resume sandboxed execution.

Invalid handoffs, authentication/permission failures, target drift, active
process groups, and manual interruption stop normally. Writers never replay:
interrupted repairs retain partial edits and require inspected reconciliation.
Existing saved runs retain their settings and gain no implicit fallback.

The [agent profile topic](../topics/review-agent-profiles.md) and
[CLI procedure](../../references/cli.md#recorded-model-fallback) describe the
contract. Regression evidence is deterministic fixture execution, including a
real local process timeout, not live model or production evidence. The required
`pnpm run verify:ci` gate covers Python, JavaScript, temporary-repository hooks,
and wiki integrity; final execution results are recorded in the delivery PR.
