---
name: review-diff
description: Reports evidence-backed findings for a scoped local Git change without repairing it. Use when the user explicitly requests a read-only diff review.
---

# Review a local diff

Read the [CLI procedure](references/cli.md) before starting or resuming. Use `start diff` with an explicit Git base, scoped files, and at least one authorized local check. Freeze the configured two-role profile; do not add an implementer.

Run review and adjudication through the helper. Preserve unrelated work and do not edit the reviewed project or dispatch repair. The coordinator assesses the change even when the reviewer finds nothing.

A `reported` run records findings and check outcomes. Report its status, finding IDs, check results, and handoff link. Accepted findings remain `UNVERIFIED`; changed code requires a new run.

For later PR delivery evidence, follow [the clean-context prerequisite](references/cli.md#preparing-review-evidence-for-delivery) before starting.
