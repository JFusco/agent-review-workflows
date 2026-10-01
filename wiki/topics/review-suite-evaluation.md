---
issues: ['https://github.com/JFusco/agent-review-workflows/issues/47']
---
# Review-suite evaluation

The opt-in `review-suite-eval` skill compares two saved runs in the invoking
conversation. Identical original requirements and targets are the prerequisite
for a comparative conclusion. Profile, instructions, and check-command
differences provide context. Existing call, ledger, finding, and check
artifacts provide observable outcomes and costs; missing measurements remain
unavailable. Quality judgments require explicit maintainer expectations.

The skill does not alter run artifacts, call providers, or add a new helper
mode. Its procedure is maintained in
[suite-eval.md](../../references/suite-eval.md).
