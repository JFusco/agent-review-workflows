---
topics: [contributor-quality-and-delivery]
plans: [2026-09-28-add-contributor-quality-gates-and-repository-wiki-00cc492088.md]
issue: 'https://github.com/jfusco/agent-review-workflows/issues/1'
issues: ['https://github.com/jfusco/agent-review-workflows/issues/1']
---

# 2026-09-28 — Contributor quality and delivery

Implemented the [archived quality plan](../plans/2026-09-28-add-contributor-quality-gates-and-repository-wiki-00cc492088.md)
for [JFusco/agent-review-workflows issue #1](https://github.com/JFusco/agent-review-workflows/issues/1)
on `codex/1-quality-hooks-wiki`, branched from freshly updated `main`.

The implementation adapts the contributor tooling pattern established in
`qa-regression-writer` while retaining this repository's Python 3.11 minimum and
workflow-specific behavior. It adds Husky, lint-staged, standalone Commitlint,
ESLint, Ruff, a virtual-environment-aware Python launcher, pinned development
dependencies, expanded ignores, and explicit local and hosted quality commands.
One pre-existing unused Python import was removed so the new correctness lint gate
passes; no runtime behavior changed.

Husky owns the active hook path. Pre-commit preserves executable legacy failures,
runs blocking staged lint, and then invokes the installer-managed wiki lifecycle
as advisory. Commit-msg enforces scoped conventional messages, and pre-push clears
Git-local environment variables before the complete gate. The temporary-repository
suite verifies hook activation, commit rejection, partially staged content,
staged Python fixes, legacy and wiki failure semantics, commit ranges, and
pre-push propagation.

GitHub now has separate `Quality` and `Commit message lint` workflows patterned
after the reference repository. The wiki installer added integrity, merge-sync,
and issue-state workflows; the two writer workflows require a configured
`PR_BOT_TOKEN` and create reviewable `bot/wiki-*` pull requests. Contributor
workflows use read-only permissions, disable Husky, and run their checks explicitly.

`AGENTS.md` now requires a verified labeled issue, an issue-numbered branch from
updated `main`, complete verification, ordinary Git commit and push commands, and
a conventional pull request whose body contains `Closes #<issue-number>`. The
flow finishes by verifying the merged PR, automatic issue closure, updated local
`main`, and a clean worktree. No `ai-commit`, `ai-pr`, automatic publication, or
release behavior was added.

The same instructions establish technical-debt controls for future skill changes:
progressive disclosure, one source of truth, deterministic handling only for
fragile boundaries, concrete justification for new mechanisms, compatibility and
cleanup expectations, least privilege, bounded execution, and regression evidence
matched to the failure boundary. Provider-backed trials remain separate from
deterministic fixtures and are not run merely to claim configuration coverage.

Local verification passed Ruff, ESLint, 38 Python unit tests, 13 tooling tests,
and wiki integrity. Hosted workflow execution, merge reconciliation, and automatic
issue closure remain to be verified on the pull request and after merge.

The first hosted Quality run exposed an implicit local dependency in the Python
fixtures: setup resolved the real `codex` and `claude` executables before any
provider stage was exercised. GitHub runners intentionally have neither. Test
setup now points the documented executable overrides at the current test
interpreter, keeping fixtures credential-free and provider-independent while
leaving production executable resolution unchanged. The complete local gate
passed again after this repair.

Historical plan discovery initially recovered three planning variants for this
repository without merged-PR evidence, so they remain `not-implemented` ledger
rows rather than executed archives. After the new generic hook, workflow, and wiki
paths became tracked, discovery produced 56 cross-repository false associations.
Their titles, sources, and path-only evidence were reviewed and recorded as
`out-of-scope`; a final discovery reported 824 unmatched candidates and no matched
or ambiguous work requiring another audit.
