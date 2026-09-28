---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#7; pnpm run verify:ci; both skill validators"]
source_tool: "repository"
source: "/private/tmp/configurable-agent-profiles-plan.md"
topics: ["review-agent-profiles"]
digest: "1dacf57a38e881eff20a8254533281fc3e464514276ba51aabd041d24d1b6f13"
---

# Configurable Per-Skill Agent Profiles

## Summary

- Extend ignored `runtime.local.json` with independent role profiles for `review-plan` and `review-implementation`.
- Preserve today's model/effort combinations as built-in defaults.
- Resolve settings in this order: explicit `start` flags, per-skill local profile, then built-in defaults.
- Freeze the resolved profile into each run so configuration changes cannot alter an active or resumed review.
- Keep provider and permission boundaries fixed: Claude reviewer, Codex coordinator, and Codex implementation writer. Unsupported configurations stop without fallback.

## Public Interfaces

- Support a partial, mergeable configuration under `skills.review-plan` and `skills.review-implementation`, using the functional roles `reviewer`, `coordinator`, and implementation-only `implementer`, each with `model` and `effort`.
- Add matching per-run flags: `--reviewer-model/effort`, `--coordinator-model/effort`, and implementation-only `--implementer-model/effort`.
- Validate JSON shape, known skill/role/property names, nonblank model identifiers, and provider-specific effort vocabulary before creating run artifacts. Let the provider CLI determine model availability and model/effort compatibility.
- Add `--external-coordinator` while retaining `--external-astra` as a documented compatibility alias. External submissions must attest the exact coordinator model and effort frozen into the run.
- Preserve existing version-1 runs by assigning their original pinned profile when no stored profile exists.

## Implementation and Documentation

- Replace direct fixed-model lookups with one resolver used by launch, resume, extraction, status, receipts, and external handoffs.
- Keep session routing, target fingerprints, revision checks, bounded passes, and write permissions independent of configurable model identity; only the implementation repair stage remains writable.
- Update both skill entrypoints and UI metadata to describe functional roles rather than fixed model names. Keep detailed configuration syntax in the CLI reference and README.
- Preserve the historical validation record: clarify that existing live evidence covers the default profile, while custom-profile behavior is established through deterministic tests rather than new paid provider trials.
- Record the decision in a new wiki topic and journal entry, archive this plan after implementation, rebuild the wiki graph, and run its integrity check.

## Test Plan

- Verify defaults, partial JSON inheritance, independent settings for the same role across both skills, and per-run override precedence.
- Verify the resolved profile remains unchanged after editing or deleting `runtime.local.json`, including resumed sessions.
- Reject malformed JSON, unknown keys, invalid role/skill combinations, blank models, invalid efforts, and mismatched external submissions without fallback.
- Verify custom models appear on initial and resumed provider argv, receipts, handoffs, status output, and external request artifacts.
- Verify custom settings cannot change providers, grant reviewer/coordinator writes, create a plan repair stage, or bypass the single-writer rule.
- Verify legacy runs retain the original Opus High, Astra Max, and Sol XHigh settings.
- Verify the installer preserves skill profiles when updating the configured Codex executable.
- Run skill validation and the complete `pnpm run verify:ci` gate.

## Delivery Assumptions

- Begin from a clean, updated `main` and create one canonical GitHub issue.
- Implement on `codex/<issue>-configurable-review-models`, use a conventional commit and pull request, wait for checks, merge, verify issue closure, and return the clean local checkout to synchronized `main`.
