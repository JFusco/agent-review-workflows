# Graph Report - agent-review-workflows  (2026-11-04)

## Corpus Check
- 26 files · ~31,644 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 441 nodes · 1302 edges · 20 communities (19 shown, 1 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8b6098ed`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- archive-plan.cjs
- audit-plan-candidates.cjs
- routing.cjs
- viewer.js
- atomicWrite
- on-merge-sync.cjs
- delivery_evidence
- plans.cjs
- navigate.cjs
- reconcile-merges.cjs
- wiki-graph.cjs
- serve-graph.cjs
- validate_pr_body.cjs
- python.cjs
- routing.js
- repoRoot
- common.cjs

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 54 edges
2. `accept()` - 35 edges
3. `advance()` - 35 edges
4. `main()` - 33 edges
5. `repoRoot()` - 26 edges
6. `reconcile()` - 23 edges
7. `render()` - 21 edges
8. `initialize()` - 20 edges
9. `target()` - 19 edges
10. `digest()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `resolveBaseBranch()` --indirect_call--> `candidate()`  [INFERRED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/plans.cjs
- `main()` --calls--> `repoRoot()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/common.cjs
- `fromArgs()` --calls--> `slash()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `validateArchiveInput()` --calls--> `ensureInside()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `validateArchiveInput()` --calls--> `hasSymlinkComponent()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs

## Import Cycles
- None detected.

## Communities (20 total, 1 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.09
Nodes (106): Exception, accept(), accepted_research(), advance(), agent_candidate(), agent_provider(), agent_settings(), assert_claude_auth() (+98 more)

### Community 1 - "archive-plan.cjs"
Cohesion: 0.09
Nodes (41): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, archive() (+33 more)

### Community 2 - "audit-plan-candidates.cjs"
Cohesion: 0.13
Nodes (31): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+23 more)

### Community 3 - "routing.cjs"
Cohesion: 0.16
Nodes (22): adjacency(), edgeCost(), edgeKey(), edgeType(), EVIDENCE_TYPE_PRIORITY, formatGithubRef(), fs, githubRefText() (+14 more)

### Community 4 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 5 - "atomicWrite"
Cohesion: 0.24
Nodes (9): main(), parse(), { discover }, fs, main(), parse(), path, { repoRoot, atomicWrite } (+1 more)

### Community 6 - "on-merge-sync.cjs"
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

### Community 7 - "delivery_evidence"
Cohesion: 0.14
Nodes (21): aggregate(), canonical_collection(), compare_runs(), condition(), delivery_evidence(), evidence_snapshot(), finding_condition(), github_identity() (+13 more)

### Community 8 - "plans.cjs"
Cohesion: 0.20
Nodes (18): walk(), association(), auditedDigests(), candidate(), collapseByTitle(), { digest, git, remoteSlug, walk, slash }, discover(), fromMarkdown() (+10 more)

### Community 9 - "navigate.cjs"
Cohesion: 0.31
Nodes (8): { collect, normalizeWikiRoot }, main(), parseArgs(), { repoRoot }, { route, formatRoute }, usage(), formatBytes(), formatRoute()

### Community 10 - "reconcile-merges.cjs"
Cohesion: 0.18
Nodes (16): collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull(), main() (+8 more)

### Community 11 - "wiki-graph.cjs"
Cohesion: 0.19
Nodes (19): { collect, resolveWikiLink, kind }, connections(), fs, main(), path, { repoRoot, slash, hasSymlinkComponent, atomicWrite }, ensureInside(), slash() (+11 more)

### Community 12 - "serve-graph.cjs"
Cohesion: 0.24
Nodes (9): createServer(), fs, http, listen(), main(), path, { repoRoot, ensureInside }, resolveRequest() (+1 more)

### Community 13 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 14 - "python.cjs"
Cohesion: 0.29
Nodes (6): fs, local, path, result, root, { spawnSync }

### Community 18 - "repoRoot"
Cohesion: 0.32
Nodes (7): repoRoot(), substantive(), { discover }, main(), path, { repoRoot, git, substantive }, { spawnSync }

### Community 19 - "common.cjs"
Cohesion: 0.29
Nodes (6): crypto, { execFileSync }, fs, path, remoteSlug(), wikiPath()

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `repoRoot` to `archive-plan.cjs`, `audit-plan-candidates.cjs`, `atomicWrite`, `on-merge-sync.cjs`, `navigate.cjs`, `reconcile-merges.cjs`, `wiki-graph.cjs`, `serve-graph.cjs`, `common.cjs`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `plans.cjs`, `archive-plan.cjs`, `repoRoot`, `common.cjs`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `atomicWrite` to `archive-plan.cjs`, `audit-plan-candidates.cjs`, `on-merge-sync.cjs`, `wiki-graph.cjs`, `common.cjs`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `review_cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08618899273104881 - nodes in this community are weakly interconnected._
- **Should `archive-plan.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.08773784355179703 - nodes in this community are weakly interconnected._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.13306451612903225 - nodes in this community are weakly interconnected._