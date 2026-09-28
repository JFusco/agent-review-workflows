---
topics: [review-agent-profiles]
plans: [2026-09-28-configurable-per-skill-agent-profiles-1dacf57a38.md]
issue: 'https://github.com/jfusco/agent-review-workflows/issues/7'
issues: ['https://github.com/jfusco/agent-review-workflows/issues/7']
---

# 2026-09-28 — Configurable review agent profiles

Implemented the per-skill model and effort configuration tracked by
[JFusco/agent-review-workflows issue #7](https://github.com/JFusco/agent-review-workflows/issues/7)
on `codex/7-configurable-review-models`, branched from updated `main`.

Ignored `runtime.local.json` now accepts partial profiles for the functional
reviewer, coordinator, and implementation-only implementer roles. Explicit
`start` flags override local values field by field, while omitted values retain
the validated Opus 5.5 High, Astra 6 Max, and Sol 6 XHigh defaults. New runs
store the complete resolved profile in version-2 state and expose it in status,
packets, handoffs, receipts, and the original snapshot.

The change preserves the review architecture rather than making providers or
permissions configurable. Claude remains the independent reviewer; Codex owns
coordination and implementation; only implementation repair receives a writable
root. Version-1 runs retain their historical pins. Model rejection remains a
visible blocker with no silent fallback.

The external-conversation path is now named `--external-coordinator`, with
`--external-astra` retained as a compatibility alias. Requests record the
frozen coordinator pair, and mismatched caller attestations are rejected before
the response is accepted.

The expanded Python suite passes 49 cases covering profile precedence and
freezing, malformed configuration, provider and write boundaries, external
matching, installer preservation, and legacy compatibility. Both edited skill
packages pass the official skill validator, and `pnpm run verify:ci` passes the
complete repository gate. No provider-backed trial was run; the existing live
record remains evidence for the built-in profile only.
