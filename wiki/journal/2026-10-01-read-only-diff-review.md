---
topics: [diff-review]
plans: [2026-10-01-final-8532f8f2e0.md]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/45']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/45'
---
# Add read-only diff review

For [issue #45](https://github.com/JFusco/agent-review-workflows/issues/45),
the review suite gained an opt-in `review-diff` entrypoint. It reuses the
existing CLI ledger and reviewer/adjudicator stages, checks a frozen scoped
diff and caller-supplied commands, and produces a read-only final report.

The helper rejects missing base, empty or out-of-scope diffs, and missing
checks before provider work. Tests cover the accepted, rejected, interrupted,
stale, and out-of-scope paths. This is the first delivery of the broader
review-suite plan; the other proposed skills remain separate deliveries.
