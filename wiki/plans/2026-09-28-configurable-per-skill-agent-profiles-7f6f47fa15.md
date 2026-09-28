---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#7; PR #8 branch codex/7-configurable-review-models; pnpm run verify:ci; both skill validators"]
source_tool: "codex"
source: "codex:/Users/joe.fusco/.codex/sessions/2026/09/28/rollout-2026-09-28T08-02-59-01a0e7e5-9725-7b31-93ab-2499f9cbed6d.jsonl"
topics: ["review-agent-profiles"]
digest: "7f6f47fa154cfc0bf29c984052f0db07ba83ccb6cadbf0433f59bbaeceee730a"
---

# Configurable Per-Skill Agent Profiles

## Summary

- Extend ignored `runtime.local.json` with independent role profiles for `review-plan` and `review-implementation`.
- Preserve today’s model/effort combinations as built-in defaults.
- Resolve settings in this order: explicit `start` flags → per-skill local profile → built-in defaults.
- Freeze the resolved profile into each run so configuration changes cannot alter an active or resumed review.
- Keep provider and permission boundaries fixed: Claude reviewer, Codex coordinator, and Codex implementation writer. Unsupported configurations stop without fallback.

## Public Interfaces

- Support this partial, mergeable configuration shape:

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

- Add matching per-run flags: `--reviewer-model/effort`, `--coordinator-model/effort`, and implementation-only `--implementer-model/effort`.
- Validate JSON shape, known skill/role/property names, nonblank model identifiers, and provider-specific effort vocabulary before creating run artifacts. Let the provider CLI determine model availability and model/effort compatibility.
- Add `--external-coordinator` while retaining `--external-astra` as a documented compatibility alias. External submissions must attest the exact coordinator model and effort frozen into the run.
- Preserve existing version-1 runs by assigning their original pinned profile when no stored profile exists.

## Implementation and Documentation

- Replace direct `MODELS` lookups in `scripts/review_cli.py` with one resolver used by launch, resume, extraction, status, receipts, and external handoffs.
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

- Begin from a clean, updated `main`; the current checkout is clean but two wiki-only commits behind `origin/main`.
- Create one canonical GitHub issue, implement on `codex/<issue>-configurable-review-models`, and commit as `feat(workflows): add configurable review agent profiles`.
- Open the templated PR with verification and rollback details, wait for required checks, merge it, verify automatic issue closure, then return the clean local checkout to synchronized `main`.
