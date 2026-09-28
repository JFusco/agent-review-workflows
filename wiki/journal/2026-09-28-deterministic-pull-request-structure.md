---
topics: [contributor-quality-and-delivery]
plans: [2026-09-28-enforce-deterministic-pull-request-structure-f5d137d40f.md]
---

# 2026-09-28 — Deterministic pull request structure

Implemented the pull-request format tracked by
[JFusco/agent-review-workflows issue #4](https://github.com/JFusco/agent-review-workflows/issues/4)
on `codex/4-deterministic-pr-structure`, branched from updated `main`.

The canonical GitHub template now asks every contributor for the same ordered
review evidence: outcome, closing issue reference, concrete changes, exact
verification, risk and rollback, and a completed repository checklist. The
format follows GitHub's native template and closing-keyword conventions rather
than introducing a custom pull-request creation command.

`scripts/validate_pr_body.cjs` enforces the template as a repository-owned,
dependency-free contract. It rejects missing, duplicated, renamed, or reordered
sections; placeholder-only core content; non-closing issue references; missing
risk or rollback notes; and unchecked required items. `pnpm run lint:pr` exposes
the same check locally, while the existing `Commit message lint` workflow runs it
against the event body alongside the conventional PR-title check.

The installer-managed wiki writer workflows retain their separately scoped,
deterministic bot bodies. `bot/wiki-*` branches are excluded from the human
issue-to-PR body validator because they reconcile work that has already merged;
contributor branches cannot use that exception.

During delivery, the repository bot secret was refreshed and renamed from
`PR_BOT_TOKEN` to `BOT_TOKEN`. Both wiki writer workflows, checkout credentials,
failure messages, tests, and durable wiki guidance now use the configured name.

Contributor and agent guidance now names the exact format and requires validation
before opening a PR. Focused unit coverage exercises valid bodies and each
failure boundary. The complete local gate passed Ruff, ESLint, 38 Python tests,
17 tooling tests, and wiki integrity before delivery.
