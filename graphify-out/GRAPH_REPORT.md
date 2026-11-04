# Graph Report - agent-review-workflows  (2026-11-04)

## Corpus Check
- 26 files · ~31,028 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 437 nodes · 1268 edges · 14 communities (13 shown, 1 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `da35c6ee`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- on-merge-sync.cjs
- common.cjs
- archive-plan.cjs
- audit-plan-candidates.cjs
- viewer.js
- routing.cjs
- delivery_evidence
- reconcile-merges.cjs
- validate_pr_body.cjs
- python.cjs
- routing.js

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 51 edges
2. `accept()` - 35 edges
3. `advance()` - 33 edges
4. `main()` - 30 edges
5. `repoRoot()` - 26 edges
6. `reconcile()` - 23 edges
7. `render()` - 21 edges
8. `initialize()` - 20 edges
9. `target()` - 19 edges
10. `collect()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `resolveBaseBranch()` --indirect_call--> `candidate()`  [INFERRED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/plans.cjs
- `main()` --calls--> `repoRoot()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/common.cjs
- `main()` --calls--> `inferPlanDate()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/dates.cjs
- `fromArgs()` --calls--> `slash()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `validateArchiveInput()` --calls--> `ensureInside()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs

## Import Cycles
- None detected.

## Communities (14 total, 1 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.09
Nodes (102): Exception, accept(), accepted_research(), advance(), agent_candidate(), agent_provider(), agent_settings(), assert_claude_auth() (+94 more)

### Community 1 - "on-merge-sync.cjs"
Cohesion: 0.11
Nodes (40): fs, { key: githubRefKey }, { loadPolicy, policyProblems }, main(), path, {
  repoRoot,
  walk,
  slash,
  digest,
  hasSymlinkComponent,
}, { spawnSync }, {
  splitFrontmatter,
  scalar,
  list,
  frontmatterProblems,
} (+32 more)

### Community 2 - "common.cjs"
Cohesion: 0.05
Nodes (64): { collect, resolveWikiLink, kind }, connections(), fs, main(), path, { repoRoot, slash, hasSymlinkComponent, atomicWrite }, { discover }, fs (+56 more)

### Community 3 - "archive-plan.cjs"
Cohesion: 0.08
Nodes (46): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, archive() (+38 more)

### Community 4 - "audit-plan-candidates.cjs"
Cohesion: 0.09
Nodes (46): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+38 more)

### Community 5 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 6 - "routing.cjs"
Cohesion: 0.12
Nodes (31): { collect, normalizeWikiRoot }, main(), parseArgs(), { repoRoot }, { route, formatRoute }, usage(), adjacency(), edgeCost() (+23 more)

### Community 7 - "delivery_evidence"
Cohesion: 0.14
Nodes (21): aggregate(), canonical_collection(), compare_runs(), condition(), delivery_evidence(), evidence_snapshot(), finding_condition(), github_identity() (+13 more)

### Community 8 - "reconcile-merges.cjs"
Cohesion: 0.18
Nodes (17): remoteSlug(), collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull() (+9 more)

### Community 10 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 11 - "python.cjs"
Cohesion: 0.29
Nodes (6): fs, local, path, result, root, { spawnSync }

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `common.cjs` to `on-merge-sync.cjs`, `archive-plan.cjs`, `audit-plan-candidates.cjs`, `routing.cjs`, `reconcile-merges.cjs`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `reconcile-merges.cjs`, `common.cjs`, `archive-plan.cjs`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `common.cjs` to `on-merge-sync.cjs`, `archive-plan.cjs`, `audit-plan-candidates.cjs`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `review_cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08663181478715459 - nodes in this community are weakly interconnected._
- **Should `on-merge-sync.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.10570824524312897 - nodes in this community are weakly interconnected._
- **Should `common.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.054773082942097026 - nodes in this community are weakly interconnected._