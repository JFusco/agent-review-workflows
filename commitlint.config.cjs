"use strict";

module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [2, "always", ["build", "chore", "ci", "docs", "feat", "fix", "perf", "refactor", "revert", "style", "test"]],
    "scope-empty": [2, "never"],
    "scope-case": [2, "always", "lower-case"],
    "subject-max-length": [2, "always", 50],
    "subject-case": [0],
    "header-max-length": [2, "always", 120],
    "body-max-line-length": [2, "always", 72],
    "footer-max-line-length": [2, "always", 72]
  }
};
