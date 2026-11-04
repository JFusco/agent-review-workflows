---
topics: [plan-review-protocol]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/89']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/89'
---
# Guard the required researcher launch

The Office feature-planning review stopped before the required research response
because nested Codex could not initialize its in-process app-server client.
Existing reviewer/adjudicator recovery explicitly excluded research, leaving no
supported launcher path for that stage.

Issue #89 adds a research-only guard while retaining the existing named permission
profile, frozen model, immutable evidence, process lock, and freshness checks.
It accepts one brief or retains one failed attempt; it cannot continue into review,
retry, select another model, run checks, or grant wider model-tool access.

The focused regression suite uses temporary repositories, controlled children,
and synthetic research/review responses. These are contract tests, not proof of
live-provider availability. The preserved Office review is resumed separately
with the shipped helper and normal launcher approval.
