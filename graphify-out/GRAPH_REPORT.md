# Graph Report - agent-review-workflows  (2026-11-08)

## Corpus Check
- 26 files · ~32,261 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 443 nodes · 1317 edges · 24 communities (23 shown, 1 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `56078d47`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- render
- wiki-graph.cjs
- audit-plan-candidates.cjs
- routing.cjs
- viewer.js
- review_cli.py
- archive-plan.cjs
- delivery_evidence
- on-merge-sync.cjs
- ReviewError
- reconcile-merges.cjs
- digest
- advance
- validate_pr_body.cjs
- python.cjs
- routing.js
- accept
- serve-graph.cjs
- HandoffResponseError
- plans.cjs
- refresh-issue-state.cjs
- common.cjs

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 56 edges
2. `advance()` - 36 edges
3. `accept()` - 35 edges
4. `main()` - 34 edges
5. `repoRoot()` - 26 edges
6. `reconcile()` - 23 edges
7. `render()` - 22 edges
8. `initialize()` - 21 edges
9. `target()` - 19 edges
10. `digest()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `resolveBaseBranch()` --indirect_call--> `candidate()`  [INFERRED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/plans.cjs
- `main()` --calls--> `repoRoot()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/common.cjs
- `main()` --calls--> `inferPlanDate()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/dates.cjs
- `fromArgs()` --calls--> `slash()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `validateArchiveInput()` --calls--> `ensureInside()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs

## Import Cycles
- None detected.

## Communities (24 total, 1 thin omitted)

### Community 0 - "render"
Cohesion: 0.29
Nodes (15): accepted_research(), agent_candidate(), completion_report(), dispatch_summary(), effective_profile(), evidence_catalog(), packet(), primary_provider() (+7 more)

### Community 1 - "wiki-graph.cjs"
Cohesion: 0.17
Nodes (21): { collect, resolveWikiLink, kind }, connections(), fs, main(), path, { repoRoot, slash, hasSymlinkComponent, atomicWrite }, ensureInside(), hasSymlinkComponent() (+13 more)

### Community 2 - "audit-plan-candidates.cjs"
Cohesion: 0.08
Nodes (52): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+44 more)

### Community 3 - "routing.cjs"
Cohesion: 0.11
Nodes (30): { collect, normalizeWikiRoot }, main(), parseArgs(), { repoRoot }, { route, formatRoute }, usage(), adjacency(), edgeCost() (+22 more)

### Community 4 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 5 - "review_cli.py"
Cohesion: 0.17
Nodes (23): build_parser(), capacity_failure(), changed(), collapsed_plan(), compare_runs(), current_rejection(), evidence_snapshot(), helper_owned_definitions() (+15 more)

### Community 6 - "archive-plan.cjs"
Cohesion: 0.12
Nodes (28): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, archive() (+20 more)

### Community 7 - "delivery_evidence"
Cohesion: 0.16
Nodes (18): aggregate(), canonical_collection(), condition(), delivery_evidence(), finding_condition(), github_identity(), github_observation(), local_check_condition() (+10 more)

### Community 8 - "on-merge-sync.cjs"
Cohesion: 0.10
Nodes (45): fs, { key: githubRefKey }, { loadPolicy, policyProblems }, main(), path, {
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
} (+37 more)

### Community 9 - "ReviewError"
Cohesion: 0.25
Nodes (18): Exception, assert_claude_auth(), command(), initialize(), inventory(), load_runtime_config(), project_files(), research_writable_roots() (+10 more)

### Community 10 - "reconcile-merges.cjs"
Cohesion: 0.18
Nodes (16): collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull(), main() (+8 more)

### Community 11 - "digest"
Cohesion: 0.19
Nodes (20): assert_idle_group(), codex_startup_failure(), digest(), dumps(), execute_process(), group_alive(), prepare_transport(), project_lock() (+12 more)

### Community 12 - "advance"
Cohesion: 0.40
Nodes (14): advance(), agent_provider(), agent_settings(), cli_argv(), diff_checks_current(), external_submission_config(), extract_response(), guard_codex_read_only() (+6 more)

### Community 13 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 14 - "python.cjs"
Cohesion: 0.29
Nodes (6): fs, local, path, result, root, { spawnSync }

### Community 18 - "accept"
Cohesion: 0.28
Nodes (17): accept(), assert_fresh(), build_repair_lock(), checks_pass(), collapsed_implementation(), complete_findings(), DerivedViewError, finding_assessments() (+9 more)

### Community 19 - "serve-graph.cjs"
Cohesion: 0.24
Nodes (9): createServer(), fs, http, listen(), main(), path, { repoRoot, ensureInside }, resolveRequest() (+1 more)

### Community 20 - "HandoffResponseError"
Cohesion: 0.50
Nodes (4): ContractResponseError, HandoffResponseError, A response violated the stage contract; read-only stages may correct it once., A submitted handoff response failed validation.

### Community 21 - "plans.cjs"
Cohesion: 0.20
Nodes (18): walk(), association(), auditedDigests(), candidate(), collapseByTitle(), { digest, git, remoteSlug, walk, slash }, discover(), fromMarkdown() (+10 more)

### Community 22 - "refresh-issue-state.cjs"
Cohesion: 0.19
Nodes (13): advanceFence(), { advanceFence, githubRefs, key }, { execFileSync }, fs, issueRefs(), main(), markClosed(), openThreadLineIndexes() (+5 more)

### Community 23 - "common.cjs"
Cohesion: 0.18
Nodes (12): { discover }, fs, main(), parse(), path, { repoRoot, atomicWrite }, atomicWrite(), crypto (+4 more)

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `audit-plan-candidates.cjs` to `wiki-graph.cjs`, `routing.cjs`, `archive-plan.cjs`, `on-merge-sync.cjs`, `reconcile-merges.cjs`, `serve-graph.cjs`, `refresh-issue-state.cjs`, `common.cjs`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `wiki-graph.cjs`, `plans.cjs`, `common.cjs`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `common.cjs` to `wiki-graph.cjs`, `audit-plan-candidates.cjs`, `archive-plan.cjs`, `on-merge-sync.cjs`, `refresh-issue-state.cjs`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.07542087542087542 - nodes in this community are weakly interconnected._
- **Should `routing.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.11491935483870967 - nodes in this community are weakly interconnected._
- **Should `archive-plan.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.11954022988505747 - nodes in this community are weakly interconnected._