---
topics: [implementation-review-evidence]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/57']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/57'
---
# Match scoped review paths literally

The remaining path-scope defect from closed issue #11 allowed Git pathspec
characters in an authorized filename to select another file. A disposable Git
reproduction showed `[id].py` omitted and unrelated `i.py` included.

For issue #57, the frozen scoped diff now uses literal matching in its tracked
diff and untracked-file detection commands. The older target path remains
unchanged so existing saved-run fingerprints keep their recorded behavior.
One temporary-repository regression case covers the reproduced boundary.
`pnpm run verify:ci` is the repository gate; no provider trial is needed for
this deterministic Git behavior.
