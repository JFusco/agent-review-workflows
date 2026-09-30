---
topics: [review-agent-profiles]
plans: [2026-09-29-upgrade-the-implementer-to-sol-6-1-extra-high-bcf5c5e977.md]
issue: 'https://github.com/jfusco/agent-review-workflows/issues/30'
issues: ['https://github.com/jfusco/agent-review-workflows/issues/30']
---

# Upgrade the new-run implementer to Sol 6.1

[JFusco/agent-review-workflows issue #30](https://github.com/JFusco/agent-review-workflows/issues/30)
changes the built-in implementation writer to `gpt-6.1-sol` / `xhigh` for new
runs. Astra remains `gpt-6-astra` / `max`, and independent Opus review and
recheck remain `claude-opus-5-5` / `high`.

The helper changes only the copied new-run default. Historical `V1_PROFILES`
remain intact, and existing version-2 runs continue to use their stored
profiles. No artifact migration or session model switch is introduced.
Installation-local and explicit start settings retain their per-field
precedence, including an explicit Sol 6 selection. The five-stage protocol,
repair lock, single writer, permission boundaries, and rejection without
fallback are unchanged.

Regression coverage pins the exact new profile in state and original snapshots,
checks initial and resumed implementer commands, reloads older Sol 6 runs,
verifies legacy defaults are independent, and exercises overrides and unchanged
plan-review settings. Tests isolate runtime configuration from the developer's
ignored installation file. The [validation record](../../VALIDATION.md) records
the executed checks and separates local evidence from the historical Sol 6
provider trials. No Sol 6.1 provider execution or repair quality is established.

The executed plan was recovered through wiki discovery and archived with this
delivery. Discovery also reported two existing cross-repository association
ambiguities, “Standardize Git delivery in seven repositories” and “Standardize
commit messages and Graphify across eight repositories”; their classification
is outside this issue's scope and remains unchanged.

If the selected CLI/account rejects Sol 6.1, the existing blocker remains
visible without fallback. Rollback restores the prior new-run default; a new
run can also explicitly select `gpt-6-sol`.
