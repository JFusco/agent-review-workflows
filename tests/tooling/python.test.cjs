"use strict";

const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");
const { ROOT, environment, run, must, write, temporary } = require("./support.cjs");

test("Python launcher prefers .venv, preserves arguments, and forwards failures", (t) => {
  const root = temporary(t);
  write(root, "scripts/python.cjs", fs.readFileSync(path.join(ROOT, "scripts/python.cjs")));
  const script = "#!/usr/bin/env node\nconsole.log(JSON.stringify({args: process.argv.slice(2), cwd: process.cwd(), noBytecode: process.env.PYTHONDONTWRITEBYTECODE})); process.exit(Number(process.env.QUALITY_TEST_PYTHON_EXIT || 0));\n";
  write(root, ".venv/bin/python", script, 0o755);
  const args = [path.join(root, "scripts/python.cjs"), "path with spaces.py", "$(not-a-shell-command)"];
  const result = must(ROOT, process.execPath, args);
  assert.deepEqual(JSON.parse(result.stdout), { args: args.slice(1), cwd: root, noBytecode: "1" });
  assert.equal(run(root, process.execPath, args, { env: environment({ QUALITY_TEST_PYTHON_EXIT: "7" }) }).status, 7);
});

test("Python launcher falls back to PATH only when .venv is absent", (t) => {
  const root = temporary(t);
  write(root, "scripts/python.cjs", fs.readFileSync(path.join(ROOT, "scripts/python.cjs")));
  write(root, "bin/python3", "#!/bin/sh\nprintf 'fallback\\n'\n", 0o755);
  const env = environment({ PATH: path.join(root, "bin") + path.delimiter + process.env.PATH });
  assert.equal(must(root, process.execPath, ["scripts/python.cjs"], { env }).stdout.trim(), "fallback");
  write(root, ".venv/bin/python", "not executable\n", 0o644);
  const result = run(root, process.execPath, ["scripts/python.cjs"], { env });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Unable to start/);
  assert.doesNotMatch(result.stdout, /fallback/);
});
