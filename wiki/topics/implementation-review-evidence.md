# Implementation review evidence

[JFusco/agent-review-workflows issue #9](https://github.com/JFusco/agent-review-workflows/issues/9)
defines the evidence and authority contract for newly started
`review-implementation` runs.

Each new run requires an explicit local Git base, an authorized file scope, and
at least one local check command. Initialization resolves the base to a commit
and constructs the complete base-to-current diff for the authorized scope. The
diff includes tracked, staged, unstaged, deleted, and explicitly scoped
untracked files while excluding unrelated repository changes. An invalid base,
missing check, empty initial diff, or oversized target fails before run
artifacts are created.

## Independent review packet

The initial reviewer receives the frozen base SHA, actual scoped diff, full
scoped text sources, verbatim requirements, and fingerprint-bound check
receipts. Check receipts retain the command arguments, exit code, output, and
target fingerprint. Failed checks remain evidence for review and prevent a
successful completion.

New findings use the existing `BLOCKER`, `WARN`, or `SUGGESTION` severity and
identify an authorized project-relative file, optionally with a line or line
range. Their stable ID, severity, location, evidence, recommended correction,
and acceptance check form an immutable definition after introduction.

## Decision and repair authority

New runs use implementation evidence version 2. The independent reviewer finds
gaps, then the coordinator directly sets each authoritative `ACCEPTED`,
`REJECTED`, or `PENDING_USER` disposition. It cannot redefine or reverify an
existing finding, but it may append a sequential, evidenced finding inside the
authorized scope. An added finding starts unverified and follows the same
accepted repair and independent recheck path.

The accepted adjudication entry contains a deterministic repair lock with the
accepted findings in order, authorized files, configured check commands, target
fingerprint, and handoff revision. The helper compares that lock with current
state and the saved adjudication artifact before the implementer receives write
access. The handoff shows the coordinator's decisions, repair lock, and current
scoped Git diff against the frozen base. The same lock reaches the implementer.

New runs also record implementation response version 2. At repair, the writer
returns the frozen identity envelope, a summary, and ordered `{id, rationale}`
assessments for accepted findings. The helper validates exact ID coverage and
field ownership, then reconstructs complete canonical findings from saved
state. Only accepted rationales change; rejected records, definitions,
dispositions, and verification fields remain saved values. The repair artifact
retains both submitted assessments and the canonical response. The full
response validator and scoped write guard run before acceptance.

Only the implementer may write within the authorized scope, and only independent
recheck may mark findings passed. New runs permit one repair and one recheck. An
incomplete recheck, including a newly discovered gap, ends unresolved without
another repair or coordinator call. A complete recheck proceeds to coordinator
finalization, subject to passing checks.

## Check recovery

The installable `review-handoff` skill exposes one stage of either existing review
chain through `status` and `step`. The helper remains the authority for routing,
frozen model settings, canonical evidence, freshness, and repair permission. The
skill adds no model or review stage and never automatically recovers a non-ready
run. See [single-stage CLI use](../../references/cli.md#single-stage-handoff) and
[issue #27](https://github.com/JFusco/agent-review-workflows/issues/27).

Configured checks may rerun only for a current implementation review in a
read-only recoverable state and only while the target fingerprint and complete
project inventory remain unchanged. A rerun preserves the previous receipt
files, gives new receipts unique attempt-qualified IDs, records both receipt
sets in an immutable revision artifact, and increments the handoff revision so
older model output is stale. It never changes configured commands, findings,
the repair count, or the target.

When failed checks are the sole reason finalization is unresolved, a fully
passing rerun makes that same finalization ready. Other blocked or unresolved
states retain their status and use their existing recovery path.

## Compatibility and evidence policy

The contract is versioned on new implementation runs. Plan review remains
read-only and may omit a base and checks. Evidence version 1 runs retain their
implementer response, reviewer reply, and two-pass behavior, including when
paused at an advisory stage. Saved implementation-plan data from the unmerged
issue #20 branch remains readable. Artifact recovery and prior fingerprints do
not change.

An absent implementation response version retains the prior full-finding
response, including for an already-created evidence version 2 run. Unsupported
explicit response versions fail closed. A response rejected after writer exit
records an interrupted repair with an actionable inspection and reconciliation
message. Reconciliation consumes one pass and advances to independent recheck;
it never replays the writer.

Deterministic temporary-repository fixtures establish the boundary cases. Two
issue #21 live branch trials exercised the provider path. The first stopped
`unresolved` at recheck after a new documentation finding, without another
repair or finalizer call. The second completed the five-stage ledger with one
locked Sol repair, Opus PASS, and Astra finalization. `VALIDATION.md` records
the run IDs, check results, and limits. These local branch trials do not imply
production verification.
