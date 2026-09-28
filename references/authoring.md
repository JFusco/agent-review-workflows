# Authoring and evaluation

Sources consulted for this implementation:

- [Anthropic skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [OpenAI: Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [Claude Code programmatic use](https://code.claude.com/docs/en/headless)
- [Codex non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode)
- [JSON Schema dialects](https://json-schema.org/understanding-json-schema/reference/schema)

Keep descriptions short and discriminating. Load only the needed supporting context. Model reasoning stays flexible; identity checks, read/write boundaries and handoff routing stay deterministic. Do not copy long provider manuals into the skills or add generic reminders after every failure.

Evaluate observable outcomes before adding instructions. Use the same raw requirements and disposable fixtures for baseline and skill-assisted runs; never supply the intended repair to an independent reviewer. Compare accepted defects, unsupported findings, scope, plan simplicity, verification, runtime and available token usage. Provider judgments are not deterministic. Track baseline and fixture evidence separately from live provider execution.

Tests must demonstrate rejection of malformed/stale handoffs, retained history, no plan-to-code transition, configured and frozen model settings, legacy-run compatibility, and only one implementation writer. Bounded live trials exercise every assigned role. No fixture carries production credentials or performs external writes.
