#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { repoRoot, git, atomicWrite } = require("./lib/common.cjs");
const { inferPlanDate } = require("./lib/dates.cjs");

const OUT_OF_SCOPE_TITLE = /^plan —|^plan -/i;
const EXPLORATORY = /audit triage|investigation only|critique \+ build plan|feature-orchestrator|operating\.md updates$/i;
const OTHER_REPO = /(?:^|\s|\/)(?:ui-design-library|Build-Orchestration|frontend-ai|frontend\/|mimecast|opti-saas|ui-design-evidence)(?:\/|\s|$)/i;
const BRANCH_TOKEN = /(?:branch[:\s]+|^|\s)((?:feat|fix|codex|refactor|chore|bot)\/[\w./-]+)/gi;

function parse(argv) {
  const out = { manifest: "", audit: "", repo: process.cwd(), baseBranch: "main", includeUnmatched: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--manifest") out.manifest = argv[++i];
    else if (argv[i] === "--audit") out.audit = argv[++i];
    else if (argv[i] === "--repo") out.repo = argv[++i];
    else if (argv[i] === "--base-branch") out.baseBranch = argv[++i];
    else if (argv[i] === "--include-unmatched") out.includeUnmatched = true;
    else if (argv[i] === "--help") out.help = true;
    else throw new Error(`unknown argument: ${argv[i]}`);
  }
  return out;
}

