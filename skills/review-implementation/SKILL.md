---
name: review-implementation
description: Reviews an implementation with Opus 5.5 High, resolves findings with Astra 6 Max, and repairs accepted defects with Sol 6 XHigh. Use when the user requests an adversarial implementation review and repair cycle.
---

# Review an implementation

Astra `gpt-6-astra` at `max` coordinates and adjudicates. Opus `claude-opus-5-5` at `high` independently reviews and rechecks. Sol `gpt-6-sol` at `xhigh` responds and implements accepted repairs. Pin these settings on every launch and resumption.

Read [the CLI procedure](references/cli.md) to start or resume. [Authoring principles](references/authoring.md) apply when changing this skill.

Establish the requested change, exact review target, acceptance criteria, authorized repair scope, and project checks from the conversation and repository. Inspect applicable project instructions and Git state. Preserve intentional and unrelated changes. Follow project issue/branch/worktree requirements before a repair. This skill grants no authority to merge, publish, deploy, or expand the assignment.

Run implementation mode with explicit scoped files and authorized local check commands. Opus reviews independently; Sol accepts or challenges each finding; Opus responds; Astra decides from evidence; Sol makes accepted scoped repairs; Opus checks the actual result. Only Sol writes implementation files. Use the current conversation for Astra stages only when it is already Astra 6 Max; otherwise the helper launches pinned sessions.

Keep repairs precise and surgical. Prefer existing components and simple mechanisms. Do not broaden the assignment to speculative cleanup or unrelated architecture work. Source, reproduced failures, and actual checks support decisions; agent agreement is insufficient verification.

Continue ordinary authorized steps without repeated approval. At most two repair/recheck passes run automatically. Surface unresolved product decisions and missing permissions. Never repeat an interrupted repair blindly or overwrite unexpected edits. Use the documented recovery procedure.

Return what changed, required checks and their actual outcomes, unresolved findings, and the final target reviewed. Link the handoff and distinguish fixture evidence from live CLI or production evidence. Never call a blocked or incomplete cycle verified.
