---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#30; scripts/review_cli.py; tests/test_review_cli.py"]
source_tool: "codex"
source: "codex:/Users/joe.fusco/.codex/sessions/2026/09/29/rollout-2026-09-29T21-07-51-01a0efda-8863-70d2-b055-0401678ad174.jsonl"
topics: ["review-agent-profiles"]
digest: "bcf5c5e977772caa41ce22f12e4007d6728666b779b41da50244e824771655bb"
---

# Upgrade the implementer to Sol 6.1 Extra High

## Summary

Change the built-in implementer for newly started implementation reviews to `gpt-6.1-sol` with `xhigh` reasoning. Keep Astra at `gpt-6-astra` / `max` for orchestration and Opus at `claude-opus-5-5` / `high` for independent review and recheck.

Sol 6.1 supports `xhigh` according to the [official model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol). This delivery establishes configuration and compatibility through deterministic tests.

## Implementation changes

- In `scripts/review_cli.py`, retain `V1_PROFILES` exactly as the historical configuration. After copying it into `DEFAULT_PROFILES`, change only the implementation implementer’s model to `gpt-6.1-sol`.
- Preserve stored profiles for existing schema-version-2 runs and historical pins for schema-version-1 runs. Do not migrate run artifacts or resume existing sessions with another model.
- Retain configuration precedence: explicit start flags → installation-local profile → built-in defaults. An explicit Sol 6 override continues to select Sol 6.
- Preserve the five-stage protocol, Astra’s repair lock, independent Opus recheck, single implementation writer, scope guards, and provider rejection without fallback.
- Update the README, CLI reference, and `review-agent-profiles` wiki topic to describe the new default and existing-run behavior. Keep skill entrypoints and agent metadata model agnostic.
- Append local validation results to the validation record. Preserve historical Sol 6 trial evidence and state that it does not establish Sol 6.1 provider execution or repair quality.
- Public change: the default implementer model for new runs. No new flags, configuration fields, schemas, dependencies, or workflow stages.

## Test plan

Extend `tests/test_review_cli.py` with focused coverage proving:

- New implementation runs freeze the exact Sol 6.1 / `xhigh`, Astra / `max`, and Opus / `high` profile into state and the original snapshot.
- Initial and resumed implementer commands use the frozen model and effort.
- Existing schema-version-2 runs frozen to Sol 6 still launch Sol 6 after loading under the upgraded helper.
- Schema-version-1 runs retain their original pins; modifying new defaults cannot alter the legacy profile table.
- Explicit installation and per-run implementer overrides retain precedence; plan reviews retain their current profile.

Run `pnpm run verify:ci`. Use the existing suite for permission, freshness, interrupted recovery, and independent-recheck coverage. No paid or provider-backed trial is required for this configuration change.

## Delivery and rollback

- Start from a safe checkout of freshly pulled `main`. Create and read back one GitHub issue through `github-issue-creator`, then branch as `codex/<issue-number>-sol-61-implementer`.
- Archive the executed plan, add a wiki journal entry, update the profile topic, and run the required wiki discovery, graph build, and integrity checks. Refresh Graphify 0.9.36 and review generated changes before staging.
- Commit as `feat(review): Upgrade implementer to Sol 6.1`. Push normally and open a PR using the canonical template with the closing issue reference, verification, and risk/rollback.
- Wait for required checks, merge, verify the issue automatically closed, then return to updated `main` and confirm a clean checkout matching `origin/main`.
- Main risk: the selected CLI/account may reject Sol 6.1. Existing rejection behavior stops the run. Rollback restores the previous new-run default; an explicit Sol 6 override is also available.

Assumption: this changes the repository-wide default for new runs; user overrides and existing runs retain their selected settings.
