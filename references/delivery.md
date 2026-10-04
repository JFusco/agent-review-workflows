# PR delivery assessment

Require an explicit GitHub PR URL and terminal implementation or diff run directory. Resolve `PYTHON` and `HELPER` through the [CLI procedure](cli.md). This assessment runs in the invoking conversation and adds no review stage or canonical ledger entry.

```sh
PYTHON HELPER delivery-evidence RUN --pr PR_URL
```

The command returns one JSON object with `report_version: 1`, UTC `observed_at`, run/PR identities, raw `evidence`, per-gate `conditions`, aggregate `status`, and `limitations`. Sources include saved requirements, scope, findings, immutable artifacts, current/historical check receipts, PR and every explicitly linked issue's title/body/state, check URLs, and command exit results. Unavailable evidence has an explanation. Semantic coverage is `not_assessed`.

Collection uses the exact PR fields `url,title,body,state,isDraft,headRefOid,baseRefOid,updatedAt,closingIssuesReferences,mergeable,reviewDecision`, issue fields `url,title,body,state`, and required checks `name,state,bucket,link`, through `gh pr view`, `gh issue view`, and `gh pr checks --required`. It reads multiple/cross-repository linked issues by explicit URL, invokes [verify-target](cli.md#verify-a-terminal-target-for-delivery) directly with observed commits, then rereads the same issue/check evidence and ends with a second PR read. Each command uses a 30-second timeout; there is no polling or credential acquisition. Local input bytes and path sets are rechecked. Collection order alone does not indicate a change.

| Condition | PASS | BLOCKED | UNKNOWN |
| --- | --- | --- | --- |
| identity | Nested verify-target passes every condition | Known nested mismatch/ineligible run | Missing commit identity or nested unavailable evidence |
| local_checks | Nonempty configured set, complete matching current/on-disk receipts, all exit 0 | Nonzero, contradictory, or stale receipts | Missing/incomplete/unreadable receipts |
| finding_verification | Empty/rejected findings, or accepted findings with PASSED independent recheck and current references | Unresolved/incomplete/stale verification | Supporting records unavailable |
| pr_state | OPEN, explicitly non-draft, matching PR identity | Draft/CLOSED/MERGED or different valid identity | Missing/unsupported state or identity |
| mergeable | MERGEABLE | CONFLICTING | UNKNOWN/empty/missing/unsupported |
| review_decision | APPROVED | REVIEW_REQUIRED/CHANGES_REQUESTED | Empty/missing/unsupported; no inference that reviews are unnecessary |
| required_checks | Nonempty explicit successful states and pass buckets, successful collection | Fail/cancel/pending, including usable nonzero output | Empty/no-required/skipped/neutral/malformed/contradictory success or unexplained nonzero all-pass output |
| linked_issues | Nonempty explicit linked URLs and complete requested fields | Issue state alone never blocks | Missing/ambiguous/inaccessible content |
| stable_observation | Required hosted/local samples unchanged | None | Changed evidence or unavailable required reread |

Consistent observations aggregate BLOCKED over UNKNOWN over PASS, with exits 1/2/0. Useful failing or pending hosted rows remain blockers even when `gh pr checks` exits nonzero (including pending exit 8). Detected hosted or local changes invalidate the combined judgment and force UNKNOWN/2, retaining both sampled observations even if an earlier value blocked. The [GitHub CLI PR](https://cli.github.com/manual/gh_pr_view), [issue](https://cli.github.com/manual/gh_issue_view), and [checks](https://cli.github.com/manual/gh_pr_checks) references document the collected fields.

Consume the packet and compare PR/issue acceptance criteria against verbatim run requirements, reviewed scope, finding decisions, and actual evidence. Assess missing or unsupported requirements and whether each check demonstrates the claimed behavior. Mechanical PASS alone does not establish READY; issue count/state or clean finding counts do not establish coverage. Without sufficient semantic evidence, return UNKNOWN. For a stable observation, preserve known mechanical blockers and return BLOCKED; otherwise return READY only with supported coverage and every applicable gate satisfied. If samples changed, return UNKNOWN and identify what needs rereading.

Report the observation time, PR/issue/check URLs, saved fingerprint, relevant finding IDs, coverage rationale, and limitations. Readiness describes that observation, not future PR state. The helper writes nothing to the run, reviewed project, or GitHub, and executes no provider or local check. Do not comment, submit reviews, rerun checks, obtain credentials, publish, or merge during assessment.
