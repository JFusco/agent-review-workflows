---
status: "implemented"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/53"]
source_tool: "repository"
source: "/private/tmp/agent-review-workflows-delivery/review-delivery-plan.md"
topics: ["review-delivery"]
digest: "59470a81edbe5f2d7a77e33903ea734e9db7985a80c9bcef153aa2ab5eb90ac2"
---

# Review-delivery delivery

1. Add `verify-target RUN --head SHA --pr-base SHA` as a read-only local identity proof for a completed implementation or reported diff review. Compare the accepted artifact, scoped files, full check context, clean checkout, ancestry, and changed paths. Return PASS, BLOCKED, or UNKNOWN JSON with distinct exits and recheck checkout stability.
2. Add a short, explicitly invoked `review-delivery` skill and focused procedure for reading an exact PR, linked issue, required checks, terminal run, and local identity result. Return READY, BLOCKED, or UNKNOWN without GitHub or project mutation.
3. Update the installer, README, CLI reference, focused regression tests, and wiki. Run the full repository gate and deliver an issue-linked PR.
