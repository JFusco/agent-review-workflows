# Review agent profiles

[JFusco/agent-review-workflows issue #7](https://github.com/JFusco/agent-review-workflows/issues/7)
defines the configurable model and effort contract for `review-plan` and
`review-implementation`. Configuration is installation-local in ignored
`runtime.local.json`; explicit `start` flags override that file, and missing
fields inherit the built-in Opus 5.5 High, Astra 6 Max, and Sol 6.1 Extra High
(`gpt-6.1-sol` / `xhigh`) profile. The new-run implementer default changed in
[JFusco/agent-review-workflows issue #30](https://github.com/JFusco/agent-review-workflows/issues/30).

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
run or its resumed sessions. Updating the helper also preserves these stored
profiles: existing Sol 6 runs continue to use Sol 6. An explicit installation or
per-run `gpt-6-sol` selection still takes precedence over the new default.

Version-1 runs have no stored profile. They deterministically resolve to their
original Opus 5.5 / `high`, Astra 6 / `max`, and Sol 6 / `xhigh` settings rather
than current defaults or local configuration. The historical profile table
remains separate from the new defaults; no run artifact migration or resumed
session model switch is performed.

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
provider-backed validation records the historical Sol 6 profile. The Sol 6.1
default change has deterministic configuration and compatibility coverage only;
neither those fixtures nor the earlier trials establish Sol 6.1 provider
execution or repair quality. See the [validation record](../../VALIDATION.md).
