# Graph Report - fixes  (2026-10-26)

## Corpus Check
- 26 files · ~28,307 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 422 nodes · 1191 edges · 20 communities (18 shown, 2 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a5b02cdc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- archive-plan.cjs
- audit-plan-candidates.cjs
- routing.cjs
- plans.cjs
- on-merge-sync.cjs
- viewer.js
- ReviewError
- reconcile-merges.cjs
- validate_pr_body.cjs
- python.cjs
- routing.js
- collapsed_plan
- advance
- accept
- DerivedViewError
- select_fallback
- HandoffResponseError

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 43 edges
2. `accept()` - 33 edges
3. `advance()` - 32 edges
4. `main()` - 29 edges
5. `repoRoot()` - 26 edges
6. `reconcile()` - 23 edges
7. `render()` - 18 edges
8. `initialize()` - 18 edges
9. `collect()` - 18 edges
10. `rerun_checks()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `resolveBaseBranch()` --indirect_call--> `candidate()`  [INFERRED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/plans.cjs
- `main()` --calls--> `inferPlanDate()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/dates.cjs
- `fromArgs()` --calls--> `cleanCursor()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/plans.cjs
- `validateArchiveInput()` --calls--> `render()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/frontmatter.cjs
- `archive()` --calls--> `walk()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs

## Import Cycles
- None detected.

## Communities (20 total, 2 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.18
Nodes (23): aggregate(), build_parser(), canonical_collection(), compare_runs(), condition(), delivery_evidence(), evidence_snapshot(), finding_condition() (+15 more)

### Community 1 - "archive-plan.cjs"
Cohesion: 0.06
Nodes (70): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, archive() (+62 more)

### Community 2 - "audit-plan-candidates.cjs"
Cohesion: 0.09
Nodes (46): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+38 more)

### Community 3 - "routing.cjs"
Cohesion: 0.15
Nodes (25): adjacency(), edgeCost(), edgeKey(), edgeType(), EVIDENCE_TYPE_PRIORITY, formatBytes(), formatGithubRef(), formatRoute() (+17 more)

### Community 4 - "plans.cjs"
Cohesion: 0.10
Nodes (30): { discover }, fs, main(), parse(), path, { repoRoot, atomicWrite }, substantive(), walk() (+22 more)

### Community 5 - "on-merge-sync.cjs"
Cohesion: 0.07
Nodes (57): fs, { key: githubRefKey }, { loadPolicy, policyProblems }, main(), path, {
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
} (+49 more)

### Community 6 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 7 - "ReviewError"
Cohesion: 0.21
Nodes (23): Exception, assert_claude_auth(), assert_fresh(), command(), completion_report(), digest(), external_submission_config(), initialize() (+15 more)

### Community 8 - "reconcile-merges.cjs"
Cohesion: 0.18
Nodes (16): collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull(), main() (+8 more)

### Community 9 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 10 - "python.cjs"
Cohesion: 0.29
Nodes (6): fs, local, path, result, root, { spawnSync }

### Community 14 - "collapsed_plan"
Cohesion: 0.26
Nodes (13): collapsed_plan(), current_rejection(), evidence_catalog(), helper_owned_definitions(), implementation_response_v2(), normalize_response(), packet(), plan_response_schema() (+5 more)

### Community 15 - "advance"
Cohesion: 0.32
Nodes (15): advance(), agent_candidate(), agent_provider(), agent_settings(), build_repair_lock(), cli_argv(), dumps(), effective_profile() (+7 more)

### Community 16 - "accept"
Cohesion: 0.31
Nodes (19): accept(), changed(), checks_pass(), collapsed_implementation(), complete_findings(), diff_checks_current(), finding_assessments(), finish_local() (+11 more)

### Community 18 - "select_fallback"
Cohesion: 0.28
Nodes (9): assert_idle_group(), capacity_failure(), execute_process(), group_alive(), project_lock(), provider_error(), ProviderCallError, A classified provider capacity failure, eligible only for read-only fallback. (+1 more)

### Community 19 - "HandoffResponseError"
Cohesion: 0.50
Nodes (4): ContractResponseError, HandoffResponseError, A submitted handoff response failed validation., A response violated the stage contract; read-only stages may correct it once.

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `archive-plan.cjs` to `reconcile-merges.cjs`, `audit-plan-candidates.cjs`, `plans.cjs`, `on-merge-sync.cjs`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `archive-plan.cjs`, `plans.cjs`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `archive-plan.cjs` to `audit-plan-candidates.cjs`, `plans.cjs`, `on-merge-sync.cjs`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `archive-plan.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.05570745044429255 - nodes in this community are weakly interconnected._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.08865248226950355 - nodes in this community are weakly interconnected._
- **Should `routing.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.1476923076923077 - nodes in this community are weakly interconnected._