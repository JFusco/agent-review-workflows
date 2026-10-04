---
status: "implemented"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/62; scripts/review_cli.py; tests/test_mechanics.py"]
source_tool: "codex"
source: "review-run:8494bd23-af6d-457b-9261-b897deae038e"
topics: ["implementation-review-evidence", "review-delivery", "review-suite-evaluation"]
digest: "05d32c1a758607c3ca703332ad87f3094285ef07981b90c7c121ac89374cc70a"
---

# Move review mechanics into deterministic code

## Scope and expected result

Extend `scripts/review_cli.py` with scripted implementation completion, read-only delivery evidence collection, and recorded-run comparison. Reuse the existing validation, persistence, rendering, and bounded command infrastructure.

New implementation runs remove exactly one finalization provider call on each otherwise equivalent successful path:

| Successful path | Existing contract | New contract |
|---|---:|---:|
| No findings | 2 | 1 |
| All findings rejected | 3 | 2 |
| Repair and independent recheck | 5 | 4 |

These are expected provider-stage counts without retries. External conversation stages and failed attempts require separate accounting. The finalization ledger event remains present with local provenance.

Preserve frozen profiles, pinned roles/models/efforts, finding definitions and IDs, fingerprints, revision checks, repair locks, single-writer permissions, bounded passes, and independent rechecks. Substantive investigation, adjudication, repair, semantic coverage, and quality assessment retain their existing owners. Plan and diff routing retain their current contracts.

## 1. Deterministic implementation completion

### Saved-run compatibility

Update `require_current_protocol` to enforce this matrix, retaining existing stage and frozen-profile validation:

| Mode | Saved `schema_version` | Required markers | Completion owner |
|---|---:|---|---|
| implementation | 2 | `implementation_evidence_version: 2`, `implementation_response_version: 2` | Frozen coordinator |
| implementation | 3 | `implementation_evidence_version: 2`, `implementation_response_version: 2` | Local finalizer |
| plan | 2 | `plan_protocol_version: 2` | Existing plan helper completion |
| diff | 2 | `implementation_evidence_version: 2` | Existing adjudication/reporting |

Require actual integer values for every required version. Reject missing required markers, unsupported values, booleans, floats, strings, version 3 on plan/diff runs, and retired stages before dispatch. Continue validating complete frozen profiles through the existing profile validator.

`initialize` writes version 3 only for new implementation runs and records it in their `original.json`. Expose the implementation saved-run version in `status_payload`, `packet`, and `render`, alongside the existing implementation response version. Existing originals and artifacts remain unchanged and readable; missing historical original-snapshot version fields do not trigger migration.

Keep artifact `schema_version: 1`, the canonical response shape, and repair response version 2. The saved-run version distinguishes finalization ownership. Its global guard ensures an older helper rejects version-3 state instead of interpreting it as coordinator-finalized. Completed version-3 implementation runs remain eligible for `verify_target`; its identity checks and result contract stay unchanged.

### Local execution and validation

Add one focused local-finalization function for version-3 implementation runs at `stage: finalize`, `status: ready`.

- Invoke it under the existing project lock after `assert_fresh`. Evaluate this branch before external-coordinator yielding, Claude authentication, call-directory creation, or provider argument construction. In `main`, select the local label before looking up or printing a provider model.
- Build the canonical finalize response from saved accepted records: current identity envelope, nonblank deterministic summary, an exact deep copy of canonical findings, and `plan_markdown: null`. Pass it through the existing `accept`/`validate_response` path, including current evidence validation, `complete_findings`, `checks_pass`, and write guards.
- Record the ledger agent as `{model: 'local-finalizer', effort: 'deterministic'}`. Create no provider invocation, authentication probe, session, or finalization external request. Retain the coordinator profile for its remaining adjudication work.
- Produce the report mechanically from the reviewed fingerprint, base, scope and diff; finding decisions; recorded repair/recheck rationales; current check receipt IDs and outcomes; and attributed stage summaries. Preserve recorded limitations through those summaries without inventing or semantically reinterpreting them. Distinguish no findings, all rejected findings, and independently verified repairs.

Use the same local function across these public paths:

