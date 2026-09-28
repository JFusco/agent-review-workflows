# Contributor quality and delivery

[JFusco/agent-review-workflows issue #1](https://github.com/JFusco/agent-review-workflows/issues/1)
establishes the repository's contributor quality and delivery baseline. Development
tooling is package-managed with Node 24.14.0, pnpm 11.1.1, Husky 9, lint-staged,
Commitlint, ESLint, and Ruff. The Python runtime remains compatible with Python
3.11 and newer; Ruff checks correctness and unused-code rules without imposing a
new formatting style.

`pnpm run verify:ci` is the complete non-fixing local and hosted gate. It runs
Python and JavaScript lint, the workflow unit suite, temporary-repository tooling
tests, and wiki integrity. `verify:push` delegates to the same gate. The Python
launcher prefers the repository virtual environment and preserves command exit
status, while the pre-push hook clears Git-local environment variables before
verification.

## Hooks and commit policy

Husky owns the active hook path. Pre-commit chains an executable legacy hook,
runs safe lint-staged fixes, and then runs the wiki lifecycle block as advisory.
Blocking checks cannot be masked by the wiki hook. Commit-msg requires a scoped
conventional message, and Commitlint checks both pull-request titles and the
explicit introduced commit range in GitHub Actions.

Allowed commit types are `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`,
`refactor`, `revert`, `style`, and `test`. Scopes are required and lowercase.
Subjects are limited to 50 characters and full headers to 120 characters.

## GitHub checks and delivery

`Quality` runs on pull requests to `main`, pushes to `main`, and manual dispatch.
It uses Node 24.14.0, the declared pnpm release, Python 3.11, frozen Node installs,
and pinned Python development requirements. `Commit message lint` reruns when a
pull request is opened, synchronized, reopened, or retitled. Both use read-only
repository permissions and disable Husky because checks run explicitly.

The Git flow in [AGENTS.md](../../AGENTS.md) requires a verified labeled issue,
an issue-numbered branch from updated `main`, the full local gate, an ordinary
Git commit and push, and a conventional pull request. The PR body must include
`Closes #<issue-number>` so GitHub links the artifacts and closes the issue after
merge. Delivery finishes only after verifying the merged PR, closed issue,
updated local `main`, and clean worktree.

[JFusco/agent-review-workflows issue #4](https://github.com/JFusco/agent-review-workflows/issues/4)
turns that prose policy into a deterministic pull-request contract. GitHub's
canonical `.github/pull_request_template.md` provides six ordered sections:
Summary, Linked issue, Changes, Verification, Risk and rollback, and Checklist.
The body validator requires meaningful review context, a GitHub closing keyword,
explicit risk and rollback notes, and every repository checklist item checked.
The Commitlint workflow validates both the conventional title and this body on
every supported pull-request event; contributors can run the same body check as
`pnpm run lint:pr` with `PR_BODY` or standard input.

Installer-managed `bot/wiki-*` pull requests retain their separately scoped,
deterministic maintenance body and are excluded from the human issue-to-PR body
validator. Contributor branches receive no exception from the closing-issue or
review-evidence requirements.

`AGENTS.md` also makes skill maintainability a repository contract. Skill changes
must use progressive disclosure, keep one source of truth, reserve deterministic
code for fragile boundaries, and justify every new abstraction, dependency,
configuration option, or stage with a concrete requirement or reproduced failure.
Changes preserve compatibility unless a break is authorized, remove obsolete
paths instead of leaving dead flags, maintain least privilege and single-writer
rules, and add boundary-appropriate regression coverage. Fixture, live-provider,
and production evidence remain distinct so validation claims stay legible.

The repository contains no `ai-commit` or `ai-pr` dependency, command, hook, or
workflow. The wiki's synchronization writers remain separately scoped bot
workflows using reviewable `bot/wiki-*` branches and `BOT_TOKEN`; they do not
replace the human-readable issue-to-PR delivery flow.
