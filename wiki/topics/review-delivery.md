---
issues: ['https://github.com/JFusco/agent-review-workflows/issues/53', 'https://github.com/JFusco/agent-review-workflows/issues/62']
---
# Review delivery

The opt-in `review-delivery` skill assesses one explicit GitHub PR against a
terminal implementation or diff review. The `delivery-evidence` helper collects the
PR, every explicitly linked issue, required checks, run requirements, finding
decisions, local receipts, and nested `verify-target` identity. The invoking
conversation evaluates semantic requirement coverage. It returns READY, BLOCKED, or UNKNOWN with cited evidence;
it does not change the run, project, or GitHub.

The read-only `verify-target` helper proves local identity using the terminal
accepted artifact, current scoped files, saved full check-context inventory,
clean checkout, Git ancestry, and changed-path scope. A matching target alone
does not prove hosted PR readiness. Unrelated files in the original review
context can prevent transfer of its check evidence to a clean PR checkout;
the existing local review remains valid, but a fresh review is required for
delivery evidence. This adds no provider stage, model profile, or writer.

Issue #62 batches mechanical collection into one read-only command, retaining
raw evidence, source references, unavailable reasons, and PASS/BLOCKED/UNKNOWN
conditions. It rereads hosted and local inputs without polling; changed evidence
invalidates the assessment as UNKNOWN even when a prior sample blocked. Stable
known blockers take precedence over missing evidence. Mechanical PASS alone
never establishes semantic coverage or READY. The
[delivery procedure](../../references/delivery.md) owns exact gate mappings.
Current local receipts need one exact on-disk match despite retained same-ID
history. Both hosted check observations are validated, and detected nested
checkout drift also invalidates the combined observation as UNKNOWN while
preserving the identity report.
No provider, check execution, credential acquisition, or project/run/GitHub write
is part of collection.
