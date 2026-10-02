---
issues: ['https://github.com/JFusco/agent-review-workflows/issues/33']
---
# Plan review protocol

Plan review aims to produce a precise, scoped, implementation-ready document.
Issue [#33](https://github.com/JFusco/agent-review-workflows/issues/33) keeps two
perspectives even when the first reviewer finds no defects: the coordinator
always assesses completeness. Independent recheck follows every refinement.

[Issue #49](https://github.com/JFusco/agent-review-workflows/issues/49) adds
concise, pragmatic review guidance to the helper prompt. A newly refined plan
uses an actionable checklist of evidenced edits and necessary verification;
an unchanged sound plan retains its text. Routing and response schemas stay
the same.

The protocol removes advisory exchanges, the separate refinement call, and the
verbatim finalization call. The common paths take two calls for a sound unchanged
plan, three for a first-pass corrected plan, and five when a second refinement is
needed. These are stage counts, not measured cost or latency improvements.

Determinism belongs to the contract and helper. Models return stage-specific
assessments and new definitions; the helper assigns IDs, preserves canonical
records, validates evidence and freshness, and routes the next stage. Prose
remains useful for rationale, evidence, corrections, acceptance criteria, and the
complete refined plan. The full contract is maintained in the
[protocol reference](../../references/plan-protocol.md).

Runs use `plan_protocol_version: 2`. Older runs remain as historical artifacts
but cannot resume; start a fresh review from the current plan and requirements.
Implementation review retains its own versioning and authority chain.
Opus 5.5 High and Astra Max remain the defaults, with per-run profiles frozen.
At most two refinement attempts are permitted, and incomplete second rechecks
remain unresolved. Completion views derive from accepted snapshots rather than
mutable draft files.

Deterministic fixtures establish routing, schema, persistence, permission, and
obsolete-run rejection. They do not establish comparative model quality, actual
provider effort, or production behavior.
