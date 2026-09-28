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

The implementer response and independent reviewer reply are advisory
assessments preserved per finding in the revision ledger and rendered handoff.
The canonical finding remains open while those assessments are collected. The
coordinator receives both assessments and alone sets the authoritative
`ACCEPTED`, `REJECTED`, or `PENDING_USER` disposition. Only accepted findings
enter repair, only the designated implementer may write within the authorized
scope, and only independent recheck may change verification fields.

## Compatibility and evidence policy

The contract is versioned on new implementation runs. Plan review remains
read-only and may omit a base and checks. Existing implementation runs retain
their recorded target and completion behavior, so artifact recovery and prior
fingerprints do not change.

Deterministic temporary-repository fixtures establish the new behavior. No new
provider-backed trial was run; earlier live trials remain evidence only for the
built-in agent profile and permission separation.
