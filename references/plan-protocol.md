# Plan review protocol 2

New plan runs record `plan_protocol_version: 2`. The helper owns identity,
canonical findings, persistence, routing, and completion. Models supply findings,
assessments, and complete plan refinements through the schema supplied for their
current stage. Prose carries evidence and judgment; it never controls routing.

## Input and response envelope

Each input packet contains `plan_protocol_version`, `run_id`, `mode`, `stage`,
`handoff_revision`, `target_fingerprint`, `round`, `agent_profile`, `requirements`,
`project_instructions`, `target`, `scope`, `findings`, `decision_ledger`, `checks`,
and `evidence_catalog`. `target` contains the complete current plan and scoped
source contents. The ledger preserves earlier dispositions and verification
assessments; current canonical findings remain authoritative.

The prompt includes the exact response schema. CLI structured output and
`external-request.json` use that same schema. Return a JSON object with these
required common fields:

| Field | Contract |
| --- | --- |
| `plan_protocol_version` | Exactly `2` |
| `run_id` | Exactly the supplied run ID |
| `stage` | Exactly the supplied stage |
| `handoff_revision` | Exactly the supplied integer revision |
| `target_fingerprint` | Exactly the supplied fingerprint |
| `summary` | Nonblank, concise prose describing substantive outcomes or limitations |

Unknown properties, missing fields, and incorrect types are rejected. Do not
return requirements, source snapshots, existing finding definitions, routing
commands, or completion flags. The helper validates the submitted schema before
normalization, then validates the complete canonical response before acceptance.

## Stage outputs

| Stage | Additional required fields |
| --- | --- |
| `review` | `new_findings` |
| `adjudicate` | `assessments`, `new_findings`, `plan_markdown` |
| `recheck` | `assessments`, `new_findings` |

Return empty arrays when there are no corresponding findings or assessments.

### New findings

Each new finding requires `severity`, `location`, `evidence`,
`correction_recommended`, and `acceptance_check`. Severities are `BLOCKER`, `WARN`,
and `SUGGESTION`; the remaining fields are nonblank prose. Locate the gap in the
plan and ground it in the requirements or current source. Acceptance checks assess
the document's specified behavior and future verification, not executed repairs.

New adjudication findings additionally require `disposition` (`ACCEPTED`,
`REJECTED`, or `PENDING_USER`) and a nonblank `rationale`. Review and recheck
findings receive `OPEN` automatically. Every new finding starts `UNVERIFIED` with
empty verification evidence.

Never supply an `id` or verification fields for a new finding. After validation,
the helper assigns sequential `FIND-001` style IDs following the highest existing
ID, in response order. Retain the original definition for the lifetime of each
accepted record; corrections to an unsupported finding use an evidenced rejection
and, when necessary, a separately defined new finding.

### Adjudication assessments and plan

Return exactly one `{id, disposition, rationale}` assessment for every existing
finding, in canonical order, including rejected and passed findings. Dispositions
are `ACCEPTED`, `REJECTED`, or `PENDING_USER`; each rationale must be nonblank.
Verification and definitions are retained by the helper.

The coordinator always assesses the complete plan, including after a clean review.
Check requirement completeness, relevant behavior and interfaces, failure
handling, assumptions, and observable acceptance criteria. Introduce only
evidence-backed, in-scope findings and avoid irrelevant boilerplate.

`plan_markdown` is required and its value follows the normalized findings:

1. Any `PENDING_USER`: return `null`; the run pauses as `needs_user`.
2. Otherwise, any accepted finding not `PASSED`: return the complete nonblank
   refined plan. Every substantive change must address an accepted finding.
3. Otherwise: return `null`; preserve the current plan and complete the review.

A refinement consumes one of two attempts, even if its bytes are unchanged. The
helper clears prior verification on all findings, refreshes the fingerprint and
revision, and routes to independent recheck. Previously passed findings plus newly
rejected findings do not require another rewrite.

### Independent recheck assessments

Return exactly one `{id, verification_status, verification_evidence, rationale}`
for every accepted finding, in canonical order. The helper retains rejected
findings without requiring model output for them. Dispositions cannot change.

Statuses are `PASSED`, `FAILED`, `BLOCKED`, or `UNVERIFIED`. Evidence entries are
exact current `evidence_catalog` keys, such as `PLAN:current`; line annotations
belong in the nonblank rationale. `PASSED` requires at least one current reference
and an explanation of how the plan satisfies the acceptance criterion.

Also examine the whole revised plan for requirement loss, contradictions, and new
gaps. Report these through `new_findings`. A passing recheck establishes that the
document addresses the objections; it never claims future implementation or tests
have passed.

## Routing, artifacts, and recovery

Review always enters adjudication. Complete findings after adjudication or recheck
produce `stage: finalize`, `status: complete` without a final provider call or
invented finalize ledger entry. An incomplete first recheck returns to
adjudication; an incomplete second recheck ends `unresolved`.

No protocol-2 provider dispatch is allowed for `respond`, `reply`, `refine`,
`repair`, or `finalize`. Protocol-2 plan review remains read-only. The existing
user-decision, frozen-profile, external-coordinator, process-lock, freshness, and
retry rules in [CLI recovery](cli.md#recovery) still apply. A rejected response
cannot change canonical findings, the plan, or the refinement count.

Accepted artifacts retain both `submitted_response` (the compact model output)
and `response` (the existing full canonical shape), plus the protocol version and
accepted target snapshot. `final.md` is regenerated from that accepted snapshot,
so a later change to the original draft cannot rewrite the completed result.
Interrupted persistence preserves orphaned artifacts; replay of an accepted
response is rejected by revision/state validation without another refinement.
If a readable-view write fails after acceptance, the durably saved next status is
preserved. Inspect `status`; for a completed run, `run RUN` regenerates the views
without invoking a provider. Do not retry an already accepted stage.

Absent `plan_protocol_version` means the legacy plan protocol: its recorded
advisory, refinement, and finalization stages and existing response shapes remain
resumable. Unsupported explicit versions are rejected. Do not migrate old runs or
remove their version markers to change behavior. To return to an older helper,
preserve protocol-2 artifacts and start fresh legacy runs; the older helper cannot
safely resume this new protocol. Implementation protocols are unaffected.
