# Graph Report - .  (2026-09-29)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 373 nodes · 995 edges · 16 communities (15 shown, 1 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 120 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `98b9faa4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- archive-plan.cjs
- on-merge-sync.cjs
- audit-plan-candidates.cjs
- common.cjs
- plans.cjs
- viewer.js
- routing.cjs
- refresh-issue-state.cjs
- reconcile-merges.cjs
- serve-graph.cjs
- validate_pr_body.cjs
- python.cjs
- routing.js

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 32 edges
2. `repoRoot()` - 26 edges
3. `accept()` - 23 edges
4. `reconcile()` - 23 edges
5. `advance()` - 21 edges
6. `main()` - 21 edges
7. `collect()` - 18 edges
8. `slash()` - 17 edges
9. `git()` - 17 edges
10. `target()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `resolveBaseBranch()` --indirect_call--> `candidate()`  [INFERRED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/plans.cjs
- `main()` --calls--> `repoRoot()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/common.cjs
- `fromArgs()` --calls--> `slash()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `fromArgs()` --calls--> `titleFromBody()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/frontmatter.cjs
- `fromArgs()` --calls--> `cleanCursor()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/plans.cjs

## Import Cycles
- None detected.

## Communities (16 total, 1 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.14
Nodes (59): Exception, accept(), advance(), advisory_stage(), agent_settings(), assert_fresh(), assert_idle_group(), build_parser() (+51 more)

### Community 1 - "archive-plan.cjs"
Cohesion: 0.09
Nodes (40): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, archive() (+32 more)

### Community 2 - "on-merge-sync.cjs"
Cohesion: 0.10
Nodes (39): fs, { key: githubRefKey }, { loadPolicy, policyProblems }, main(), path, {
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
} (+31 more)

### Community 3 - "audit-plan-candidates.cjs"
Cohesion: 0.10
Nodes (39): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+31 more)

### Community 4 - "common.cjs"
Cohesion: 0.11
Nodes (30): { collect, resolveWikiLink, kind }, connections(), fs, main(), path, { repoRoot, slash, hasSymlinkComponent, atomicWrite }, crypto, { execFileSync } (+22 more)

### Community 5 - "plans.cjs"
Cohesion: 0.13
Nodes (26): { discover }, fs, main(), parse(), path, { repoRoot, atomicWrite }, atomicWrite(), walk() (+18 more)

### Community 6 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 7 - "routing.cjs"
Cohesion: 0.15
Nodes (24): adjacency(), edgeCost(), edgeKey(), edgeType(), EVIDENCE_TYPE_PRIORITY, formatBytes(), formatGithubRef(), fs (+16 more)

### Community 8 - "refresh-issue-state.cjs"
Cohesion: 0.18
Nodes (21): advanceFence(), closingIssues(), githubRefs(), key(), normalizeGithubQuery(), normalizeRepository(), parseGithubQuery(), ref() (+13 more)

### Community 9 - "reconcile-merges.cjs"
Cohesion: 0.18
Nodes (16): collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull(), main() (+8 more)

### Community 10 - "serve-graph.cjs"
Cohesion: 0.24
Nodes (9): createServer(), fs, http, listen(), main(), path, { repoRoot, ensureInside }, resolveRequest() (+1 more)

### Community 11 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 12 - "python.cjs"
Cohesion: 0.29
Nodes (6): fs, local, path, result, root, { spawnSync }

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `audit-plan-candidates.cjs` to `archive-plan.cjs`, `on-merge-sync.cjs`, `common.cjs`, `plans.cjs`, `refresh-issue-state.cjs`, `reconcile-merges.cjs`, `serve-graph.cjs`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `archive-plan.cjs`, `on-merge-sync.cjs`, `common.cjs`, `plans.cjs`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `plans.cjs` to `archive-plan.cjs`, `on-merge-sync.cjs`, `audit-plan-candidates.cjs`, `common.cjs`, `refresh-issue-state.cjs`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `review_cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13825136612021857 - nodes in this community are weakly interconnected._
- **Should `archive-plan.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.08748615725359911 - nodes in this community are weakly interconnected._
- **Should `on-merge-sync.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.10220673635307782 - nodes in this community are weakly interconnected._