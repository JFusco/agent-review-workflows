# Graph Report - agent-review-workflows  (2026-11-25)

## Corpus Check
- 31 files · ~33,787 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 503 nodes · 1458 edges · 22 communities (21 shown, 1 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 130 edges (avg confidence: 0.51)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e0c3eb27`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- digest
- audit-plan-candidates.cjs
- routing.cjs
- viewer.js
- ReviewError
- dates.cjs
- delivery_evidence
- on-merge-sync.cjs
- render
- reconcile-merges.cjs
- wiki-graph.cjs
- plans.cjs
- validate_pr_body.cjs
- advance
- routing.js
- create_trial.py
- ref_node_fs
- common.cjs
- ref_node_path
- discover-plans.cjs
- archive-plan.cjs

## God Nodes (most connected - your core abstractions)
1. `ReviewError` - 57 edges
2. `advance()` - 37 edges
3. `accept()` - 35 edges
4. `main()` - 34 edges
5. `repoRoot()` - 26 edges
6. `reconcile()` - 23 edges
7. `render()` - 22 edges
8. `initialize()` - 21 edges
9. `digest()` - 19 edges
10. `target()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `resolveBaseBranch()` --indirect_call--> `candidate()`  [INFERRED]
  scripts/wiki/audit-plan-candidates.cjs → scripts/wiki/lib/plans.cjs
- `verifyBase()` --indirect_call--> `isMapInput()`  [INFERRED]
  scripts/graphify/publish-refresh.cjs → scripts/graphify/map-files.cjs
- `refreshNeeded()` --indirect_call--> `isMapInput()`  [INFERRED]
  scripts/graphify/refresh.cjs → scripts/graphify/map-files.cjs
- `isRefreshPR()` --calls--> `mapOnly()`  [EXTRACTED]
  scripts/graphify/refresh-pr.cjs → scripts/graphify/map-files.cjs
- `main()` --calls--> `archive()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/archive-plan.cjs

## Import Cycles
- None detected.

## Communities (22 total, 1 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.07
Nodes (33): collections, contextlib, copy, datetime, fcntl, hashlib, jsonschema, math (+25 more)

### Community 1 - "digest"
Cohesion: 0.17
Nodes (23): assert_idle_group(), cli_argv(), codex_startup_failure(), digest(), dumps(), execute_process(), group_alive(), plan_revision_diff() (+15 more)

### Community 2 - "audit-plan-candidates.cjs"
Cohesion: 0.12
Nodes (33): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+25 more)

### Community 3 - "routing.cjs"
Cohesion: 0.11
Nodes (30): { collect, normalizeWikiRoot }, main(), parseArgs(), { repoRoot }, { route, formatRoute }, usage(), adjacency(), edgeCost() (+22 more)

### Community 4 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 5 - "ReviewError"
Cohesion: 0.20
Nodes (21): Exception, agent_candidate(), assert_claude_auth(), command(), initialize(), inventory(), load_runtime_config(), plan_response_schema() (+13 more)

### Community 6 - "dates.cjs"
Cohesion: 0.15
Nodes (21): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, STATUSES (+13 more)

### Community 7 - "delivery_evidence"
Cohesion: 0.14
Nodes (21): aggregate(), canonical_collection(), compare_runs(), condition(), delivery_evidence(), evidence_snapshot(), finding_condition(), github_identity() (+13 more)

### Community 8 - "on-merge-sync.cjs"
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

### Community 9 - "render"
Cohesion: 0.24
Nodes (23): accepted_research(), collapsed_plan(), current_rejection(), dispatch_summary(), effective_profile(), evidence_catalog(), guard_codex_research(), helper_owned_definitions() (+15 more)

### Community 10 - "reconcile-merges.cjs"
Cohesion: 0.17
Nodes (17): ref_node_os, collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull() (+9 more)

### Community 11 - "wiki-graph.cjs"
Cohesion: 0.17
Nodes (20): { collect, resolveWikiLink, kind }, connections(), fs, main(), path, { repoRoot, slash, hasSymlinkComponent, atomicWrite }, remoteSlug(), slash() (+12 more)

### Community 12 - "plans.cjs"
Cohesion: 0.20
Nodes (18): walk(), association(), auditedDigests(), candidate(), collapseByTitle(), { digest, git, remoteSlug, walk, slash }, discover(), fromMarkdown() (+10 more)

### Community 13 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 14 - "advance"
Cohesion: 0.28
Nodes (25): accept(), advance(), agent_provider(), assert_fresh(), build_repair_lock(), checks_pass(), collapsed_implementation(), complete_findings() (+17 more)

### Community 16 - "create_trial.py"
Cohesion: 0.27
Nodes (8): argparse, importlib_util, json, os, pathlib, shutil, subprocess, tempfile

### Community 17 - "ref_node_fs"
Cohesion: 0.12
Nodes (25): ref_node_child_process, ref_node_fs, changedPaths(), { execFileSync }, files, isMapInput(), mapOnly(), { branch, title, body } (+17 more)

### Community 18 - "common.cjs"
Cohesion: 0.19
Nodes (12): ref_node_crypto, crypto, { execFileSync }, fs, path, repoRoot(), substantive(), { discover } (+4 more)

### Community 19 - "ref_node_path"
Cohesion: 0.12
Nodes (17): ref_node_http, ref_node_path, fs, local, path, result, root, { spawnSync } (+9 more)

### Community 20 - "discover-plans.cjs"
Cohesion: 0.32
Nodes (7): { discover }, fs, main(), parse(), path, { repoRoot, atomicWrite }, atomicWrite()

### Community 21 - "archive-plan.cjs"
Cohesion: 0.16
Nodes (21): archive(), cell(), { cleanCursor }, { digest, repoRoot, slugify, slash, ensureInside, hasSymlinkComponent, atomicWrite, walk }, ensureIndex(), fromArgs(), fs, { inferPlanDate } (+13 more)

## Knowledge Gaps
- **101 isolated node(s):** `{ execFileSync }`, `files`, `{ execFileSync }`, `{ setTimeout: delay }`, `{ changedPaths, isMapInput, mapOnly }` (+96 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `common.cjs` to `audit-plan-candidates.cjs`, `routing.cjs`, `dates.cjs`, `on-merge-sync.cjs`, `reconcile-merges.cjs`, `wiki-graph.cjs`, `ref_node_path`, `discover-plans.cjs`, `archive-plan.cjs`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `common.cjs`, `wiki-graph.cjs`, `plans.cjs`, `dates.cjs`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `discover-plans.cjs` to `audit-plan-candidates.cjs`, `on-merge-sync.cjs`, `wiki-graph.cjs`, `common.cjs`, `archive-plan.cjs`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `{ execFileSync }`, `files`, `{ execFileSync }` to the rest of the system?**
  _101 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `review_cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06722689075630252 - nodes in this community are weakly interconnected._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.12477718360071301 - nodes in this community are weakly interconnected._
- **Should `routing.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.11491935483870967 - nodes in this community are weakly interconnected._