function gh(args, root) {
  try {
    return execFileSync("gh", args, { cwd: root, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  } catch {
    return "";
  }
}

function isAncestor(root, sha, base) {
  if (!sha || !base) return false;
  try {
    execFileSync("git", ["merge-base", "--is-ancestor", sha, base], { cwd: root, stdio: "ignore" });
    return true;
  } catch {
    return false;
  }
}

function resolveBaseBranch(root, requested) {
  if (requested && git(["rev-parse", "--verify", requested], root)) return requested;
  for (const candidate of [requested, "main", "master"].filter(Boolean)) {
    if (git(["rev-parse", "--verify", candidate], root)) return candidate;
  }
  return git(["rev-parse", "--abbrev-ref", "HEAD"], root) || "HEAD";
}

function loadMergedPrs(root, baseBranch) {
  const raw = gh(["pr", "list", "--state", "merged", "--limit", "200", "--json", "number,headRefName,title,mergeCommit,baseRefName,url"], root);
  if (raw) {
    try {
      return JSON.parse(raw)
        .filter((pr) => pr.mergeCommit?.oid && isAncestor(root, pr.mergeCommit.oid, baseBranch))
        .map((pr) => ({
          number: pr.number,
          branch: pr.headRefName,
          title: pr.title || "",
          merge: pr.mergeCommit.oid,
          url: pr.url || "",
          base: pr.baseRefName || baseBranch,
        }));
    } catch {}
  }
  const out = [];
  const log = git(["log", baseBranch, "--merges", "--format=%H|%s", "-200"], root);
  for (const line of log.split("\n").filter(Boolean)) {
    const [hash, ...rest] = line.split("|");
    const subject = rest.join("|");
    const match = subject.match(/Merge pull request #(\d+) from [\w.-]+\/([^\s]+)/i);
    if (!match) continue;
    out.push({ number: Number(match[1]), branch: match[2], title: subject, merge: hash, url: "", base: baseBranch });
  }
  return out;
}

function words(title) {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 3 && !["plan", "fix", "feat", "with", "from", "into", "this", "that", "repo", "repository"].includes(w));
}

const GENERIC_TITLE_WORDS = new Set([
  "cumulative", "conductor", "project", "knowledge", "confluence", "documentation",
  "version", "update", "improve", "enhance", "fix", "feature", "release", "plugin",
]);

function distinctiveTitleWords(title) {
  return words(title).filter((w) => !GENERIC_TITLE_WORDS.has(w));
}

function extractPaths(reasons, body, tracked) {
  const paths = new Set();
  for (const r of reasons || []) {
    const m = r.match(/^tracked paths: (.+)$/);
    if (m) m[1].split(", ").forEach((p) => paths.add(p.trim()));
  }
  for (const m of body.matchAll(/[`"]?([a-zA-Z0-9_@./-]+\.(?:md|py|cjs|json|jsonc|yml|yaml|ts|tsx|js|plugin))[`"]?/g)) {
    if (tracked.includes(m[1])) paths.add(m[1]);
  }
  return [...paths];
}

function branchIssueNumbers(branch) {
  const nums = new Set();
  for (const match of String(branch).matchAll(/(?:^|\/)(\d{2,})(?:[-/]|$)/g)) nums.add(Number(match[1]));
  return [...nums];
}

function planIssueNumbers(title, body, sources) {
  const text = `${title}\n${body}\n${(sources || []).map((s) => s.source || "").join("\n")}`;
  return [...text.matchAll(/(?:issue|pr)\s*#(\d+)|#(\d{2,})\b/gi)].map((m) => Number(m[1] || m[2])).filter(Boolean);
}

function planBranchHints(title, body, sources) {
  const hints = new Set();
  const text = `${title}\n${body}\n${(sources || []).map((s) => s.source || "").join("\n")}`;
  for (const match of text.matchAll(BRANCH_TOKEN)) hints.add(match[1].toLowerCase());
  for (const match of text.matchAll(/\b((?:feat|fix|codex|refactor|chore)\/[\w.-]+)\b/gi)) hints.add(match[1].toLowerCase());
  return [...hints].filter((hint) => !/^(?:feat|fix|codex|refactor|chore)\/\d+$/.test(hint));
}

function prSemanticallyMatches(plan, pr) {
  const titleWords = distinctiveTitleWords(plan.title);
  const branchWords = pr.branch.toLowerCase().split(/[/\-_]+/).filter((w) => w.length > 3);
  const branchTitleOverlap = titleWords.filter((w) => branchWords.some((b) => b.includes(w) || w.includes(b))).length;
  if (branchTitleOverlap >= 2) return true;
  if (planIssueNumbers(plan.title, plan.body, plan.sources).includes(pr.number)) return true;
  for (const hint of planBranchHints(plan.title, plan.body, plan.sources)) {
    if (pr.branch.toLowerCase() === hint || pr.branch.toLowerCase().includes(hint) || hint.includes(pr.branch.toLowerCase())) return true;
  }
  const prText = `${pr.branch} ${pr.title}`.toLowerCase();
  return titleWords.filter((w) => prText.includes(w)).length >= 2;
}

function headTipDelivery(root, baseBranch, paths) {
  const tip = git(["rev-parse", baseBranch], root).trim();
  const out = git(["show", "--format=%H|%s", "--name-only", tip], root);
  const lines = out.split("\n").filter(Boolean);
  if (!lines.length) return null;
  const [hash, ...subjectParts] = lines[0].split("|");
  const subject = subjectParts.join("|");
  const changed = new Set(lines.slice(1));
  const overlap = paths.filter((p) => changed.has(p));
  if (overlap.length >= 3) return { hash, subject, overlap };
  return null;
}

function scorePr(plan, pr) {
  const titleWords = words(plan.title);
  const blob = `${plan.title}\n${plan.body}`.toLowerCase();
  let score = 0;
  const planIssues = planIssueNumbers(plan.title, plan.body, plan.sources);
  for (const n of planIssues) {
    if (n === pr.number) score += 12;
    if (branchIssueNumbers(pr.branch).includes(n)) score += 10;
  }
  for (const n of branchIssueNumbers(pr.branch)) {
    if (blob.includes(`#${n}`) || blob.includes(`issue #${n}`) || blob.includes(`pr #${n}`)) score += 10;
  }
  for (const hint of planBranchHints(plan.title, plan.body, plan.sources)) {
    if (pr.branch.toLowerCase() === hint || pr.branch.toLowerCase().includes(hint) || hint.includes(pr.branch.toLowerCase())) score += 10;
  }
  if (blob.includes(pr.branch.toLowerCase())) score += 8;
  const prText = `${pr.branch} ${pr.title}`.toLowerCase();
  const branchWords = pr.branch.toLowerCase().split(/[/\-_]+/).filter((w) => w.length > 3);
  score += titleWords.filter((w) => prText.includes(w)).length;
  const branchTitleOverlap = titleWords.filter((w) => branchWords.some((b) => b.includes(w) || w.includes(b))).length;
  score += branchTitleOverlap;
  if (branchTitleOverlap >= 3) score += 4;
  if (pr.branch.startsWith("bot/") && !blob.includes("bot/")) score -= 5;
  return score;
}

function findPrForMergeSubject(mergedPrs, subject) {
  const match = subject.match(/Merge pull request #(\d+) from [\w.-]+\/(\S+)/i);
  if (!match) return null;
  const number = Number(match[1]);
  const branch = match[2];
  return mergedPrs.find((pr) => pr.number === number) || mergedPrs.find((pr) => pr.branch === branch);
}

function prEvidence(pr) {
  return `PR #${pr.number} branch ${pr.branch} merge ${pr.merge.slice(0, 12)}`;
}

function grepCommits(root, phrase, baseBranch) {
  if (!phrase || phrase.length < 5) return [];
  const out = git(["log", baseBranch, `--grep=${phrase}`, "-i", "--format=%H|%s", "-20"], root);
  return out.split("\n").filter(Boolean).map((line) => {
    const [hash, ...rest] = line.split("|");
    return { hash, subject: rest.join("|") };
  });
}

function pathCommits(root, paths, baseBranch) {
  const hits = [];
  for (const p of paths.slice(0, 6)) {
    const out = git(["log", baseBranch, "--format=%H|%s", "-8", "--", p], root);
    for (const line of out.split("\n").filter(Boolean)) {
      const [hash, ...rest] = line.split("|");
      hits.push({ hash, subject: rest.join("|"), path: p });
    }
  }
  return hits;
}

function scoreSubject(subject, titleWords) {
  const s = subject.toLowerCase();
  return titleWords.filter((w) => s.includes(w)).length;
}

function fmtCommit(hit) {
  return `commit ${hit.hash.slice(0, 12)} ${hit.subject}`;
}

function classify(root, candidate, context) {
  const { title, reasons, body } = candidate;
  const { baseBranch, mergedPrs } = context;
  const titleWords = words(title);
  const tracked = candidate._tracked || [];
  const paths = extractPaths(reasons, body, tracked);
  const blob = `${title}\n${body}`;

  if (OUT_OF_SCOPE_TITLE.test(title) || EXPLORATORY.test(title)) {
    return { status: "out-of-scope", evidence: ["Exploratory or planning-only artifact"] };
  }
  if (OTHER_REPO.test(blob) && !/(cumulative-conductor|ba-cockpit|conductor-config|skills\/)/i.test(blob)) {
    return { status: "out-of-scope", evidence: ["Plan targets another repository, not this codebase"] };
  }

  const ranked = mergedPrs
    .map((pr) => ({ pr, score: scorePr(candidate, pr) }))
    .filter((item) => item.score >= 4)
    .sort((a, b) => b.score - a.score);

  if (ranked.length > 0 && ranked[0].score >= 6 && prSemanticallyMatches(candidate, ranked[0].pr)) {
    const top = ranked[0].pr;
    const evidence = [prEvidence(top)];
    if (ranked[1] && ranked[1].score >= 6 && ranked[0].score - ranked[1].score <= 2 && prSemanticallyMatches(candidate, ranked[1].pr)) {
      evidence.push(prEvidence(ranked[1].pr));
    }
    return { status: "implemented", evidence };
  }

  const phrases = [...new Set([
    titleWords.slice(0, 4).join(" "),
    titleWords.slice(0, 2).join(" "),
    ...titleWords.filter((w) => w.length > 6),
  ].filter((p) => p.length >= 5))];

  const grepHits = [];
  for (const phrase of phrases) grepHits.push(...grepCommits(root, phrase, baseBranch));
  const mergeHit = grepHits
    .map((h) => findPrForMergeSubject(mergedPrs, h.subject))
    .find((pr) => pr && prSemanticallyMatches(candidate, pr));
  if (mergeHit) {
    return { status: "implemented", evidence: [prEvidence(mergeHit)] };
  }
  const relevantGrep = grepHits.filter((h) => scoreSubject(h.subject, titleWords) >= 2);
  const weakGrep = grepHits.filter((h) => scoreSubject(h.subject, titleWords) === 1);
  const pathHits = pathCommits(root, paths, baseBranch).filter((h) => scoreSubject(h.subject, titleWords) >= 1);

  if (ranked.length > 0 && ranked[0].score >= 4) {
    const top = ranked[0].pr;
    if (prSemanticallyMatches(candidate, top)) {
      return {
        status: ranked[0].score >= 6 ? "implemented" : "partial",
        evidence: ranked[0].score >= 6
          ? [prEvidence(top)]
          : [prEvidence(top), "Weak plan↔branch match; review before treating as fully delivered on base branch"],
      };
    }
  }

  const headTip = headTipDelivery(root, baseBranch, paths);
  if (headTip) {
    return {
      status: "partial",
      evidence: [
        fmtCommit(headTip),
        `HEAD tip touches ${headTip.overlap.length} plan paths; no merged PR branch identified for this plan`,
      ],
    };
  }

  if (relevantGrep.length >= 1) {
    return {
      status: "partial",
      evidence: [
        ...relevantGrep.slice(0, 2).map(fmtCommit),
        `Commits on ${baseBranch} but no merged PR branch identified for this plan`,
      ],
    };
  }
  if (weakGrep.length >= 2 || (weakGrep.length >= 1 && pathHits.length >= 1)) {
    return {
      status: "partial",
      evidence: [...weakGrep.slice(0, 2), ...pathHits.slice(0, 1)].map(fmtCommit),
    };
  }
  if (reasons?.length === 1 && reasons[0] === "session cwd") {
    return { status: "not-implemented", evidence: ["Session cwd match only; no merged PR branch on base branch"] };
  }
  return {
    status: "not-implemented",
    evidence: [`No merged PR branch on ${baseBranch}; referenced paths: ${paths.slice(0, 3).join(", ") || "none"}`],
  };
}

function sessionKey(sources) {
  if (!Array.isArray(sources)) return "";
  for (const item of sources) {
    const source = String(item?.source || "");
    const raw = source.replace(/^(?:codex|cursor|claude):/i, "");
    const codex = raw.match(/\/\.codex\/sessions\/(.+)$/i);
    if (codex) return codex[1].toLowerCase().replace(/\.jsonl$/i, "");
    const cursor = raw.match(/\/\.cursor\/plans\/(.+)$/i);
    if (cursor) return cursor[1].toLowerCase();
    const claude = raw.match(/\/\.claude\/plans\/(.+)$/i);
    if (claude) return claude[1].toLowerCase();
  }
  return "";
}

function titleOverlap(a, b) {
  return words(a).filter((w) => words(b).includes(w)).length;
}

function propagateSiblingDelivery(candidates, entries, directIds) {
  const byId = new Map(entries.map((entry) => [entry.id, entry]));
  for (const candidate of candidates) {
    const entry = byId.get(candidate.id);
    if (!entry || entry.status !== "not-implemented") continue;
    const session = sessionKey(candidate.sources);
    if (!session) continue;
    for (const sibling of candidates) {
      if (sibling.id === candidate.id || !directIds.has(sibling.id)) continue;
      if (sessionKey(sibling.sources) !== session) continue;
      if (titleOverlap(candidate.title, sibling.title) < 2) continue;
      const siblingEntry = byId.get(sibling.id);
      if (!siblingEntry || siblingEntry.status !== "implemented") continue;
      const branchEvidence = siblingEntry.evidence.find((e) => /^PR #\d+ branch /.test(e));
      if (!branchEvidence) continue;
      entry.status = "implemented";
      entry.evidence = [branchEvidence, `Sibling plan "${sibling.title}" merged on base branch`];
      break;
    }
  }
  return entries;
}

function audit(manifest, root, options = {}) {
  if (!Array.isArray(manifest.candidates)) throw new Error("manifest.candidates must be an array");
  const baseBranch = resolveBaseBranch(root, options.baseBranch || "main");
  const mergedPrs = loadMergedPrs(root, baseBranch);
  const tracked = manifest.repository?.tracked || git(["ls-files"], root).split(/\r?\n/).filter(Boolean);
  const context = { baseBranch, mergedPrs };
  const audited = [];
  for (const candidate of manifest.candidates) {
    if (!options.includeUnmatched && candidate.association === "unmatched") continue;
    if (candidate.association !== "matched" && candidate.association !== "ambiguous" && !options.includeUnmatched) continue;
    candidate._tracked = tracked;
    audited.push(candidate);
  }
  const entries = [];
  const directIds = new Set();
  for (const candidate of audited) {
    const result = classify(root, candidate, context);
    if (!result) continue;
    entries.push({ id: candidate.id, status: result.status, evidence: result.evidence, topics: [] });
    if (result.status === "implemented" && !result.evidence.some((e) => e.startsWith("Sibling plan"))) {
      directIds.add(candidate.id);
    }
  }
  propagateSiblingDelivery(audited, entries, directIds);
  for (const entry of entries) {
    const candidate = audited.find((item) => item.id === entry.id);
    entry.date = inferPlanDate(root, candidate, entry.evidence, entry.status);
  }
  const totals = {};
  for (const entry of entries) totals[entry.status] = (totals[entry.status] || 0) + 1;
  entries.sort((a, b) => a.id.localeCompare(b.id));
  return { entries, totals, baseBranch, mergedPrCount: mergedPrs.length };
}

function main() {
  try {
    const args = parse(process.argv.slice(2));
    if (args.help) {
      console.log("Usage: audit-plan-candidates.cjs --manifest <file> [--audit <file>] [--repo <path>] [--base-branch main] [--include-unmatched]");
      return 0;
    }
    if (!args.manifest) throw new Error("--manifest is required");
    const root = repoRoot(args.repo);
    const manifest = JSON.parse(fs.readFileSync(path.resolve(args.manifest), "utf8"));
    const { entries, totals, baseBranch, mergedPrCount } = audit(manifest, root, args);
    const payload = { entries };
    if (args.audit) {
      const output = path.resolve(args.audit);
      atomicWrite(output, JSON.stringify(payload, null, 2) + "\n", { mode: 0o600 });
      fs.chmodSync(output, 0o600);
    } else {
      console.log(JSON.stringify(payload, null, 2));
    }
    console.error(`PASS drafted ${entries.length} plan audits on ${baseBranch} (${mergedPrCount} merged PRs) ${JSON.stringify(totals)}`);
    return 0;
  } catch (error) {
    console.error(`FAIL ${error.message}`);
    return 2;
  }
}

if (require.main === module) process.exit(main());
module.exports = { parse, classify, audit, loadMergedPrs, prEvidence, propagateSiblingDelivery, main };
