---
topics: [review-agent-profiles]
plans: [2026-11-04-bound-codex-launcher-recovery-518cb66bca.md]
issues: ['https://github.com/JFusco/agent-review-workflows/issues/83']
---
# Recover a bounded Codex adjudication launch

The ASTRAL investigation reported Codex 0.163.0-alpha.11 failing before model
execution inside the managed invoking sandbox. A disposable diff fixture
reproduced the exact in-process app-server permission error. Its cause remains
unknown; neither SQLite warnings nor successful anonymous socketpair creation
establish the denied operation. ASTRAL and its existing evidence were untouched.

The repair adds a separate `step --codex-read-only` boundary. The selected frozen
role, target freshness, current checks and owned-process lock remain mandatory.
Only one ready Codex review/adjudicate/recheck attempt is eligible. No check,
research, writer, finalization, corrective retry or fallback can run through it.
The existing Claude reviewer-only route is unchanged. The exact startup failure
now produces a bounded stage/receipt diagnostic without echoing arbitrary stderr.

The actual managed conversation invoked the guard through explicit host-tool
approval. Astra/max completed fixture adjudication, preserving the failed call,
review artifact, source and checks. Its session confirms read-only model execution
and no approvals; actual model commands were denied project writes, temporary
file writes and loopback TCP. The outer launcher needs approved host access;
nested startup remains unsupported in the reproduced context. No credentials
were inspected or copied and no global configuration was changed.

See [validation](../../VALIDATION.md#codex-guarded-launcher-recovery-2026-11-04)
for the run/session IDs and the explicit synthetic-reviewer limitation. Eleven
focused command tests cover failed receipts, malformed and stale checks, stage
guards, live process ownership, recovery and single-attempt behavior. Full CI
and independent delivery review are required before merging the issue branch.

An initial Opus 5.5/high review found two gaps: forbidden-stage tests stopped at
protocol validation before reaching the guard, and recovery links did not route
directly to the new boundary. The corrections use valid plan/implementation
states, assert the guard's own rejection, mutation-check those exclusions, and
link each entrypoint to the right procedure. The first report remains partial:
Astra dispatch required separate explicit authorization, and source corrections
require a fresh review rather than reusing its stale target. The initial full
host CI passed 190 Python and 17 tooling tests; final host CI passed 191 Python
and 17 tooling tests, lint and wiki integrity. The initial nested CI failure was an existing macOS sandbox
initialization restriction, preserved separately from the host pass.
