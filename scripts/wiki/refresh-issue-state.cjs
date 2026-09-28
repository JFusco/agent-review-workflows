#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { repoRoot, walk, atomicWrite, ensureInside, hasSymlinkComponent } = require("./lib/common.cjs");
const { advanceFence, githubRefs, key } = require("./lib/github-refs.cjs");

const CLOSED_SUFFIX = " — closed <!-- wiki-issue-state:closed -->";
const OWNED_CLOSED_RE = /\s+—\s+closed\s+<!--\s*wiki-issue-state:closed\s*-->\s*$/;
const AUTHORED_CLOSED_RE = /\s+—\s+closed\s*$/;

function issueRefs(text) { return githubRefs(text, { includeLabeled: false }).filter((item) => item.kind === "issue"); }
function setIssueState(text, url, state) {
  const line = String(text);
  if (!line.includes(url)) return line;
  if (state === "open") return line.replace(OWNED_CLOSED_RE, "");
  if (state === "closed" && !OWNED_CLOSED_RE.test(line) && !AUTHORED_CLOSED_RE.test(line)) return line.replace(/\s*$/, "") + CLOSED_SUFFIX;
  return line;
}
function markClosed(text, url) { return setIssueState(text, url, "closed"); }
function openThreadLineIndexes(lines) {
  const indexes = [];
  let inOpenThreads = false;
  let fence = null;
  for (let index = 0; index < lines.length; index++) {
    const state = advanceFence(lines[index], fence);
    fence = state.fence;
    if (state.marker) continue;
    if (fence) continue;
    if (/^##\s/.test(lines[index])) inOpenThreads = /^##\s+Open threads\b/i.test(lines[index]);
    if (inOpenThreads) indexes.push(index);
  }
  return indexes;
}
function ghState(issue) {
  return execFileSync("gh", ["api", `repos/${issue.repository}/issues/${issue.number}`, "--jq", ".state"], { encoding: "utf8" }).trim().toLowerCase() || null;
}
function refresh(topicsDir, lookup = ghState, root = path.resolve(topicsDir, "..", "..")) {
  const changes = [];
  const warnings = [];
  const resolvedRoot = path.resolve(root);
  const resolvedTopics = path.resolve(topicsDir);
  if (!ensureInside(resolvedRoot, resolvedTopics) || hasSymlinkComponent(resolvedRoot, resolvedTopics)) throw new Error("wiki topics path is outside the repository or contains a symbolic link");
  if (!fs.existsSync(topicsDir)) return { changes, warnings };
  const records = walk(topicsDir, (item) => item.endsWith(".md")).map((file) => ({ file, lines: fs.readFileSync(file, "utf8").split("\n") }));
  const references = new Map();
  for (const record of records) {
    for (const index of openThreadLineIndexes(record.lines)) {
      const line = record.lines[index];
      for (const issue of issueRefs(line)) references.set(key(issue), issue);
    }
  }
  const states = new Map();
  for (const [issueKey, issue] of [...references].sort(([a], [b]) => a.localeCompare(b))) {
    try {
      const state = String(lookup(issue) || "").trim().toLowerCase();
      if (!['open', 'closed'].includes(state)) throw new Error("no valid state");
      states.set(issueKey, state);
    } catch (error) {
      warnings.push(`${issue.repository} issue #${issue.number}: ${error.message || "lookup failed"}`);
    }
  }
  for (const record of records) {
    let touched = false;
    for (const index of openThreadLineIndexes(record.lines)) {
      const line = record.lines[index];
      const refs = issueRefs(line);
      if (!refs.length) continue;
      const known = refs.map((issue) => states.get(key(issue))).filter(Boolean);
      if (known.length !== refs.length) continue;
      const closed = known.every((state) => state === "closed");
      const reopened = known.some((state) => state === "open");
      let next = line;
      if (closed && !OWNED_CLOSED_RE.test(line) && !AUTHORED_CLOSED_RE.test(line)) next = line.replace(/\s*$/, "") + CLOSED_SUFFIX;
      else if (reopened && OWNED_CLOSED_RE.test(line)) next = line.replace(OWNED_CLOSED_RE, "");
      if (next !== line) {
        record.lines[index] = next;
        touched = true;
      }
    }
    if (touched) {
      atomicWrite(record.file, record.lines.join("\n"));
      changes.push(path.basename(record.file));
    }
  }
  return { changes, warnings };
}
function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--repo") args.repo = argv[++i];
    else if (argv[i] === "--wiki") args.wiki = argv[++i];
    else if (argv[i] === "--state-map") args.stateMap = argv[++i];
    else throw new Error(`unknown argument: ${argv[i]}`);
  }
  return args;
}
function main() {
  try {
    const args = parseArgs(process.argv.slice(2));
    const root = repoRoot(args.repo || process.cwd());
    const wiki = args.wiki ? path.resolve(args.wiki) : path.join(root, "wiki");
    let lookup = ghState;
    if (args.stateMap) {
      const states = JSON.parse(fs.readFileSync(path.resolve(args.stateMap), "utf8"));
      lookup = (issue) => states[key(issue)] || states[`${issue.repository}#${issue.number}`] || states[issue.url] || states[String(issue.number)] || null;
    }
    const result = refresh(path.join(wiki, "topics"), lookup, root);
    for (const warning of result.warnings) console.warn(`warning: issue-state lookup failed for ${warning}; citation left unchanged`);
    console.log(`PASS issue-state refresh: ${result.changes.length} topic(s) changed`);
    return 0;
  } catch (error) {
    console.error(`FAIL ${error.message}`);
    return 2;
  }
}

if (require.main === module) process.exit(main());
module.exports = { CLOSED_SUFFIX, OWNED_CLOSED_RE, AUTHORED_CLOSED_RE, issueRefs, setIssueState, markClosed, openThreadLineIndexes, ghState, refresh, parseArgs, main };
