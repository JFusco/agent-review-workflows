#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { repoRoot, remoteSlug } = require("./lib/common.cjs");
const { reconcile } = require("./on-merge-sync.cjs");

const DAY_MS = 24 * 60 * 60 * 1000;
const GH_RESPONSE_BUFFER_BYTES = 64 * 1024 * 1024;

function parseArgs(argv, now = new Date()) {
  const options = { dryRun: false };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--dry-run") options.dryRun = true;
    else if (["--repo", "--repository", "--base", "--pr", "--since"].includes(token)) {
      const value = argv[index + 1];
      if (!value || value.startsWith("--")) throw new Error(`${token} requires a value`);
      options[token.slice(2)] = value;
      index += 1;
    } else throw new Error(`unknown argument: ${token}`);
  }
  if (options.pr && options.since) throw new Error("--pr and --since are mutually exclusive");
  if (options.pr && (!/^\d+$/.test(options.pr) || Number(options.pr) < 1)) throw new Error("--pr must be a positive integer");
  if (options.since && !/^\d{4}-\d{2}-\d{2}$/.test(options.since)) throw new Error("--since must use YYYY-MM-DD");
  if (options.since) {
    const parsed = new Date(`${options.since}T00:00:00Z`);
    if (!Number.isFinite(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== options.since) throw new Error("--since must be a real calendar date");
  }
  if (!options.pr && !options.since) options.since = new Date(now.getTime() - 90 * DAY_MS).toISOString().slice(0, 10);
  options.base ||= "main";
  return options;
}

function flattenPages(value) {
  if (!Array.isArray(value)) throw new Error("GitHub API response must be an array");
  return value.flatMap((page) => Array.isArray(page) ? page : [page]);
}

function githubRequest(endpoint, { paginate = false } = {}) {
  const args = ["api", endpoint];
  if (paginate) args.push("--paginate", "--slurp");
  const output = execFileSync("gh", args, {
    encoding: "utf8",
    maxBuffer: GH_RESPONSE_BUFFER_BYTES,
    stdio: ["ignore", "pipe", "pipe"],
  });
  const parsed = JSON.parse(output);

  return paginate ? flattenPages(parsed) : parsed;
}

function isWikiBotPull(pull) {
  return String(pull?.head?.ref || "").startsWith("bot/wiki-");
}

function selectMergedPulls(pulls, since) {
  const boundary = Date.parse(`${since}T00:00:00Z`);

  return pulls
    .filter((pull) => pull?.merged_at && Date.parse(pull.merged_at) >= boundary && !isWikiBotPull(pull))
    .sort((left, right) => Date.parse(left.merged_at) - Date.parse(right.merged_at) || Number(left.number) - Number(right.number));
}

function mergeContext(repository, pull, files, commits) {
  return {
    schemaVersion: 1,
    repository,
    number: pull.number,
    title: pull.title,
    body: pull.body || "",
    url: pull.html_url,
    mergedAt: pull.merged_at,
    changedFiles: files.map((file) => ({ path: file.filename, status: file.status || "modified" })),
    changedPaths: files.map((file) => file.filename),
    commits: commits.map((commit) => ({ hash: commit.sha, subject: String(commit.commit?.message || "").split("\n")[0] })),
  };
}

function copyWikiForDryRun(root) {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(), "wiki-reconcile-"));
  const source = path.join(root, "wiki");
  if (!fs.existsSync(source)) throw new Error("wiki/ is required for merge reconciliation");
  fs.cpSync(source, path.join(temporary, "wiki"), { recursive: true });
  return temporary;
}

function collectPulls({ repository, base, pr, since, request }) {
  if (pr) {
    const pull = request(`repos/${repository}/pulls/${pr}`);
    if (!pull.merged_at) throw new Error(`PR #${pr} is not merged`);
    if (isWikiBotPull(pull)) throw new Error(`PR #${pr} is a wiki bot pull request`);
    return [pull];
  }
  const endpoint = `repos/${repository}/pulls?state=closed&base=${encodeURIComponent(base)}&sort=updated&direction=asc&per_page=100`;

  return selectMergedPulls(request(endpoint, { paginate: true }), since);
}

function reconcilePulls(options) {
  const root = repoRoot(options.repo || process.cwd());
  const repository = options.repository || process.env.GITHUB_REPOSITORY || remoteSlug(root);
  if (!/^[^/\s]+\/[^/\s]+$/.test(repository || "")) throw new Error("--repository or GITHUB_REPOSITORY must be an owner/repository slug");
  const request = options.request || githubRequest;
  const pulls = collectPulls({ ...options, repository, request });
  const targetRoot = options.dryRun ? copyWikiForDryRun(root) : root;
  const results = [];
  try {
    for (const pull of pulls) {
      try {
        const files = request(`repos/${repository}/pulls/${pull.number}/files?per_page=100`, { paginate: true });
        const commits = request(`repos/${repository}/pulls/${pull.number}/commits?per_page=100`, { paginate: true });
        const changed = reconcile(mergeContext(repository, pull, files, commits), targetRoot);
        results.push({ number: pull.number, mergedAt: pull.merged_at, changed, status: changed.length ? "changed" : "unchanged" });
      } catch (error) {
        results.push({ number: pull.number, mergedAt: pull.merged_at, changed: [], status: "error", error: error.message });
      }
    }
    const summary = {
      schemaVersion: 1,
      repository,
      mode: options.pr ? "single" : "batch",
      dryRun: Boolean(options.dryRun),
      since: options.since || null,
      processed: results.length,
      changed: results.filter((item) => item.status === "changed").length,
      unchanged: results.filter((item) => item.status === "unchanged").length,
      errors: results.filter((item) => item.status === "error").length,
      results,
    };
    if (summary.errors) {
      const error = new Error(`merge reconciliation failed for ${summary.errors} pull request(s)`);
      error.summary = summary;
      throw error;
    }
    return summary;
  } finally {
    if (options.dryRun) fs.rmSync(targetRoot, { recursive: true, force: true });
  }
}

function main() {
  try {
    const summary = reconcilePulls(parseArgs(process.argv.slice(2)));
    process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
    return 0;
  } catch (error) {
    if (error.summary) process.stdout.write(`${JSON.stringify(error.summary, null, 2)}\n`);
    console.error(`FAIL ${error.message}`);
    return 2;
  }
}

if (require.main === module) process.exit(main());
module.exports = { collectPulls, flattenPages, githubRequest, isWikiBotPull, mergeContext, parseArgs, reconcilePulls, selectMergedPulls, main };
