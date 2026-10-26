---
topics: [review-agent-profiles, implementation-review-evidence]
issues:
  [
    'https://github.com/jfusco/agent-review-workflows/issues/67',
    'https://github.com/jfusco/agent-review-workflows/issues/68',
    'https://github.com/jfusco/agent-review-workflows/issues/69',
  ]
issue: 'https://github.com/jfusco/agent-review-workflows/issues/67'
---
# Review contract recovery without rigid blocks

Implementation runs blocked deterministically on correct work.
[Issue #67](https://github.com/JFusco/agent-review-workflows/issues/67): a
catalog-sized `verification_evidence` enum made Codex structured output fail
with `max_output_tokens` before any response. The provider schema no longer
enumerates catalog keys; `validate_response` still rejects references outside
the current evidence catalog. The provider-side cause is not established.

[Issue #68](https://github.com/JFusco/agent-review-workflows/issues/68):
implementation adjudicate and recheck echoed full finding records, and exact
comparison rejected a location whose lines moved after repair and evidence on a
new adjudication finding. The helper now owns those fields at both stages: it
restores saved definitions over echoed copies and starts new adjudication
findings `UNVERIFIED` with no evidence. Saved definitions stay immutable, the
raw response is retained as `submitted_response`, and verification still needs
current catalog evidence.

[Issue #69](https://github.com/JFusco/agent-review-workflows/issues/69) makes
the remaining read-only failures recoverable. A contract rejection re-dispatches
the same stage once per selected candidate with the rejection reason, then uses
the recorded fallback list. Incomplete `max_output_tokens` responses are
fallback-eligible. `retry --timeout` records a raised per-call timeout, and the
ceiling is now 14400 seconds. Writers, extraction integrity errors, target
drift, and live process groups keep their existing stops.

Evidence is deterministic fixtures in `tests/test_review_cli.py` replaying both
#68 sequences, the #67 catalog shape, correction and fallback ordering, and
timeout bounds. No live-provider trial was run. The
[agent profile topic](../topics/review-agent-profiles.md) records the policy.
