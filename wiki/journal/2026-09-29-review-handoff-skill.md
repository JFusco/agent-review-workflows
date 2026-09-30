---
topics: [implementation-review-evidence]
plans: [2026-09-29-add-a-minimal-review-handoff-skill-665a8120fd.md]
issue: 'https://github.com/jfusco/agent-review-workflows/issues/27'
issues: ['https://github.com/jfusco/agent-review-workflows/issues/27']
---

# 2026-09-29 — Single-stage review handoff skill

[Issue #27](https://github.com/JFusco/agent-review-workflows/issues/27) adds
`review-handoff` for dispatching one authorized stage of an existing review run.
It uses the existing helper's `status` and `step` commands, preserving canonical
packets, frozen role configuration, scope checks, and revision validation. It
does not introduce another model call, protocol stage, schema, or recovery path.

The skill stops after one attempt and reports status and the existing handoff
artifact. Missing or ambiguous runs require clarification. Non-ready runs and
implementation repair requests in Plan mode do not dispatch. The installer now
includes the skill with the same conflict preflight and shared references.

The authoring approach follows the linked Anthropic and OpenAI guidance in
`references/authoring.md`: concise discovery and instructions, deterministic
existing tools, and narrowly scoped behavior. Command fixtures cover single-stage
dispatch, frozen settings, non-ready states, and stale-target rejection; installer
fixtures cover idempotence and preservation. `VALIDATION.md` records static
request walkthroughs separately from fixture execution. No provider-backed trial
was performed for this change.
