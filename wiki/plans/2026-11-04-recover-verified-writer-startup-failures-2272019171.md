---
status: "partial"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/86; /private/tmp/review-writer-recovery-no5Rij/writer-tests.log"]
source_tool: "codex"
source: "/private/tmp/review-writer-recovery-no5Rij/executed-plan.md"
topics: ["writer-startup-recovery"]
digest: "2272019171418ea031c3033cd4c23a5acfeb5521db4367247c9fa9d3bed83c0b"
---

# Recover verified writer startup failures

Implement issue JFusco/agent-review-workflows#86 without changing ASTRAL or global defaults.

1. Add recover-startup for a recognized Codex pre-model startup failure only after full inventory, target, HEAD/index, repair-lock, check-context, call-identity/transport and stopped-group validation. Preserve failures and the actual one-repair limit.
2. Add a single-attempt codex-repair-only guard retaining the frozen writer, project-only command sandbox and post-write checks. Defer configured checks and independent recheck to sandbox continuation.
3. Cover public success, denial, stale/malformed/ambiguous evidence, partial writes, process ownership and repeat attempts with controlled children. Validate the actual pinned writer on a harmless disposable project; do not treat synthetic setup as independent review.
4. Update shared skill procedures, validation and wiki, refresh Graphify, run verify:ci and focused independent review. Deliver the scoped issue branch and PR, merge only under the user's direct tangent authorization, and verify installed symlinks use the maintained bytes.
5. Return to ASTRAL's preserved locked six-finding repair using the supported recovery. Apply one repair and independent recheck; prepare a new byte-bound fixture execution request only after clearance. Do not reuse consumed execution approval.
