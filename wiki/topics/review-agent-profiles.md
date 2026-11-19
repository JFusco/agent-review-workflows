# Review agent profiles

[JFusco/agent-review-workflows issue #7](https://github.com/JFusco/agent-review-workflows/issues/7)
defines the configurable model and effort contract. Plan, implementation, and
diff reviews share the profile resolution rules in the
[CLI procedure](../../references/cli.md#agent-profiles).

[Issue #102](https://github.com/JFusco/agent-review-workflows/issues/102) selects
Astra 6.2 High for plan research, Astra 6.2 Max for coordination, and Sol 6.2
XHigh for scoped repair. Opus 5.5 High remains the routine independent reviewer.
Fable 5.2 High is a per-run reviewer choice for difficult work. The
[model refresh journal](../journal/2026-11-19-review-model-profiles.md) records the
rationale and verification boundary.

New runs freeze provider routing in `agent_providers`. The reviewer uses Claude;
research and coordination use Codex. Implementation defaults to a Codex writer
and supports explicitly selecting a Claude writer. The
[Opus writer journal](../journal/2026-11-08-opus-implementer.md) records the
previous default and the Claude writer permission scope. The
[CLI procedure](../../references/cli.md#recorded-model-fallback) owns read-only
fallback policy.

## Resolution and persistence

The helper validates the entire local JSON shape before creating run artifacts.
Each field resolves from an explicit start override, then the selected skill's
local profile, then the built-in default. The complete result is stored in a
run's state and original snapshot and is exposed in status, packets, handoffs,
and receipts. Later configuration or built-in default changes preserve stored
profiles for existing runs. Runs that predate provider snapshots retain their
historical Codex writer routing.

Saved runs missing current protocol markers stop before dispatch. Existing current
runs retain their saved primary profile and timeout, and have no fallback when
no candidate snapshot exists. New runs freeze default reviewer Claude → Codex
and coordinator Astra → Sol candidates. Selections and failed attempts remain
visible through recovery; sessions are never resumed across model switches.

## External coordinator boundary

`--external-coordinator` yields coordinator stages to a matching conversation.
The request and submission must match the currently selected frozen candidate.
Caller attestation remains separate from observed provider configuration.

## Timeout and capacity recovery

[Issue #64](https://github.com/JFusco/agent-review-workflows/issues/64) extends the
new-run default from 900 to 1800 seconds per model call/check, with the existing
1–3600-second override. Explicit capacity failures can advance an ordered,
validated fallback list, retaining the canonical findings and revision.
The CLI procedure owns configuration, eligibility, evidence, and recovery.
Writers never replay automatically, and a host reviewer-only dispatch yields
before any Codex fallback so execution can resume in the sandbox.

[Issue #69](https://github.com/JFusco/agent-review-workflows/issues/69) removes
rigid read-only blocks: a contract rejection gets one recorded corrective
re-prompt per selected candidate before fallback, incomplete `max_output_tokens`
responses are fallback-eligible, and `retry --timeout` records a raised per-call
timeout up to 14400 seconds. See the
[contract recovery journal](../journal/2026-10-26-review-contract-recovery.md).

The [check-blocked recheck recovery journal](../journal/2026-11-08-check-blocked-recheck-recovery.md)
records recovery after transient checks pass, preserving independent verification
and the one-writer limit.

## Evidence policy

Deterministic fixtures cover configuration precedence, frozen profiles,
provider routing, exact startup arguments, legacy recovery, and permission
boundaries. The profile refresh tests verify dispatch configuration. Model
availability, runtime behavior, and review quality require live evidence. See the
[validation record](../../VALIDATION.md) for historical trials.

## Reviewer authentication context

[Issue #42](https://github.com/JFusco/agent-review-workflows/issues/42)
records that a sandboxed Claude CLI can report logged out while the host CLI
uses an active login from the same configuration directory. The helper now
checks authentication with the run's saved Claude executable before a reviewer
call. An unavailable login leaves the stage ready without a provider call or
new handoff record. A guarded reviewer-only step permits approved host access
for that single Claude stage; configured checks continue in the sandbox.
Codex normally continues there, with an explicit guarded recovery exception below.
The [CLI procedure](../../references/cli.md#claude-login-visibility-in-a-sandbox)
owns the execution sequence. Authentication is never copied into run artifacts,
and the frozen profile and reviewer tool limits are unchanged.

## Codex launcher context

[Issue #83](https://github.com/JFusco/agent-review-workflows/issues/83) adds
`step --codex-read-only` for an explicitly approved host launcher when nested
Codex startup fails. It dispatches one selected read-only attempt, requires
current checks, and rejects research, repair, finalization and external
coordination. It performs no checks, fallback, correction or completion tail.
Model tools retain their read-only sandbox and execution-network denial.
The [CLI recovery procedure](../../references/cli.md#codex-launch-recovery) owns
the sequence; the [journal](../journal/2026-11-04-codex-launch-boundary.md)
distinguishes the reproduced failure, actual guarded canary and fixture coverage.

## Repair feasibility before locking

Implementation adjudication checks whether the correction and its acceptance
criteria fit the frozen files, commands, and source evidence. Missing
prerequisites use the existing pending-decision path before any writer runs;
unsupported criteria are rejected with their original records preserved. The
[CLI procedure](../../references/cli.md) owns the detailed decision contract.
