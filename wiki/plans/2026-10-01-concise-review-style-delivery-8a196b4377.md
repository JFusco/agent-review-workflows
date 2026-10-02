---
status: "implemented"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/49"]
source_tool: "repository"
source: "/private/tmp/agent-review-workflows-delivery/review-style-plan.md"
topics: ["plan-review-protocol", "implementation-review-evidence"]
digest: "8a196b43775e1807223b89aff720f0ff45272ad59b4ec2155951061e07b4c3f7"
---

# Concise review style delivery

Implement issue https://github.com/JFusco/agent-review-workflows/issues/49.

- Add concise pragmatic senior architect guidance to the existing helper
  prompt for plan and implementation reviews.
- Request exact evidenced locations, immediate scope, simple corrections,
  lean tests, and no filler; format newly refined plans as a checklist.
- Link both skill entrypoints to shared CLI guidance without adding stages,
  schemas, configuration, or provider calls.
- Add focused prompt assertions, update the wiki, run the repository gate,
  and stop at an open PR.
