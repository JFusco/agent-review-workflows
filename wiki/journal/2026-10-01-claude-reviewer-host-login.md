---
topics: [review-agent-profiles]
plans: [2026-10-01-reuse-the-existing-claude-login-for-reviews-d6e46e6de5.md]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/42']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/42'
---
# Reuse the host Claude login for reviewer stages

On 2026-10-01, read-only `claude auth status` checks reported logged out in
the Codex sandbox and logged in on the host, using the same Claude
configuration directory. The helper previously inherited the invoking
context, so a sandboxed reviewer call could fail before producing evidence.

For [issue #42](https://github.com/JFusco/agent-review-workflows/issues/42),
the helper checks the pinned Claude binary's auth status after any initial
implementation checks and before creating a reviewer call. A missing login
leaves the stage ready. `step --reviewer-only` checks the role under the
project lock and requires current implementation check receipts before a
host-approved Claude dispatch. The shared CLI procedure routes later Codex
stages back through the sandbox. No token or credential is copied into a run.

Deterministic fixtures cover malformed and unavailable auth status, unchanged
run state after preflight failure, and rejection of host dispatch for Codex
stages or missing and stale checks. No paid provider invocation was used to
establish this routing behavior.
