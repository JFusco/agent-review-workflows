# Validation record

Executed 2026-09-28 using disposable, credential-free Python fixture projects. These results establish local workflow behavior and live provider CLI execution, not production verification.

## Default-profile configuration

| Role | Requested configuration | Observed evidence |
| --- | --- | --- |
| Orchestrator and plan refiner | Astra 6 Max | Codex session records confirm `gpt-6-astra`, `max`, read-only sandbox, and no approval prompts on initial and resumed turns. |
| Reviewer | Opus 5.5 High | Claude `modelUsage` identifies `claude-opus-5-5`; every initial/resumed invocation explicitly requests `--effort high`. The CLI result does not independently report effort. |
| Implementation writer | Sol 6 XHigh | Codex session records confirm `gpt-6-sol`, `xhigh`; the older response was read-only, and repair used an explicit writable project root with execution network access disabled. |

Claude Code version: **2.1.283**. The working Codex runtime is the app-bundled **0.158.0-alpha.2**. PATH Codex **0.153.4** rejected Sol 6 for the current ChatGPT account. These live trials used the newer executable through installation-local configuration and the built-in model profile; they did not change the user's PATH or global Codex settings. Astra also executed successfully through 0.153.4 during the plan trial.

CLI configuration records are observations from the local runtime, not independent provider attestation of internal reasoning.

## Local validation

- **33 tests passed**, covering strict schema handling, duplicates, stale targets and context revisions, rejected findings, evidence references, required check gates, plan-only behavior, initial/resumed model settings, scope protection, interrupted persistence, reconciliation, process groups, inherited locks, and symlink installation.
- Both skills passed the official `skill-creator` frontmatter and scaffold validator.
- Independent read-only helper review found concrete completion and recovery gaps. The fixes received regression tests; the reviewer confirmed the reported gaps addressed, including surviving child processes.

### Single-stage handoff skill (2026-09-29)

