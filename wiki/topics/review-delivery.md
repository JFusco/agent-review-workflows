---
issues: ['https://github.com/JFusco/agent-review-workflows/issues/53']
---
# Review delivery

The opt-in `review-delivery` skill assesses one explicit GitHub PR against a
terminal implementation or diff review. The invoking conversation reads the
PR, linked issue, required checks, run requirements, finding decisions, and
local receipts. It returns READY, BLOCKED, or UNKNOWN with cited evidence;
it does not change the run, project, or GitHub.

The read-only `verify-target` helper proves local identity using the terminal
accepted artifact, current scoped files, saved full check-context inventory,
clean checkout, Git ancestry, and changed-path scope. A matching target alone
does not prove hosted PR readiness. Unrelated files in the original review
context can prevent transfer of its check evidence to a clean PR checkout;
the existing local review remains valid, but a fresh review is required for
delivery evidence. This adds no provider stage, model profile, or writer.
