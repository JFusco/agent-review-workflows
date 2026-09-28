# Review agent profiles

[JFusco/agent-review-workflows issue #7](https://github.com/JFusco/agent-review-workflows/issues/7)
defines the configurable model and effort contract for `review-plan` and
`review-implementation`. Configuration is installation-local in ignored
`runtime.local.json`; explicit `start` flags override that file, and missing
fields inherit the built-in Opus 5.5 High, Astra 6 Max, and Sol 6 XHigh profile.

Profiles use functional roles rather than model names. Both skills have a
Claude `reviewer` and Codex `coordinator`; only implementation review has a
Codex `implementer`. Provider routing, read/write permissions, target
fingerprints, handoff revisions, bounded passes, and the single-writer rule are
not configurable. Unsupported model or effort combinations stop at the
provider boundary without substitution.

## Resolution and persistence

The helper validates the entire local JSON shape before creating run artifacts.
Each field resolves from an explicit start override, then the selected skill's
local profile, then the built-in default. The complete result is stored in a
version-2 run's state and original snapshot and is exposed in status, packets,
handoffs, and receipts. Later configuration edits or deletion cannot alter a
run or its resumed sessions.

Version-1 runs have no stored profile. They deterministically resolve to their
original pinned settings rather than current local configuration, preserving
artifact and recovery compatibility.

## External coordinator boundary

`--external-coordinator` yields coordinator stages to a matching conversation;
`--external-astra` remains a compatibility alias. The external request records
the frozen model and effort, and submission succeeds only when the caller
attests that exact pair. This attestation is recorded as caller-supplied rather
than provider-verified.

## Evidence policy

Deterministic fixtures cover configuration precedence, freezing, malformed
input, initial and resumed arguments, exact external submission, installer
preservation, legacy recovery, and unchanged permission boundaries. Existing
provider-backed validation proves only the built-in profile; configurable
profile support does not claim a new live-provider trial.
