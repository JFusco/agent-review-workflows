# Graph Report - agent-review-workflows  (2026-11-20)

## Corpus Check
- 26 files · ~32,374 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 447 nodes · 1369 edges · 18 communities (16 shown, 2 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 125 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c722c37c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- digest
- audit-plan-candidates.cjs
- routing.cjs
- viewer.js
- ReviewError
- common.cjs
- delivery_evidence
- on-merge-sync.cjs
- accept
- reconcile-merges.cjs
- advance
- render
- validate_pr_body.cjs
- rerun_checks
- routing.js
- serve-graph.cjs

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 59 edges
2. `advance()` - 37 edges
3. `accept()` - 35 edges
4. `main()` - 34 edges
5. `repoRoot()` - 26 edges
6. `reconcile()` - 23 edges
7. `render()` - 22 edges
8. `initialize()` - 21 edges
9. `target()` - 19 edges
10. `collect()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `inferPlanDate()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/dates.cjs
- `validateArchiveInput()` --calls--> `slugify()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `validateArchiveInput()` --calls--> `render()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/frontmatter.cjs
- `main()` --calls--> `inferPlanDate()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/dates.cjs
- `main()` --calls--> `atomicWrite()`  [EXTRACTED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/common.cjs

## Import Cycles
- None detected.

## Communities (18 total, 2 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.07
Nodes (10): build_parser(), capacity_failure(), changed(), ContractResponseError, DerivedViewError, HandoffResponseError, plan_response_schema(), provider_error() (+2 more)

### Community 1 - "digest"
Cohesion: 0.21
Nodes (15): assert_idle_group(), codex_startup_failure(), digest(), dumps(), execute_process(), group_alive(), prepare_transport(), project_lock() (+7 more)

### Community 2 - "audit-plan-candidates.cjs"
Cohesion: 0.10
Nodes (43): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+35 more)

### Community 3 - "routing.cjs"
Cohesion: 0.15
Nodes (23): adjacency(), edgeCost(), edgeKey(), edgeType(), EVIDENCE_TYPE_PRIORITY, formatBytes(), formatGithubRef(), formatRoute() (+15 more)

### Community 4 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 5 - "ReviewError"
Cohesion: 0.19
Nodes (19): assert_claude_auth(), command(), initialize(), inventory(), load_runtime_config(), project_files(), research_writable_roots(), resolve_agent_profile() (+11 more)

### Community 6 - "common.cjs"
Cohesion: 0.05
Nodes (84): fs, local, path, result, root, { spawnSync }, fs, main() (+76 more)

### Community 7 - "delivery_evidence"
Cohesion: 0.13
Nodes (22): aggregate(), canonical_collection(), compare_runs(), condition(), delivery_evidence(), evidence_snapshot(), finding_condition(), github_identity() (+14 more)

### Community 8 - "on-merge-sync.cjs"
Cohesion: 0.10
Nodes (42): slugify(), fieldSpan(), keyPattern(), list(), parseListLiteral(), quote(), render(), scalar() (+34 more)

### Community 9 - "accept"
Cohesion: 0.24
Nodes (17): accept(), build_repair_lock(), collapsed_implementation(), collapsed_plan(), current_rejection(), helper_owned_definitions(), implementation_response_v2(), normalize_response() (+9 more)

### Community 10 - "reconcile-merges.cjs"
Cohesion: 0.18
Nodes (14): collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull(), main() (+6 more)

### Community 11 - "advance"
Cohesion: 0.40
Nodes (14): advance(), agent_provider(), agent_settings(), cli_argv(), diff_checks_current(), external_submission_config(), extract_response(), guard_codex_read_only() (+6 more)

### Community 12 - "render"
Cohesion: 0.35
Nodes (13): accepted_research(), agent_candidate(), dispatch_summary(), effective_profile(), evidence_catalog(), packet(), primary_provider(), render() (+5 more)

### Community 13 - "validate_pr_body.cjs"
Cohesion: 0.36
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 14 - "rerun_checks"
Cohesion: 0.31
Nodes (13): assert_fresh(), checks_pass(), complete_findings(), completion_report(), finding_assessments(), finish_local(), next_artifact(), perform_checks() (+5 more)

### Community 19 - "serve-graph.cjs"
Cohesion: 0.22
Nodes (9): createServer(), fs, http, listen(), attempt(), main(), path, resolveRequest() (+1 more)

## Knowledge Gaps
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `common.cjs` to `on-merge-sync.cjs`, `serve-graph.cjs`, `audit-plan-candidates.cjs`, `reconcile-merges.cjs`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Should `review_cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06854838709677419 - nodes in this community are weakly interconnected._
- **Why does `ReviewError` connect `ReviewError` to `review_cli.py`, `digest`, `delivery_evidence`, `accept`, `advance`, `render`, `rerun_checks`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.09696969696969697 - nodes in this community are weakly interconnected._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `common.cjs`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Should `routing.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.14855072463768115 - nodes in this community are weakly interconnected._
- **Should `common.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.053650326109825376 - nodes in this community are weakly interconnected._