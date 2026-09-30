---
status: "implemented"
executed: true
evidence: ["https://github.com/JFusco/agent-review-workflows/issues/27; skills/review-handoff/SKILL.md; tests/test_review_cli.py"]
source_tool: "codex"
source: "codex:/Users/joe.fusco/.codex/sessions/2026/09/29/rollout-2026-09-29T19-58-23-01a0ef9a-edf2-7700-a810-5f6e148d0ba4.jsonl"
topics: ["implementation-review-evidence"]
digest: "665a8120fd4f154ac4d3133843d00a403f03428013015864db90099bf9f241fc"
---

# Add a minimal `review-handoff` skill

## Summary

Create a skill that dispatches **one authorized stage of an existing plan or implementation review run** through the existing `step` command.

The helper remains responsible for routing, evidence packets, validation, permissions, and persistence. No additional agent, model call, workflow stage, or handoff schema.

## Skill behavior

- Accept an existing run directory from the request or unambiguous conversation context. Ask when the run is missing or ambiguous; never select the latest run automatically.
- Resolve the installed helper and interpreter using the existing installation procedure.
- Read `status`. For a `ready` run, execute `step RUN` exactly once using the frozen CLI role configuration.
- For any other status, report it and link the existing recovery procedure. Do not retry, reconcile, submit coordinator judgments, or invent user decisions.
- Return the attempted stage, resulting status, and link to `handoff.md`. A successful handoff does not imply the entire review is complete.
- Preserve existing authorization boundaries, including the prohibition on implementation writes while the invoking conversation is in Plan mode.

The skill never rewrites the evidence packet or chooses the receiving model. An invocation may execute the authorized repair stage through the designated implementer.

## Implementation and authoring

- Add `skills/review-handoff/SKILL.md`, minimal `agents/openai.yaml`, and the repository’s existing shared-reference symlink pattern.
- Use this description: “Dispatches the next authorized stage of an existing plan or implementation review run. Use for a single review-chain handoff.”
- Keep the entrypoint to the input, command sequence, stopping behavior, and output. Link to the shared CLI procedure for installation and recovery.
- Extend the existing installer and its fixtures to include the skill. Retain normal implicit discovery.
- Document single-stage use in the shared CLI reference and repository skill listing. Preserve the existing full-run workflows.
- Leave runtime profiles, response schemas, saved artifacts, and helper routing unchanged.

This follows Anthropic’s guidance on concise instructions and deterministic scripts for fragile operations, and OpenAI’s guidance to reuse existing tools, define clear boundaries, and avoid unnecessary resources. Keep those sources in the authoring reference rather than copying their manuals into the skill. [Anthropic guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [OpenAI guidance](https://developers.openai.com/plugins/build/skills).

## Validation and delivery

- Validate skill metadata and installed reference resolution; test repeated installation and refusal to replace unrelated content.
- Use deterministic fixtures to verify one-stage execution, preserved frozen configuration, and existing rejection of stale targets and invalid repair locks.
- Verify blocked, interrupted, terminal, and externally awaiting runs do not dispatch another agent or trigger recovery automatically. Reuse existing regression coverage where sufficient.
- Check representative requests: explicit handoff, indirect “next agent” request, missing run, and unrelated general handoff. Distinguish authoring checks and fixture results from live model evidence; no paid provider trials are required.
- Run skill validation and `pnpm run verify:ci`.
- On implementation, follow the repository’s issue → branch → PR → checks → merge delivery flow, including the executed-plan archive and wiki updates. Preserve the existing untracked `graphify-out/` directory.

## Defaults

Version one supports only existing review chains. Each invocation advances at most one stage; another explicit invocation may advance the next stage. No new dependencies, configuration options, general-purpose orchestration, or automatic recovery.
