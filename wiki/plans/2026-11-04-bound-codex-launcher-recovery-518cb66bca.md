---
status: "implemented"
executed: true
evidence: ["Issue 83; ten command regressions passed; guarded live run 3546ab44-7bcd-4dd6-b6f0-2c92619ad574 reported with observed tool denials"]
source_tool: "repository"
source: "/private/tmp/workflow-83-plan.md"
topics: ["review-agent-profiles"]
digest: "518cb66bcad95f58e4b173ed21c7a6d8eeea37aee4b930b61a01deb2a276f8b0"
---

# Bound Codex launcher recovery

1. Reproduce the reported app-server initialization failure with the pinned CLI on a disposable project; retain the failed call without inferring the denied operation.
2. Add a separate guarded `step --codex-read-only` route that dispatches one selected read-only attempt under existing freshness and ownership checks. Reject checks, research, writers, finalization and external-coordinator combinations; suppress correction and fallback in this boundary.
3. Recognize only the exact Codex startup failure with empty stdout and report a bounded stage/receipt diagnostic before capacity matching.
4. Prove rejection, receipt preservation and single dispatch through controlled-child command tests. Validate the explicit approved launcher route from the managed conversation with actual model-tool write/network denial on a disposable fixture.
5. Update the common CLI procedure, affected entrypoints, validation record and wiki together. Preserve installed links, old runs and all ASTRAL artifacts.

Delivery gates: full CI, independent read-only review, canonical issue/PR, current hosted checks and explicitly authorized manual merge. The implementation archive does not claim those later delivery gates have already passed.
