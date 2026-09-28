---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#4; codex/4-deterministic-pr-structure; pnpm run verify:ci (38 Python tests, 17 tooling tests)"]
source_tool: "repository"
source: "/private/tmp/agent-review-pr-structure-plan.md"
topics: ["contributor-quality-and-delivery"]
digest: "f5d137d40ffacac35c724d3b350c02beb6f8271af789f630e4364dd90e638d00"
---

# Enforce deterministic pull request structure

Implement the bounded work tracked by
[JFusco/agent-review-workflows issue #4](https://github.com/JFusco/agent-review-workflows/issues/4):

1. Add one canonical GitHub pull-request template with ordered review sections.
2. Require a closing issue reference, exact verification, risk and rollback, and
   a completed repository checklist.
3. Add a dependency-free body validator and run it in the existing pull-request
   lint workflow.
4. Document the same contract for contributors and agents.
5. Add focused regression coverage and record the work in the repository wiki.
6. Do not add an AI commit or pull-request helper.
