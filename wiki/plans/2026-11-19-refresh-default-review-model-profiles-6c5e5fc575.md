---
status: "implemented"
executed: true
evidence: ["scripts/review_cli.py default profiles and tests/test_review_cli.py profile and CLI argument fixtures"]
source_tool: "repository"
source: "/private/tmp/review-model-profiles-vc51pwil/plan.md"
topics: ["review-agent-profiles"]
digest: "6c5e5fc575d1034122a834bc0a4589e1308165495fc7e5e1b5fa5dc685e496ee"
---

# Refresh default review model profiles

- Update the native Claude Code installation to at least 2.1.321 and verify the
  binary resolved by the installed review helper and its required flags.
- Set new-run defaults to Astra 6.2 High for plan research, Astra 6.2 Max for
  coordination, and Sol 6.2 XHigh for scoped repair. Keep Opus 5.5 High for
  independent review and document the Fable 5.2 High per-run choice.
- Verify local installation settings and global links, preserve saved profiles,
  fallback policy and permissions, and run repository verification before delivery.
