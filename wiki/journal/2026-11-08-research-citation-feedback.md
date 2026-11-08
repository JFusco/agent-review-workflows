---
topics: [plan-review-protocol]
plans: [2026-11-08-repair-research-citation-validation-feedback-488b0fbd3f.md]
issues: ['https://github.com/JFusco/agent-review-workflows/issues/95']
---
# Research citation validation and retry feedback

The observed Migrator review rejected two briefs before accepting the third.
The first linked web sources to Brain searches. The second omitted two local
source IDs from its searches even though successful command output showed both
files were read. Those rejected calls consumed approximately 23 minutes.
The explicit retry still received the first rejection reason.

The validator now reports all search-reference inconsistencies together with
source IDs and zero-based search positions. Provider schema descriptions explain
the existing linkage contract and require a consistency check before submission.
The helper continues to reject unsupported evidence without inventing reads or
repairing briefs automatically.

Read-only contract failures retain append-only rejection history separately from
the one-correction-per-stage/revision/candidate budget. Retry uses the latest
same-stage/revision rejection. Existing correction records and raw call outputs
remain intact; older saved runs need no migration. Run comparison exposes the
additional recovery history without claiming provider evidence.

Regression fixtures cover the two-failure sequence, exhausted correction budget,
explicit retries, unchanged raw responses, successful acceptance, legacy history,
stage/revision isolation, malformed references, and provider schema delivery.
The delivery check is `pnpm run verify:ci`; results are recorded in the pull
request. No additional paid provider trial is needed for these deterministic
boundaries, and no live failure-rate improvement is claimed.

All six review skills under each of `~/.claude/skills`, `~/.codex/skills`, and
`~/.agents/skills` were verified through the installer to resolve to the maintained
checkout. Existing correct links were retained. The original active review's
artifacts and unrelated Graphify manifest changes remain outside this fix.
