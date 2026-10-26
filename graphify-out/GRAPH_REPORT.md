# Graph Report - agent-review-workflows  (2026-10-26)

## Corpus Check
- 26 files · ~27,888 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 417 nodes · 1176 edges · 20 communities (18 shown, 2 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `93f19f9f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- common.cjs
- audit-plan-candidates.cjs
- routing.cjs
- archive-plan.cjs
- on-merge-sync.cjs
- viewer.js
- ReviewError
- reconcile-merges.cjs
- validate_pr_body.cjs
- python.cjs
- routing.js
- accept
- advance
- rerun_checks
- serve-graph.cjs
- execute_process
- HandoffResponseError

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 43 edges
2. `accept()` - 32 edges
3. `advance()` - 31 edges
4. `main()` - 29 edges
5. `repoRoot()` - 26 edges
6. `reconcile()` - 23 edges
7. `initialize()` - 18 edges
8. `collect()` - 18 edges
9. `rerun_checks()` - 17 edges
10. `render()` - 17 edges

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

## Communities (20 total, 2 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.16
Nodes (25): aggregate(), build_parser(), canonical_collection(), changed(), compare_runs(), condition(), delivery_evidence(), evidence_snapshot() (+17 more)

### Community 1 - "common.cjs"
Cohesion: 0.06
Nodes (64): main(), parse(), { collect, resolveWikiLink, kind }, connections(), fs, main(), path, { repoRoot, slash, hasSymlinkComponent, atomicWrite } (+56 more)

### Community 2 - "audit-plan-candidates.cjs"
Cohesion: 0.13
Nodes (31): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+23 more)

### Community 3 - "routing.cjs"
Cohesion: 0.15
Nodes (25): adjacency(), edgeCost(), edgeKey(), edgeType(), EVIDENCE_TYPE_PRIORITY, formatBytes(), formatGithubRef(), formatRoute() (+17 more)

### Community 4 - "archive-plan.cjs"
Cohesion: 0.09
Nodes (40): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, archive() (+32 more)

### Community 5 - "on-merge-sync.cjs"
Cohesion: 0.07
Nodes (59): fs, { key: githubRefKey }, { loadPolicy, policyProblems }, main(), path, {
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
} (+51 more)

### Community 6 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 7 - "ReviewError"
Cohesion: 0.22
Nodes (22): Exception, assert_claude_auth(), assert_fresh(), command(), digest(), initialize(), inventory(), load_runtime_config() (+14 more)

### Community 8 - "reconcile-merges.cjs"
Cohesion: 0.18
Nodes (16): collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull(), main() (+8 more)

### Community 9 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 10 - "python.cjs"
Cohesion: 0.29
Nodes (6): fs, local, path, result, root, { spawnSync }

### Community 14 - "accept"
Cohesion: 0.24
Nodes (19): accept(), build_repair_lock(), collapsed_implementation(), collapsed_plan(), DerivedViewError, effective_profile(), evidence_catalog(), implementation_response_v2() (+11 more)

### Community 15 - "advance"
Cohesion: 0.38
Nodes (16): advance(), agent_candidate(), agent_provider(), agent_settings(), cli_argv(), diff_checks_current(), dumps(), external_submission_config() (+8 more)

### Community 16 - "rerun_checks"
Cohesion: 0.31
Nodes (11): checks_pass(), complete_findings(), completion_report(), finding_assessments(), finish_local(), local_finalization(), next_artifact(), perform_checks() (+3 more)

### Community 17 - "serve-graph.cjs"
Cohesion: 0.24
Nodes (9): createServer(), fs, http, listen(), main(), path, { repoRoot, ensureInside }, resolveRequest() (+1 more)

### Community 18 - "execute_process"
Cohesion: 0.29
Nodes (8): assert_idle_group(), capacity_failure(), execute_process(), group_alive(), project_lock(), provider_error(), ProviderCallError, A classified provider capacity failure, eligible only for read-only fallback.

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `common.cjs` to `audit-plan-candidates.cjs`, `archive-plan.cjs`, `on-merge-sync.cjs`, `reconcile-merges.cjs`, `serve-graph.cjs`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `common.cjs`, `archive-plan.cjs`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `common.cjs` to `audit-plan-candidates.cjs`, `archive-plan.cjs`, `on-merge-sync.cjs`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `common.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.05875251509054326 - nodes in this community are weakly interconnected._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.13306451612903225 - nodes in this community are weakly interconnected._
- **Should `routing.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.1476923076923077 - nodes in this community are weakly interconnected._