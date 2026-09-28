# Validation record

Executed 2026-09-28 using disposable, credential-free Python fixture projects. These results establish local workflow behavior and live provider CLI execution, not production verification.

## Default-profile configuration

| Role | Requested configuration | Observed evidence |
| --- | --- | --- |
| Orchestrator and plan refiner | Astra 6 Max | Codex session records confirm `gpt-6-astra`, `max`, read-only sandbox, and no approval prompts on initial and resumed turns. |
| Reviewer | Opus 5.5 High | Claude `modelUsage` identifies `claude-opus-5-5`; every initial/resumed invocation explicitly requests `--effort high`. The CLI result does not independently report effort. |
| Implementation responder and writer | Sol 6 XHigh | Codex session records confirm `gpt-6-sol`, `xhigh`; response is read-only, repair uses the fixture project as an explicit writable root with execution network access disabled. |

Claude Code version: **2.1.283**. The working Codex runtime is the app-bundled **0.158.0-alpha.2**. PATH Codex **0.153.4** rejected Sol 6 for the current ChatGPT account. These live trials used the newer executable through installation-local configuration and the built-in model profile; they did not change the user's PATH or global Codex settings. Astra also executed successfully through 0.153.4 during the plan trial.

CLI configuration records are observations from the local runtime, not independent provider attestation of internal reasoning.

## Local validation

- **33 tests passed**, covering strict schema handling, duplicates, stale targets and context revisions, rejected findings, evidence references, required check gates, plan-only behavior, initial/resumed model settings, scope protection, interrupted persistence, reconciliation, process groups, inherited locks, and symlink installation.
- Both skills passed the official `skill-creator` frontmatter and scaffold validator.
- Independent read-only helper review found concrete completion and recovery gaps. The fixes received regression tests; the reviewer confirmed the reported gaps addressed, including surviving child processes.

### Configurable-profile extension

Issue [#7](https://github.com/JFusco/agent-review-workflows/issues/7) added installation-local per-skill profiles and explicit per-run overrides. The expanded 49-test Python suite deterministically covers defaults, precedence, profile freezing, malformed configuration, provider and write boundaries, exact external-coordinator attestation, version-1 compatibility, and installer preservation. No new provider-backed trial was run: the live results below remain evidence for the built-in profile only, while custom-profile behavior is fixture evidence.

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
commands. No new provider-backed trial was run. The live results below remain
evidence for the built-in role and permission behavior only; they do not attest
the new evidence contract.

## Live trials

| Workflow | Result | Evidence |
| --- | --- | --- |
| Implementation | Completed in one repair pass. Opus identified the incorrect divisor; Sol changed one line; two unittest cases passed; Opus independently marked the finding passed; Astra finalized without changing the reviewed finding. | [Final result](validation/implementation/final.md), [handoff](validation/implementation/handoff.md) |
| Plan | Completed in one refinement pass. Opus identified four issues in a deliberately overcomplicated plan. Astra produced a direct scoped plan. Opus verified all four plan corrections. Astra returned the reviewed plan verbatim. Project files remained unchanged. | [Final plan](validation/plan/final.md), [handoff](validation/plan/handoff.md) |

Each successful trial has seven accepted handoff artifacts. Each used eight provider calls because one read-only output was rejected and retried after a focused correction. The implementation finalizer initially paraphrased reviewed finding text; finalization now explicitly preserves the entire array. The plan reviewer initially decorated evidence identifiers with prose; the provider schema now enumerates the exact valid references. Neither rejected output advanced the workflow.

Earlier trial failures also informed narrow fixes: provider-facing schemas omit the locally validated dialect URI because Claude did not register it; plan acceptance criteria explicitly assess the document instead of requiring its future code changes to have happened. A prior plan attempt stopped at the two-pass limit rather than implementing code to satisfy that mistaken criterion. No unavailable model was substituted.

## Ordinary-prompt comparison

A separate fresh Astra 6 Max invocation received the same raw requirements, overcomplicated plan and source files, with an ordinary request to review and refine the plan. It also produced a correct scoped correction and preserved the empty-input exception. Its plan proposed three additional test cases; the review workflow retained the existing sufficient tests and made additions optional.

This one small fixture does **not** establish a general quality advantage for the multi-agent workflow. The observed benefit is independent critique, recorded dispositions, revision binding and explicit verification. The ordinary prompt required one model call; the completed review cycle required eight during validation. [Baseline output](validation/baseline/call/answer.md).

## Evidence and limits

[Machine-readable results](validation/summary.json) retain call counts, observed local session configuration, provider elapsed time and actual check output. `validation/` contains ignored local copies of native prompts, outputs, process receipts, original targets, handoffs and immutable revisions. [The manifest](validation/manifest.json) records their file hashes. Invocation paths intentionally retain the original temporary locations; these are evidence archives, not relocated resumable runs.

The installed helper also supports using a conversation whose model and effort exactly match the frozen coordinator profile. Local tests cover yielding the external request and rejecting a mismatched submission; the provider-backed submit path was not exercised. Live trials used CLI Astra. Linux portability, large repositories, other programming languages, future CLI releases and production systems were not exercised. Parser tests establish covered rejection cases, not perfect handling of every possible malformed output.
