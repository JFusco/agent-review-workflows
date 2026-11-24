---
status: "implemented"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/117 and .github/workflows/graphify-refresh.yml"]
source_tool: "repository"
source: "/private/tmp/review-graphify-auto.2iPySM/automatic-graphify.md"
topics: ["contributor-quality-and-delivery"]
digest: "3ae7cd1d4896814be01c5e3ef3e2dc3de46452e018daecffd9142551f50bca8e"
---

# Refresh the review workflow map after source merges

Adapt the Office Graphify workflow to the review-workflows repository. Detect mapped script changes from the graph's recorded source revision, extract with the repository-pinned Graphify version, and publish the tracked artifacts through one bot PR. Require the repository's Quality, commit lint, and Wiki integrity checks on the generated head. Leave the working-copy map and the contributor merge boundary in place.
