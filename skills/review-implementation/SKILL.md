---
name: review-implementation
description: Independently reviews an implementation, resolves findings, and repairs accepted defects. Use when the user requests an adversarial implementation review and repair cycle.
---

# Review an implementation

A Claude reviewer independently reviews and rechecks. A Codex coordinator adjudicates, locks accepted repairs, and finalizes successful rechecks. A separate Codex implementer makes the locked repairs. Resolve each model and effort from the configured `review-implementation` profile and explicit start overrides. Freeze that profile into the run and never substitute another configuration.

Read [the CLI procedure](references/cli.md) to start or resume. [Authoring principles](references/authoring.md) apply when changing this skill.
If the sandbox hides an existing host Claude login, follow the procedure's [guarded reviewer dispatch](references/cli.md#claude-login-visibility-in-a-sandbox) and keep checks and Codex stages sandboxed.

Establish the requested change, acceptance criteria, authorized repair scope, explicit local Git base, and project checks from the conversation and repository. Inspect applicable project instructions and Git state. Preserve intentional and unrelated changes. Follow project issue/branch/worktree requirements before a repair. This skill grants no authority to merge, publish, deploy, or expand the assignment.

Run implementation mode with explicit scoped files, `--base`, and at least one authorized local check command. The initial reviewer receives the actual scoped diff, full scoped sources, verbatim requirements, and current check receipts. New findings identify a scoped file with severity, evidence, a surgical correction, and an acceptance check. The coordinator decides the findings and locks accepted repairs; the implementer repairs once; the reviewer rechecks the revised diff and fresh checks. Only the implementer writes implementation files. Use the current conversation for coordinator stages only when its actual model and effort exactly match the frozen run profile; otherwise the helper launches pinned sessions.

The coordinator must retain canonical finding definitions but may add a sequential, evidence-backed finding within the authorized scope during adjudication. The adjudication entry locks accepted findings, authorized files, checks, fingerprint, and revision before repair. Its decisions, lock, and current scoped diff are visible in `handoff.md`; the same lock reaches the implementer. A failed or incomplete recheck ends unresolved without another repair. When configured checks failed for a transient environment reason and the target is provably unchanged, use the documented `rerun-checks` recovery.

For newly started runs, the repair response assesses accepted finding IDs and rationales only. The helper reconstructs canonical findings from saved state; the writer does not restate definitions, dispositions, or independent verification. Existing runs retain their saved response contract. See the CLI procedure for the exact schema and recovery behavior.

Follow the shared [review style](references/cli.md#review-style). Source, reproduced failures, and actual checks support decisions; agent agreement is insufficient verification.

Continue ordinary authorized steps without repeated approval. New runs allow one repair and one recheck. Surface unresolved product decisions and missing permissions. Never repeat an interrupted repair blindly or overwrite unexpected edits. Use the documented recovery procedure.

Return what changed, required checks and their actual outcomes, unresolved findings, and the final target reviewed. Link the handoff and distinguish fixture evidence from live CLI or production evidence. Never call a blocked or incomplete cycle verified.
