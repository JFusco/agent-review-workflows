---
status: "implemented"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/76; scripts/review_cli.py; tests/test_review_transport.py"]
source_tool: "codex"
source: "Approved conversation plan: Smooth review delivery and context handling"
topics: ["plan-review-protocol"]
digest: "5fcf17c685ee5602af59dc6b31039fa3830033b6512eb8966e359c2a15629acb"
---

# Smooth review delivery and context handling

## Approved outcome

Prevent observed Codex message-size failure and Claude resumed-context failure
through the maintained helper. Preserve pinned models, independent verification,
the two-refinement plan-review limit and single-writer safeguards.

## Packet delivery

Preserve complete canonical packets and the 4 MiB ceiling. Up to 900,000 UTF-8
bytes remain inline; larger inputs use validated, readable per-call evidence
bundles for either CLI. Keep full source, diff, requirements, decisions, checks,
response schema, hashes and run/stage/revision identity. Handle long lines
losslessly without treating display labels as source. Missing or changed evidence
blocks launch. External coordinator contracts remain unchanged.

## Sessions and failures

Start each read-only CLI invocation fresh, including corrective and fallback
attempts, using the frozen selected model. Apply to future dispatches of supported
saved runs without changing historical or in-flight calls. Fresh invocations
require explicit new session IDs; recorded resumed calls retain exact identity
checks. Writer session behavior and reconciliation are unchanged.

Classify structured provider errors before legacy text matching. Distinguish
empty permission_denials with prompt_too_long from real denials. Context failures
use only frozen fallbacks; transport rejection must not switch models. Do not add
same-model retry loops, writer replay or additional review passes.

## Progress and completion

Report transport, session and selected model without dumping source. Distinguish
selection, dispatch and passed review. Retain an actionable unresolved handoff at
the two-refinement stop; never start another cycle automatically.

## Validation and delivery

Add deterministic regressions for UTF-8 thresholds, Unicode, long lines, complete
reconstruction, corrupt/missing evidence, identity, real denials, malformed errors,
fallback bounds, freshness, process guards and interrupted persistence. Retain
existing saved-run compatibility and writer safeguards. Complete verify:ci.
Update shared references, affected skill/README and wiki. Use issue-linked Git
and PR delivery; stop at the verified open PR. No live provider trial, installation
update, live-run recovery, merge, deployment or Brain publication is included.
