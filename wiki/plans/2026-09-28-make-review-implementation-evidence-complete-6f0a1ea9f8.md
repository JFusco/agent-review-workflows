---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#9; codex/9-implementation-review-evidence; pnpm run verify:ci; review-implementation skill validator"]
source_tool: "codex"
source: "codex:/Users/joe.fusco/.codex/sessions/2026/09/28/rollout-2026-09-28T08-37-38-01a0e805-5272-7183-ac6c-4080f363254b.jsonl"
topics: ["implementation-review-evidence"]
digest: "6f0a1ea9f8dcbda5fca63cda086760a1d3822534405dd10c628c545c3abb7a30"
---

# Make `review-implementation` evidence-complete

## Summary

Require every new implementation review to use an explicit Git base, an authorized scoped diff, verbatim requirements, and at least one real check result. Preserve the reviewer → coordinator → implementer separation, existing models, bounded passes, permissions, and response schema.

## Implementation changes

- In `scripts/review_cli.py`, make `--base` and at least one `--check` mandatory for new implementation runs. Resolve the base to a local commit and validate all inputs before creating run artifacts; do not infer a base.
- Always provide the reviewer with:
  - the frozen base SHA;
  - the base-to-current diff limited to `--scope`;
  - tracked, staged, unstaged, deleted, and scoped untracked files;
  - full scoped file contents for context;
  - the requirements text without summarization;
  - check command, exit code, output, and matching target fingerprint.
- Build untracked-file patches deterministically with Git no-index diffs, reject undiffable or oversized targets, and reject an initially empty implementation diff. Refresh the diff and rerun checks after each repair against the same frozen base.
- Keep `--scope` as both the review boundary and repair allowlist; unrelated repository changes remain excluded and untouched.
- Tighten finding instructions and validation: preserve stable IDs and the existing `BLOCKER`/`WARN`/`SUGGESTION` enum, require a project-relative scoped file location with an optional line/range, concrete evidence, a surgical correction, and an acceptance check.
- Record the implementer recommendation and reviewer reply per finding in the existing decision ledger. Treat both as advisory until the coordinator adjudicates; only that adjudication can authorize repair. Only the implementer writes, and only the independent reviewer can mark accepted findings verified.
- Preserve response-schema compatibility, existing run recovery, and plan-review behavior. Previously created base-less or check-less runs remain resumable under their frozen contract.

## Documentation and records

- Update the `review-implementation` skill, CLI reference, README, and validation report from one consistent contract; leave plan-review instructions and agent metadata unchanged.
- Document that failed checks remain review evidence but prevent successful completion, while an unexecutable check blocks before review.
- Archive this executed plan and add a focused implementation-review-evidence wiki topic and dated journal entry; rebuild and validate the wiki graph.

## Test plan

- Prove missing/invalid base, missing checks, empty diff, malformed scope, and oversized input fail before a run directory is created.
- Cover committed, staged, unstaged, deleted, nonempty untracked, and empty untracked files; verify out-of-scope changes are absent.
- Assert the initial reviewer packet contains the exact requirements, diff, source context, and fingerprint-bound check results with no prior agent conclusions.
- Verify failed checks are visible to the reviewer and cannot be bypassed by a no-findings response.
- Verify implementer and reviewer recommendations both reach the coordinator, only coordinator adjudication enters repair, repair cannot alter dispositions, and recheck sees the revised diff and fresh checks.
- Reject missing, generic, or out-of-scope finding locations while retaining valid file and line/range forms.
- Retain coverage for stale handoffs, legacy runs, write guards, recovery, stable IDs, two-pass limits, and configurable agent profiles.
- Run `pnpm run verify:ci`. Record this as deterministic fixture evidence; do not spend a provider-backed trial because packet construction, routing, and enforcement are locally provable.

## Delivery and assumptions

- “Actual diff” means the selected authorized scope, not the whole repository. Implementation reviews now require Git; plan reviews remain unchanged.
- Start from updated `main`, create and read back `[Feature] Require evidence-complete implementation reviews` with `enhancement` and `documentation`, then branch as `codex/<issue>-implementation-review-evidence`.
- Commit as `feat(workflows): require implementation evidence`, push normally, and open a template-complete PR with `Closes #<issue>`, exact verification results, and rollback guidance.
- Wait for required checks, merge, verify the issue closes automatically, then return local `main` to a clean state matching `origin/main`.
