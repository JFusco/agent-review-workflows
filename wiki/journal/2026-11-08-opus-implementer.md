---
topics: [review-agent-profiles]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/98']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/98'
---

# Use Opus 5.5 High for new implementation repairs

The requested implementer default is now `claude-opus-5-5` / `high`.
The independent reviewer and writer use distinct sessions even though they
request the same model. Astra coordination is unchanged.

`scripts/review_cli.py` freezes provider routing with the model profile for
new runs. Saved runs without `agent_providers` retain the original Codex
writer, with no artifact migration. Explicit Codex model and effort overrides
remain supported. The internal `sol` role key stays unchanged for artifact
compatibility; rendered labels identify the implementation writer and provider.

Claude repair exposes read/search and file-edit tools with exact scoped Edit
allow rules, Manual permissions, and unanswered prompts denied. Safe/restricted
mode and disabled hooks remain in place. No shell, MCP, network, or agent tool
is exposed. Large input bundles retain project access through `--add-dir`.
The helper still enforces the repair lock, one writer attempt, post-write scope
checks, and independent recheck. Failed writers require reconciliation and
never select fallback or automatically retry. Reviewer-only host dispatch and
Codex startup recovery cannot launch the Claude writer.

Deterministic tests cover profile/provider persistence, historical Codex
routing, literal scoped permissions, independent sessions, invalid effort,
auth preflight, interruption, and existing recovery boundaries. These fixtures
and local CLI help inspection do not establish Opus writer provider execution
or repair quality on their own. The subsequently requested independent review
executed a separate Opus writer session: its receipt reports
`claude-opus-5-5` in Claude modelUsage, with `high` requested and effort not
independently exposed. The review identified fixture compatibility gaps and a
historical recovery-packet regression; the scoped repair addressed them.

The user's follow-up risk assessment adds a pre-lock feasibility check to
implementation adjudication. Astra must assess acceptance criteria against
requirements and available proof, inspect relevant dependencies, and identify
missing authorized files or commands before writing. Invalid criteria are
rejected; missing prerequisites use the existing `PENDING_USER` route. Scope
never expands automatically, and the existing one-repair limit and persisted
schema remain unchanged. This responds to the observed review that reached
recheck without receipts for all accepted regression checks. It is model
judgment guidance, not a deterministic guarantee of semantic correctness.

The final independent recheck confirmed the prompt repair and found no new
defects. Its required gate remained blocked by two temporary-repository commit
timeouts after all 226 Python tests passed; both hook tests passed unchanged
on a focused retry. Failed review receipts remain preserved. Delivery runs
the full gate again on the integrated tree.

Rollback can select `gpt-6.1-sol` / `xhigh` explicitly for a new run. Existing
runs always retain their saved routing and settings.
