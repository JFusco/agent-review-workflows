---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#21; scripts/review_cli.py; tests/test_review_cli.py; pnpm run verify:ci"]
source_tool: "repository"
source: "/private/tmp/agent-review-collapse-plan.md"
topics: ["implementation-review-evidence"]
digest: "fe6bc3ca4e9358c9168023e1cb194b20654f10f3499005e776166cc9b09e2ba1"
---

# Collapse Implementation Review to Five Calls

## Summary

For new `review-implementation` runs, use `Opus review → Astra adjudicate and lock → Sol repair → Opus recheck → Astra finalize`. Sol is the only writer. Astra may add a sequential, evidence-backed finding within the authorized scope, as required by issue #17.

A failed or incomplete recheck ends `unresolved` after Opus, without another repair or Astra call. A successful recheck proceeds to Astra finalization.

## Implementation Changes

- Set `implementation_evidence_version` to `2` for new runs. Keep the existing `schema_version` and preserve the recorded protocol for older runs, including runs waiting at `respond` or `reply`.
- Route v2 reviews with findings directly to adjudication. Keep Astra’s full finding contract: existing definitions and order are fixed; new findings require sequential IDs, scoped locations, and `UNVERIFIED` status.
- Derive a `repair_lock` within Astra’s accepted adjudication entry. It records accepted findings in order, authorized files, exact check commands, target fingerprint, and the post-adjudication revision. Persist that entry in state and its artifact, render it in the handoff, and send it unchanged to Sol. Validate it immediately before granting repair access.
- Remove the separate implementation-plan printout and later-artifact copies for v2. Preserve existing `implementation_plan` data when resuming an older run that contains it.
- Allow one v2 repair and one independent recheck. Complete findings proceed to finalization; incomplete findings or new recheck findings end `unresolved`. Existing check-only finalization recovery through `rerun-checks` remains available.

## Verification

Test the successful five-stage ledger, the shorter no-findings and all-rejected paths, adjudication additions, pending user decisions, lock persistence and tamper rejection, scope and writer guards, interrupted repair, failed recheck termination, check rerun recovery, and legacy-run resumption. Run `pnpm run verify:ci`.

## Delivery

Start from a clean, freshly pulled `main`. Create a new collapse issue and `codex/<issue-number>-collapse-implementation-review` branch; reference issue #20 as the superseded plan-log proposal. Update the skill, CLI reference, README, validation record, and wiki in the same delivery. Commit, push, open a template-compliant PR, wait for required checks, merge, verify the new issue closed automatically, and return to clean `main`. Leave issue #20 for Joe to close as superseded.

## Assumptions

This changes implementation review only. Deterministic fixtures provide verification unless they expose a need for a disposable provider trial.
