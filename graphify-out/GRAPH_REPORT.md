# Graph Report - agent-review-workflows  (2026-11-22)

## Corpus Check
- 26 files · ~32,806 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 474 nodes · 1403 edges · 22 communities (21 shown, 1 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 121 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7d6a42d0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- review_cli.py
- digest
- audit-plan-candidates.cjs
- routing.cjs
- viewer.js
- ReviewError
- archive-plan.cjs
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
- common.cjs
- repoRoot
- serve-graph.cjs
- check.cjs
- build-graph.cjs

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
- `main()` --calls--> `repoRoot()`  [EXTRACTED]
  scripts/wiki/apply-plan-audit.cjs → scripts/wiki/lib/common.cjs
- `fromArgs()` --calls--> `digest()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `fromArgs()` --calls--> `slash()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/common.cjs
- `fromArgs()` --calls--> `cleanCursor()`  [EXTRACTED]
  scripts/wiki/archive-plan.cjs → scripts/wiki/lib/plans.cjs

## Import Cycles
- None detected.

## Communities (22 total, 1 thin omitted)

### Community 0 - "review_cli.py"
Cohesion: 0.06
Nodes (36): collections, contextlib, copy, datetime, fcntl, hashlib, jsonschema, math (+28 more)

### Community 1 - "digest"
Cohesion: 0.17
Nodes (23): assert_idle_group(), cli_argv(), codex_startup_failure(), digest(), dumps(), execute_process(), group_alive(), plan_revision_diff() (+15 more)

### Community 2 - "audit-plan-candidates.cjs"
Cohesion: 0.12
Nodes (33): audit(), branchIssueNumbers(), classify(), distinctiveTitleWords(), { execFileSync }, extractPaths(), findPrForMergeSubject(), fmtCommit() (+25 more)

### Community 3 - "routing.cjs"
Cohesion: 0.15
Nodes (25): adjacency(), edgeCost(), edgeKey(), edgeType(), EVIDENCE_TYPE_PRIORITY, formatBytes(), formatGithubRef(), formatRoute() (+17 more)

### Community 4 - "viewer.js"
Cohesion: 0.19
Nodes (25): addMetaLink(), addMetaRow(), addRelationship(), applyView(), buildIndexes(), buildLegend(), buildModel(), buildRenderer() (+17 more)

### Community 5 - "ReviewError"
Cohesion: 0.23
Nodes (20): Exception, agent_candidate(), assert_claude_auth(), command(), guard_codex_research(), initialize(), inventory(), load_runtime_config() (+12 more)

### Community 6 - "archive-plan.cjs"
Cohesion: 0.09
Nodes (39): { archive, validateArchiveInput, STATUSES }, fs, { inferPlanDate }, main(), parse(), path, { repoRoot }, archive() (+31 more)

### Community 7 - "delivery_evidence"
Cohesion: 0.14
Nodes (21): aggregate(), canonical_collection(), compare_runs(), condition(), delivery_evidence(), evidence_snapshot(), finding_condition(), github_identity() (+13 more)

### Community 8 - "on-merge-sync.cjs"
Cohesion: 0.09
Nodes (46): fieldSpan(), keyPattern(), list(), parseListLiteral(), quote(), render(), scalar(), splitFrontmatter() (+38 more)

### Community 9 - "render"
Cohesion: 0.27
Nodes (21): accepted_research(), collapsed_plan(), current_rejection(), dispatch_summary(), effective_profile(), evidence_catalog(), helper_owned_definitions(), implementation_response_v2() (+13 more)

### Community 10 - "reconcile-merges.cjs"
Cohesion: 0.17
Nodes (17): ref_node_os, collectPulls(), copyWikiForDryRun(), { execFileSync }, flattenPages(), fs, githubRequest(), isWikiBotPull() (+9 more)

### Community 11 - "wiki-graph.cjs"
Cohesion: 0.17
Nodes (20): ensureInside(), remoteSlug(), slash(), collect(), frontmatterTarget(), fs, { githubRefs, withoutFencedCode }, kind() (+12 more)

### Community 12 - "plans.cjs"
Cohesion: 0.18
Nodes (20): digest(), walk(), association(), auditedDigests(), candidate(), cleanCursor(), collapseByTitle(), { digest, git, remoteSlug, walk, slash } (+12 more)

### Community 13 - "validate_pr_body.cjs"
Cohesion: 0.39
Nodes (8): fs, main(), readableText(), REQUIRED_CHECKS, REQUIRED_SECTIONS, sections(), validatePullRequestBody(), withoutComments()

### Community 14 - "advance"
Cohesion: 0.28
Nodes (25): accept(), advance(), agent_provider(), assert_fresh(), build_repair_lock(), checks_pass(), collapsed_implementation(), complete_findings() (+17 more)

### Community 16 - "create_trial.py"
Cohesion: 0.27
Nodes (8): argparse, importlib_util, json, os, pathlib, shutil, subprocess, tempfile

### Community 17 - "common.cjs"
Cohesion: 0.13
Nodes (14): ref_node_child_process, ref_node_crypto, ref_node_fs, fs, local, path, result, root (+6 more)

### Community 18 - "repoRoot"
Cohesion: 0.17
Nodes (14): ref_node_path, { discover }, fs, main(), parse(), path, { repoRoot, atomicWrite }, repoRoot() (+6 more)

### Community 19 - "serve-graph.cjs"
Cohesion: 0.22
Nodes (10): ref_node_http, createServer(), fs, http, listen(), main(), path, { repoRoot, ensureInside } (+2 more)

### Community 20 - "check.cjs"
Cohesion: 0.22
Nodes (10): fs, { key: githubRefKey }, { loadPolicy, policyProblems }, main(), path, {
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
} (+2 more)

### Community 21 - "build-graph.cjs"
Cohesion: 0.31
Nodes (8): { collect, resolveWikiLink, kind }, connections(), fs, main(), path, { repoRoot, slash, hasSymlinkComponent, atomicWrite }, atomicWrite(), hasSymlinkComponent()

## Knowledge Gaps
- **89 isolated node(s):** `fs`, `path`, `{ spawnSync }`, `root`, `local` (+84 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `repoRoot()` connect `repoRoot` to `audit-plan-candidates.cjs`, `archive-plan.cjs`, `on-merge-sync.cjs`, `reconcile-merges.cjs`, `wiki-graph.cjs`, `common.cjs`, `serve-graph.cjs`, `check.cjs`, `build-graph.cjs`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `git()` connect `audit-plan-candidates.cjs` to `archive-plan.cjs`, `wiki-graph.cjs`, `plans.cjs`, `common.cjs`, `repoRoot`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `atomicWrite()` connect `build-graph.cjs` to `audit-plan-candidates.cjs`, `archive-plan.cjs`, `on-merge-sync.cjs`, `common.cjs`, `repoRoot`?**
  _High betweenness centrality (0.009) - this node is a cross-community bridge._
- **What connects `fs`, `path`, `{ spawnSync }` to the rest of the system?**
  _89 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `review_cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06116642958748222 - nodes in this community are weakly interconnected._
- **Should `audit-plan-candidates.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.12477718360071301 - nodes in this community are weakly interconnected._
- **Should `routing.cjs` be split into smaller, more focused modules?**
  _Cohesion score 0.1476923076923077 - nodes in this community are weakly interconnected._