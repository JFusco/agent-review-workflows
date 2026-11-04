---
name: review-plan
description: Researches, independently reviews, and refines a draft plan before implementation. Use when the user requests adversarial plan review or refinement.
---

# Review a plan

Use a separate Codex researcher, Claude reviewer, and Codex coordinator to independently review a draft, resolve supported objections, and return a complete refined plan. Resolve their model and effort from the configured `review-plan` profile and explicit start overrides. Freeze the primary profile and ordered fallback candidates into the run. Only the helper may select a recorded read-only fallback under the [shared policy](references/cli.md#recorded-model-fallback); never substitute an unrecorded configuration.

Read [the CLI procedure](references/cli.md) when starting or resuming a cycle. [Authoring principles](references/authoring.md) apply when changing this skill.
For sandbox-hidden Claude login, follow [Claude reviewer dispatch](references/cli.md#claude-login-visibility-in-a-sandbox); for researcher startup failure, follow [guarded researcher launch](references/cli.md#research-startup-recovery-and-guarded-researcher-launch); for other Codex startup failures, follow [Codex launch recovery](references/cli.md#codex-launch-recovery). Keep checks and writers sandboxed; host launcher access requires the documented guard and invoking-tool approval.

Capture the original request, complete draft, scope, constraints, success criteria, and relevant source evidence. Read applicable project instructions. Ask only for material information the conversation and project cannot establish.

Run plan mode with [required research](references/research.md) before independent review. The researcher investigates existing solutions, consults Brain, and reads current primary web sources; a validated cited brief is required even when source limitations must be disclosed. The reviewer independently critiques; the coordinator always assesses completeness, adjudicates findings, and returns any complete refinement in the same response; the reviewer independently rechecks refined plans; the helper completes deterministically. Follow the supplied stage schema and [plan protocol](references/plan-protocol.md); the helper owns canonical records, finding IDs, and routing. Use the current conversation for coordinator stages only when its actual model and effort exactly match the frozen run profile. Otherwise use the helper's pinned CLI stage dispatch with [helper-owned packet delivery and sessions](references/cli.md#packet-delivery-and-sessions).

Follow the shared [review style](references/cli.md#review-style). Retain sound decisions; a review need not manufacture defects. Make the final choices and acceptance criteria clear enough to implement.

Assess the complete accepted brief for source applicability, overlooked reuse, unsupported assumptions, and unjustified components. Reuse it through ordinary refinements; material changes to requirements or scope require a new run. Let evidence decide disagreements. Keep stable finding IDs, supported rejection reasons, and current revision context. Do not repeat a withdrawn finding without new evidence. Continue ordinary authorized review steps without approval at each step. Stop at the recorded two-pass limit or a material user decision.

Return the complete final plan, substantive refinements, and any unresolved decisions. Link the readable handoff. Do not describe an unresolved plan as ready. Plan review never authorizes application implementation, a commit, or publication. Preserve the original draft; the refined plan is a separate run artifact.
