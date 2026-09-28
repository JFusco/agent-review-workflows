#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const root = path.resolve(__dirname, "..");
const local = path.join(root, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
const python = fs.existsSync(local) ? local : "python3";
const result = spawnSync(python, process.argv.slice(2), {
  cwd: root,
  stdio: "inherit",
  env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" }
});

if (result.error) {
  console.error(`Unable to start ${python}: ${result.error.message}`);
  console.error("Create .venv with a working Python 3.11+ interpreter and install requirements-dev.lock.");
  process.exitCode = 1;
} else if (result.signal) {
  console.error(`Python terminated by ${result.signal}; check the selected interpreter: ${python}`);
  process.exitCode = 1;
} else {
  process.exitCode = result.status ?? 1;
}
