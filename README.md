# Agent Review Workflows

Agent Review Workflows provides three installable agent skills that coordinate evidence-backed review through Claude Code and Codex CLI:

- `review-plan`: a Claude reviewer critiques; a Codex coordinator refines and finalizes the plan.
- `review-implementation`: a Claude reviewer finds and rechecks defects; a Codex coordinator locks accepted repairs and closes successful reviews; a Codex implementer makes the scoped repair.
- `review-handoff`: dispatches one authorized stage of an existing review run through the helper, then reports its status.

The built-in profile remains Opus 5.5 High, Astra 6 Max, and Sol 6 XHigh. Installation-local profiles and explicit per-run overrides can select other model and effort combinations without changing provider or permission boundaries.

Invoke a skill in Codex by name. Finishing ordinary work does not launch a cycle. Plan review always stops before application implementation.

Each workflow keeps a revision-bound decision ledger, separates review from repair, and requires independent rechecks before completion. The implementation workflow gives write access only to its designated repair agent; the plan workflow never edits application code.

## How it works

1. The helper snapshots an explicitly scoped target and records its fingerprint.
2. For implementations, it runs the configured checks and gives the reviewer the frozen-base diff, scoped sources, verbatim requirements, and exact check receipts.
3. The configured Claude reviewer independently reports located, severity-ranked findings. The coordinator decides them, may add an evidenced in-scope gap, and locks the accepted repairs, authorized files, checks, fingerprint, and revision in its adjudication entry.
4. The implementer alone makes one scoped repair. The reviewer rechecks it once; an incomplete recheck ends unresolved, while a passing recheck proceeds to coordinator finalization.
5. The workflow writes a readable handoff with the decisions, repair lock, and scoped Git diff, plus immutable revision artifacts outside the reviewed project.

Transient configured-check failures on an unchanged implementation target can be recovered with `rerun-checks`. The command retains old receipts, creates revision-bound current receipts, and never replays model or repair work.

No model is silently substituted, and publication, deployment, or merge actions are outside the workflow.

## Use

From any project in Codex CLI, invoke `$review-plan` with the draft or `$review-implementation` with the change to review. A plain skill cannot change the invoking conversation's model; current-chat coordinator stages are allowed only when that conversation exactly matches the run's frozen coordinator profile.

For one stage of an existing run, invoke `$review-handoff` with its run directory. It uses the existing `step` command and the run's frozen CLI model settings, with no dedicated handoff model or additional stage. See [Single-stage handoff](references/cli.md#single-stage-handoff).

New implementation runs require Git, an explicit local `--base`, one or more `--scope` files, and at least one `--check`. They fail before creating artifacts if the base is invalid or the initial scoped diff is empty. Plan runs and previously created review runs retain their existing contracts.

## Configure models and effort

Add any desired partial overrides to the ignored `runtime.local.json` beside this README. Missing fields retain the built-in profile:

```json
{
  "skills": {
    "review-plan": {
      "reviewer": { "model": "claude-opus-5-5", "effort": "high" },
      "coordinator": { "model": "gpt-6-astra", "effort": "max" }
    },
    "review-implementation": {
      "reviewer": { "model": "claude-opus-5-5", "effort": "high" },
      "coordinator": { "model": "gpt-6-astra", "effort": "max" },
      "implementer": { "model": "gpt-6-sol", "effort": "xhigh" }
    }
  }
}
```

`start` also accepts `--reviewer-model`, `--reviewer-effort`, `--coordinator-model`, `--coordinator-effort`, and implementation-only `--implementer-model` / `--implementer-effort`. Explicit flags override the installation profile, which overrides built-in defaults. The complete result is recorded in the run and used unchanged on resume. Configuration errors fail before run artifacts are created; provider rejection stops the run without fallback.

## Install

Requires macOS or Linux, Python 3.11+, Git for implementation reviews, authenticated `claude` and `codex` CLIs, and access to the configured models. From this directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock
corepack enable
corepack install
pnpm install --frozen-lockfile
.venv/bin/python scripts/install_skills.py
```

The installer adds links under `~/.agents/skills` and refuses to replace unrelated existing files. `--skills-dir` overrides that location. The source tree can live anywhere; links should be reinstalled after moving it. No global provider, model, permission, or project settings are changed.

If the Codex executable on PATH cannot access a selected model, install with `--codex-bin /path/to/compatible/codex`. This updates only `codex_binary` in ignored `runtime.local.json` and preserves saved skill profiles. `AGENT_REVIEW_CODEX_BIN` and `AGENT_REVIEW_CLAUDE_BIN` override local executable selection; otherwise the helper uses PATH. Runs capture the selected executable. Missing or unsupported models stop the cycle without substitution.

[CLI use and recovery](references/cli.md) describes profile validation, explicit scope, artifact storage, current-chat coordinator integration, and continuation after interruption. [Authoring](references/authoring.md) records best-practice sources and evaluation principles.

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

## Maintainer code map

Graphify 0.9.36 maps maintained scripts; `.graphifyignore` excludes tests,
documentation, generated files, dependencies, and local state. This code map
is separate from the Markdown-only context wiki. The repository-local
[Graphify skill](.agents/skills/graphify/SKILL.md) covers queries and refreshes.
After `pnpm install --frozen-lockfile` and installing Graphify 0.9.36, run
`graphify hook install` and `graphify hook status` once per clone. Native Git
hooks refresh the map after commits and checkouts; run
`PYTHONHASHSEED=0 graphify update .` after pulls or merges. Commit the graph,
HTML, report, manifest, analysis, and labels; keep caches, machine paths, and
query memory local. No agent tool hooks are installed.
