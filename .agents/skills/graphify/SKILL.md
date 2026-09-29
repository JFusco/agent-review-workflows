---
name: graphify
description: Use the shared Graphify code map to trace current source relationships in maintained scripts. Verify exact behavior in source and history in the context wiki.
---

# Graphify code map

Use Graphify 0.9.36 from the repository root. The shared map is in
`graphify-out/`; `.graphifyignore` limits it to maintained scripts. The map does
not replace wiki history.

- For broad current-code questions, run `graphify query "<question>"`.
  Use `graphify explain "<symbol>"`, `graphify path "<from>" "<to>"`, or
  `graphify affected "<symbol>"` for focused relationships and impact.
- Follow returned file and line references into source. Confirm `INFERRED`
  and `AMBIGUOUS` relationships there. For an exact file or command question,
  inspect source directly; use wiki navigation for rationale and history.
- After eligible code changes, pulls, or merges, run
  `PYTHONHASHSEED=0 graphify update .`. Native post-commit and post-checkout
  hooks refresh the map in the background; review output before staging.
- To rebuild without model calls, run
  `PYTHONHASHSEED=0 GRAPHIFY_MAX_WORKERS=1 graphify extract . --code-only --force`
  and then `PYTHONHASHSEED=0 graphify update .`.
- On a fresh clone, install dependencies and run `graphify hook install`.
  Verify with `graphify hook status`. The Git hooks and local merge driver
  are native Graphify integrations; no agent tool hooks are installed.
- Keep `graphify-out/memory/` empty. Optional query outcomes belong in
  ignored `graphify-out/local-memory/` via `--memory-dir`.
