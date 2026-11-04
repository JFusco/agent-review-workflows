---
status: "implemented"
executed: true
evidence: ["scripts/review_cli.py; tests/test_research_launch.py: 10 focused tests passed; issue #89"]
source_tool: "codex"
source: "/private/tmp/office-feature-planning-review-20261104/research-recovery-plan.md"
topics: ["plan-review-protocol"]
digest: "9a9c8cadb107894e70f9187db01fd24f86257c514a3644f2e6b34f3cd15d3f3c"
---

# Fix researcher launch recovery and resume feature planning

## Implementation

Add `step --codex-research-only` to the maintained review helper. Require a current schema-3 plan run, a ready research stage, valid frozen researcher configuration, unchanged inputs, valid original permission roots, and no surviving owned process. Dispatch exactly one attempt using the existing restricted research profile; preserve failure receipts, record the launch boundary, and accept the brief through the existing schema, fingerprint and persistence checks. Do not retry, fall back, run checks or advance into review from the guarded command. Update recovery documentation, affected skill references, validation and wiki records.

## Verification and shipping

Use controlled children and temporary repositories to cover successful recovery, stale inputs, invalid permissions, wrong stages, active processes, duplicate acceptance and single-attempt failures. Run `pnpm run verify:ci`. Preserve the unrelated Graphify manifest change. Follow issue, branch, conventional commit and PR delivery; merge after required checks under Joe's explicit authorization.

## Operational follow-up

Use the shipped helper to resume preserved Office plan-review run be89d50b-8f7d-42cb-8004-8a8e206b541d through the normal launcher approval mechanism. Revalidate freshness; preserve the old run and create a fresh review if Office source changed. Complete independent research/review/refinement/recheck and return the final feature implementation plan. This operational follow-up is recorded separately from the helper's deterministic regression evidence.
