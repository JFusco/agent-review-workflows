---
topics: [implementation-review-evidence]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/105']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/105'
---

# Limit the inventory count only outside Git

A repository with 21,718 tracked files could not start any review: the helper
stopped with `Project inventory exceeds 20,000 files`. A Git project must use
its repository root, so the suggested smaller standalone project was not
available.

The 20,000-file ceiling protected the recursive directory walk used for
non-Git projects, which has no other bound. A Git inventory comes from
`git ls-files --cached --others --exclude-standard` and is bounded by what the
repository tracks or does not ignore. `project_files()` now applies the ceiling
only to the non-Git walk; the message and every other inventory, scope and
freshness guard are unchanged. Saved runs are unaffected.

Each inventory pass still hashes every listed file, so very large repositories
take longer per pass. That cost was not changed.

A temporary-directory test proves a Git project above the limit lists every
file and a non-Git project above it still fails. The CLI reference states the
limit's scope. No live provider trial is needed for this local guard.
