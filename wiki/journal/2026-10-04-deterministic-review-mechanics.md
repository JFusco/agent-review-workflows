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

Final parsing regression: duplicate keys, nonfinite values, and numeric overflow
in optional JSONL usage are unavailable evidence. They cannot poison the JSON
packet or invalidate otherwise comparable original inputs. The shared strict
JSON decoder also rejects unrepresentable numeric values in required inputs.

The bounded implementation review accepted four additional defects
(FIND-001 through FIND-004). Repairs reuse exact receipt membership, nested
checkout stability, required-check validation for both observations, and the
complete frozen-profile validator before local completion mutates evidence.
Four focused temporary-repository/mocked-boundary regressions failed before
repair and pass afterward. The full gate passed lint, 142 Python tests, and
17 tooling tests, then exited 2 for the stale generated wiki graph. Generated
graphs remained unchanged under that repair scope. Independent recheck in run
`c8622599-17f3-4acc-8e56-c079da647e65` confirmed all four code fixes and found
no new defects, but marked the full acceptance checks BLOCKED because the wiki
gate failed. That run remains unresolved with its original evidence intact.

The invoking agent refreshed the wiki graph and Graphify 0.9.36 map after the
bounded cycle stopped. Subsequent review and delivery results are recorded in
[PR #63](https://github.com/JFusco/agent-review-workflows/pull/63), separately
from that stopped cycle. The updated [validation record](../../VALIDATION.md)
distinguishes fixture behavior, provider review judgments, and the gate failure;
it makes no latency, billing, hosted readiness, or production claim.

On 2026-10-26 the branch absorbed recorded read-only fallbacks from
[PR #65](https://github.com/JFusco/agent-review-workflows/pull/65). The
fallback dispatch loop keeps derived-view recovery, and `step` skips the model
banner at local finalization. An independent read-only review of the merge
found that `delivery-evidence` accepted only the primary reviewer for recheck
provenance. It now accepts any frozen reviewer candidate, and a fixture
regression covers a fallback recheck and an unfrozen model.
