---
topics: [contributor-quality-and-delivery]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/39']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/39'
---
# PR delivery boundary

Issue [#39](https://github.com/JFusco/agent-review-workflows/issues/39)
aligns the repository's agent delivery endpoint with the other project
instructions. The former `AGENTS.md` flow told agents to wait for checks,
merge the PR, verify issue closure, and return to a synchronized `main`.

The revised flow keeps the verified issue, current-main branch point, full
local gate, ordinary commit and push, canonical PR template, and closing
keyword. Agents now run `pnpm run lint:pr`, open a PR, read it back, and stop.
Review and merging remain with the user; the delivery branch and issue stay
open until the user acts. The review workflow implementation is unchanged.
