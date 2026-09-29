---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#24 and .agents/skills/graphify/SKILL.md"]
source_tool: "codex"
source: "Codex eight-repository implementation plan, 2026-09-29"
topics: ["maintainer-workflow"]
digest: "e4b953bbda2b05f653806d4f02245b6e48aaf231392b1a869f76eab1a9099480"
---

# Standardize commit messages and Graphify across eight repositories

Apply the same commit-writing guidance to design-passport, agent-review-workflows, cms-field-vocabulary, context-wiki, qa-operations, qa-regression-writer, qa-team, and research-operations. Use design-passport's Graphify setup as the reference: a repository-local guidance skill, a shared code map refreshed by native Git hooks, and the existing wiki for history and decisions.

- Add concise guidance: a specific scoped action subject of at most 50 characters; an optional why, impact, or tradeoff body; and Conventional Commits breaking-change syntax. Keep existing required scopes, allowed types, 72-character body lines, and PR checks. Change only cms-field-vocabulary's commitlint subject limit from 100 to 50. Do not rewrite history.
- Keep design-passport's Graphify setup. In qa-operations, qa-team, and research-operations, replace Graphify-installed agent hooks and duplicate instructions with a repository-local skill while preserving code-map coverage, shared outputs, and native Git hooks; preserve QA Operations SQL support.
- Add Graphify 0.9.36 code-only maps to agent-review-workflows and qa-regression-writer maintained scripts; cms-field-vocabulary src and scripts; and context-wiki scripts and shipped repository scripts. Exclude documentation, wiki content, tests, generated files, dependencies, and local state. Add the local skill, Claude link, setup instructions, and native Git hooks. Keep each wiki graph separate.
- Record each change in its wiki. Preserve unrelated agent settings and hooks. Remove Graphify-owned agent integrations only where the local skill replaces them.
- Verify commitlint, Graphify hooks and focused queries, ignored local state, skill and wiki checks, each repository's pnpm run verify:ci, and pnpm run lint:pr. Deliver each through an issue branch and PR, then stop without merging.