| Entry point | Version-3 behavior when finalization is eligible |
|---|---|
| `run RUN` | Complete locally before returning; report `finalize` / `complete`. |
| `run RUN --external-coordinator` | Complete locally; yield only genuine coordinator stages. No finalization request is written. A historical adjudication request may remain unchanged. |
| Ordinary `step RUN` | Dispatch at most one provider stage, then complete any resulting eligible local finalization before returning. Starting at finalize dispatches zero providers and returns `complete`. |
| `submit RUN ...` | After accepting an authorized coordinator adjudication, complete any resulting eligible local finalization and return `complete`; otherwise report its ordinary next state. Reject submissions whose current stage is locally owned finalize. |
| `rerun-checks RUN` | After saving successful check recovery, complete eligible local finalization and report `complete`, preserving cited receipts and the check-rerun event. |
| `step RUN --reviewer-only` | Dispatch one authorized reviewer stage only. When it makes completion eligible, return `finalize` / `ready` for sandbox continuation. Reject entry at finalize. |

For eligible local execution, print `finalize: local-finalizer (deterministic)`. Normal successful commands retain exit 0 and print their actual status; `unresolved` is not successful review completion. Rejected commands, freshness/validation failures, and I/O errors exit 2. Non-ready runs retain ordinary continuation behavior without implicit retry or recovery.

Failed or missing configured checks leave finalization `unresolved`; incomplete findings never become eligible. A version-3 check rerun at ready finalization that fails also leaves it `unresolved`. Other blocked or unresolved stages retain their existing recovery requirements. Supported version-2 runs retain coordinator finalization, external submission, frozen sessions, and check-recovery behavior.

### Persistence and recovery

Reuse `accept`'s immutable artifact allocation and atomic state save. The order is: write the finalize artifact, save `complete` with its single ledger entry and incremented revision, then render derived views. Local finalization does not save an intermediate provider `running` state.

Keep local execution outside the provider-dispatch exception handler. For version-3 implementation acceptance, wrap errors or interruptions from only `accept`'s final `render` call in a narrow `DerivedViewError` subclass of `ReviewError`, retaining the original cause. This call occurs after acceptance and any post-repair checks and receipt-state save have finished. Extend `advance`'s durable-acceptance guard to preserve the saved next status only for that identified rendering failure when the handoff revision advanced, including ready finalization or completion. Do not apply this extension to validation, artifact/state persistence, or check-execution errors. Leave the existing plan/diff guard and version-2 behavior unchanged.

Post-repair check-execution, receipt-writing, or freshness errors continue through the existing handler, which saves the accepted run as `stage: recheck`, `status: blocked`. Recover through `retry`, which checks target freshness and reruns the full configured check set before restoring ready. Ordinary continuation must not dispatch recheck while this recovery is incomplete, and must not replay the accepted repair. Completed checks with nonzero results remain valid review evidence: they permit independent recheck but prevent completion under the existing gates.

A failure before the completion state save leaves finalize/ready and may leave an immutable orphan artifact. The next ordinary `run` or `step` repeats only local completion, records the orphan through `next_artifact`, and accepts completion once. A failure after the save leaves `complete`; report the error and regenerate views through ordinary `run` or `step`, with no additional revision or finalize event.

For completed version-3 runs, render both `handoff.md` and `final.md` from the terminal accepted artifact and saved accepted ledger/report content. The handoff's scoped diff must use that artifact's target, never `target(state)`. Regeneration must remain possible after the checkout changes or becomes unavailable. Ongoing-review freshness checks remain in force before acceptance.

On complete runs, ordinary `run` and `step` regenerate views only. `retry`, `rerun-checks`, `reconcile`, `submit`, and `decide` reject them. Interrupted repairs still require inspected reconciliation; unsupported or interrupted saved contracts are never silently converted.

## 2. Delivery evidence command

Add `review_cli.py delivery-evidence RUN --pr PR_URL`.

Dispatch this command before the generic mutating run/lock path in `main`. Read artifacts directly and call `verify_target()` directly; do not call `status` as a subprocess, render reports, save state, execute checks, resolve provider executables, fetch commits, or acquire credentials.

Return one JSON object on stdout with `report_version: 1`, `command: delivery-evidence`, UTC `observed_at`, explicit run and PR identifiers, `evidence`, `conditions`, `status`, and `limitations`. Evidence includes saved identity and requirements, scope, findings, check receipts, PR/issue title and body, hosted checks, source paths/URLs, and command exit results. Mark semantic coverage `not_assessed`. Missing values carry explanations instead of fabricated defaults. CLI usage errors exit 2; collection failures are represented in the JSON conditions.

### Collection

Use explicit URLs and these argument lists through the existing `command()` function, with its 30-second per-call timeout:

```text
gh pr view PR_URL --json url,title,body,state,isDraft,headRefOid,baseRefOid,updatedAt,closingIssuesReferences,mergeable,reviewDecision
gh issue view ISSUE_URL --json url,title,body,state
gh pr checks PR_URL --required --json name,state,bucket,link
```

