---
name: review-implementation
description: Independently reviews an implementation, resolves findings, and repairs accepted defects. Use when the user requests an adversarial implementation review and repair cycle.
---

# Review an implementation

A Claude reviewer independently reviews and rechecks. A Codex coordinator adjudicates and finalizes. A separate Codex implementer responds and makes accepted repairs. Resolve each model and effort from the configured `review-implementation` profile and explicit start overrides. Freeze that profile into the run and never substitute another configuration.

Read [the CLI procedure](references/cli.md) to start or resume. [Authoring principles](references/authoring.md) apply when changing this skill.

Establish the requested change, acceptance criteria, authorized repair scope, explicit local Git base, and project checks from the conversation and repository. Inspect applicable project instructions and Git state. Preserve intentional and unrelated changes. Follow project issue/branch/worktree requirements before a repair. This skill grants no authority to merge, publish, deploy, or expand the assignment.

Run implementation mode with explicit scoped files, `--base`, and at least one authorized local check command. The initial reviewer receives the actual scoped diff, full scoped sources, verbatim requirements, and current check receipts. New findings identify a scoped file with severity, evidence, a surgical correction, and an acceptance check. The implementer recommends acceptance or rejection without writing; the reviewer independently replies; the coordinator alone adjudicates; the implementer makes accepted scoped repairs; the reviewer checks the revised diff and fresh checks. Only the implementer writes implementation files. Use the current conversation for coordinator stages only when its actual model and effort exactly match the frozen run profile; otherwise the helper launches pinned sessions.

Keep repairs precise and surgical. Prefer existing components and simple mechanisms. Do not broaden the assignment to speculative cleanup or unrelated architecture work. Source, reproduced failures, and actual checks support decisions; agent agreement is insufficient verification.

Continue ordinary authorized steps without repeated approval. At most two repair/recheck passes run automatically. Surface unresolved product decisions and missing permissions. Never repeat an interrupted repair blindly or overwrite unexpected edits. Use the documented recovery procedure.

Return what changed, required checks and their actual outcomes, unresolved findings, and the final target reviewed. Link the handoff and distinguish fixture evidence from live CLI or production evidence. Never call a blocked or incomplete cycle verified.
