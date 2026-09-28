"use strict";

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const assert = require("node:assert/strict");

const ROOT = path.resolve(__dirname, "../..");
const gitLocalVariables = spawnSync("git", ["rev-parse", "--local-env-vars"], { encoding: "utf8" }).stdout.trim().split(/\r?\n/);

function environment(extra = {}) {
  const env = { ...process.env, HUSKY: "1" };
  for (const variable of gitLocalVariables) delete env[variable];
  return { ...env, ...extra };
}

function run(root, command, args, options = {}) {
  return spawnSync(command, args, { cwd: root, encoding: "utf8", timeout: 30000, env: environment(), ...options });
}

function must(root, command, args, options = {}) {
  const result = run(root, command, args, options);
  assert.equal(result.status, 0, `${command} ${args.join(" ")}\n${result.error || ""}\n${result.stdout}\n${result.stderr}`);
  return result;
}

function write(root, file, content, mode) {
  const target = path.join(root, file);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, content, mode ? { mode } : undefined);
}

function temporary(t) {
  const root = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), "agent-review-tooling-")));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  return root;
}

function repository(t) {
  const root = temporary(t);
  must(root, "git", ["init", "--initial-branch=main"]);
  must(root, "git", ["config", "user.name", "Quality hook test"]);
  must(root, "git", ["config", "user.email", "quality-test@example.invalid"]);
  must(root, "git", ["config", "commit.gpgsign", "false"]);
  must(root, "git", ["config", "core.hooksPath", ".disabled-hooks"]);
  return root;
}

function fixture(t) {
  const root = repository(t);
  for (const file of [
    ".husky/pre-commit",
    ".husky/commit-msg",
    ".husky/pre-push",
    "commitlint.config.cjs",
    "eslint.config.cjs",
    "lint-staged.config.mjs",
    "pyproject.toml",
    "scripts/python.cjs"
  ]) {
    write(root, file, fs.readFileSync(path.join(ROOT, file)));
  }
  fs.symlinkSync(path.join(ROOT, "node_modules"), path.join(root, "node_modules"), "junction");
  write(root, "scripts/wiki/pre-commit.cjs", "require('node:fs').appendFileSync('.git/wiki-called', 'wiki\\n'); process.exit(Number(process.env.QUALITY_TEST_WIKI_EXIT || 0));\n");
  const scripts = JSON.parse(fs.readFileSync(path.join(ROOT, "package.json"), "utf8")).scripts;
  write(root, "package.json", JSON.stringify({ private: true, scripts }, null, 2) + "\n");
  write(root, ".gitignore", "node_modules/\n.venv/\n.husky/_/\n.ruff_cache/\n");
  write(root, "sample.cjs", '"use strict";\nmodule.exports = 1;\n');
  must(root, "git", ["add", "."]);
  must(root, "git", ["commit", "-m", "chore(test): Seed fixture"]);
  must(root, "pnpm", ["run", "prepare"]);
  return root;
}

module.exports = { ROOT, environment, run, must, write, temporary, repository, fixture };