Issue [#27](https://github.com/JFusco/agent-review-workflows/issues/27) adds
`review-handoff` around the existing `status` and `step` commands. No provider
invocation or runtime protocol was added. The skill-creator validator passes.
Three command-level fixture tests cover single-stage dispatch for plan and both
implementation evidence versions, frozen reviewer settings and canonical packet
delivery, non-ready states without dispatch or recovery, and stale-target
rejection before dispatch. Installer tests cover all three skills, shared
reference resolution, repeated installation, configuration preservation, and
conflict preflight before any link is created.

Authoring walkthroughs checked the following requests against the skill's
description and instructions. These are static checks, not observed model
activation or live-provider evidence:

| Request | Defined behavior |
| --- | --- |
| “Use $review-handoff for this run directory.” | Inspect status, dispatch one authorized ready stage, report status and handoff. |
| “Send this review run to the next agent.” | Apply the same one-stage workflow. |
| “Hand off the review,” without a known run | Ask for the run; never infer the latest run. |
| “Write a project handoff for my teammate.” | Outside this skill's review-run boundary. |
| A blocked run, or an implementation repair during Plan mode | Report the blocker without dispatch or automatic recovery. |

Existing tests continue to establish repair-lock, scope, malformed-response,
revision, and independent-recheck boundaries. No new provider-backed trial or
production verification is claimed for this skill.

### Configurable-profile extension

Issue [#7](https://github.com/JFusco/agent-review-workflows/issues/7) added installation-local per-skill profiles and explicit per-run overrides. The expanded 49-test Python suite deterministically covers defaults, precedence, profile freezing, malformed configuration, provider and write boundaries, exact external-coordinator attestation, version-1 compatibility, and installer preservation. No provider-backed trial of custom profiles was run; that behavior remains fixture evidence.

### Evidence-complete implementation review

Issue [#9](https://github.com/JFusco/agent-review-workflows/issues/9) makes the
review input and decision boundary explicit for newly started implementation
runs. The expanded 58-test Python suite verifies mandatory local bases and
check commands, pre-artifact rejection, tracked and scoped-untracked diff capture,
deletions, unrelated-change exclusion, complete reviewer packets, located
findings, immutable finding definitions, advisory role assessments,
coordinator-only adjudication, recheck-only verification, and legacy
compatibility.

This extension uses credential-free temporary Git repositories and local check
commands. No provider-backed trial was run for that extension at the time; the
earlier live trials below establish built-in role and permission behavior, not
the issue #9 evidence contract.

### Five-call implementation protocol

Issue [#21](https://github.com/JFusco/agent-review-workflows/issues/21) introduces
implementation evidence version 2. The 71-test Python suite uses temporary Git
repositories to cover direct review-to-adjudication routing, the five-stage
successful ledger, the adjudication repair lock, scope and artifact tampering,
one repair and recheck, unresolved findings, check-only recovery, and version-1
advisory continuation. The handoff displays the current scoped diff. These are
deterministic fixture results, distinct from the branch trials below.

### Issue #21 live branch trials

Two provider-backed runs reviewed `codex/21-collapse-implementation-review`
against the frozen local `main` base with `pnpm run verify:ci` as the check and
Opus 5.5 High, Astra 6 Max, and Sol 6 XHigh as the requested profile. The
recorded CLI calls used those models; Claude's output did not independently
attest its requested effort.

- Run `632a4901-30d4-4e45-a0ed-29a04f2673b2` reached review, adjudication,
  repair, and recheck, then ended `unresolved` without another repair or Astra
  call. Opus found a missing version-1 regression; Astra accepted it and added
  the cited-check-receipt recovery defect. Sol repaired both within the lock.
  The fresh check passed 71 Python and 17 tooling tests, and Opus marked both
  accepted findings PASSED but found the stale 69-test validation count.
- Run `ae875591-5c8e-47a1-8285-d47787aec614` reviewed that target, then
  completed the five-stage ledger: review, adjudication with a saved repair
  lock, one Sol repair of the validation count, independent Opus PASS, and
  Astra finalization. Its fresh post-repair `pnpm run verify:ci` receipt passed
  71 Python tests, 17 tooling tests, and wiki integrity. The lock and scoped
  diff are visible in that run's `handoff.md`.

These are local branch/provider results, not production verification. The
first two Opus attempts could not authenticate inside the filesystem sandbox;
the CLI sign-in succeeded and the live calls ran with host credential access.
No model fallback was used. Sol's sandbox also needed a writable temporary
directory for a full gate run; the passing receipts are from completed runs,
not the earlier environment failures.

## Earlier live trials

| Workflow | Result | Evidence |
| --- | --- | --- |
| Implementation | Completed in one repair pass. Opus identified the incorrect divisor; Sol changed one line; two unittest cases passed; Opus independently marked the finding passed; Astra finalized without changing the reviewed finding. | [Final result](validation/implementation/final.md), [handoff](validation/implementation/handoff.md) |
| Plan | Completed in one refinement pass. Opus identified four issues in a deliberately overcomplicated plan. Astra produced a direct scoped plan. Opus verified all four plan corrections. Astra returned the reviewed plan verbatim. Project files remained unchanged. | [Final plan](validation/plan/final.md), [handoff](validation/plan/handoff.md) |

Each earlier successful trial has seven accepted handoff artifacts. Each used eight provider calls because one read-only output was rejected and retried after a focused correction. The implementation finalizer initially paraphrased reviewed finding text; finalization now explicitly preserves the entire array. The plan reviewer initially decorated evidence identifiers with prose; the provider schema now enumerates the exact valid references. Neither rejected output advanced the workflow.

Earlier trial failures also informed narrow fixes: provider-facing schemas omit the locally validated dialect URI because Claude did not register it; plan acceptance criteria explicitly assess the document instead of requiring its future code changes to have happened. A prior plan attempt stopped at the two-pass limit rather than implementing code to satisfy that mistaken criterion. No unavailable model was substituted.

## Ordinary-prompt comparison

A separate fresh Astra 6 Max invocation received the same raw requirements, overcomplicated plan and source files, with an ordinary request to review and refine the plan. It also produced a correct scoped correction and preserved the empty-input exception. Its plan proposed three additional test cases; the review workflow retained the existing sufficient tests and made additions optional.

This one small fixture does **not** establish a general quality advantage for the multi-agent workflow. The observed benefit is independent critique, recorded dispositions, revision binding and explicit verification. The ordinary prompt required one model call; the completed review cycle required eight during validation. [Baseline output](validation/baseline/call/answer.md).

## Evidence and limits

[Machine-readable results](validation/summary.json) retain call counts, observed local session configuration, provider elapsed time and actual check output. `validation/` contains ignored local copies of native prompts, outputs, process receipts, original targets, handoffs and immutable revisions. [The manifest](validation/manifest.json) records their file hashes. Invocation paths intentionally retain the original temporary locations; these are evidence archives, not relocated resumable runs.

The installed helper also supports using a conversation whose model and effort exactly match the frozen coordinator profile. Local tests cover yielding the external request and rejecting a mismatched submission; the provider-backed submit path was not exercised. Live trials used CLI Astra. Linux portability, large repositories, other programming languages, future CLI releases and production systems were not exercised. Parser tests establish covered rejection cases, not perfect handling of every possible malformed output.

## Sol 6.1 new-run default (2026-09-29)

Issue [#30](https://github.com/JFusco/agent-review-workflows/issues/30) changes
only the built-in implementer for new implementation runs to `gpt-6.1-sol` /
`xhigh`. Astra remains `gpt-6-astra` / `max`, and Opus remains
`claude-opus-5-5` / `high`. The [official model documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
lists `xhigh` support; it does not establish availability through any particular
CLI or account.

`pnpm run verify:ci` passed locally: Python and JavaScript lint, **78 Python
tests**, **17 tooling tests**, and wiki integrity. Focused regression coverage
establishes the exact new profile in saved state and original snapshots, frozen
initial/resumed implementer arguments, existing version-2 Sol 6 compatibility,
unchanged version-1 pins despite new-default edits, per-field override
precedence, and unchanged plan-review defaults. The existing suite continues to
cover scope, permission, freshness, interrupted recovery, repair locks, and
independent recheck. Graphify 0.9.36 refreshed the code map without model calls;
the wiki graph was rebuilt and checked.

These results are deterministic local configuration and compatibility evidence.
No paid or provider-backed Sol 6.1 trial was run. The historical Sol 6 trial
records above are preserved and do not establish Sol 6.1 provider execution or
repair quality. Unsupported selections still stop at the provider boundary
without fallback; existing runs retain their profiles and artifacts.
