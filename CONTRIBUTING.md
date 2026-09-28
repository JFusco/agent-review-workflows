# Contributing

Thanks for helping improve Agent Review Workflows. Contributions should keep the review protocol explicit, evidence-backed, and narrowly scoped.

## Set up the project

The project requires macOS or Linux, Python 3.11 or newer, and Git. Provider-backed workflow runs additionally require authenticated `claude` and `codex` CLIs with access to the pinned models.

```sh
git clone https://github.com/JFusco/agent-review-workflows.git
cd agent-review-workflows
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
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

## Run the tests

Run the full local suite from the repository root:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

The local suite is the required check for code changes. Add or update regression coverage for changes to workflow state, schema validation, permissions, recovery, or scope protection.

You can also create disposable fixture projects without contacting a model provider:

```sh
.venv/bin/python scripts/create_trial.py
```

Do not run provider-backed trials merely to exercise the test suite. Invoking `review_cli.py run RUN` uses the existing Claude Code and Codex CLI authentication and may consume subscription or paid usage. When live validation is necessary, use credential-free disposable fixtures and document what was actually observed without treating requested settings as provider attestation.

## Submit a change

Before opening a pull request:

1. Run the full local test suite.
2. Confirm `git status` contains no local runtime configuration, credentials, or run artifacts.
3. Summarize the behavior changed, the checks run, and any live-provider evidence separately.
4. Keep unrelated cleanup out of the pull request.

Bug reports and proposals should include the affected workflow, the observed state or error, reproduction steps, expected behavior, and any non-sensitive handoff evidence that helps explain the issue.
