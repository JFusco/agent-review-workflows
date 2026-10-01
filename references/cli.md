# CLI procedure

Resolve the skill symlink to its source, then take the parent of `skills` as the installation root. Use that root's `.venv/bin/python` with `scripts/review_cli.py`. Do not assume the current working directory is the installation. All paths passed to `--scope` are project-relative **files**, including intended new or deleted files.

## Agent profiles

The ignored installation-local `runtime.local.json` may contain partial profiles under `skills.review-plan` and `skills.review-implementation`. The plan skill supports `reviewer` (Claude) and `coordinator` (Codex); the implementation skill also supports `implementer` (Codex). Each role accepts `model` and `effort` only. Providers and permissions are fixed and cannot be configured.

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
      "implementer": { "model": "gpt-6.1-sol", "effort": "xhigh" }
    }
  }
}
```

Those values are also the built-in defaults. Claude effort accepts `low`, `medium`, `high`, `xhigh`, or `max`. Codex effort accepts `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`, or `ultra`; the selected model may support only a subset. Model identifiers must be nonblank and contain no whitespace. The provider CLI remains authoritative for model availability and model/effort compatibility; rejection stops the workflow without fallback.

At `start`, explicit `--reviewer-model` / `--reviewer-effort`, `--coordinator-model` / `--coordinator-effort`, and implementation-only `--implementer-model` / `--implementer-effort` override the selected skill profile. Resolution is per field: start flag, then installation profile, then built-in default. The helper validates the entire local configuration before creating a run and stores the complete resolved profile in its state, original snapshot, status, packet, and handoff. Later edits or deletion of `runtime.local.json` never change that run or its resumed sessions.

The Sol 6.1 / `xhigh` default applies only to new implementation runs. Existing version-2 runs use their frozen profile, including Sol 6 / `xhigh`; version-1 runs retain the original Opus 5.5 / `high`, Astra 6 / `max`, and Sol 6 / `xhigh` pins. No artifact migration or session model switch occurs. An installation-local `implementer.model` of `gpt-6-sol` or explicit `--implementer-model gpt-6-sol` continues to select Sol 6 for a new run; effort follows the same per-field precedence.

## Start

Write the user's authorized requirements, repair boundaries, acceptance checks, and relevant project prerequisites to a UTF-8 file outside the target project. Preserve a conversation draft as a separate UTF-8 plan file outside that project. Never pass credentials. For large reviews narrow scope: packets have a 4 MiB limit and are never silently truncated.

Examples below use `PYTHON` and `HELPER` to mean the resolved interpreter and script paths; invoke them as separate shell arguments.

```text
PYTHON HELPER start plan --project /path/to/project --requirements /path/to/requirements.md --plan /path/to/draft.md --scope src/relevant.py
PYTHON HELPER start implementation --project /path/to/project --requirements /path/to/requirements.md --scope src/changed.py --scope tests/test_changed.py --base origin/main --check "python3 -m unittest discover -s tests"
PYTHON HELPER start plan --project /path/to/project --requirements /path/to/requirements.md --plan /path/to/draft.md --coordinator-model gpt-6-luna --coordinator-effort high
```

`start` snapshots the target without calling a model. It prints the run directory. Select scope from the actual user request or diff. Resolve unclear targets with the user. New implementation runs require `--base`, resolve it once to a local commit, require at least one `--check`, and reject an empty initial scoped diff before creating run artifacts. Plan runs may omit both. Include all files the repair may touch, but exclude unrelated work. Configuration, agent instructions, and secret files are not supported automatic repair targets.

The implementation target contains the frozen base SHA, full scoped text files, and the base-to-current scoped diff. The diff includes committed, staged, unstaged, deleted, and explicitly scoped untracked files; unrelated repository changes are excluded. The same base is retained after repair so recheck sees the revised complete change. Existing runs without this evidence contract remain resumable with their recorded behavior.

Checks are user-authorized local commands, parsed into argv without a shell. Shell pipelines and operators are not supported. The helper executes them from the target project before initial implementation review and after each repair; choose disposable/non-production checks. The reviewer receives each command, exit code, output, and target fingerprint. A nonzero result remains review evidence and prevents completion; a command that cannot execute blocks before review. Required project browser/build/test gates still apply.

Artifact root precedence: `--runs-dir`, `AGENT_REVIEW_RUNS_DIR`, `$CODEX_HOME/review-runs`, then `~/.codex/review-runs`. Artifacts must remain outside the target project. The target defaults to the invocation directory; Git projects must use their repository root. Run permissions may require access to this artifact directory and the selected project.

## Run and interact

```text
PYTHON HELPER run /path/to/run
PYTHON HELPER status /path/to/run
PYTHON HELPER rerun-checks /path/to/run
```

The helper serializes the protocol and launches all three provider roles through the CLIs. Inspect `handoff.md`, `final.md`, `artifacts/`, and `calls/` within the run. `step` runs one stage. Stop at `complete`, `unresolved`, `needs_user`, or a reported blocker. No automatic model fallback, recursive agent delegation, or publication occurs.

### Claude login visibility in a sandbox

The helper checks `auth status --json` with the run's saved Claude executable immediately before each Claude reviewer call. For an initial implementation review, configured checks run and their receipts are saved first. If login is unavailable in that execution context, the reviewer stage remains `ready`; no provider call, session, or ledger entry is created. A malformed or failed status check also stops before dispatch. Do not run `claude auth login` inside a sandbox that cannot see the host's existing login.

When sandboxed `claude auth status` reports logged out but the same command in an approved host context reports logged in, keep the run directory accessible in both contexts and use this sequence for a full review:

1. Run `PYTHON HELPER run RUN` in the sandbox. Let it stop at the reviewer auth-context diagnostic; initial implementation checks are now recorded in the sandbox.
2. Confirm `PYTHON HELPER status RUN` is `ready` at a Claude `review`, legacy `reply`, or `recheck` stage. Check host `claude auth status` without recording its raw output or credentials.
3. Use approved host execution for `PYTHON HELPER step RUN --reviewer-only` only. The guard checks the role under the project lock and rejects Codex stages or implementation reviews without current check receipts. It dispatches one reviewer stage with the frozen model, tools, session, packet, and schema.
4. Resume `PYTHON HELPER run RUN` in the sandbox. Repeat the guarded host step only if another Claude reviewer stage is reached. Continue through the normal terminal state without asking the user to log in for each stage.

Never run an unrestricted `run` or ordinary `step` with host access as an auth workaround. If host authentication is also absent or expired, the user must complete one interactive host CLI login before a reviewer stage can proceed. Do not copy Keychain contents, OAuth tokens, API keys, or raw auth output into environment files, packets, or run artifacts. A host permission decision remains subject to the invoking tool's policy.

If this conversation verifiably matches the frozen coordinator model and effort, use `run RUN --external-coordinator`. `--external-astra` remains a compatibility alias. At `awaiting_coordinator`, read `external-request.json`, produce the requested response JSON in a separate file outside the target project (for example, within the run directory), then submit with the exact requested values:

```text
PYTHON HELPER submit RUN --response /path/to/response.json --model MODEL --effort EFFORT
PYTHON HELPER run RUN --external-coordinator
```

External configuration is recorded as caller-attested, not provider-verified. The submitted pair must exactly match the frozen profile. Never assert a different configuration to bypass this requirement. Otherwise use the coordinator's CLI path. A plain skill cannot change its invoking conversation's model.

The current packet contains the full plan or implementation diff, scoped sources, verbatim governing requirements, current checks, all finding dispositions, revision ledger, and current evidence references. Treat older sessions as supplemental context. The canonical record retains every finding ID even if rejected. No findings is a valid review. New implementation runs use model-supplied sequential IDs; never rewrite an existing finding's severity, location, evidence, correction, or acceptance check. New implementation findings are OPEN/UNVERIFIED and use a scoped project-relative `path`, `path:line`, or `path:start-end` location with `BLOCKER`, `WARN`, or `SUGGESTION` severity. Only independent recheck can newly mark PASSED, with current evidence and a supporting rationale.

New plan runs record `plan_protocol_version: 2` and follow the [stage-specific plan contract](plan-protocol.md). Review always advances to adjudication, which also assesses completeness and produces any required full refinement. Revised plans receive independent recheck, with at most two refinements; the helper completes without a final model call. Providers return compact assessments and new findings, and the helper assigns IDs and normalizes immutable canonical records. External submissions must use the exact schema in `external-request.json`. Runs without this version retain their existing advisory/refine/finalize stages and response contract; no migration or model change occurs.

New implementation runs record `implementation_evidence_version: 2` and use `review → adjudicate → repair → recheck → finalize` when findings are accepted and verified. The coordinator decides directly from the independent review, scoped source, and checks. Runs recorded with version 1 retain their `respond` and `reply` advisory stages and two-pass limit, including runs paused at either stage.

New implementation runs also record `implementation_response_version: 2` in state and the original snapshot; status, packet, and handoff expose it. At `repair` only, Sol returns the identity envelope (`implementation_response_version`, `run_id`, `stage`, `handoff_revision`, `target_fingerprint`), a nonblank `summary`, and `assessments`: one `{id, rationale}` for every `ACCEPTED` finding in canonical order. Each rationale must be substantive. The stage schema rejects missing, duplicate, unknown, reordered, or extra fields, including definition, disposition, and verification fields. The helper checks the saved repair lock, validates this compact response, reconstructs full canonical findings from persisted state, and applies only the accepted rationales. Rejected findings remain untouched. The full canonical validator and scoped write guard still run before acceptance. The repair artifact keeps both `submitted_response` and the canonical `response`.

An absent `implementation_response_version` preserves the older full-finding response for existing runs, including paused version-2 evidence runs; unsupported explicit versions fail closed. No saved run is migrated, and the version marker does not change frozen models, stage routing, or repair limits. A rejected response after writer exit leaves the edits in place and records an interrupted repair with the offending field when identifiable. Inspect the target and use the recovery procedure below; do not retry the writer.

Adjudication retains every existing finding in canonical order and cannot change its definition or verification state. The coordinator may append a sequential, evidence-backed finding when the scoped source and review packet establish a missed gap. New findings require an authorized scoped location, start `UNVERIFIED` without verification receipts, and must pass repair and independent recheck. The accepted adjudication entry contains the repair lock: accepted findings in order, authorized scope, exact check command arrays, target fingerprint, and handoff revision. The helper checks it against current state and its saved artifact before Sol receives write access. The same lock is in Sol's packet, and `handoff.md` shows the lock alongside decisions and the current scoped diff against the frozen base.

New implementation runs allow one repair and one recheck. If Opus leaves an accepted finding incomplete or introduces a new finding, the helper ends the run `unresolved` without another repair or coordinator call. A complete recheck enters finalization; failing configured checks keep it unresolved until a passing `rerun-checks` on the unchanged target reopens that finalization. No-findings runs proceed from review to finalization, and all-rejected runs proceed from adjudication to finalization, subject to passing checks.

Every response echoes the run, stage, target fingerprint, and handoff revision. The revision changes after an accepted response, reconciliation, or user decision, preventing an old response from answering a new instruction. Plan acceptance checks assess the revised document; passing means the plan is ready to implement, not that its code or future tests already passed. Implementation checks run before initial review and after repair, including when no findings remain. Failing or missing configured checks prevent completion.

## Single-stage handoff

Use `review-handoff` with one existing run directory to dispatch at most one authorized stage:

```text
PYTHON HELPER status /path/to/run
PYTHON HELPER step /path/to/run
```

Call `step` only when `status` reports `ready` and the invoking conversation permits the stage. It selects the receiving CLI role and frozen model settings, sends the canonical packet, and accepts the response through the existing validation and persistence path. No model overrides or external-coordinator flags are needed. An implementation repair may write only through the designated implementer; Plan mode in the invoking conversation still prohibits dispatching that repair.

For a Claude stage with a sandbox-hidden login, follow [Claude login visibility in a sandbox](#claude-login-visibility-in-a-sandbox). A sandboxed `step` may stop after recording initial checks but before dispatch; a subsequent approved host `step RUN --reviewer-only` is the single dispatched stage. Stop after that one reviewer dispatch. The reviewer-only guard fails before provider execution if the stage changed or initial implementation checks are missing.

Stop after one attempt and report the attempted stage, resulting status, blocker if any, and `handoff.md`. A ready next stage requires another invocation. Non-ready states, including external-coordinator waits, use [Recovery](#recovery) or the existing [external submission procedure](#run-and-interact); the handoff skill performs neither automatically. If output is lost, read `status` without replaying `step`. The existing `run` command and full review skills continue to support complete cycles.

## Recovery

- `blocked`, or an orphaned read-only `running` stage: inspect the saved process output. `retry RUN` only resets a read-only stage after target freshness checks; then run again. Never change models to clear a blocker.
- A transient configured-check failure on an unchanged current implementation target: run `rerun-checks RUN`. The command is allowed only in a read-only recoverable state, retains prior receipt files in the artifact history, writes uniquely identified current receipts, increments the handoff revision, and invalidates stale agent output. It does not change the configured commands, target, findings, stage, or repair count. A check-only unresolved finalization becomes ready only after every configured check passes; other blocked or unresolved states retain their status and still require their normal recovery.
- `interrupted` repair: inspect actual changes, Git state, process output, and scope. Stop any still-running process first. Then `reconcile RUN --note "actual inspected partial changes"`. This advances to independent recheck, counts a repair pass, and never reruns the write automatically.
- `needs_user`: obtain the user's actual decision, then `decide RUN --instruction "user decision"` and run again. Do not invent approval.
- Unexpected target changes or out-of-scope writes: preserve them, report the discrepancy, and start a new appropriately scoped run only after inspection. No automatic reset, checkout, or rollback.
- Session loss: retain handoff artifacts. Start a fresh run using the current target and include relevant past decisions in the requirements. Never use `--last`.

`started.json` records each process group. A project lock covers the helper and inherited child processes; surviving process groups block new stages and recovery. After a crash, inspect and stop the recorded process group before retrying. Never terminate unrelated processes. Reconciliation preserves uncommitted artifacts in the lineage, clears prior verification, and rechecks actual partial changes. The helper does not automatically replay an interrupted write.

## Prerequisites and boundaries

Python 3.11+, Git for implementation reviews, the pinned requirements installed in the installation virtual environment, Codex CLI and Claude Code on PATH, and working CLI login. Current tested CLI baselines are recorded in the validation report; the helper uses supported flags and fails on incompatible versions. Per-agent/check timeout defaults to 900 seconds and may be explicitly set to 1–3600 seconds.

The configured Claude reviewer runs with read/search tools, safe/restricted mode, no MCP tools, and hooks disabled; subscription authentication remains available. Codex roles run from an isolated runtime directory with user configuration ignored, explicit sandbox/approval settings, no nested agents, and no network access for execution tools. The implementer receives project write access only at repair stages; all other stages use read-only execution. Project instructions are supplied as context rather than enabling hooks or integrations. Managed host policies still apply; do not bypass them.

The helper's receipts report only observable configuration. It never equates a requested flag with provider attestation. Global permissions are not modified. Ignored runtime/build files are outside the project content guard; scoped tracked/nonignored files and Git staging/history are checked. No production/browser/provider verification is implied by a local pass.

The content inventory is capped at 20,000 tracked/nonignored files; full handoffs are capped at 4 MiB. The helper fails visibly instead of silently dropping history or source. `final.md` is a recoverable view of the accepted final artifact; check `status: complete` before treating it as a completed cycle.
