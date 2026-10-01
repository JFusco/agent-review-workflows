# Graph Report - agent-review-workflows  (2026-10-01)

## Corpus Check
- 26 files · ~22,767 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 380 nodes · 1036 edges · 18 communities (17 shown, 1 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 120 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `003de33c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- archive-plan.cjs
- on-merge-sync.cjs
- audit-plan-candidates.cjs
- plans.cjs
- wiki-graph.cjs
- viewer.js
- routing.cjs
- common.cjs
- reconcile-merges.cjs
- serve-graph.cjs
- validate_pr_body.cjs
- python.cjs
- routing.js
- apply-plan-audit.cjs
- discover-plans.cjs

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 36 edges
2. `accept()` - 27 edges
3. `repoRoot()` - 26 edges
4. `advance()` - 24 edges
5. `reconcile()` - 23 edges
6. `main()` - 22 edges
7. `collect()` - 18 edges
8. `initialize()` - 17 edges
9. `slash()` - 17 edges
10. `git()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `resolveBaseBranch()` --indirect_call--> `candidate()`  [INFERRED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/plans.cjs
- `main()` --calls--> `archive()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/archive-plan.cjs
- `main()` --calls--> `validateArchiveInput()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/archive-plan.cjs
- `main()` --calls--> `repoRoot()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/common.cjs
- `main()` --calls--> `inferPlanDate()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/dates.cjs

## Import Cycles
- None detected.

## Communities (18 total, 1 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.13
Nodes (66): Exception, accept(), advance(), advisory_stage(), agent_settings(), assert_fresh(), assert_idle_group(), build_parser() (+58 more)

### Community 1 - "archive-plan.cjs"
Cohesion: 0.17
Nodes (20): archive(), cell(), { cleanCursor }, { digest, repoRoot, slugify, slash, ensureInside, hasSymlinkComponent, atomicWrite, walk }, ensureIndex(), fromArgs(), fs, { inferPlanDate } (+12 more)

### Community 2 - "on-merge-sync.cjs"
Cohesion: 0.09
Nodes (47): slugify(), fieldSpan(), keyPattern(), list(), parseListLiteral(), quote(), render(), scalar() (+39 more)

### Community 3 - "audit-plan-candidates.cjs"
Cohesion: 0.09
Nodes (46): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+38 more)

### Community 4 - "plans.cjs"
Cohesion: 0.20
Nodes (17): walk(), association(), auditedDigests(), cleanCursor(), collapseByTitle(), { digest, git, remoteSlug, walk, slash }, discover(), fromMarkdown() (+9 more)

### Community 5 - "wiki-graph.cjs"
Cohesion: 0.15
Nodes (23): { collect, resolveWikiLink, kind }, connections(), fs, main(), path, { repoRoot, slash, hasSymlinkComponent, atomicWrite }, ensureInside(), hasSymlinkComponent() (+15 more)

### Community 6 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 7 - "routing.cjs"
Cohesion: 0.08
Nodes (41): fs, { key: githubRefKey }, { loadPolicy, policyProblems }, main(), path, {
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
} (+33 more)

### Community 8 - "common.cjs"
Cohesion: 0.21
Nodes (11): crypto, { execFileSync }, fs, path, repoRoot(), substantive(), { discover }, main() (+3 more)

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

### Community 16 - "apply-plan-audit.cjs"
Cohesion: 0.28
Nodes (8): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, STATUSES

### Community 17 - "discover-plans.cjs"
Cohesion: 0.33
Nodes (6): { discover }, fs, main(), parse(), path, { repoRoot, atomicWrite }

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `common.cjs` to `archive-plan.cjs`, `on-merge-sync.cjs`, `audit-plan-candidates.cjs`, `wiki-graph.cjs`, `routing.cjs`, `reconcile-merges.cjs`, `serve-graph.cjs`, `apply-plan-audit.cjs`, `discover-plans.cjs`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `common.cjs`, `plans.cjs`, `wiki-graph.cjs`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `archive-plan.cjs` to `on-merge-sync.cjs`, `audit-plan-candidates.cjs`, `wiki-graph.cjs`, `common.cjs`, `discover-plans.cjs`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `review_cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12906057945566285 - nodes in this community are weakly interconnected._
- **Should `on-merge-sync.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.08974358974358974 - nodes in this community are weakly interconnected._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.08865248226950355 - nodes in this community are weakly interconnected._