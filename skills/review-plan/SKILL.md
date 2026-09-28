---
name: review-plan
description: Independently reviews and refines a draft plan before implementation. Use when the user requests adversarial plan review or refinement.
---

# Review a plan

Use a Claude reviewer and Codex coordinator to independently review a draft, resolve supported objections, and return a complete refined plan. Resolve their model and effort from the configured `review-plan` profile and explicit start overrides. Freeze that profile into the run and never substitute another configuration.

Read [the CLI procedure](references/cli.md) when starting or resuming a cycle. [Authoring principles](references/authoring.md) apply when changing this skill.

Capture the original request, complete draft, scope, constraints, success criteria, and relevant source evidence. Read applicable project instructions. Ask only for material information the conversation and project cannot establish.

Run the plan mode. The reviewer independently critiques; the coordinator evaluates its handoff, exchanges a rebuttal where needed, and refines the whole plan; the reviewer rechecks material revisions; the coordinator returns the final plan. Use the current conversation for coordinator stages only when its actual model and effort exactly match the frozen run profile. Otherwise use the helper's pinned CLI sessions.

Refine deliberately. Keep changes precise, surgical, and in scope. Prefer existing components and straightforward mechanics. Challenge unnecessary abstractions, dependencies, configuration, and workflow stages. Require added complexity to solve a concrete need. Retain sound decisions; a review need not manufacture defects. Make the final choices and acceptance criteria clear enough for another engineer to implement.

Let evidence decide disagreements. Keep stable finding IDs, supported rejection reasons, and current revision context. Do not repeat a withdrawn finding without new evidence. Continue ordinary authorized review steps without approval at each step. Stop at the recorded two-pass limit or a material user decision.

Return the complete final plan, substantive refinements, and any unresolved decisions. Link the readable handoff. Do not describe an unresolved plan as ready. Plan review never authorizes application implementation, a commit, or publication. Preserve the original draft; the refined plan is a separate run artifact.
