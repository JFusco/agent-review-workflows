---
topics: [implementation-review-evidence]
plans: [2026-09-28-collapse-implementation-review-to-five-calls-fe6bc3ca4e.md]
---
# Collapse implementation review

Issue [#21](https://github.com/JFusco/agent-review-workflows/issues/21) replaces the seven-call implementation path with independent review, authoritative adjudication and repair lock, one scoped repair, one independent recheck, and finalization when verification succeeds. An incomplete recheck ends unresolved. The earlier plan-log proposal in issue #20 remains unmerged; its useful plan content is represented by the adjudication lock instead of a separate stage or printout.

The lock is a deterministic record of accepted findings, authorized files, checks, fingerprint, and revision. It is saved in the adjudication artifact, checked before Sol can write, and rendered with the scoped Git diff in the handoff. The protocol uses `implementation_evidence_version: 2`; older runs retain their recorded advisory path. The coordinator continues to preserve evidence-backed in-scope discoveries from issue #17.

Temporary-repository tests cover the five-stage ledger, lock consistency and tamper rejection, pending decisions, recheck failure, cited-check-receipt recovery, and legacy continuation. The full repository gate is `pnpm run verify:ci`.

Two live provider runs on the issue branch tested the actual change. The first ended `unresolved` after Opus recheck: Sol's accepted code and test repairs passed, but Opus newly found an inaccurate test count in `VALIDATION.md`. This confirmed the one-repair limit and no finalization after a new recheck finding. A fresh run carried that evidence forward. Astra locked the documentation correction, Sol changed only the count, Opus independently marked it PASSED with no new findings, and Astra finalized. The successful run's ledger has exactly review, adjudicate, repair, recheck, and finalize. The local run IDs and exact checks are recorded in `VALIDATION.md`; neither run is production evidence.
