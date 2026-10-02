---
status: "implemented"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/47"]
source_tool: "repository"
source: "/private/tmp/agent-review-workflows-delivery/review-suite-eval-plan.md"
topics: ["review-suite-evaluation"]
digest: "1654c27d2ae0753b5c0c15d8f7206653e20846703b3fde300769c2f4c7bd831f"
---

# Review-suite-eval delivery

Implement the evaluation portion of the reviewed three-skill plan for issue
https://github.com/JFusco/agent-review-workflows/issues/47.

- Add an explicitly invoked, instruction-only skill and focused reference.
- Require identical original requirements and targets before comparison.
- Compare recorded attempts, accepted stages, findings, check outcomes,
  process durations, and identifiable provider usage; mark gaps unavailable.
- Require maintainer expectations for quality judgments.
- Update installer coverage, README, authoring reference, and wiki.
- Validate manually and with the repository gate, then stop at an open PR.
