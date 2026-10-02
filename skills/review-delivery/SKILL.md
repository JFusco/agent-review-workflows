---
name: review-delivery
description: Assesses an explicit GitHub PR against a terminal review run and delivery gates. Use when asked for PR readiness from saved review evidence.
---

# Review PR delivery

Require a GitHub PR URL and a completed implementation or reported diff run directory. Follow the [delivery procedure](references/delivery.md) and its [clean-context prerequisite](references/cli.md#preparing-review-evidence-for-delivery).

Report READY, BLOCKED, or UNKNOWN with the PR, issue, checks, run fingerprint, and relevant finding IDs. Leave the run, project, and GitHub unchanged.
