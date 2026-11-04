# Writer startup recovery

Issue [86](https://github.com/JFusco/agent-review-workflows/issues/86) separates
a recognized pre-model Codex startup failure from uncertain implementation work.
`recover-startup` restores readiness only with an unchanged full inventory,
HEAD/index, target, original repair lock and check context, matching original
call/transport, no response and a stopped owned group. It retains failed receipts
and records recovery without consuming an actual repair pass. Generic failures,
partial writes and interrupted model work still use reconciliation.

An explicitly approved `step --codex-repair-only` permits one first locked writer
with the existing project-only command sandbox and denied execution-tool network.
It retains all post-write scope guards. Acceptance saves the new target and one
repair pass, then stops at blocked recheck. Sandbox `retry` runs post-repair checks;
the independent reviewer still verifies the repair. The launcher cannot run
configured checks, select fallback, re-prompt or advance another provider stage.

The source of truth for exact commands and prerequisites is
[the shared CLI procedure](../../references/cli.md#repair-startup-recovery-and-guarded-writer-launch).
Controlled-child regressions establish deterministic boundaries; provider
execution is recorded separately in [validation](../../VALIDATION.md).
