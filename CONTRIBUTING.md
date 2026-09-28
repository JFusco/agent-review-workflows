# Contributing

Thanks for helping improve Agent Review Workflows. Contributions should keep the review protocol explicit, evidence-backed, and narrowly scoped.

## Set up the project

The project requires macOS or Linux, Python 3.11 or newer, Node 24.14.0,
pnpm 11.1.1 through Corepack, and Git. Provider-backed workflow runs additionally
require authenticated `claude` and `codex` CLIs with access to the pinned models.

```sh
git clone https://github.com/JFusco/agent-review-workflows.git
cd agent-review-workflows
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock
corepack enable
corepack install
pnpm install --frozen-lockfile
pnpm run verify:ci
```

Installing the skills globally is optional for local development:

```sh
.venv/bin/python scripts/install_skills.py
```

The installer creates symlinks under `~/.agents/skills` and refuses to replace unrelated content.

## Make a focused change

- Preserve the pinned agent roles, models, and reasoning settings unless a change is supported by current provider behavior and validation evidence.
- Keep plan review read-only and stop it before application implementation.
- Keep implementation writes limited to the designated repair agent and explicit file scope.
- Preserve stable finding IDs, target fingerprints, revision checks, and independent rechecks.
- Do not add automatic model fallback, recursive delegation, publication, deployment, or merge behavior.
- Never commit credentials, provider authentication data, `runtime.local.json`, virtual environments, or local run artifacts.

Read [references/authoring.md](references/authoring.md) before changing skill instructions, prompts, or evaluation behavior. Read [references/cli.md](references/cli.md) before changing orchestration, recovery, permissions, or artifact handling.

The `prepare` script installs Husky for the current checkout. Generated hook
dispatchers, dependencies, virtual environments, caches, local runtime settings,
and validation runs remain untracked.

## Run the quality gates

Run the complete non-fixing local gate from the repository root:

```sh
pnpm run verify:ci
```

This runs Ruff and ESLint, the Python unit suite, temporary-repository tooling
tests, and wiki integrity. `pnpm run verify:push` is the same gate used by the
pre-push hook. Add or update regression coverage for changes to workflow state,
schema validation, permissions, recovery, scope protection, or contributor
tooling.

The pre-commit hook runs safe staged-file lint fixes without absorbing unstaged
content. Blocking lint and any executable legacy hook run before the wiki's
advisory lifecycle check. The commit-msg hook requires `type(scope): subject`;
the pre-push hook clears Git-local environment variables before running the full
gate. GitHub checks validate both the pull-request title and every commit in the
explicit base-to-head range.

Examples:

```text
ci(quality): Add contributor gates
fix(protocol): Preserve target fingerprint
docs(wiki): Record delivery policy
```

Allowed types are `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`,
`refactor`, `revert`, `style`, and `test`. Scopes are required and lowercase;
subjects are at most 50 characters and do not end in a period. This setup contains
no `ai-commit` or `ai-pr` package, generator, hook, or workflow.

You can also create disposable fixture projects without contacting a model provider:

```sh
.venv/bin/python scripts/create_trial.py
```

Do not run provider-backed trials merely to exercise the test suite. Invoking `review_cli.py run RUN` uses the existing Claude Code and Codex CLI authentication and may consume subscription or paid usage. When live validation is necessary, use credential-free disposable fixtures and document what was actually observed without treating requested settings as provider attestation.

## Submit a change

Before opening a pull request:

1. Create and verify a labeled GitHub issue, then branch from updated `main`.
2. Run `pnpm run verify:ci`.
3. Confirm `git status` contains no local runtime configuration, credentials, or run artifacts.
4. Summarize the behavior changed, the checks run, and any live-provider evidence separately.
5. Include `Closes #<issue-number>` in the pull-request body so the PR is linked
   and the issue closes on merge.
6. Keep unrelated cleanup out of the pull request.

Bug reports and proposals should include the affected workflow, the observed state or error, reproduction steps, expected behavior, and any non-sensitive handoff evidence that helps explain the issue.
