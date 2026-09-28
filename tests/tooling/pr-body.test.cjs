"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { REQUIRED_CHECKS, validatePullRequestBody } = require("../../scripts/validate_pr_body.cjs");

function validBody() {
  return `## Summary

Add a deterministic pull request contract for consistent review evidence.

## Linked issue

Closes #4

## Changes

- Add a canonical template and validator.

## Verification

- pnpm run verify:ci passed locally.

## Risk and rollback

- Risk: Existing open pull requests must adopt the new structure.
- Rollback: Revert the validator commit and rerun Commitlint.

## Checklist

${REQUIRED_CHECKS.map((item) => `- [x] ${item}`).join("\n")}
`;
}

test("the canonical pull request body passes", () => {
  assert.deepEqual(validatePullRequestBody(validBody()), []);
});

test("section order and meaningful content are enforced", () => {
  const body = validBody()
    .replace("## Summary\n\nAdd a deterministic pull request contract for consistent review evidence.", "## Summary\n\n<!-- placeholder -->")
    .replace("## Changes", "## Verification")
    .replace("## Verification\n\n- pnpm run verify:ci passed locally.", "## Changes\n\n- Add a canonical template and validator.");
  const errors = validatePullRequestBody(body);
  assert.ok(errors.some((error) => error.includes("headings exactly once and in order")));
  assert.ok(errors.some((error) => error.startsWith("Summary must contain")));
});

test("issue linkage, risk, rollback, and checklist completion are required", () => {
  const body = validBody()
    .replace("Closes #4", "Related issue #4")
    .replace("- Risk: Existing open pull requests must adopt the new structure.", "- Risk: <!-- placeholder -->")
    .replace("- Rollback: Revert the validator commit and rerun Commitlint.", "- Rollback: <!-- placeholder -->")
    .replace(`- [x] ${REQUIRED_CHECKS[0]}`, `- [ ] ${REQUIRED_CHECKS[0]}`);
  const errors = validatePullRequestBody(body);
  assert.ok(errors.some((error) => error.startsWith("Linked issue must")));
  assert.ok(errors.some((error) => error.includes("nonempty `Risk:`")));
  assert.ok(errors.some((error) => error.includes("nonempty `Rollback:`")));
  assert.ok(errors.some((error) => error.includes(REQUIRED_CHECKS[0])));
});
