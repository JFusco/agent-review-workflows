---
topics: [plan-review-protocol]
issues: ['https://github.com/jfusco/agent-review-workflows/issues/92']
issue: 'https://github.com/jfusco/agent-review-workflows/issues/92'
---
# Make complete bundles readable under restricted Claude tools

The Office implementation review produced no code review because restricted
file tools could not read the external evidence index. The helper now starts
Claude file-bundle calls inside their owned per-call directory. Every indexed
part remains below that root, while safe mode, read/search-only tools, schemas,
profiles, target fingerprints and the bounded cycle remain intact.

A controlled subprocess reproduces the old containment denial and reads every
part under the selected root. Focused routing tests retain inline, Codex and
research behavior. The original failed Office call and source remain preserved;
continuation is live evidence separate from these transport fixtures.
