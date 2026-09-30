---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#33; scripts/review_cli.py; tests/test_plan_protocol.py; 16 deterministic protocol fixtures passed"]
source_tool: "codex"
source: "codex:/Users/joe.fusco/.codex/sessions/2026/09/30/rollout-2026-09-30T14-05-30-01a0f37e-357b-7f50-bc6a-edbcfda9f8d4.jsonl"
topics: ["plan-review-protocol"]
digest: "aacda16d5f2acd41eded5472d0389c58db735bc26095458105e0df5745fc93be"
---

# Deterministic, efficient plan review

## Summary

Introduce a versioned plan-review protocol that produces precise, implementation-ready plans through predictable, validated handoffs.

The normal sequence becomes:

**Opus review → Astra adjudication and refinement → Opus recheck when refined → helper completion**

Astra always assesses completeness, including after a clean Opus review. Sound, unchanged plans finish in two model calls; corrected plans normally finish in three. Preserve the two-refinement limit.

Keep **Opus 5.5 High** and **GPT-6 Astra Max**, with existing configuration overrides and frozen per-run profiles. This change covers new plan-review runs and their handoffs. Existing runs retain their recorded behavior; implementation-review protocols remain unchanged.

## Deterministic input/output contracts

Extend the existing schema-generation and response-normalization helpers. Maintain the existing full canonical finding representation internally; models return only the information their stage owns.

**Common input packet**

Every stage receives the protocol version, run ID, stage, handoff revision, target fingerprint, refinement count, frozen profile, governing requirements and instructions, complete current plan, scoped source evidence, canonical findings, decision history, and current evidence catalog. Supply the exact response schema alongside that packet.

**Common response envelope**

Require `plan_protocol_version`, `run_id`, `stage`, `handoff_revision`, `target_fingerprint`, and a concise `summary`. Validate identity fields against the current request. Reject unknown properties and incorrect types.

| Stage | Required stage-specific output | Helper responsibility |
|---|---|---|
| `review` | `new_findings` | Assign stable IDs; initialize findings as `OPEN` and `UNVERIFIED` |
| `adjudicate` | `assessments`, `new_findings`, `plan_markdown` | Apply dispositions, preserve definitions and verification, accept a required refinement |
| `recheck` | `assessments`, `new_findings` | Apply independent verification; preserve definitions and dispositions |

Define the collections precisely:

- **New findings:** Require `severity`, `location`, `evidence`, `correction_recommended`, and `acceptance_check`. The helper assigns sequential `FIND-001` identifiers in response order. Models cannot supply IDs or verification fields for new findings.
- **Adjudication assessments:** Require exactly one `{id, disposition, rationale}` for every existing finding, in canonical order. Allowed dispositions are `ACCEPTED`, `REJECTED`, and `PENDING_USER`. New adjudication findings additionally require their disposition and rationale.
- **Recheck assessments:** Require exactly one `{id, verification_status, verification_evidence, rationale}` for every currently accepted finding, in canonical order. The helper carries rejected findings forward unchanged. Newly discovered findings enter as `OPEN` and `UNVERIFIED`.
- **Verification:** Preserve the existing verdict values. `PASSED` requires current evidence-catalog references and a substantive explanation. Models cannot alter another stage’s fields.

Validate the submitted shape before normalization, then validate the resulting canonical response before acceptance. CLI execution and external coordinator submission use the same schemas and acceptance path.

Use prose for evidence, corrections, acceptance criteria, rationale, concise summaries, and the complete refined plan. Routing and completion must never depend on parsing that prose.

## Review behavior and transitions

