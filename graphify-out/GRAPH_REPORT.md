# Graph Report - agent-review-workflows  (2026-10-29)

## Corpus Check
- 26 files · ~29,299 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 429 nodes · 1219 edges · 18 communities (17 shown, 1 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2dda165c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- delivery_evidence
- archive-plan.cjs
- audit-plan-candidates.cjs
- routing.cjs
- plans.cjs
- on-merge-sync.cjs
- viewer.js
- review_cli.py
- reconcile-merges.cjs
- validate_pr_body.cjs
- python.cjs
- routing.js
- wiki-graph.cjs
- common.cjs
- refresh-issue-state.cjs
- serve-graph.cjs

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 46 edges
2. `accept()` - 33 edges
3. `advance()` - 32 edges
4. `main()` - 29 edges
5. `repoRoot()` - 26 edges
6. `reconcile()` - 23 edges
7. `render()` - 19 edges
8. `initialize()` - 18 edges
9. `collect()` - 18 edges
10. `rerun_checks()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `resolveBaseBranch()` --indirect_call--> `candidate()`  [INFERRED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/plans.cjs
- `main()` --calls--> `repoRoot()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/common.cjs
- `main()` --calls--> `inferPlanDate()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/dates.cjs
- `fromArgs()` --calls--> `slash()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `fromArgs()` --calls--> `cleanCursor()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/plans.cjs

## Import Cycles
- None detected.

## Communities (18 total, 1 thin omitted)

### Community 0 - "delivery_evidence"
Cohesion: 0.15
Nodes (20): aggregate(), compare_runs(), condition(), delivery_evidence(), evidence_snapshot(), finding_condition(), github_identity(), github_observation() (+12 more)

### Community 1 - "archive-plan.cjs"
Cohesion: 0.13
Nodes (26): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, archive() (+18 more)

### Community 2 - "audit-plan-candidates.cjs"
Cohesion: 0.09
Nodes (46): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+38 more)

### Community 3 - "routing.cjs"
Cohesion: 0.12
Nodes (31): { collect, normalizeWikiRoot }, main(), parseArgs(), { repoRoot }, { route, formatRoute }, usage(), adjacency(), edgeCost() (+23 more)

### Community 4 - "plans.cjs"
Cohesion: 0.20
Nodes (18): walk(), association(), auditedDigests(), candidate(), collapseByTitle(), { digest, git, remoteSlug, walk, slash }, discover(), fromMarkdown() (+10 more)

### Community 5 - "on-merge-sync.cjs"
Cohesion: 0.10
Nodes (44): fs, { key: githubRefKey }, { loadPolicy, policyProblems }, path, {
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
}, slugify() (+36 more)

### Community 6 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 7 - "review_cli.py"
Cohesion: 0.09
Nodes (95): Exception, accept(), advance(), agent_candidate(), agent_provider(), agent_settings(), assert_claude_auth(), assert_fresh() (+87 more)

### Community 8 - "reconcile-merges.cjs"
Cohesion: 0.18
Nodes (16): collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull(), main() (+8 more)

### Community 9 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 10 - "python.cjs"
Cohesion: 0.29
Nodes (6): fs, local, path, result, root, { spawnSync }

### Community 14 - "wiki-graph.cjs"
Cohesion: 0.16
Nodes (23): { collect, resolveWikiLink, kind }, connections(), fs, main(), path, { repoRoot, slash, hasSymlinkComponent, atomicWrite }, main(), ensureInside() (+15 more)

### Community 15 - "common.cjs"
Cohesion: 0.14
Nodes (18): { discover }, fs, main(), parse(), path, { repoRoot, atomicWrite }, atomicWrite(), crypto (+10 more)

### Community 16 - "refresh-issue-state.cjs"
Cohesion: 0.19
Nodes (13): advanceFence(), { advanceFence, githubRefs, key }, { execFileSync }, fs, issueRefs(), main(), markClosed(), openThreadLineIndexes() (+5 more)

### Community 17 - "serve-graph.cjs"
Cohesion: 0.24
Nodes (9): createServer(), fs, http, listen(), main(), path, { repoRoot, ensureInside }, resolveRequest() (+1 more)

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `common.cjs` to `archive-plan.cjs`, `audit-plan-candidates.cjs`, `routing.cjs`, `on-merge-sync.cjs`, `reconcile-merges.cjs`, `wiki-graph.cjs`, `refresh-issue-state.cjs`, `serve-graph.cjs`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `plans.cjs`, `wiki-graph.cjs`, `common.cjs`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `common.cjs` to `archive-plan.cjs`, `audit-plan-candidates.cjs`, `on-merge-sync.cjs`, `wiki-graph.cjs`, `refresh-issue-state.cjs`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `archive-plan.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.12698412698412698 - nodes in this community are weakly interconnected._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.08865248226950355 - nodes in this community are weakly interconnected._
- **Should `routing.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.11553030303030302 - nodes in this community are weakly interconnected._