---
topics: [writer-startup-recovery]
issue: 'https://github.com/jfusco/agent-review-workflows/issues/86'
issues: ['https://github.com/jfusco/agent-review-workflows/issues/86']
---

# Recover a writer that cannot start

ASTRAL's supervisor review reached a locked repair, but nested Codex exited before
producing output. Read-only host recovery worked; the writer had no guarded route.
Issue [86](https://github.com/JFusco/agent-review-workflows/issues/86) adds strict
startup recovery and a separate single-attempt writer launcher that retains the
model command sandbox and independent recheck.

Twelve focused controlled-child tests pass, including inventory/HEAD/index drift,
malformed and uncertain receipts, stale locks/checks, process ownership, denied
stages, out-of-scope writes and deferred checks. An actual pinned-writer canary
completed one repair and passed independent Opus recheck; its initial review and
adjudication were synthetic setup. Native command output recorded denied
outside-write and loopback-network probes. Exact evidence and limits are in
[validation](../../VALIDATION.md). ASTRAL's original interrupted run and all
evidence remain unchanged during this workflow delivery.
