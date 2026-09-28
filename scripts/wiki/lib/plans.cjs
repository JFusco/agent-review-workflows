"use strict";

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { digest, git, remoteSlug, walk, slash } = require("./common.cjs");
const { splitFrontmatter, scalar, titleFromBody } = require("./frontmatter.cjs");

const PLAN_PATH = /(^|\/)(plans?|docs\/plans?|\.claude\/plans?|\.cursor\/plans?)\/.*\.md$/i;

function cleanCursor(text) {
  const parsed = splitFrontmatter(text);
  if (!parsed.raw) return text.trim() + "\n";
  const privateKeys = ["name", "overview", "todos", "isProject"];
  if (!privateKeys.some((key) => new RegExp(`^${key}:`, "m").test(parsed.raw))) return text.trim() + "\n";
  const name = scalar(parsed.raw, "name");
  const body = parsed.body.trim();
  return `${body.startsWith("#") || !name ? "" : `# ${name}\n\n`}${body}\n`;
}

function planTitle(body) {
  return (String(body).match(/^#\s+(.+)$/m) || [])[1]?.trim().toLowerCase() || "";
}

function proposedPlans(file) {
  const byTitle = new Map();
  let cwd = "";
  for (const line of fs.readFileSync(file, "utf8").split(/\r?\n/)) {
    if (!line.trim()) continue;
    let event;
    try { event = JSON.parse(line); } catch { continue; }
    if (event.type === "session_meta" && event.payload?.cwd) cwd = event.payload.cwd;
    const payload = event.payload || {};
    const bodies = [];
    const item = payload.item || {};
    if (item.type === "Plan" && typeof item.text === "string" && item.text.trim()) bodies.push(item.text);
    const role = payload.role || (payload.message && payload.message.role);
    if (role === "assistant") {
      const content = payload.content || (payload.message && payload.message.content) || "";
      const chunks = Array.isArray(content) ? content.map((part) => typeof part === "string" ? part : part.text || "").join("\n") : String(content);
      for (const match of chunks.matchAll(/<proposed_plan>\s*([\s\S]*?)\s*<\/proposed_plan>/g)) {
        if (match[1].trim()) bodies.push(match[1]);
      }
    }
    for (const text of bodies) {
      const body = `${text.trim()}\n`;
      const title = planTitle(body);
      if (!title) continue;
      byTitle.set(title, { body, cwd });
    }
  }
  return [...byTitle.values()];
}

function sourceTimestamp(source) {
  const text = String(source?.source || source || "");
  const rollout = text.match(/rollout-(\d{4})-(\d{2})-(\d{2})T(\d{2})-(\d{2})-(\d{2})/);
  if (rollout) {
    const ms = Date.parse(`${rollout[1]}-${rollout[2]}-${rollout[3]}T${rollout[4]}:${rollout[5]}:${rollout[6]}Z`);
    if (!Number.isNaN(ms)) return ms;
  }
  if (text.startsWith("/") || text.includes(path.sep)) {
    try {
      if (fs.existsSync(text)) return fs.statSync(text).mtimeMs;
    } catch {}
  }
  return 0;
}

function latestSourceMs(item) {
  return Math.max(0, ...(item.sources || []).map(sourceTimestamp));
}

function normalizeTitle(title) {
  return String(title || "").trim().toLowerCase().replace(/\s+/g, " ");
}

function collapseByTitle(items) {
  const groups = new Map();
  for (const item of items) {
    const key = normalizeTitle(item.title) || item.digest;
    const prev = groups.get(key);
    if (!prev || latestSourceMs(item) > latestSourceMs(prev) || (latestSourceMs(item) === latestSourceMs(prev) && item.body.length > prev.body.length)) {
      groups.set(key, item);
    }
  }
  return [...groups.values()];
}

function association(body, sourceCwd, repo) {
  const normalizedRoot = slash(repo.root).toLowerCase();
  const text = body.toLowerCase();
  if (typeof sourceCwd === "string" && sourceCwd && path.resolve(sourceCwd) === repo.root) return { state: "matched", reasons: ["session cwd"] };
  const reasons = [];
  if (text.includes(normalizedRoot)) reasons.push("repository path");
  if (repo.slug && text.includes(repo.slug)) reasons.push("GitHub repository");
  const grounded = repo.tracked.filter((item) => item.includes("/") && text.includes(item.toLowerCase())).slice(0, 3);
  if (grounded.length) reasons.push(`tracked paths: ${grounded.join(", ")}`);
  if (reasons.length) return { state: "matched", reasons };
  if (text.includes(path.basename(repo.root).toLowerCase())) return { state: "ambiguous", reasons: ["repository basename only"] };
  return { state: "unmatched", reasons: [] };
}

function fromMarkdown(file, tool, repo, repoLocal = false) {
  const raw = fs.readFileSync(file, "utf8");
  const body = tool === "cursor" ? cleanCursor(raw) : raw.trim() + "\n";
  const matched = repoLocal ? { state: "matched", reasons: ["repository-local plan"] } : association(body, "", repo);
  return candidate(body, tool, file, matched);
}

function candidate(body, sourceTool, source, matched) {
  const hash = digest(body);
  return {
    id: hash.slice(0, 16), digest: hash, title: titleFromBody(body, path.basename(source, path.extname(source))),
    body, source_tool: sourceTool, sources: [{ tool: sourceTool, source }], association: matched.state, reasons: matched.reasons,
  };
}

function gitHistoryPlans(repo) {
  const names = git(["log", "--all", "--format=", "--name-only", "--", "plans", "docs/plans", ".claude/plans", ".cursor/plans"], repo.root)
    .split(/\r?\n/).filter((name) => PLAN_PATH.test(slash(name)));
  const seen = new Set();
  const out = [];
  for (const name of names) {
    if (seen.has(name)) continue;
    seen.add(name);
    const commits = git(["log", "--all", "--format=%H", "--", name], repo.root).split(/\r?\n/).filter(Boolean);
    for (const commit of commits) {
      const body = git(["show", `${commit}:${name}`], repo.root);
      if (body) out.push(candidate(body.trim() + "\n", "repository-history", `git:${commit}:${name}`, { state: "matched", reasons: ["repository Git history"] }));
    }
  }
  return out;
}

function auditedDigests(root) {
  const found = new Set();
  for (const file of walk(path.join(root, "wiki"), (name) => name.endsWith(".md"))) {
    const text = fs.readFileSync(file, "utf8");
    for (const match of text.matchAll(/(?:^digest:\s*["']?([a-f0-9]{32,64})|<!--\s*plan:([a-f0-9]{32,64})\s*-->)/gmi)) found.add(match[1] || match[2]);
  }
  return found;
}

function discover(root, extraDirs = [], options = {}) {
  const home = process.env.WIKI_HOME ? path.resolve(process.env.WIKI_HOME) : os.homedir();
  const repo = { root: path.resolve(root), slug: remoteSlug(root), tracked: git(["ls-files"], root).split(/\r?\n/).filter(Boolean) };
  const all = [];
  const cutoff = options.sinceDays ? Date.now() - options.sinceDays * 86400000 : 0;
  const recent = (file) => !cutoff || fs.statSync(file).mtimeMs >= cutoff;
  const localDirs = ["plans", "docs/plans", ".claude/plans", ".cursor/plans"].map((dir) => path.join(root, dir)).concat(extraDirs.map((dir) => path.resolve(root, dir)));
  for (const dir of localDirs) for (const file of walk(dir, (name) => name.endsWith(".md")).filter(recent)) all.push(fromMarkdown(file, "repository", repo, true));
  for (const file of walk(path.join(home, ".claude", "plans"), (name) => name.endsWith(".md")).filter(recent)) all.push(fromMarkdown(file, "claude", repo));
  for (const file of walk(path.join(home, ".cursor", "plans"), (name) => name.endsWith(".md")).filter(recent)) all.push(fromMarkdown(file, "cursor", repo));
  for (const store of [path.join(home, ".codex", "sessions"), path.join(home, ".codex", "archived_sessions")]) {
    for (const file of walk(store, (name) => name.endsWith(".jsonl")).filter(recent)) {
      for (const plan of proposedPlans(file)) all.push(candidate(plan.body, "codex", file, association(plan.body, plan.cwd, repo)));
    }
  }
  if (!cutoff) all.push(...gitHistoryPlans(repo));
  const excluded = auditedDigests(root);
  const byDigest = new Map();
  for (const item of all) {
    if (excluded.has(item.digest)) continue;
    const previous = byDigest.get(item.digest);
    if (!previous) byDigest.set(item.digest, item);
    else {
      for (const source of item.sources) if (!previous.sources.some((existing) => existing.tool === source.tool && existing.source === source.source)) previous.sources.push(source);
      if (previous.association !== "matched" && item.association === "matched") {
        previous.association = item.association;
        previous.reasons = item.reasons;
      }
    }
  }
  const candidates = collapseByTitle([...byDigest.values()]).sort((a, b) => a.id.localeCompare(b.id));
  const counts = { matched: 0, ambiguous: 0, unmatched: 0 };
  for (const item of candidates) counts[item.association]++;
  return { version: 1, repository: repo, summary: { total: candidates.length, ...counts }, candidates };
}

module.exports = { cleanCursor, proposedPlans, discover, association, collapseByTitle, normalizeTitle };
