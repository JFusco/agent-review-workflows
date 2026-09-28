#!/usr/bin/env node
"use strict";

const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { repoRoot, git, substantive } = require("./lib/common.cjs");
const { discover } = require("./lib/plans.cjs");

function main() {
  const root = repoRoot(process.cwd());
  const staged = git(["diff", "--cached", "--name-only", "--diff-filter=ACMRD"], root).split(/\r?\n/).filter(Boolean);
  if (substantive(staged) && !staged.some((item) => item.startsWith("wiki/journal/"))) console.warn("wiki warning: substantive staged changes have no journal entry");
  try {
    const manifest = discover(root, [], { sinceDays: 2 });
    const pending = manifest.candidates.filter((item) => item.association !== "unmatched");
    if (pending.length) console.warn(`wiki warning: ${pending.length} historical plan candidates still need an evidence audit`);
  } catch (error) { console.warn(`wiki warning: plan discovery failed open: ${error.message}`); }
  const graphInputs = staged.filter((item) => (item.startsWith("wiki/") && item.endsWith(".md") && item !== "wiki/connections.md")
    || /^scripts\/wiki\/(?:build-graph|lib\/(?:common|frontmatter|github-refs|wiki-graph))\.cjs$/.test(item));
  const watched = ["wiki", "scripts/wiki/build-graph.cjs", "scripts/wiki/lib/common.cjs", "scripts/wiki/lib/frontmatter.cjs", "scripts/wiki/lib/github-refs.cjs", "scripts/wiki/lib/wiki-graph.cjs", "scripts/wiki/graph/data/graph.json"];
  const wikiStatus = git(["status", "--porcelain", "--untracked-files=all", "--", ...watched], root).split(/\r?\n/).filter(Boolean);
  const hasUnstagedInput = wikiStatus.some((line) => line.startsWith("??") || (line.length > 1 && line[1] !== " "));
  if (hasUnstagedInput) {
    console.warn("wiki warning: unstaged wiki changes or graph inputs detected; rebuild skipped to avoid staging output derived from uncommitted content");
    return 0;
  }
  if (!graphInputs.length) return 0;
  const build = spawnSync(process.execPath, [path.join(root, "scripts/wiki/build-graph.cjs")], { cwd: root, encoding: "utf8" });
  if (build.status === 0) {
    const stagedGraph = spawnSync("git", ["add", "--", "wiki/connections.md", "scripts/wiki/graph/data/graph.json"], { cwd: root, encoding: "utf8" });
    if (stagedGraph.status !== 0) console.warn(`wiki warning: generated graph could not be staged: ${(stagedGraph.stderr || stagedGraph.stdout).trim()}`);
  } else console.warn(`wiki warning: graph rebuild failed open: ${(build.stderr || build.stdout).trim()}`);
  return 0;
}
if (require.main === module) process.exit(main());
module.exports = { main };
