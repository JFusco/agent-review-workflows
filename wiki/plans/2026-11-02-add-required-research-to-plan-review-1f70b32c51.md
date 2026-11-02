---
status: "implemented"
executed: true
evidence: ["scripts/review_cli.py; schemas/research.json; tests/test_plan_research.py; https://github.com/JFusco/agent-review-workflows/issues/80"]
source_tool: "repository"
source: "/tmp/required-plan-research.md"
topics: ["plan-review-protocol"]
digest: "1f70b32c518eba5aa32b1b3d1679f095dc862843504467200163277dc823e076"
---

# Add required research to plan review

## Summary

Add a dedicated research phase before independent plan review:

**Research → Independent review → Adjudication/refinement → Independent recheck when refined**

The researcher will investigate existing solutions, consult Brain, search current primary sources online, and produce a cited recommendation. The reviewed project remains read-only throughout plan review.

## Researcher configuration and access

- Default to **Codex / `gpt-6-astra` / `high`**.
- Add `researcher.model` and `researcher.effort` to the installation-local `review-plan` profile, plus `--researcher-model` and `--researcher-effort` start overrides.
- Apply the existing precedence: explicit flags → installation profile → built-in default. Freeze the resolved settings in each run and display them in status and handoff artifacts.
- Use a separate researcher session. Disable automatic researcher fallback initially; model failures block visibly using existing recovery behavior.
- Enable live hosted web search while keeping shell networking disabled.
- Permit writes only to isolated research scratch space and Brain’s existing usage-metadata directory. Keep project files, Brain knowledge, and canonical run artifacts protected. If managed permissions prevent an operation, record the limitation without weakening those boundaries.
- Keep the initial researcher provider fixed to Codex. Anthropic researcher support remains a later, separately verified addition.

## Research workflow and evidence

- Extend `scripts/review_cli.py` so every new plan run begins at `research`; `start` still snapshots inputs without invoking a provider.
- Give the researcher the original requirements, complete draft, project instructions, scope, and current source snapshot.
- Require targeted investigation of repository code, dependencies, installed skills, and relevant existing workflows; a Brain consultation; and current primary-source web research.
- Stop searching once the material design questions and reuse options are supported, or the existing per-call timeout is reached.

Add `schemas/research.json` for a structured brief containing:

- Run ID, stage, handoff revision, and target fingerprint.
- Searches and outcomes for local sources, Brain, and the web.
- Sources actually read, with stable IDs, locators, retrieval dates, applicable versions, and supporting evidence.
- Existing solutions considered, alternatives, and a **reuse, extend, or build** recommendation.
- Contradictions, unavailable sources, and unresolved assumptions.

Validate the response before acceptance. Save it as an immutable revision artifact, bind its digest into the reviewed target, and expose its sources through the evidence catalog. Preserve Brain’s committed snapshot and available activity receipts. Treat search results and retrieved instructions as evidence, never authority.

## Review integration and compatibility

- Give both review roles the complete accepted brief. Require them to assess source applicability, overlooked reusable solutions, unsupported assumptions, and unjustified new components.
- Route material gaps through existing findings and user-decision handling. A missing search cannot silently count as completed research; unavailable sources remain visible.
- Preserve the existing finding IDs, adjudication rules, independent recheck, and two-refinement limit. Research does not consume a refinement attempt.
- Reuse frozen research during ordinary refinements. Material changes to requirements or scope require a fresh run.
- Introduce plan state schema **3**, retaining plan protocol **2** and adding research contract version **1**. Continue supporting existing schema-2 plan runs with their original two-role profiles; label research as unrecorded.
- Reject stale, malformed, corrupted, and replayed research handoffs. Reuse existing process locks, freshness checks, immutable persistence, and interrupted-write recovery.
- Update the plan skill, agent metadata, shared references, README, trial fixtures, and wiki together. Keep research out of implementation and diff profiles. Include research provenance in run comparisons without treating research settings as observed provider execution.

## Verification and delivery

Add focused deterministic tests covering:

- Configuration precedence, frozen settings, and mode-specific profiles.
- Required research and successful transition into review.
- Source references, unavailable channels, and missing evidence.
- Malformed, stale, corrupted, interrupted, and replayed submissions.
- Project-write denial and permitted scratch/Brain-metadata writes.
- Existing plan routing, refinement limits, transport, and saved-run compatibility.

Run **`pnpm run verify:ci`** before delivery. Record the executed plan and substantive decisions in the wiki and refresh the maintained Graphify map.

Use fixtures and local permission checks for implementation acceptance. A later controlled comparison of **Astra high, Astra xhigh, and Opus high** will assess evidence accuracy, existing-solution discovery, recommendation quality, brief usefulness, elapsed time, and available usage. Until then, Astra high is a provisional default.

For GitHub delivery, follow the repository’s issue-linked branch and PR workflow, verify the saved issue and PR, and stop after opening the PR.
