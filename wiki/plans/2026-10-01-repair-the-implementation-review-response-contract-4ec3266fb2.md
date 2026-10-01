---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#36; scripts/review_cli.py; tests/test_review_cli.py; PYTHONPATH=tests .venv/bin/python -m unittest test_review_cli -q"]
source_tool: "codex"
source: "Approved Codex plan for JFusco/agent-review-workflows#36"
topics: ["implementation-review-evidence"]
digest: "4ec3266fb2d411742260a305ca021a392efdb9d499cdd1f8969cd9de086c3b3b"
---

# Repair the implementation-review response contract

## Summary

The offline reproduction confirmed that Sol’s completed repair was rejected because its full JSON response changed frozen finding definitions and verification evidence. The repository is clean on `main`; the baseline `pnpm run verify:ci` passed (96 Python tests, 17 tooling tests, lint, and wiki integrity). Change only the repair response for newly created implementation runs.

## Contract and implementation

- Record `implementation_response_version: 2` in new implementation run state and its original snapshot, and expose it in status and handoffs. Runs without the marker retain their saved full-response contract and frozen profiles; unsupported explicit versions fail closed.
- For version-2 `repair`, generate a strict schema requiring the identity envelope, `summary`, and an ordered `assessments` array. Each assessment contains only `{id, rationale}` for an accepted finding. Require every accepted ID exactly once in canonical order; reject unknown IDs, extra fields, and any submitted definition, disposition, or verification field.
- Validate the submitted shape, then deep-copy persisted findings and apply only accepted finding rationales. Retain rejected findings unchanged and keep adjudication decisions in the ledger. Run the existing canonical validator, repair-lock check, freshness and identity checks, and write guard before acceptance. Store both the compact submitted response and the reconstructed canonical response in the artifact.
- Identify the offending finding and field in response errors. When a writer exits successfully but its response is rejected, record an actionable `interrupted` error directing inspection and reconciliation. Keep the existing one-repair/one-recheck sequence; add no writer replay, provider call, fallback, or stage.

## Verification

- Add temporary-repository fixtures based on the handoff’s field-change pattern. Prove a valid scoped repair preserves definitions, dispositions, verification status, and evidence exactly, then reaches an independent recheck where `PASSED` still requires current evidence and rationale.
- Reject missing, duplicate, unknown, and reordered IDs; extra frozen fields, including changed evidence while `UNVERIFIED`; stale envelope values; and missing or altered repair locks. Assert rejected responses leave state, ledger, and repair count unchanged.
- Simulate edits followed by a rejected response: preserve the edits, block automatic retry, and verify inspected reconciliation consumes one pass and advances to recheck. Cover legacy paused runs, frozen models, write scope, five-stage routing, and terminal new recheck findings.
- Run `pnpm run verify:ci`. Treat these fixtures as local contract evidence; the recovered Design Passport incident needs no replay or provider trial.

## Documentation and delivery

Update the repair instructions and CLI reference, the implementation-review wiki topic and journal, and the executed-plan archive in the same change. The generated repair schema lives in `scripts/review_cli.py`; retain the existing full canonical schema for persisted responses.

Follow the repository’s issue-to-merge flow: refresh `main`, create and read back one scoped issue, branch from updated `main`, implement and verify, update Graphify, commit, open a template-compliant PR, wait for checks, merge, verify issue closure, and return to clean synchronized `main`.
