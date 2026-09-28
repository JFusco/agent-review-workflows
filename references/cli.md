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
      "implementer": { "model": "gpt-6-sol", "effort": "xhigh" }
    }
  }
}
```

Those values are also the built-in defaults. Claude effort accepts `low`, `medium`, `high`, `xhigh`, or `max`. Codex effort accepts `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`, or `ultra`; the selected model may support only a subset. Model identifiers must be nonblank and contain no whitespace. The provider CLI remains authoritative for model availability and model/effort compatibility; rejection stops the workflow without fallback.

At `start`, explicit `--reviewer-model` / `--reviewer-effort`, `--coordinator-model` / `--coordinator-effort`, and implementation-only `--implementer-model` / `--implementer-effort` override the selected skill profile. Resolution is per field: start flag, then installation profile, then built-in default. The helper validates the entire local configuration before creating a run and stores the complete resolved profile in its state, original snapshot, status, packet, and handoff. Later edits or deletion of `runtime.local.json` never change that run or its resumed sessions. Legacy version-1 runs retain the original default profile.

## Start

Write the user's authorized requirements, repair boundaries, acceptance checks, and relevant project prerequisites to a UTF-8 file outside the target project. Preserve a conversation draft as a separate UTF-8 plan file outside that project. Never pass credentials. For large reviews narrow scope: packets have a 4 MiB limit and are never silently truncated.

Examples below use `PYTHON` and `HELPER` to mean the resolved interpreter and script paths; invoke them as separate shell arguments.

```text
PYTHON HELPER start plan --project /path/to/project --requirements /path/to/requirements.md --plan /path/to/draft.md --scope src/relevant.py
PYTHON HELPER start implementation --project /path/to/project --requirements /path/to/requirements.md --scope src/changed.py --scope tests/test_changed.py --base origin/main --check "python3 -m unittest discover -s tests"
PYTHON HELPER start plan --project /path/to/project --requirements /path/to/requirements.md --plan /path/to/draft.md --coordinator-model gpt-6-luna --coordinator-effort high
```

`start` snapshots the target without calling a model. It prints the run directory. Select scope from the actual user request or diff. Resolve unclear targets with the user. `--base` is optional; when supplied it is resolved once to a local commit. Without it the supplied current files are reviewed. Include all files the repair may touch, but exclude unrelated work. Configuration, agent instructions, and secret files are not supported automatic repair targets.

Checks are user-authorized local commands, parsed into argv without a shell. Shell pipelines and operators are not supported. The helper executes them from the target project; choose disposable/non-production checks. Required project browser/build/test gates still apply. If unavailable, record the limitation instead of inventing a pass.

Artifact root precedence: `--runs-dir`, `AGENT_REVIEW_RUNS_DIR`, `$CODEX_HOME/review-runs`, then `~/.codex/review-runs`. Artifacts must remain outside the target project. The target defaults to the invocation directory; Git projects must use their repository root. Run permissions may require access to this artifact directory and the selected project.

## Run and interact

```text
PYTHON HELPER run /path/to/run
PYTHON HELPER status /path/to/run
```

The helper serializes the protocol and launches all three provider roles through the CLIs. Inspect `handoff.md`, `final.md`, `artifacts/`, and `calls/` within the run. `step` runs one stage. Stop at `complete`, `unresolved`, `needs_user`, or a reported blocker. No automatic model fallback, recursive agent delegation, or publication occurs.

If this conversation verifiably matches the frozen coordinator model and effort, use `run RUN --external-coordinator`. `--external-astra` remains a compatibility alias. At `awaiting_coordinator`, read `external-request.json`, produce the requested response JSON in a separate file outside the target project (for example, within the run directory), then submit with the exact requested values:

```text
PYTHON HELPER submit RUN --response /path/to/response.json --model MODEL --effort EFFORT
PYTHON HELPER run RUN --external-coordinator
```

External configuration is recorded as caller-attested, not provider-verified. The submitted pair must exactly match the frozen profile. Never assert a different configuration to bypass this requirement. Otherwise use the coordinator's CLI path. A plain skill cannot change its invoking conversation's model.

The current packet contains the full plan or scoped sources, governing requirements, all finding dispositions, revision ledger, and current evidence references. Treat older sessions as supplemental context. Retain every finding ID even if rejected. Review/recheck can introduce new IDs. New findings are OPEN/UNVERIFIED. Only independent recheck can newly mark PASSED, with current evidence and a supporting rationale. No findings is a valid review.

Every response echoes the run, stage, target fingerprint, and handoff revision. The revision changes after an accepted response, reconciliation, or user decision, preventing an old response from answering a new instruction. Plan acceptance checks assess the revised document; passing means the plan is ready to implement, not that its code or future tests already passed. Implementation checks run before initial review and after repair, including when no findings remain. Failing or missing configured checks prevent completion.

## Recovery

- `blocked`, or an orphaned read-only `running` stage: inspect the saved process output. `retry RUN` only resets a read-only stage after target freshness checks; then run again. Never change models to clear a blocker.
- `interrupted` repair: inspect actual changes, Git state, process output, and scope. Stop any still-running process first. Then `reconcile RUN --note "actual inspected partial changes"`. This advances to independent recheck, counts a repair pass, and never reruns the write automatically.
- `needs_user`: obtain the user's actual decision, then `decide RUN --instruction "user decision"` and run again. Do not invent approval.
- Unexpected target changes or out-of-scope writes: preserve them, report the discrepancy, and start a new appropriately scoped run only after inspection. No automatic reset, checkout, or rollback.
- Session loss: retain handoff artifacts. Start a fresh run using the current target and include relevant past decisions in the requirements. Never use `--last`.

`started.json` records each process group. A project lock covers the helper and inherited child processes; surviving process groups block new stages and recovery. After a crash, inspect and stop the recorded process group before retrying. Never terminate unrelated processes. Reconciliation preserves uncommitted artifacts in the lineage, clears prior verification, and rechecks actual partial changes. The helper does not automatically replay an interrupted write.

## Prerequisites and boundaries

Python 3.11+, the pinned requirements installed in the installation virtual environment, Codex CLI and Claude Code on PATH, and working CLI login. Current tested CLI baselines are recorded in the validation report; the helper uses supported flags and fails on incompatible versions. Per-agent/check timeout defaults to 900 seconds and may be explicitly set to 1–3600 seconds.

The configured Claude reviewer runs with read/search tools, safe/restricted mode, no MCP tools, and hooks disabled; subscription authentication remains available. Codex roles run from an isolated runtime directory with user configuration ignored, explicit sandbox/approval settings, no nested agents, and no network access for execution tools. The implementer receives project write access only at repair stages; all other stages use read-only execution. Project instructions are supplied as context rather than enabling hooks or integrations. Managed host policies still apply; do not bypass them.

The helper's receipts report only observable configuration. It never equates a requested flag with provider attestation. Global permissions are not modified. Ignored runtime/build files are outside the project content guard; scoped tracked/nonignored files and Git staging/history are checked. No production/browser/provider verification is implied by a local pass.

The content inventory is capped at 20,000 tracked/nonignored files; full handoffs are capped at 4 MiB. The helper fails visibly instead of silently dropping history or source. `final.md` is a recoverable view of the accepted final artifact; check `status: complete` before treating it as a completed cycle.
