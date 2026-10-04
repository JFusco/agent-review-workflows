# Graph Report - agent-review-workflows  (2026-10-04)

## Corpus Check
- 26 files · ~27,220 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 409 nodes · 1136 edges · 14 communities (13 shown, 1 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4b518398`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- archive-plan.cjs
- on-merge-sync.cjs
- dates.cjs
- audit-plan-candidates.cjs
- viewer.js
- routing.cjs
- reconcile-merges.cjs
- validate_pr_body.cjs
- python.cjs
- routing.js
- serve-graph.cjs

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 40 edges
2. `accept()` - 32 edges
3. `advance()` - 28 edges
4. `main()` - 28 edges
5. `repoRoot()` - 26 edges
6. `reconcile()` - 23 edges
7. `collect()` - 18 edges
8. `rerun_checks()` - 17 edges
9. `initialize()` - 17 edges
10. `slash()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `resolveBaseBranch()` --indirect_call--> `candidate()`  [INFERRED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/plans.cjs
- `main()` --calls--> `archive()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/archive-plan.cjs
- `main()` --calls--> `validateArchiveInput()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/archive-plan.cjs
- `main()` --calls--> `repoRoot()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/common.cjs
- `validateArchiveInput()` --calls--> `slugify()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs

## Import Cycles
- None detected.

## Communities (14 total, 1 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.08
Nodes (95): Exception, accept(), advance(), agent_settings(), aggregate(), assert_claude_auth(), assert_fresh(), assert_idle_group() (+87 more)

### Community 1 - "archive-plan.cjs"
Cohesion: 0.06
Nodes (77): archive(), cell(), { cleanCursor }, { digest, repoRoot, slugify, slash, ensureInside, hasSymlinkComponent, atomicWrite, walk }, ensureIndex(), fromArgs(), fs, { inferPlanDate } (+69 more)

### Community 2 - "on-merge-sync.cjs"
Cohesion: 0.07
Nodes (58): fs, { key: githubRefKey }, { loadPolicy, policyProblems }, main(), path, {
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
} (+50 more)

### Community 3 - "dates.cjs"
Cohesion: 0.15
Nodes (21): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, STATUSES (+13 more)

### Community 4 - "audit-plan-candidates.cjs"
Cohesion: 0.12
Nodes (32): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+24 more)

### Community 5 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 6 - "routing.cjs"
Cohesion: 0.12
Nodes (31): { collect, normalizeWikiRoot }, main(), parseArgs(), { repoRoot }, { route, formatRoute }, usage(), adjacency(), edgeCost() (+23 more)

### Community 7 - "reconcile-merges.cjs"
Cohesion: 0.18
Nodes (16): collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull(), main() (+8 more)

### Community 8 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 9 - "python.cjs"
Cohesion: 0.29
Nodes (6): fs, local, path, result, root, { spawnSync }

### Community 13 - "serve-graph.cjs"
Cohesion: 0.24
Nodes (9): createServer(), fs, http, listen(), main(), path, { repoRoot, ensureInside }, resolveRequest() (+1 more)

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `archive-plan.cjs` to `on-merge-sync.cjs`, `dates.cjs`, `audit-plan-candidates.cjs`, `routing.cjs`, `reconcile-merges.cjs`, `serve-graph.cjs`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `git()` connect `archive-plan.cjs` to `dates.cjs`, `audit-plan-candidates.cjs`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `archive-plan.cjs` to `on-merge-sync.cjs`, `audit-plan-candidates.cjs`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `review_cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08462199312714777 - nodes in this community are weakly interconnected._
- **Should `archive-plan.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.05622489959839357 - nodes in this community are weakly interconnected._
- **Should `on-merge-sync.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.07043650793650794 - nodes in this community are weakly interconnected._