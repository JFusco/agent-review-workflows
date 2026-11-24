---
topics: [contributor-quality-and-delivery]
plans: [2026-11-24-refresh-the-review-workflow-map-after-source-merges-3ae7cd1d48.md]
---

# Refresh the shared Graphify map after source merges

PR #111 refreshed the shared code map manually after the writer startup fix in PR #114. The native Git hooks work in local checkouts, so a GitHub merge could otherwise leave the tracked map behind.

The workflow compares the graph's recorded source revision with current main. It runs Graphify 0.9.36 for mapped script changes and proposes only tracked Graphify artifacts. A manifest-only change does not open a PR. The generated PR uses a dedicated bot branch and merges only after the full Quality gate, commit lint, and Wiki integrity pass on its exact head. A manual run on main retries a failed refresh.

[Tracking issue #117](https://github.com/JFusco/agent-review-workflows/issues/117) · [Office workflow reference](https://github.com/JFusco/the-office/pull/575)
