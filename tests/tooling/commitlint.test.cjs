"use strict";

const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");
const { ROOT, run, must, write, repository, fixture } = require("./support.cjs");

const cli = path.join(ROOT, "node_modules/@commitlint/cli/cli.js");
const config = path.join(ROOT, "commitlint.config.cjs");

test("standalone Commitlint enforces the selected message policy", () => {
  const cases = [
    ["ci(quality): Add hooks", true],
    ["fix(custom-scope): preserve output", true],
    ["feat(api)!: Change request", true],
    ["feat(api): Change request\n\nBREAKING CHANGE: request fields changed", true],
    ["Merge branch 'feature'", true],
    ["fix: Missing scope", false],
    ["fix(API): Uppercase scope", false],
    ["unknown(api): Invalid type", false],
    ["fix(api): Trailing period.", false],
    ["fix(api):", false],
    [`fix(api): ${"x".repeat(50)}`, true],
    [`fix(api): ${"x".repeat(51)}`, false],
    [`fix(${"s".repeat(112)}): x`, true],
    [`fix(${"s".repeat(113)}): x`, false],
    [`fix(api): Add checks\n\n${"x".repeat(72)}`, true],
    [`fix(api): Add checks\n\n${"x".repeat(73)}`, false]
  ];
  for (const [message, valid] of cases) {
    const result = run(ROOT, process.execPath, [cli, "--config", config], { input: message + "\n" });
    assert.equal(result.status, valid ? 0 : 1, `${JSON.stringify(message)}\n${result.error || ""}\n${result.stdout}\n${result.stderr}`);
  }
});

test("commit range checks only introduced commits", (t) => {
  const root = repository(t);
  write(root, "seed", "seed\n");
  must(root, "git", ["add", "."]);
  must(root, "git", ["commit", "-m", "Historical unscoped message"]);
  const base = must(root, "git", ["rev-parse", "HEAD"]).stdout.trim();
  must(root, "git", ["commit", "--allow-empty", "-m", "ci(quality): Add gates"]);
  const args = [cli, "--config", config, "--from", base, "--to", "HEAD"];
  must(root, process.execPath, args);
  must(root, "git", ["commit", "--allow-empty", "-m", "Invalid intermediate message"]);
  must(root, "git", ["commit", "--allow-empty", "-m", "ci(quality): Add another gate"]);
  assert.equal(run(root, process.execPath, args).status, 1);
});

test("the installed commit-msg hook blocks an invalid commit", (t) => {
  const root = fixture(t);
  const before = must(root, "git", ["rev-parse", "HEAD"]).stdout;
  const rejected = run(root, "git", ["commit", "--allow-empty", "-m", "Missing conventional format"]);
  assert.notEqual(rejected.status, 0, rejected.stdout + rejected.stderr);
  assert.equal(must(root, "git", ["rev-parse", "HEAD"]).stdout, before);
  const message = "commit message.txt";
  write(root, message, "ci(quality): Accept a valid commit\n");
  must(root, "git", ["commit", "--allow-empty", "-F", message]);
  assert.notEqual(must(root, "git", ["rev-parse", "HEAD"]).stdout, before);
  fs.unlinkSync(path.join(root, message));
});
