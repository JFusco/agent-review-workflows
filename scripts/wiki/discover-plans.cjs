#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { repoRoot, atomicWrite } = require("./lib/common.cjs");
const { discover } = require("./lib/plans.cjs");

function parse(argv) {
  const out = { repo: process.cwd(), plansDirs: [], json: "", sinceDays: 0 };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--repo") out.repo = argv[++i];
    else if (argv[i] === "--plans-dir") out.plansDirs.push(argv[++i]);
    else if (argv[i] === "--json") out.json = argv[++i];
    else if (argv[i] === "--since-days") out.sinceDays = Number(argv[++i]);
    else if (argv[i] === "--help") out.help = true;
    else throw new Error(`unknown argument: ${argv[i]}`);
  }
  return out;
}

function main() {
  let args;
  try { args = parse(process.argv.slice(2)); } catch (error) { console.error(`FAIL ${error.message}`); return 2; }
  if (args.help) {
    console.log("Usage: discover-plans.cjs [--repo <path>] [--plans-dir <path> ...] [--since-days <n>] [--json <manifest.json>]");
    return 0;
  }
  if (!Number.isFinite(args.sinceDays) || args.sinceDays < 0) {
    console.error("FAIL --since-days must be a non-negative number");
    return 2;
  }
  const root = repoRoot(args.repo);
  const manifest = discover(root, args.plansDirs, { sinceDays: args.sinceDays });
  if (args.json) {
    const output = path.resolve(args.json);
    atomicWrite(output, JSON.stringify(manifest, null, 2) + "\n", { mode: 0o600 });
    fs.chmodSync(output, 0o600);
    console.log(`PASS wrote ${manifest.summary.total} candidates to ${output}`);
  } else {
    console.log(JSON.stringify({ repository: manifest.repository.root, summary: manifest.summary, candidates: manifest.candidates.map(({ body: _body, ...item }) => item) }, null, 2));
  }
  if (manifest.summary.ambiguous) console.warn(`warning: ${manifest.summary.ambiguous} candidates require repository-association review`);
  return 0;
}

if (require.main === module) process.exit(main());
module.exports = { parse, main };
