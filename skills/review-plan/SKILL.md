---
name: review-plan
description: Reviews a draft plan with Opus 5.5 High and refines it with Astra 6 Max before implementation. Use when the user requests adversarial plan review or refinement.
---

# Review a plan

Use Claude Code and Codex CLI to independently review a draft, resolve supported objections, and return a complete refined plan. All Astra work uses `gpt-6-astra` at `max`; Opus uses `claude-opus-5-5` at `high`. Never substitute another configuration.

Read [the CLI procedure](references/cli.md) when starting or resuming a cycle. [Authoring principles](references/authoring.md) apply when changing this skill.

Capture the original request, complete draft, scope, constraints, success criteria, and relevant source evidence. Read applicable project instructions. Ask only for material information the conversation and project cannot establish.

Run the plan mode. Opus independently reviews; Astra evaluates its handoff, exchanges a rebuttal where needed, and refines the whole plan; Opus rechecks material revisions; Astra returns the final plan. Use the current conversation for Astra stages only when its actual configuration is Astra 6 Max. Otherwise use the helper's pinned CLI sessions.

Refine deliberately. Keep changes precise, surgical, and in scope. Prefer existing components and straightforward mechanics. Challenge unnecessary abstractions, dependencies, configuration, and workflow stages. Require added complexity to solve a concrete need. Retain sound decisions; a review need not manufacture defects. Make the final choices and acceptance criteria clear enough for another engineer to implement.

Let evidence decide disagreements. Keep stable finding IDs, supported rejection reasons, and current revision context. Do not repeat a withdrawn finding without new evidence. Continue ordinary authorized review steps without approval at each step. Stop at the recorded two-pass limit or a material user decision.

Return the complete final plan, substantive refinements, and any unresolved decisions. Link the readable handoff. Do not describe an unresolved plan as ready. Plan review never authorizes application implementation, a commit, or publication. Preserve the original draft; the refined plan is a separate run artifact.
