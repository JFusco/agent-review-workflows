---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#42; scripts/review_cli.py; tests/test_review_cli.py"]
source_tool: "codex"
source: "Codex user-approved plan, 2026-10-01"
topics: ["review-agent-profiles"]
digest: "d6e46e6de5a62cfcf15c579103e3da30131b6ba6384f8b15e409e0df2b0ca97f"
---

# Reuse the existing Claude login for reviews

## Summary

Keep checks and Codex stages sandboxed. Use approved host execution only for Claude reviewer stages. The same Claude configuration directory reports logged out inside the sandbox and logged in on the host.

## Changes

- In `scripts/review_cli.py`, check authentication with the run's pinned Claude binary before launching a reviewer. If the login is unavailable, leave the stage ready and report an auth-context error without a provider call.
- Add a guarded, single-stage reviewer command. Run the full review in the sandbox, dispatch each Claude review or recheck through approved host execution, then resume sandboxed progression. Reject Codex and repair stages at the guard.
- Document the routing once in `references/cli.md` and link it from the affected review skills. Preserve pinned models, read-only Claude tools, session recovery, and scope checks. Do not copy credentials into run artifacts.
- Deliver through the repository issue, PR, verification, and wiki flow. Preserve the active checkout's unrelated edits; install the merged revision in a separate stable checkout before switching installed skill links.

## Verification

- Test the auth-context mismatch, a failed preflight with no provider call, and rejection of host dispatch for non-reviewer stages.
- Run `pnpm run verify:ci`. Verify installed links and repeat read-only auth-status checks in both contexts. Do not run a paid provider trial for this routing change.

## Assumptions

Use the existing host Claude.ai login. A real logout or expiration requires one interactive host CLI sign-in; host execution may require Codex approval.
