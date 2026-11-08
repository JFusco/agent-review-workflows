# Review agent profiles

[JFusco/agent-review-workflows issue #7](https://github.com/JFusco/agent-review-workflows/issues/7)
defines the configurable model and effort contract for `review-plan` and
`review-implementation`. Configuration is installation-local in ignored
`runtime.local.json`; explicit `start` flags override that file, and missing
fields inherit Opus 5.5 High for independent review and implementation, and
Astra 6 Max for coordination. The previous Sol 6.1 default was introduced in
[JFusco/agent-review-workflows issue #30](https://github.com/JFusco/agent-review-workflows/issues/30).

Profiles use functional roles rather than model names. Both skills have a
Claude `reviewer` and Codex `coordinator`; only implementation review has a
separate Claude `implementer` by default. Explicit Codex writer selections remain
supported. New runs freeze provider routing in `agent_providers`; older runs
without that snapshot retain their original Codex writer. Read/write permissions, target
fingerprints, handoff revisions, bounded passes, and the single-writer rule are
not configurable. The [Opus writer journal](../journal/2026-11-08-opus-implementer.md)
records the new default and scoped Claude permissions. Read-only fallback routing follows the bounded frozen policy in
the [CLI procedure](../../references/cli.md#recorded-model-fallback).

## Resolution and persistence

The helper validates the entire local JSON shape before creating run artifacts.
Each field resolves from an explicit start override, then the selected skill's
local profile, then the built-in default. The complete result is stored in a
version-2 run's state and original snapshot and is exposed in status, packets,
handoffs, and receipts. Later configuration edits or deletion cannot alter a
run or its resumed sessions. Updating the helper also preserves these stored
profiles: existing Sol 6 runs continue to use Sol 6. An explicit installation or
per-run `gpt-6-sol` selection still takes precedence over the new default.

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

Deterministic fixtures cover configuration precedence, freezing, malformed
input, initial and resumed arguments, exact external submission, installer
preservation, legacy recovery, and unchanged permission boundaries. Existing
provider-backed validation records the historical Sol 6 profile. The Sol 6.1
default change has deterministic configuration and compatibility coverage only;
neither those fixtures nor the earlier trials establish Sol 6.1 provider
execution or repair quality. See the [validation record](../../VALIDATION.md).

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
