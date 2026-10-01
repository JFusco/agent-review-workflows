---
name: review-plan
description: Independently reviews and refines a draft plan before implementation. Use when the user requests adversarial plan review or refinement.
---

# Review a plan

Use a Claude reviewer and Codex coordinator to independently review a draft, resolve supported objections, and return a complete refined plan. Resolve their model and effort from the configured `review-plan` profile and explicit start overrides. Freeze that profile into the run and never substitute another configuration.

Read [the CLI procedure](references/cli.md) when starting or resuming a cycle. [Authoring principles](references/authoring.md) apply when changing this skill.
If the sandbox hides an existing host Claude login, follow the procedure's [guarded reviewer dispatch](references/cli.md#claude-login-visibility-in-a-sandbox) and keep coordinator stages sandboxed.

Capture the original request, complete draft, scope, constraints, success criteria, and relevant source evidence. Read applicable project instructions. Ask only for material information the conversation and project cannot establish.

Run the plan mode. For new runs, the reviewer independently critiques; the coordinator always assesses completeness, adjudicates findings, and returns any complete refinement in the same response; the reviewer independently rechecks refined plans; the helper completes deterministically. Follow the supplied stage schema and [plan protocol](references/plan-protocol.md); the helper owns canonical records, finding IDs, and routing. Existing runs retain their recorded stages. Use the current conversation for coordinator stages only when its actual model and effort exactly match the frozen run profile. Otherwise use the helper's pinned CLI sessions.

Refine deliberately. Keep changes precise, surgical, and in scope. Prefer existing components and straightforward mechanics. Challenge unnecessary abstractions, dependencies, configuration, and workflow stages. Require added complexity to solve a concrete need. Retain sound decisions; a review need not manufacture defects. Make the final choices and acceptance criteria clear enough for another engineer to implement.

Let evidence decide disagreements. Keep stable finding IDs, supported rejection reasons, and current revision context. Do not repeat a withdrawn finding without new evidence. Continue ordinary authorized review steps without approval at each step. Stop at the recorded two-pass limit or a material user decision.

Return the complete final plan, substantive refinements, and any unresolved decisions. Link the readable handoff. Do not describe an unresolved plan as ready. Plan review never authorizes application implementation, a commit, or publication. Preserve the original draft; the refined plan is a separate run artifact.
