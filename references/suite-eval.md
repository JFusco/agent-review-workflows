# Review-suite comparison

Require explicit baseline and candidate run directories. Resolve the installed helper/interpreter through the [CLI procedure](cli.md), then collect recorded evidence:

```sh
PYTHON HELPER compare-runs BASELINE_RUN CANDIDATE_RUN
```

The helper returns one JSON object with `report_version: 1`, UTC `observed_at`, `status`, `comparability`, `baseline`, `candidate`, and `limitations`. It requires readable originals/state and compares original requirements exactly as strings and targets as JSON values, without normalizing plan/source/diff text. COMPARABLE/0 means equal inputs, NOT_COMPARABLE/1 means different inputs, and UNKNOWN/2 means missing/malformed required inputs or changing evidence. Profile, recorded recovery (frozen fallbacks, selections, fallback history, response corrections, timeout and its history; empty when a run predates them), instruction, check-command, and protocol differences are separate context; equality does not establish equivalent execution or quality. Historical unsupported contracts may be inspected without migration or current-default substitution.

Each run reports:

- Recorded launch attempts from `calls/*/invocation.json`, independently of accepted ledger entries. Failed/rejected attempts still count; directories lacking invocation records are incomplete evidence, not launches. Missing sibling process receipts make duration/outcome unavailable.
- Accepted CLI, external, deterministic, operator, synthetic fixture, and unclassified events. CLI provenance includes `Claude modelUsage` and `not exposed by CLI output` even when observed model is null. External caller attestation does not manufacture a CLI attempt or measurement. Calls and ledger stages are not paired by position/stage name.
- Requested invocation settings separately from accepted ledger settings and observed metadata; observed effort stays unavailable when absent. Discrepancies do not change input comparability or imply fallback.
- Provider CLI and helper-managed check process time separately, with measured coverage and null/reason for unavailable measurements. CLI time includes tool work and is neither inference latency nor whole-run wall time. Current state receipts are copies of historical evidence, not extra executions.
- Final findings, current and historical check receipts, recorded protocol/profile context, and evidence paths.

Individual telemetry retains source paths and original field names. Claude JSON exposes `usage.input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `total_cost_usd`, and each `modelUsage` model's `inputTokens`, `outputTokens`, `cacheReadInputTokens`, `cacheCreationInputTokens`, `costUSD`. Fresh usage is labeled a reported main-loop result and cost/model totals as reported invocation totals. Resumed incremental accounting stays unknown; recorded cumulative totals are visible without inferred deltas. See [Claude cost tracking](https://code.claude.com/docs/en/agent-sdk/cost-tracking).

Codex JSONL `turn.completed` usage preserves `input_tokens`, `cached_input_tokens`, `output_tokens`, optional `reasoning_output_tokens`, event position, and recorded thread/session identity. These are reported turn-completion measurements; resumed additivity is not inferred. USD cost is unavailable when absent. See [Codex non-interactive output](https://learn.chatgpt.com/docs/non-interactive-mode).

This report version emits no cross-call token/cost totals or cumulative deltas. Do not add model breakdowns to their enclosing totals or describe estimates as billed savings. Missing optional telemetry does not invalidate input comparability. Relevant file sets/bytes are reread before returning; added, removed, or changed originals/state/call/check/output records force UNKNOWN, without locks or caches.

Use the packet to assess coverage, unsupported findings, scope, plan simplicity, and verification only against explicitly supplied maintainer expectations. Cite expectations and run evidence. Without expectations, semantic quality is unavailable. Finding counts and typed output do not prove quality; do not attribute every difference to the skill. Return a concise side-by-side comparison and limitations. Save any report outside both reviewed projects. Leave runs/projects unchanged and invoke no providers, GitHub, or project commands.
