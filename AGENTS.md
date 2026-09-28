# Agent Review Workflows

Keep review behavior explicit, evidence-backed, and narrowly scoped. Preserve the
pinned agent roles, models, reasoning settings, target fingerprints, revision
checks, stable finding IDs, and independent rechecks. Plan review remains
read-only; implementation writes remain limited to the designated repair agent
and authorized file scope. Never add silent model fallback, recursive delegation,
publication, deployment, or merge behavior to the review workflows themselves.

Run `pnpm run verify:ci` before delivery. This checks maintained Python and
JavaScript, the Python unit suite, temporary-repository hook tests, and wiki
integrity. Use `type(scope): subject` commit messages. Keep wiki hook failures
advisory after blocking staged-file checks. Do not install or invoke `ai-commit`
or `ai-pr`.

## Skill change quality

Treat skill instructions, agent metadata, schemas, and orchestration as a single
maintained contract. Before changing them, read `references/authoring.md` and the
relevant sections of `references/cli.md`.

- Keep skill descriptions short and discriminating. Put only always-needed rules
  in `SKILL.md`; route detailed procedures and evidence to focused references.
- Maintain one source of truth for each rule. Do not copy provider manuals,
  duplicate policy across entrypoints, or add generic reminders after one failure.
- Leave judgment-heavy investigation to the model. Use deterministic code only
  for fragile identity, permission, schema, freshness, routing, persistence, and
  recovery boundaries.
- Add an instruction, abstraction, dependency, configuration option, or workflow
  stage only for a concrete requirement or reproduced failure. Prefer extending
  the existing helper and contracts over parallel paths or compatibility layers.
- Preserve public behavior and artifact compatibility unless the change explicitly
  authorizes a break. Document migrations, recovery, and removal of obsolete paths;
  do not leave dead flags, unreachable code, or ownerless TODOs.
- Keep permissions least-privileged, reviewers read-only, and implementation to one
  writer. Never weaken scope guards, target fingerprints, revision checks, stable
  finding IDs, bounded passes, or evidence requirements to make a test pass.
- Define observable acceptance criteria and add the smallest regression coverage
  that proves them. Include malformed, stale, interrupted, permission, and
  idempotence cases when the changed boundary can fail that way.
- Keep fixture, live-provider, and production evidence distinct. Do not run paid or
  provider-backed trials when deterministic fixtures establish the change; when a
  live trial is necessary, use a disposable project with no production access.
- Update affected skill text, references, schemas, tests, and wiki records in the
  same delivery. Run `pnpm run verify:ci` and do not describe unexecuted settings
  or requested model configuration as observed provider evidence.

## Git delivery flow

For repository changes that include delivery, complete this sequence:

1. Confirm the worktree is safe to switch, then switch to `main` and run
   `git pull --ff-only` so the branch point is the current remote main.
2. Create one actionable GitHub issue with the repository's canonical labels
   using the `github-issue-creator` workflow, and read the saved issue back before
   creating downstream artifacts.
3. Create `codex/<issue-number>-<short-slug>` from that updated `main`.
4. Implement only the issue scope, record substantive work in the wiki in the
   same delivery, and run `pnpm run verify:ci`.
5. Commit with a valid conventional message, then push the issue branch with
   ordinary Git commands.
6. Open a pull request with a conventional title. The body must summarize the
   change and verification and include `Closes #<issue-number>` so GitHub visibly
   links the PR to the issue and closes the issue when the PR merges.
7. Wait for required checks, merge the PR, and verify both the merged PR state and
   the issue's automatic closed state.
8. Return the local checkout to `main`, run `git pull --ff-only`, and verify it
   matches `origin/main` with a clean worktree.

<!-- wiki-skill:start -->
## Context wiki

Use `wiki/` as this repository's durable record of executed plans, decisions, and substantive change history. Never bulk-load `wiki/`.

- For an exact current-code, file, symbol, or command question, inspect the named source or use targeted source `rg`; do not load history.
- For a direct single-topic history or rationale question, start at `wiki/INDEX.md` when it exists and open only the page it routes to.
- Only for a cross-page why, wiring, ownership, or impact question, run `node scripts/wiki/navigate.cjs --intent why --query "<terms>"` before opening wiki pages. Use `wiring` for ownership/dependencies and `impact` for change scope.
- Query with exact slugs, identifiers, symbols, or repository-qualified GitHub references. Never use a bare issue or PR number such as `#123`.
- When both endpoints are known, use exact `--from` and `--to` node IDs.
- Trust the router's deterministic weighted shortest route, which accounts for relationship cost, hubs, and page bytes. Open only its itinerary; never add candidates, neighbors, or adjacent pages.
- Read itinerary pages sequentially, never speculatively in parallel, and stop as soon as the answer is grounded.
- If resolution is ambiguous, rerun with one returned exact ID; never open every candidate.
- Never use `grep`, `find`, or recursive `rg` as initial wiki discovery. After a router miss, run at most one root-scoped exact search: `rg -n --fixed-strings "<exact term>" wiki/`. If it fails, inspect one known source path or ask one focused question; never widen the search.
- Never read generated graph JSON directly.
- After executing a Claude, Codex, or Cursor plan, archive it and add the journal/topic updates in the same delivery per `wiki/MECHANICS.md`.
- Run `node scripts/wiki/discover-plans.cjs` to recover missed plans, `node scripts/wiki/build-graph.cjs` after wiki edits, and `node scripts/wiki/check.cjs` before completion.
- The Sigma.js graph indexes only Markdown under `wiki/`; never add code nodes.

This managed block was installed for Codex, Cursor, and Claude (via `@AGENTS.md` in `CLAUDE.md`).
<!-- wiki-skill:end -->
