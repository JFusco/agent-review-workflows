---
topics: [implementation-review-evidence, review-delivery, review-suite-evaluation]
plans: [2026-10-04-move-review-mechanics-into-deterministic-code-05d32c1a75.md]
issues: ['https://github.com/JFusco/agent-review-workflows/issues/62']
---
# Move review mechanics into the existing helper

Issue #62 executes the independently reviewed plan after seven accepted findings
passed independent recheck. New implementation state version 3 removes the
provider finalization call and retains canonical finding definitions, role pins,
repair locks, current check gates, scope guards, and independent rechecks. Saved
version-2 coordinator contracts remain resumable without migration.

`delivery-evidence` collects local and hosted mechanical gates with repeated
observations, explicit unavailable reasons, and no semantic coverage inference.
`compare-runs` separates launch attempts, accepted provenance, provider/check
time, and individual telemetry. It does not infer token/cost totals or savings.
Both commands are read-only and use the existing helper rather than another
framework. Semantic delivery and quality judgments remain with the invoking
model. Jev evaluation is deferred until a concrete semantic workload and recorded
baseline warrant it.

Temporary Git and mocked provider/GitHub fixtures cover compatibility, entry
points, immutable completion, orphan/render recovery, blocked post-repair
checks, historical rendering, delivery conditions, event/usage accounting, and
changing evidence. `tests/test_mechanics.py`, `tests/test_review_cli.py`, and
`pnpm run verify:ci` provide local verification. These fixtures do not prove
live-provider performance, billed savings, hosted acceptance, or production
behavior. Rollback preserves version-3 artifacts for a compatible helper and
never retags them as version 2.
