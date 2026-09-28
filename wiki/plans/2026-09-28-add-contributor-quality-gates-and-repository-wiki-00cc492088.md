---
status: "implemented"
executed: true
evidence: ["JFusco/agent-review-workflows#1; codex/1-quality-hooks-wiki; pnpm run verify:ci (38 Python tests, 13 tooling tests)"]
source_tool: "repository"
source: "/private/tmp/agent-review-workflows-quality-plan.md"
topics: ["contributor-quality-and-delivery"]
digest: "00cc492088d3f755ed97544e74ead834054a22f6fc4212783ade5d9c7b59f1d2"
---

# Add contributor quality gates and repository wiki

Implement the bounded work tracked by
[JFusco/agent-review-workflows issue #1](https://github.com/JFusco/agent-review-workflows/issues/1):

1. Adapt the relevant Husky, lint-staged, Commitlint, ESLint, Ruff, Python launcher,
   and GitHub Actions patterns from `qa-regression-writer` to this repository.
2. Install the canonical context wiki mechanics and integrate the advisory wiki
   lifecycle after blocking pre-commit checks.
3. Document an issue-linked Git flow in `AGENTS.md`, including a PR body that
   closes the issue on merge and post-merge verification.
4. Expand `.gitignore` for local development artifacts without hiding maintained
   source.
5. Add focused tooling tests and run the complete local gate.
6. Do not add `ai-commit`, `ai-pr`, release, publication, or provider calls.
