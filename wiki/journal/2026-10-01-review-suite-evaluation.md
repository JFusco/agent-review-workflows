---
topics: [review-suite-evaluation]
plans: [2026-10-01-review-suite-eval-delivery-1654c27d2a.md]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/47']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/47'
---
# Add maintainer review-suite evaluation

For [issue #47](https://github.com/JFusco/agent-review-workflows/issues/47),
the suite gained an opt-in skill for comparing existing review runs. It uses
saved evidence and returns a concise assessment in the invoking conversation.
The procedure refuses comparative conclusions when original inputs differ
and labels absent measurements or expectations unavailable. It adds no
provider stage, helper mode, or runtime profile.
