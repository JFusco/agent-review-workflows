# Review-suite comparison

Use the two run directories supplied by the maintainer. Read each `original.json` and require exact equality of `requirements` and `target`; differing inputs are non-comparable. Record `agent_profile`, `instructions`, and `check_commands` differences as context. Do not attribute every outcome difference to the skill.

Read existing evidence only:

- `calls/*/invocation.json`: attempted provider calls.
- `calls/*/process.json`: completed call `elapsed_seconds`, `exit_code`, and `interruption`.
- `calls/*/stdout.log`: token usage only when the provider output identifies the fields and their accounting scope. Otherwise mark usage unavailable.
- `state.json`: accepted `ledger` stages, final finding dispositions and verification statuses, and current check receipts.
- `checks/*.json`: saved check outcomes and fingerprints, including prior receipts.

Separate attempts from accepted stages, agent time from check time, and requested profiles from observed provider metadata. Do not infer whole-run wall time from call durations. Mark missing or ambiguous values unavailable.

Judge coverage and unsupported findings only against an explicitly supplied maintainer expectations file. Cite each relevant expectation and the run evidence. Without such a file, show observable outcomes and costs, and mark quality judgment unavailable; finding counts alone do not establish quality.

Return a concise side-by-side comparison with evidence paths and limitations in the conversation. If a report is saved, keep it outside both reviewed projects. Do not edit either run, invoke providers, or add a comparison helper.
