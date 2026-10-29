---
topics: [plan-review-protocol]
plans: [2026-10-29-smooth-review-delivery-and-context-handling-5fcf17c685.md]
issues: ['https://github.com/JFusco/agent-review-workflows/issues/76']
---
# Reliable packet delivery and fresh read-only review stages

The approved plan addresses two independent failures: a native Codex message
rejection at 1,048,576 characters, and a resumed Claude recheck reporting
`prompt_too_long`. The incident's exact context overage remains unknown.

The maintained helper retains complete canonical prompts and derives a readable,
validated evidence bundle above a conservative 900,000 UTF-8-byte threshold.
Display fragments preserve long lines and Unicode without requiring a CLI to read
one giant escaped JSON string. Per-call records distinguish characters, bytes,
transport and session mode. Integrity checks prove artifact contents, not model
reading or provider access.

Future read-only CLI attempts start fresh with frozen model settings and current
canonical evidence. Historical resumed invocations retain exact session checks;
writer behavior and interrupted repair reconciliation are unchanged. Structured
context errors with empty permission-denial lists can use the existing bounded
fallback chain. Real denials and transport failures do not authorize model changes.
The two-refinement plan stop now explains the required follow-up explicitly.

Focused deterministic transport and historical session-identity regressions passed.
The delivery gate is the complete `pnpm run verify:ci`; its final result belongs in
the issue-linked PR. No live-provider trial, installation update, live-run recovery,
merge or Brain publication is part of this delivery.

The GitHub connector verified remote main equals local commit
`2dda165cdbfb946591c952def1de5ae574031e9f` after local Git failed DNS resolution.
The connector created and read back issue #76 with the existing bug label.

The first full Python run completed 166 tests with one existing path-resolution
error: an explicit `CODEX_HOME` still evaluated the unused `Path.home()` default.
The host could not resolve a home directory when the fixture cleared the
environment. Run-directory resolution now evaluates that fallback only when no
explicit location exists; the existing regression forces home lookup to fail so
its precedence contract is deterministic. Full verification is rerun after this
small compatibility correction.
