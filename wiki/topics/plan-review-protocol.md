---
issues: ['https://github.com/JFusco/agent-review-workflows/issues/33', 'https://github.com/JFusco/agent-review-workflows/issues/89']
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

## Reliable stage inputs

[Issue #76](https://github.com/JFusco/agent-review-workflows/issues/76) keeps the
same two-refinement budget while starting future read-only CLI attempts fresh,
including on supported saved runs. Complete current packets carry the review
context; prior session history is supplemental evidence. Large inputs use a
validated readable file bundle rather than an oversized inline message.
Structured context errors can use only the already-frozen fallback chain; real
permission denials and writer interruptions still stop. Details are maintained in
[the shared CLI procedure](../../references/cli.md#packet-delivery-and-sessions).

Deterministic transport fixtures cover UTF-8 thresholds, reconstruction of long
lines, evidence corruption, and permission failures. They do not prove provider
file access, complete model reading, latency improvements or review quality.

## Required research

[Issue #80](https://github.com/JFusco/agent-review-workflows/issues/80) adds a
separate Codex research stage for new state-schema-3 plan runs while retaining
plan protocol 2 and introducing research contract 1. Saved schema-2 runs still
use the original two roles and are labeled research unrecorded. The preceding
stage counts describe that historical path; new unchanged, first-refined, and
second-refined plans require three, four, and six accepted provider stages.

Research investigates reusable local solutions, Brain, and current primary web
sources before independent review. Its immutable accepted brief and digest stay
fixed through ordinary refinements and are supplied completely to both review
roles. Missing searches fail validation; source and recording limitations remain
visible. Material changes to requirements or scope require a new run. Existing
finding IDs, user-decision routing, independent rechecks, and two-refinement limit
remain in force. The researcher cannot write to the reviewed project.

The provisional researcher default is Codex Astra high, configurable and frozen
per run, with no automatic researcher fallback. Permission-profile and evidence
contracts are defined once in the [research reference](../../references/research.md).
Local fixtures and sandbox probes do not establish live model quality or usage;
the planned Astra high/xhigh and Opus high comparison remains separate.

## Researcher launch recovery

[Issue #89](https://github.com/JFusco/agent-review-workflows/issues/89) adds a
separate `step --codex-research-only` boundary for the required researcher when
nested Codex startup fails. The existing read-only review guard still excludes
research. After sandboxed retry/freshness checks, an explicitly approved launcher
runs one attempt using the original restricted research profile and frozen model.
Accepted research enters the ordinary independent review path; failures retain
receipts without automatic retries or fallback. The
[recovery procedure](../../references/cli.md#research-startup-recovery-and-guarded-researcher-launch)
is the authoritative contract. No saved-run migration or global permission change
is needed. Controlled tests establish the boundary; live execution is separate.

## Restricted bundle access

[Issue #92](https://github.com/JFusco/agent-review-workflows/issues/92) runs
Claude file-bundle calls from their owned call directory. The restricted file
tools can read all frozen evidence without gaining access to the live project
or broader temporary files. Inline calls, Codex execution, model profiles, and
evidence bytes retain their existing behavior. Controlled-child tests reproduce
the earlier denial and exercise complete indexed reads; live review is separate.

## Research citation feedback

[Issue #95](https://github.com/JFusco/agent-review-workflows/issues/95) addresses
repeated research rejection caused by missing source-to-search links and channel
mismatches. The provider schema explains the linking contract; validation names
all offending search references together. A missing link is a brief consistency
failure and does not establish that the source was never read.

Read-only rejection history supplies the latest error independently of the
bounded automatic correction history. Explicit retry preserves that budget and
uses feedback only from the same stage and revision. Historical briefs, frozen
roles, permissions, and evidence acceptance remain unchanged. The authoritative
details are in the [research reference](../../references/research.md).
Deterministic fixtures reproduce the observed two-rejection sequence; they do
not establish a measured reduction in live provider failures or cost.
