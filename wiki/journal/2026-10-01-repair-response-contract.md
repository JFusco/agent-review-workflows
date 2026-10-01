---
topics: [implementation-review-evidence]
plans: [2026-10-01-repair-the-implementation-review-response-contract-4ec3266fb2.md]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/36']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/36'
---
# Repair response ownership

Issue [#36](https://github.com/JFusco/agent-review-workflows/issues/36)
implements the approved [plan](../plans/2026-10-01-repair-the-implementation-review-response-contract-4ec3266fb2.md)
for an implementation-review response rejected after Sol completed scoped edits.
The offline incident reproduction showed changed canonical definitions and
verification evidence in the full writer response. The recovered Design
Passport review was not replayed.

New implementation runs record `implementation_response_version: 2`. The repair
stage receives a strict response schema with identity, summary, and ordered
accepted-finding `{id, rationale}` assessments. The helper reconstructs full
findings from saved state, preserves frozen fields and rejected records, and
retains both submitted and canonical responses in the repair artifact. Older
runs continue using their recorded full-response contract and frozen profile.

Rejected output now identifies the finding and field when possible. A response
rejected after writer exit records an actionable interrupted repair; inspection
and reconciliation advance to independent recheck without replaying Sol. The
repair lock, scoped write guard, independent verification, five-stage path,
and one-pass limit remain in force.

Temporary-repository fixtures cover valid reconstruction, invalid IDs and
fields, stale identity, lock tampering, post-write rejection, reconciliation,
legacy behavior, and distinct execution-failure diagnostics. The repository
gate is `pnpm run verify:ci`. These fixtures provide local contract evidence,
not a live-provider quality claim.
