# Graph Report - agent-review-workflows  (2026-10-01)

## Corpus Check
- 26 files · ~22,957 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 381 nodes · 1041 edges · 14 communities (13 shown, 1 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 120 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7abe9cd4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- on-merge-sync.cjs
- audit-plan-candidates.cjs
- plans.cjs
- archive-plan.cjs
- viewer.js
- routing.cjs
- reconcile-merges.cjs
- serve-graph.cjs
- validate_pr_body.cjs
- python.cjs
- routing.js

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 37 edges
2. `accept()` - 27 edges
3. `repoRoot()` - 26 edges
4. `advance()` - 25 edges
5. `reconcile()` - 23 edges
6. `main()` - 22 edges
7. `collect()` - 18 edges
8. `initialize()` - 17 edges
9. `slash()` - 17 edges
10. `git()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `resolveBaseBranch()` --indirect_call--> `candidate()`  [INFERRED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/plans.cjs
- `main()` --calls--> `repoRoot()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/common.cjs
- `main()` --calls--> `inferPlanDate()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/dates.cjs
- `fromArgs()` --calls--> `cleanCursor()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/plans.cjs
- `validateArchiveInput()` --calls--> `slugify()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs

## Import Cycles
- None detected.

## Communities (14 total, 1 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.13
Nodes (67): Exception, accept(), advance(), advisory_stage(), agent_settings(), assert_claude_auth(), assert_fresh(), assert_idle_group() (+59 more)

### Community 2 - "on-merge-sync.cjs"
Cohesion: 0.09
Nodes (47): slugify(), fieldSpan(), keyPattern(), list(), parseListLiteral(), quote(), render(), scalar() (+39 more)

### Community 3 - "audit-plan-candidates.cjs"
Cohesion: 0.09
Nodes (46): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+38 more)

### Community 4 - "plans.cjs"
Cohesion: 0.10
Nodes (30): { discover }, fs, main(), parse(), path, { repoRoot, atomicWrite }, repoRoot(), substantive() (+22 more)

### Community 5 - "archive-plan.cjs"
Cohesion: 0.07
Nodes (55): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, archive() (+47 more)

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

- **Why does `repoRoot()` connect `plans.cjs` to `on-merge-sync.cjs`, `audit-plan-candidates.cjs`, `archive-plan.cjs`, `routing.cjs`, `reconcile-merges.cjs`, `serve-graph.cjs`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `plans.cjs`, `archive-plan.cjs`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `archive-plan.cjs` to `on-merge-sync.cjs`, `audit-plan-candidates.cjs`, `plans.cjs`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `review_cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12745098039215685 - nodes in this community are weakly interconnected._
- **Should `on-merge-sync.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.08748114630467571 - nodes in this community are weakly interconnected._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.08865248226950355 - nodes in this community are weakly interconnected._