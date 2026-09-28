# Agent Review Workflows

Agent Review Workflows provides two installable agent skills that coordinate evidence-backed review through Claude Code and Codex CLI:

- `review-plan`: Opus 5.5 High reviews; Astra 6 Max refines and finalizes the plan.
- `review-implementation`: Opus 5.5 High reviews; Sol 6 XHigh responds and repairs; Astra 6 Max adjudicates and summarizes.

Invoke either skill in Codex by name. Finishing ordinary work does not launch a cycle. Plan review always stops before application implementation.

Each workflow keeps a revision-bound decision ledger, separates review from repair, and requires independent rechecks before completion. The implementation workflow gives write access only to its designated repair agent; the plan workflow never edits application code.

## How it works

1. The helper snapshots an explicitly scoped target and records its fingerprint.
2. Claude Opus independently reviews the plan or implementation.
3. Codex agents respond to findings, adjudicate disagreements, and make only authorized changes.
4. Claude Opus rechecks the resulting target and configured checks gate completion.
5. The workflow writes a readable handoff and immutable revision artifacts outside the reviewed project.

No model is silently substituted, and publication, deployment, or merge actions are outside the workflow.

## Use

From any project in Codex CLI, invoke `$review-plan` with the draft or `$review-implementation` with the change to review. To start the orchestrator explicitly:

```sh
codex --model gpt-6-astra -c 'model_reasoning_effort="max"' '$review-plan Review the draft plan we just prepared.'
```

## Install

Requires macOS or Linux, Python 3.11+, Git for Git projects, authenticated `claude` and `codex` CLIs, and access to the pinned models. From this directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock
corepack enable
corepack install
pnpm install --frozen-lockfile
.venv/bin/python scripts/install_skills.py
```

The installer adds links under `~/.agents/skills` and refuses to replace unrelated existing files. `--skills-dir` overrides that location. The source tree can live anywhere; links should be reinstalled after moving it. No global provider, model, permission, or project settings are changed.

If the Codex executable on PATH cannot access a selected model, install with `--codex-bin /path/to/compatible/codex`. This records only this installation's executable in ignored `runtime.local.json`. `AGENT_REVIEW_CODEX_BIN` and `AGENT_REVIEW_CLAUDE_BIN` override local selection; otherwise the helper uses PATH. Runs capture the selected executable. Missing or unsupported models stop the cycle without substitution.

[CLI use and recovery](references/cli.md) describes explicit scope, artifact storage, existing-chat Astra integration, and continuation after interruption. [Authoring](references/authoring.md) records best-practice sources and evaluation principles.

## Validate

```sh
pnpm run verify:ci
.venv/bin/python scripts/create_trial.py
```

The complete quality gate runs Python and JavaScript lint, the workflow unit
suite, temporary-repository hook and commit-policy tests, and context-wiki
integrity. Husky applies staged checks before commits, Commitlint enforces scoped
conventional messages, and the pre-push hook runs the same full gate. GitHub runs
the quality gate and validates both pull-request titles and introduced commits.
No `ai-commit` or `ai-pr` tool is installed or used.

The trial creator makes separate disposable Git projects and prints their run directories. It does not call models. Running `review_cli.py run RUN` invokes paid/subscription provider sessions according to your existing CLI authentication. Keep trial runs separate from production projects. See [VALIDATION.md](VALIDATION.md) for executed results and limits.

`calls/` captures prompts, CLI output, and observable execution metadata; `artifacts/` preserves revision lineage; `handoff.md` is the readable decision ledger; `final.md` exists only after successful finalization. These are sensitive local project artifacts, not files to publish automatically.

## Project layout

- `skills/` contains the installable skill instructions and agent metadata.
- `scripts/review_cli.py` implements the review protocol and recovery commands.
- `scripts/install_skills.py` installs safe, idempotent skill links.
- `schemas/response.json` defines the structured handoff contract.
- `references/` documents CLI operation, recovery, and authoring principles.
- `tests/` covers protocol, scope, recovery, and model-setting invariants.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for environment setup, test commands, and change boundaries.
