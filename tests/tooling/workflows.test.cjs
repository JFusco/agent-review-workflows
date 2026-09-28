"use strict";

const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");
const { ROOT } = require("./support.cjs");

function read(relative) {
  return fs.readFileSync(path.join(ROOT, relative), "utf8");
}

test("GitHub workflows run the explicit quality and commit-range gates", () => {
  const quality = read(".github/workflows/quality.yml");
  assert.match(quality, /pull_request:\n\s+branches: \[main\]/);
  assert.match(quality, /push:\n\s+branches: \[main\]/);
  assert.match(quality, /workflow_dispatch: \{\}/);
  assert.match(quality, /HUSKY: "0"/);
  assert.match(quality, /run: pnpm run verify:ci/);

  const commitlint = read(".github/workflows/commitlint.yml");
  assert.match(commitlint, /types: \[opened, synchronize, reopened, edited\]/);
  assert.match(commitlint, /printf '%s\\n' "\$PR_TITLE" \| pnpm run lint:commit --verbose/);
  assert.match(commitlint, /PR_BODY: \$\{\{ github\.event\.pull_request\.body \}\}/);
  assert.match(commitlint, /if: \$\{\{ !startsWith\(github\.event\.pull_request\.head\.ref, 'bot\/wiki-'\) \}\}/);
  assert.match(commitlint, /run: pnpm run lint:pr/);
  assert.match(commitlint, /pnpm run lint:commit --from "\$BASE_SHA" --to "\$HEAD_SHA" --verbose/);
});

test("developer automation contains no AI commit or PR helper", () => {
  const manifest = JSON.parse(read("package.json"));
  const packages = { ...manifest.dependencies, ...manifest.devDependencies };
  assert.equal(Object.hasOwn(packages, "@verndale/ai-commit"), false);
  assert.equal(Object.hasOwn(packages, "@verndale/ai-pr"), false);
  const automation = [
    read(".husky/commit-msg"),
    read(".husky/pre-commit"),
    read(".husky/pre-push"),
    read(".github/workflows/quality.yml"),
    read(".github/workflows/commitlint.yml")
  ].join("\n");
  assert.doesNotMatch(automation, /\bai-(?:commit|pr)\b/);
});
