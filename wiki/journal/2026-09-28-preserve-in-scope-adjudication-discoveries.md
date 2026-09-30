---
topics: [implementation-review-evidence]
plans: [2026-09-28-preserve-in-scope-adjudication-discoveries-a85c7cc5ea.md]
issue: 'https://github.com/jfusco/agent-review-workflows/issues/17'
issues: ['https://github.com/jfusco/agent-review-workflows/issues/17']
---
# Preserve in-scope adjudication discoveries

Issue [#17](https://github.com/JFusco/agent-review-workflows/issues/17) corrects the too-narrow adjudication contract introduced by issue #14 and PR #15. The user clarified that implementation review must prioritize accuracy and close gaps within the authorized scope; preventing the coordinator from retaining a newly established defect defeated that purpose.

The ID-only, canonically normalized provider contract remains on the implementer response and reviewer reply, where it prevents advisory mutation. Adjudication again receives the full finding shape. It must preserve existing finding order, definitions, and verification state, but may append sequential, scoped findings supported by the combined evidence packet. New adjudication findings start unverified with no verification receipts and therefore cannot bypass accepted repair or independent recheck.

Regression coverage proves valid additions and rejects omitted or reordered existing findings, mutations, duplicate or nonsequential IDs, out-of-scope locations, and premature verification claims.

Affected durable topic: [implementation review evidence](../topics/implementation-review-evidence.md).