Collect every explicitly linked issue by URL, including multiple and cross-repository links. Do not select an inferred issue or treat issue count or repository location as semantic coverage.

Read the PR, its linked issues, and required checks; invoke `verify_target` using the observed head and base; then reread the same issue content and required checks and finish with a second PR read. Compare all collected PR fields, linked issue identities/content, and required check records, ignoring collection order only. Retain both observations when they differ. No polling or retries.

Record and recheck the bytes and relevant path sets of local run/artifact/receipt inputs before returning. Changes during collection invalidate the combined observation. Use the existing identity command's local checkout stability checks without weakening them.

Parse usable hosted-check JSON even on nonzero exits, including pending exit 8. Missing `gh`, authentication/access failures, timeouts, network errors, and malformed responses make affected evidence UNKNOWN. A nonzero exit with no usable required-check list cannot establish a pass. These fields and pending exit behavior follow the [GitHub CLI checks reference](https://cli.github.com/manual/gh_pr_checks); the PR and issue field lists are documented in the [PR reference](https://cli.github.com/manual/gh_pr_view) and [issue reference](https://cli.github.com/manual/gh_issue_view).

### Mechanical conditions

Each condition contains `status`, `explanation`, and supporting source references/details.

| Condition | Mapping |
|---|---|
| `identity` | Nest the unchanged `verify_target` report and propagate its aggregate status, including `eligible_run`. If PR commit identity cannot be obtained, use UNKNOWN without inventing commit arguments. |
| `local_checks` | PASS requires a nonempty configured set, complete current receipts matching saved commands and fingerprint, matching on-disk receipts, and all exit codes zero. Known nonzero results or contradictory/stale receipts are BLOCKED. Missing, unreadable, or incomplete evidence is UNKNOWN. |
| `finding_verification` | Empty or wholly rejected findings pass this gate. Each accepted finding otherwise requires PASSED independent recheck with supporting accepted recheck records and resolvable current evidence. Known incomplete verification, unresolved dispositions, or stale evidence is BLOCKED; unavailable supporting records are UNKNOWN. |
| `pr_state` | OPEN and explicitly non-draft is PASS. Draft, CLOSED, or MERGED is BLOCKED. Missing/unsupported values are UNKNOWN. A returned valid PR identity differing from the requested PR is BLOCKED. |
| `mergeable` | MERGEABLE is PASS; CONFLICTING is BLOCKED; UNKNOWN, empty, missing, or unsupported values are UNKNOWN. |
| `review_decision` | APPROVED is PASS; REVIEW_REQUIRED and CHANGES_REQUESTED are BLOCKED; empty, missing, or unsupported values are UNKNOWN. Empty does not prove reviews are unnecessary. |
| `required_checks` | A nonempty, successfully collected list of explicit successful results is PASS. Known fail, cancel, or pending buckets are BLOCKED. Skipping, skipped/neutral or unsupported states, missing fields, an empty list, and a 'no required checks' result are UNKNOWN. Require successful state evidence as well as a pass bucket; contradictory output cannot establish PASS. |
| `linked_issues` | PASS means a nonempty set of explicit linked issue URLs was resolved and its requested fields collected. Missing or ambiguous linkage or inaccessible issues is UNKNOWN. Preserve issue state and label title/body 'semantic coverage not assessed'; issue state alone does not establish coverage or block delivery. |
| `stable_observation` | PASS means the sampled hosted and local evidence remained unchanged. Detected changes or an unavailable required reread are UNKNOWN, with affected evidence identified. |

For a consistent observation, aggregate BLOCKED over UNKNOWN over PASS. Useful known failing check results remain blockers even if other required evidence is missing; all-pass rows with an unexplained nonzero command exit remain UNKNOWN. Mechanical PASS/BLOCKED/UNKNOWN exits 0/1/2.

A detected change between observations invalidates the combined assessment and returns UNKNOWN/2, even when an earlier sampled value was blocking. Retain those values as unstable observations, not a current readiness judgment. This preserves the delivery procedure's distinction between inconsistent observations and missing evidence within a consistent observation.

Update `review-delivery` to consume this packet, assess PR/issue requirements against run requirements, reviewed scope, decisions, and actual evidence, and produce the final READY/BLOCKED/UNKNOWN judgment. Mechanical PASS alone does not establish READY. The command writes nothing to the project, run, or GitHub.

## 3. Recorded-run comparison command

Add `review_cli.py compare-runs BASELINE_RUN CANDIDATE_RUN`.

Dispatch before the generic run protocol/lock path. Read saved artifacts without invoking providers, GitHub, project commands, or rendering. Historical artifacts may be inspected even when their contracts are no longer resumable; never migrate them or substitute current defaults for missing recorded metadata.

Return `report_version: 1`, `command: compare-runs`, UTC `observed_at`, `status`, `comparability`, `baseline`, `candidate`, and `limitations`. Each run section includes its path/identity, recorded protocol/profile context, classified events and counts, process measurements, final findings, current and historical checks, telemetry records, and evidence paths. Unavailable measurements use null plus a reason, never zero by default.

Require readable original snapshots and state records. Compare `original.json` requirements exactly as strings and targets by exact JSON value equality, without normalizing plan, source, or diff text. Report profile, instruction, check-command, and protocol differences as context. Equality establishes input comparability, not equivalent execution or quality.

### Event and measurement classification

- Count one recorded provider launch attempt per `calls/*/invocation.json`, independently of ledger acceptance. Read its sibling `process.json` for `elapsed_seconds`, `exit_code`, and `interruption`. Missing process receipts leave outcomes and durations unavailable. A call directory without an invocation record is incomplete evidence, not a counted launch.
- Classify accepted ledger entries separately. Recognize current CLI provenance sources `Claude modelUsage` and `not exposed by CLI output`; the latter still identifies a CLI acceptance even though model/effort observations are unavailable. Caller-attested external coordinator entries count as accepted external provider stages with unavailable CLI attempts, duration, and usage. Do not manufacture corresponding call directories.
- Identify `local-checks` and `local-finalizer` as deterministic events and `operator` as an operator event. Keep fixture provenance explicitly synthetic. Retain unfamiliar or missing provenance as unclassified accepted events rather than silently treating it as CLI execution. Report accepted totals and these subtotals separately.
- Failed or rejected attempts without accepted ledger entries remain attempts. Do not associate calls and ledger entries solely by position or matching stage names.
- Read helper-managed check durations from `checks/*/process.json`, and check outcomes/fingerprints from `checks/*.json` plus the state's current receipts. Retain earlier receipts as history without counting duplicate state copies as additional executions.
- Report provider CLI elapsed time and helper-managed check elapsed time separately, with measured-record coverage and explicit missing values. Provider process time includes its tool work; it is not pure inference latency or whole-run wall time.
- Read requested model/effort from invocation arguments and, separately, accepted ledger agent settings. Preserve `agent.observed` and Claude `modelUsage` model keys as observations with their sources. Missing observed effort stays unavailable. Show requested-versus-observed discrepancies without changing input comparability or inferring a fallback.

### Token and cost records

Read only fields present in recorded output and preserve their original field names and evidence locations:

- Claude result JSON: `usage.input_tokens`, `usage.output_tokens`, `usage.cache_read_input_tokens`, `usage.cache_creation_input_tokens`; `total_cost_usd`; and each `modelUsage` entry's `inputTokens`, `outputTokens`, `cacheReadInputTokens`, `cacheCreationInputTokens`, and `costUSD`.
- Codex JSONL: each `turn.completed` event's `usage.input_tokens`, `usage.cached_input_tokens`, `usage.output_tokens`, and optional `usage.reasoning_output_tokens`. Preserve event position and recorded thread/session identity when available. This supported event shape is documented in [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode). USD cost is unavailable when the output does not expose it.

For fresh single-invocation Claude results, label usage as the reported main-loop result and cost/model usage as reported invocation totals. Resumed Claude totals can include earlier session spend and differ by producer version; label their incremental accounting scope unknown unless the saved evidence establishes it. The [Claude cost documentation](https://code.claude.com/docs/en/agent-sdk/cost-tracking) explains the resumed-total distinction. Label Codex values as reported turn-completion usage; do not assume a resumed completion is an independently additive measurement merely from its event name.

This command version reports token/cost records individually and emits no cross-call token or cost totals or inferred cumulative deltas. Keep ambiguous raw records visible while marking normalized per-call measurements unavailable. Never add per-model breakdowns to their enclosing totals or convert reported cost estimates into actual billed savings.

### Stability and result status

Capture the relevant file sets and content digests, then reread them before returning. Added, removed, or changed originals, state, invocation/process records, check records, or collected output yield UNKNOWN. Do not create lock files or caches for collection.

Return COMPARABLE/0 for equal original inputs, NOT_COMPARABLE/1 for unequal original inputs, and UNKNOWN/2 for missing or malformed required inputs or changing evidence. Missing optional process/usage telemetry does not invalidate otherwise comparable inputs; identify the resulting measurement gaps.

Update `review-suite-eval` and `references/suite-eval.md` to use this command and remove the prohibition on a comparison helper. Semantic quality assessment remains with the invoking model against explicitly supplied maintainer expectations. Without those expectations, quality judgment is unavailable. Finding counts and typed output do not prove coverage or quality.

## 4. Future verification

Use deterministic fixtures, temporary repositories, and mocked provider/GitHub boundaries. Extend the existing tests rather than adding a parallel test framework.

- Completion and compatibility: prove the 2-to-1, 3-to-2, and 5-to-4 provider-stage paths; exact canonical finding preservation; local provenance; current gates; version-2 coordinator/external finalization and frozen-profile resumption; completed version-3 `verify_target` eligibility; and rejection of invalid matrix combinations, non-integer versions, stale targets/evidence, failed checks, and unauthorized writes.
- Entry points: exercise ordinary run/step, a no-findings external-coordinator run with no external request created, external adjudication submission, check-only recovery reaching complete, and reviewer-only dispatch leaving eligible finalization ready for sandbox continuation. Assert statuses, exits, local labels, and zero provider/authentication calls at local finalize.
- Recovery: inject failures before completion state save and after durable save during rendering. Require preserved orphan lineage, one accepted finalize event, no provider replay, and no new artifact on repeated continuation. Reject recovery/submission commands on complete runs. After completion, change or remove the checkout and prove both historical views regenerate from accepted records without reading the current target.
- Post-repair recovery: inject a check-execution interruption and a receipt-write failure after repair acceptance. Require saved recheck/blocked, retained repair acceptance and repair count, and no reviewer dispatch by ordinary run or step. Verify retry reestablishes complete current receipts before recheck becomes ready, without replaying repair. Separately inject a render failure after post-repair receipts are saved and require recheck/ready with those receipts intact. Retain coverage that completed nonzero check receipts permit recheck but prevent completion, and that version-2 behavior is unchanged.
- Delivery: cover each condition's PASS/BLOCKED/UNKNOWN mapping, nested `verify_target` status, nonzero check output including exit 8, empty/no-required/skipped results, ambiguous review and mergeability values, multiple/cross-repository/missing issue links, inaccessible or malformed evidence, missing commits, dirty context, and hosted/local changes during collection. Verify consistent-blocker precedence and the instability UNKNOWN result.
- Comparison: cover equal/different inputs and archived contracts, failed attempts without ledger entries, CLI acceptance without observed model metadata, external submissions, fixture provenance, local-finalizer/local-checks/operator events, requested/observed mismatch, separate check timing, missing telemetry, resumed cumulative/ambiguous usage, and concurrent file changes.
- For both collection commands, assert one JSON report, documented exit codes, zero provider/check execution, and unchanged reviewed project/run bytes.

Run `pnpm run verify:ci` during implementation delivery. These fixtures establish routing, persistence, and collection behavior; they do not establish live-provider latency, dollar savings, production verification, or hosted acceptance. No implementation or test execution is claimed by this plan review.

## 5. Documentation, delivery, and rollback

Update affected implementation/handoff/delivery/evaluation skill text, focused CLI/delivery/comparison references, README, validation records, and wiki together. Document the compatibility matrix, command reports, entry-point statuses, recovery, and evidence limitations. Keep canonical model-response finalization support for version-2 runs. Correct affected compatibility prose without restoring retired protocols or changing unrelated metadata.

Future implementation follows AGENTS.md: confirm the worktree is safe, update `main` with `git pull --ff-only`, create and read back one canonically labeled issue through the issue-creation workflow, then create `codex/<issue-number>-<short-slug>`. Implement only this scope. Archive the executed plan, update routed wiki topics/journal, and refresh the maintained Graphify map with version 0.9.36.

Complete `pnpm run verify:ci`, a valid scoped conventional commit, and PR lint. Push normally, open the issue-linked PR using every canonical template heading and required checkbox, read the saved PR back, and stop with it open. Merging remains with the user. This plan review itself authorizes none of those writes.

Rollback preserves run evidence. Reverting the helper leaves version-3 runs requiring a compatible helper; never retag them as version 2. Supported pre-update version-2 runs continue through their saved coordinator contract.

Add no Jev dependency, paid experiment, or placeholder integration. Revisit Jev only after identifying a standalone semantic workload it could replace, representative evaluation examples and quality expectations, recorded baseline call/usage/timing evidence, and a credible net reduction in cost or latency. That evaluation is outside this delivery.
