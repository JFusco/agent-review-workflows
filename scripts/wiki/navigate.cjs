#!/usr/bin/env node
"use strict";

const { repoRoot } = require("./lib/common.cjs");
const { collect, normalizeWikiRoot } = require("./lib/wiki-graph.cjs");
const { route, formatRoute } = require("./routing.cjs");

function parseArgs(argv) {
  const args = { json: false, wikiRoot: "wiki", maxBytes: null };
  for (let i = 0; i < argv.length; i++) {
    const key = argv[i];
    if (key === "--intent") args.intent = argv[++i];
    else if (key === "--query") args.query = argv[++i];
    else if (key === "--from") args.from = argv[++i];
    else if (key === "--to") args.to = argv[++i];
    else if (key === "--repo") args.repo = argv[++i];
    else if (key === "--wiki-root") args.wikiRoot = argv[++i];
    else if (key === "--max-bytes") args.maxBytes = Number(argv[++i]);
    else if (key === "--json") args.json = true;
    else if (key === "--help") args.help = true;
    else throw new Error(`unknown argument: ${key}`);
  }
  args.wikiRoot = normalizeWikiRoot(args.wikiRoot);
  if (args.maxBytes != null && (!Number.isInteger(args.maxBytes) || args.maxBytes < 1)) throw new Error("--max-bytes must be a positive integer");
  return args;
}

function usage() { return "Usage: navigate.cjs --intent why|wiring|impact (--query <term>|--from <node>) [--to <node>] [--wiki-root <dir>] [--max-bytes <n>] [--json]"; }
function main(argv = process.argv.slice(2)) {
  try {
    const args = parseArgs(argv);
    if (args.help) { console.log(usage()); return 0; }
    if (!args.intent || (!args.query && !args.from)) throw new Error(usage());
    const root = repoRoot(args.repo || process.cwd());
    const result = route(collect(root, { wikiRoot: args.wikiRoot }), args);
    process.stdout.write(args.json ? `${JSON.stringify(result, null, 2)}\n` : formatRoute(result));
    return result.status === "ok" ? 0 : 2;
  } catch (error) {
    console.error(`FAIL ${error.message}`);
    return 2;
  }
}

if (require.main === module) process.exit(main());
module.exports = { parseArgs, main, usage };
