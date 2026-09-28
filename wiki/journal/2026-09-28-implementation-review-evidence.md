---
topics: [implementation-review-evidence]
plans: [2026-09-28-make-review-implementation-evidence-complete-6f0a1ea9f8.md]
issue: 'https://github.com/jfusco/agent-review-workflows/issues/9'
issues: ['https://github.com/jfusco/agent-review-workflows/issues/9']
---

# 2026-09-28 — Evidence-complete implementation review

Implemented the evidence and authority contract tracked by
[JFusco/agent-review-workflows issue #9](https://github.com/JFusco/agent-review-workflows/issues/9)
on `codex/9-implementation-review-evidence`, branched from updated `main`.

New implementation runs now require an explicit local Git base and at least one
authorized local check. Initialization validates both before creating the run
directory and rejects an empty initial scoped diff. The frozen target combines
the base SHA, verbatim requirements, full scoped text sources, and a complete
base-to-current diff for the authorized paths, including scoped untracked files
and deletions without admitting unrelated repository changes.

Checks run before the initial review and after repair. Their arguments, exit
codes, output, and target fingerprints remain visible to the independent
reviewer. Failed checks are evidence rather than hidden setup failures, but they
cannot satisfy the completion gate.

New findings identify a scoped file with the existing severity vocabulary and
may include a line or line range. Their stable definition cannot be rewritten
after introduction. The implementer recommendation and reviewer reply are now
stored separately in each ledger revision and rendered in the handoff; both are
advisory, and the canonical finding remains open until adjudication. The
coordinator alone authorizes repair, the implementer remains the only writer,
and independent recheck alone changes verification fields.

The new contract is marked only on newly initialized implementation runs.
Existing implementation artifacts retain their historical diff and check
behavior, while plan review remains read-only and does not require either input.
The public response schema, configured role profiles, provider routing,
permission boundaries, and bounded passes are unchanged.

The expanded Python suite passes 58 cases covering pre-artifact failures, diff
composition, complete reviewer evidence, finding validation, immutable
definitions, preserved advisory assessments, coordinator authority, and legacy
compatibility. The implementation skill passes the official validator. No new
provider-backed trial was run; the contract is established with disposable,
credential-free Git fixtures and local checks.

At the user's request, the repository guidance also drops an obsolete
package-specific prohibition so `AGENTS.md` stays focused on behavior and
delivery requirements.
