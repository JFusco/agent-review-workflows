# Graph Report - agent-review-restricted-bundles  (2026-11-04)

## Corpus Check
- 26 files · ~31,671 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 442 nodes · 1305 edges · 19 communities (18 shown, 1 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b2781a6d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- accept
- archive-plan.cjs
- audit-plan-candidates.cjs
- routing.cjs
- viewer.js
- review_cli.py
- on-merge-sync.cjs
- delivery_evidence
- plans.cjs
- ReviewError
- reconcile-merges.cjs
- digest
- advance
- validate_pr_body.cjs
- python.cjs
- routing.js
- rerun_checks

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 54 edges
2. `advance()` - 36 edges
3. `accept()` - 35 edges
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
- `fromArgs()` --calls--> `slash()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `fromArgs()` --calls--> `cleanCursor()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/plans.cjs
- `validateArchiveInput()` --calls--> `ensureInside()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `validateArchiveInput()` --calls--> `hasSymlinkComponent()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs

## Import Cycles
- None detected.

## Communities (19 total, 1 thin omitted)

### Community 0 - "accept"
Cohesion: 0.23
Nodes (23): accept(), accepted_research(), build_repair_lock(), checks_pass(), collapsed_implementation(), collapsed_plan(), dispatch_summary(), effective_profile() (+15 more)

### Community 1 - "archive-plan.cjs"
Cohesion: 0.07
Nodes (50): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, archive() (+42 more)

### Community 2 - "audit-plan-candidates.cjs"
Cohesion: 0.12
Nodes (33): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+25 more)

### Community 3 - "routing.cjs"
Cohesion: 0.12
Nodes (31): { collect, normalizeWikiRoot }, main(), parseArgs(), { repoRoot }, { route, formatRoute }, usage(), adjacency(), edgeCost() (+23 more)

### Community 4 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 5 - "review_cli.py"
Cohesion: 0.15
Nodes (20): build_parser(), capacity_failure(), changed(), compare_runs(), ContractResponseError, current_rejection(), evidence_snapshot(), HandoffResponseError (+12 more)

### Community 6 - "on-merge-sync.cjs"
Cohesion: 0.05
Nodes (84): { collect, resolveWikiLink, kind }, connections(), fs, main(), path, { repoRoot, slash, hasSymlinkComponent, atomicWrite }, fs, { key: githubRefKey } (+76 more)

### Community 7 - "delivery_evidence"
Cohesion: 0.16
Nodes (18): aggregate(), canonical_collection(), condition(), delivery_evidence(), finding_condition(), github_identity(), github_observation(), local_check_condition() (+10 more)

### Community 8 - "plans.cjs"
Cohesion: 0.10
Nodes (30): { discover }, fs, main(), parse(), path, { repoRoot, atomicWrite }, substantive(), association() (+22 more)

### Community 9 - "ReviewError"
Cohesion: 0.19
Nodes (21): Exception, assert_claude_auth(), command(), DerivedViewError, initialize(), inventory(), load_runtime_config(), project_files() (+13 more)

### Community 10 - "reconcile-merges.cjs"
Cohesion: 0.18
Nodes (16): collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull(), main() (+8 more)

### Community 11 - "digest"
Cohesion: 0.21
Nodes (19): assert_idle_group(), codex_startup_failure(), digest(), dumps(), execute_process(), group_alive(), prepare_transport(), project_lock() (+11 more)

### Community 12 - "advance"
Cohesion: 0.35
Nodes (16): advance(), agent_candidate(), agent_provider(), agent_settings(), cli_argv(), diff_checks_current(), external_submission_config(), extract_response() (+8 more)

### Community 13 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 14 - "python.cjs"
Cohesion: 0.29
Nodes (6): fs, local, path, result, root, { spawnSync }

### Community 18 - "rerun_checks"
Cohesion: 0.36
Nodes (11): assert_fresh(), complete_findings(), completion_report(), finding_assessments(), finish_local(), next_artifact(), perform_checks(), reconcile() (+3 more)

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `archive-plan.cjs` to `audit-plan-candidates.cjs`, `routing.cjs`, `on-merge-sync.cjs`, `plans.cjs`, `reconcile-merges.cjs`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `plans.cjs`, `archive-plan.cjs`, `on-merge-sync.cjs`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `on-merge-sync.cjs` to `plans.cjs`, `archive-plan.cjs`, `audit-plan-candidates.cjs`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `archive-plan.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.06848357791754019 - nodes in this community are weakly interconnected._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.12477718360071301 - nodes in this community are weakly interconnected._
- **Should `routing.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.11553030303030302 - nodes in this community are weakly interconnected._