1. **Review:** Opus assesses the draft against requirements and source evidence. The helper always advances to adjudication, including when there are no findings.
2. **Adjudication:** Astra evaluates every finding and independently checks the complete plan for missing decisions, contradictions, unnecessary complexity, and inadequate acceptance criteria. It may introduce evidence-backed, in-scope findings.
3. **User decisions:** Any `PENDING_USER` finding requires `plan_markdown: null` and pauses as `needs_user`. The existing `decide` command records the actual user instruction, advances the revision, and returns to adjudication.
4. **Refinement:** If any accepted finding remains unverified, failed, or blocked, and no user decision is pending, require a complete, nonempty `plan_markdown`. Incorporate accepted corrections while preserving sound choices. Every substantive change must correspond to an accepted finding.
5. **Unchanged completion:** If all findings are rejected or already passed, require `plan_markdown: null` and complete deterministically. Empty findings also qualify. Do not force another rewrite merely because previously passed findings remain in the ledger.
6. **Recheck:** After refinement, Opus verifies accepted findings and checks the whole revised document for requirement loss, contradictions, and new gaps. New findings prevent completion.
7. **Bounded retry:** An incomplete first recheck returns to adjudication. An incomplete second recheck ends `unresolved`. A complete recheck finishes without a final model call.

Each accepted refinement response consumes one attempt, including a byte-identical plan, preventing a no-progress loop. Refinement invalidates prior verification and updates the target fingerprint and handoff revision. Enforce the limit through both dispatch and response acceptance.

A passing plan review establishes document readiness for implementation. It does not claim that future code or tests have passed.

## Implementation and compatibility

- Add `plan_protocol_version: 2` to new plan states, original snapshots, packets, and accepted artifacts; expose it in status and readable handoffs. Missing versions retain legacy behavior. Reject unsupported explicit versions.
- Extend [review_cli.py](/Users/joe.fusco/Projects/agent-review-workflows/scripts/review_cli.py) using its existing provider-schema, normalization, validation, persistence, and routing paths. Reuse canonical field definitions rather than introducing a parallel orchestration system.
- Persist the submitted structured response alongside the normalized canonical response. Preserve finding definitions, stable IDs, rejected findings, disposition history, and independent verification evidence.
- For new plan runs, remove provider dispatch for `respond`, `reply`, separate `refine`, and `finalize`. Retain `finalize` as the completed terminal stage marker without inventing a model-call ledger entry.
- Generate `final.md` from the last accepted artifact’s stored plan. Regeneration must preserve reviewed content even if the original draft later changes.
- Preserve read-only project guards, original-draft protection, revision and fingerprint checks, process locks, explicit retries, frozen models, and external-coordinator identity checks.
- Update the plan skill, CLI reference, README, validation record, and affected handoff guidance. Document detailed contracts in one focused protocol reference; keep the skill entrypoint concise. Archive the executed plan and update the wiki during implementation delivery.

## Verification and delivery

Extend [test_review_cli.py](/Users/joe.fusco/Projects/agent-review-workflows/tests/test_review_cli.py) with deterministic fixtures covering:

- Every stage’s exact schema, normalization, helper-assigned IDs, and rejection of missing, duplicate, reordered, unexpected, or unauthorized fields.
- Clean two-call completion; Astra finding a gap after a clean review; three-call correction; second-attempt success; terminal unresolved results.
- All-rejected and mixed passed/rejected outcomes without unnecessary rewriting.
- Whole-plan recheck instructions and new findings discovered during recheck.
- Pending user decisions, stale responses, external submission parity, and rejection of a third refinement.
- Immutable definitions, independent verification authority, and verification invalidation after refinement.
- Interrupted persistence, replay rejection without double-counting, artifact regeneration, and unchanged original/project files.
- Legacy plan runs paused at every removed stage, plus unchanged implementation-review behavior.

Run `pnpm run verify:ci` after implementation. The current baseline already passed in this conversation: 78 Python tests, 17 tooling tests, lint, and wiki integrity.

Use deterministic fixtures for protocol acceptance. Make no comparative model-quality or measured speed claims without separate evidence.

Deliver through the repository’s prescribed flow: updated safe `main`, verified issue, issue branch, scoped implementation and wiki updates, verification, conventional commit, issue-linked PR, required checks, merge verification, and clean synchronized local `main`.
