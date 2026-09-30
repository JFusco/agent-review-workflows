---
name: review-handoff
description: Dispatches the next authorized stage of an existing plan or implementation review run. Use for a single review-chain handoff.
---

# Hand off one review stage

Use an existing run directory supplied by the user or unambiguously identified in the conversation. Ask for the run when missing or ambiguous; never select the latest run automatically. This skill does not start a review or prepare general-purpose handoff prose.

Read [Single-stage handoff](references/cli.md#single-stage-handoff) for the command sequence and resolve the installed helper and interpreter as described at the top of that reference.

Respect the invoking conversation's permissions and mode. Do not dispatch an implementation repair from Plan mode. The existing run must already authorize the stage and repair scope; the skill adds no authority.

Inspect `status RUN`. When ready and authorized, call `step RUN` exactly once, using the frozen CLI role configuration. Do not use `run`, external-coordinator flags, or direct provider calls. The helper supplies the canonical packet and stage-specific response schema and selects the receiving agent; do not summarize or rewrite its input.

Stop after that attempt, even if another stage is ready. For a non-ready status or error, report it and link [Recovery](references/cli.md#recovery); do not retry, reconcile, submit judgments, or decide for the user. If command output is incomplete, inspect `status RUN` without replaying the step.

Return the attempted stage (or that none was dispatched), resulting status, any blocker, and the existing `handoff.md` link. Distinguish completion of one stage from completion of the review.
