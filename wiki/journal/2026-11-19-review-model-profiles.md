---
topics: [review-agent-profiles]
plans: [2026-11-19-refresh-default-review-model-profiles-6c5e5fc575.md]
issues: ['https://github.com/JFusco/agent-review-workflows/issues/102']
---

# Refresh default review model profiles

Plan research now requests Astra 6.2 High. Coordination requests Astra 6.2
Max across plan, implementation, and diff reviews. Those roles weigh sources,
requirements, and evidence across the review packet. Scoped repair moves to
Sol 6.2 XHigh and uses the existing Codex writer boundary. The repair lock and
checks give it specific changes to make and verify. OpenAI recommends Sol for
revising code after feedback. [OpenAI Codex guidance](https://learn.chatgpt.com/docs/whats-new/gpt-62-astra-sol)

Opus 5.5 High remains the independent reviewer. Fable 5.2 High is available via
an explicit reviewer override for targeted comparisons. The installed review
helper resolved Claude Code 2.1.328 after the update, and CLI help exposed the
required schema and permission flags. [Fable 5.2 CLI requirements](https://support.claude.com/en/articles/15424964-claude-fable-models-on-your-plan)

Saved runs use their frozen profiles and provider routing. Deterministic tests
cover the new defaults and flags, the Fable override, the previous Claude writer
path, and saved-run compatibility. These checks establish local configuration
and routing. Model quality and account access need separate provider evidence.
