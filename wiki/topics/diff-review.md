---
issues: ['https://github.com/JFusco/agent-review-workflows/issues/45']
---
# Diff review

The opt-in `review-diff` skill reviews a caller-supplied base, explicit file
scope, nonempty scoped diff, and at least one check command. It uses the shared
run ledger, pinned read-only reviewer profile, target fingerprint, stable
finding IDs, and independent adjudication. The helper executes checks and
records their outputs before review. An accepted report identifies findings,
check outcomes, and the accepted diff without writing to the target.

Review evidence is tied to the scoped diff and command list. Changed source or
commands require a fresh run; interrupted checks resume through the helper.
Deterministic fixtures establish preflight, routing, stale evidence, and
recovery behavior. They do not establish provider review quality.
