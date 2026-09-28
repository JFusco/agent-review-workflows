#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { digest, repoRoot, slugify, slash, ensureInside, hasSymlinkComponent, atomicWrite, walk } = require("./lib/common.cjs");
const { inferPlanDate } = require("./lib/dates.cjs");
const { titleFromBody, render } = require("./lib/frontmatter.cjs");
const { cleanCursor } = require("./lib/plans.cjs");

const STATUSES = new Set(["implemented", "partial", "not-implemented", "superseded", "out-of-scope"]);

function parse(argv) {
  const out = { file: "", manifest: "", candidate: "", status: "", evidence: [], topics: [], sourceTool: "", source: "", date: "" };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (!arg.startsWith("-") && !out.file) out.file = arg;
    else if (arg === "--manifest") out.manifest = argv[++i];
    else if (arg === "--candidate") out.candidate = argv[++i];
    else if (arg === "--status") out.status = argv[++i];
    else if (arg === "--evidence") out.evidence.push(argv[++i]);
    else if (arg === "--topic") out.topics.push(argv[++i]);
    else if (arg === "--source-tool") out.sourceTool = argv[++i];
    else if (arg === "--source") out.source = argv[++i];
    else if (arg === "--date") out.date = argv[++i];
    else if (arg === "--repo") out.repo = argv[++i];
    else if (arg === "--help") out.help = true;
    else throw new Error(`unknown argument: ${arg}`);
  }
  return out;
}

function fromArgs(args) {
  if (args.manifest) {
    const manifest = JSON.parse(fs.readFileSync(path.resolve(args.manifest), "utf8"));
    if (!Array.isArray(manifest.candidates)) throw new Error("manifest.candidates must be an array");
    const found = manifest.candidates.find((item) => item.id === args.candidate || item.digest === args.candidate);
    if (!found) throw new Error(`candidate not found: ${args.candidate}`);
    if (!Array.isArray(found.sources) || found.sources.some((item) => !item || typeof item.source !== "string" || !item.source.trim() || (item.tool !== undefined && typeof item.tool !== "string"))) throw new Error(`candidate sources are invalid: ${args.candidate}`);
    return { body: found.body, title: found.title, digest: found.digest, sourceTool: found.source_tool, source: found.sources.map((item) => `${item.tool || found.source_tool}:${item.source}`).join(", ") };
  }
  if (!args.file) throw new Error("provide a plan file or --manifest and --candidate");
  const file = path.resolve(args.file);
  const text = fs.readFileSync(file, "utf8");
  const body = args.sourceTool === "cursor" ? cleanCursor(text) : text.trim() + "\n";
  return { body, title: titleFromBody(body, path.basename(file, path.extname(file))), digest: digest(body), sourceTool: args.sourceTool || "repository", source: args.source || slash(file) };
}

function ensureIndex(root) {
  const file = path.join(root, "wiki", "plans", "INDEX.md");
  if (!fs.existsSync(file)) throw new Error("wiki/plans/INDEX.md is missing; initialize the wiki first");
  return file;
}

function validDate(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

function stringList(name, value, allowEmpty = false) {
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string" || (!allowEmpty && !item.trim()))) throw new Error(`${name} must be an array of non-empty strings`);
  return value.map((item) => item.trim()).filter(Boolean);
}

function cell(value) { return String(value).replace(/\r?\n/g, " ").replace(/\|/g, "\\|").trim(); }
function label(value) { return String(value).replace(/\r?\n/g, " ").replace(/\\/g, "\\\\").replace(/\|/g, "\\|").replaceAll("[", "\\[").replaceAll("]", "\\]").trim(); }

function validateArchiveInput(root, item, audit) {
  if (!STATUSES.has(audit.status)) throw new Error(`invalid status: ${audit.status}`);
  if (!validDate(audit.date)) throw new Error(`invalid date: ${audit.date}`);
  const evidence = stringList("evidence", audit.evidence || []);
  const topics = stringList("topics", audit.topics || [], true);
  if (["implemented", "partial"].includes(audit.status) && !evidence.length) throw new Error(`${audit.status} requires implementation evidence`);
  if (["implemented", "partial"].includes(audit.status) && !topics.length) throw new Error(`${audit.status} requires at least one topic`);
  if (topics.some((topic) => topic.split(/[\\/]/).includes("..") || path.isAbsolute(topic))) throw new Error("topics must not escape wiki/topics");
  for (const topic of topics) {
    const relative = topic.startsWith("wiki/topics/") ? topic.slice("wiki/topics/".length) : topic;
    const topicFile = path.join(root, "wiki", "topics", relative.endsWith(".md") ? relative : `${relative}.md`);
    if (!ensureInside(path.join(root, "wiki", "topics"), topicFile) || hasSymlinkComponent(root, topicFile) || !fs.existsSync(topicFile) || !fs.lstatSync(topicFile).isFile()) throw new Error(`topic does not exist: ${topic}`);
  }
  if (!item || typeof item.body !== "string" || !item.body.trim()) throw new Error("plan body must be a non-empty string");
  const normalizedBody = item.body.trim() + "\n";
  const computed = digest(normalizedBody);
  if (typeof item.digest !== "string" || !/^[a-f0-9]{64}$/.test(item.digest) || item.digest !== computed) throw new Error("plan digest does not match its body");
  if (typeof item.sourceTool !== "string" || !item.sourceTool.trim()) throw new Error("source_tool is required");
  if (typeof item.source !== "string" || !item.source.trim()) throw new Error("source is required");
  const indexFile = ensureIndex(root);
  if (hasSymlinkComponent(root, indexFile)) throw new Error("wiki/plans/INDEX.md must not be a symbolic link");
  const index = fs.readFileSync(indexFile, "utf8");
  const marker = "<!-- wiki-plan-rows -->";
  if (!index.includes(marker)) throw new Error(`missing ${marker} in wiki/plans/INDEX.md`);
  const archiveBody = ["implemented", "partial"].includes(audit.status);
  const title = typeof item.title === "string" && item.title.trim() ? item.title.trim() : titleFromBody(normalizedBody, "Untitled plan");
  const filename = archiveBody ? `${audit.date}-${slugify(title)}-${item.digest.slice(0, 10)}.md` : "";
  const output = filename ? path.join(root, "wiki", "plans", filename) : "";
  if (output && (!ensureInside(path.join(root, "wiki", "plans"), output) || hasSymlinkComponent(root, output))) throw new Error("archive path is unsafe");
  const fields = { status: audit.status, executed: true, evidence, source_tool: item.sourceTool.trim(), source: item.source.trim(), topics, digest: item.digest };
  const bytes = output ? render(fields, normalizedBody) : "";
  if (output && fs.existsSync(output) && (!fs.lstatSync(output).isFile() || fs.readFileSync(output, "utf8") !== bytes)) throw new Error(`refusing to overwrite non-identical archive: ${output}`);
  return { root, item: { ...item, body: normalizedBody, title }, audit: { ...audit, evidence, topics }, indexFile, index, marker, archiveBody, filename, output, bytes };
}

function archive(root, item, audit) {
  const prepared = validateArchiveInput(root, item, audit);
  const comment = `<!-- plan:${prepared.item.digest} -->`;
  if (prepared.index.includes(comment)) {
    if (prepared.archiveBody) {
      const bodyExists = walk(path.join(root, "wiki", "plans"), (file) => file.endsWith(".md") && path.basename(file) !== "INDEX.md")
        .some((file) => fs.readFileSync(file, "utf8").includes(`digest: "${prepared.item.digest}"`));
      if (!bodyExists) throw new Error(`plan ledger references ${prepared.item.digest} but its archive body is missing`);
    }
    return { state: "unchanged", digest: prepared.item.digest };
  }
  const planCell = prepared.archiveBody ? `[${label(prepared.item.title)}](./${prepared.filename})` : cell(prepared.item.title);
  const row = `| ${prepared.audit.date} | ${planCell} | ${prepared.audit.status} | ${cell(prepared.audit.evidence.join("; ") || "—")} | ${cell(prepared.audit.topics.join(", ") || "—")} ${comment} |`;
  const nextIndex = prepared.index.replace(prepared.marker, `${row}\n${prepared.marker}`);
  const outputExisted = prepared.output && fs.existsSync(prepared.output);
  try {
    if (prepared.output && !outputExisted) atomicWrite(prepared.output, prepared.bytes);
    atomicWrite(prepared.indexFile, nextIndex);
  } catch (error) {
    if (prepared.output && !outputExisted) {
      try { fs.unlinkSync(prepared.output); } catch (cleanup) { if (cleanup.code !== "ENOENT") error.message += `; cleanup failed: ${cleanup.message}`; }
    }
    throw error;
  }
  return { state: "archived", digest: prepared.item.digest, file: prepared.output || null };
}

function main() {
  let args;
  try { args = parse(process.argv.slice(2)); } catch (error) { console.error(`FAIL ${error.message}`); return 2; }
  if (args.help) {
    console.log("Usage: archive-plan.cjs <plan.md> --status <status> [--evidence <text> ...] [--topic <slug> ...]\n       archive-plan.cjs --manifest <file> --candidate <id> --status <status> ...");
    return 0;
  }
  try {
    const item = fromArgs(args);
    if (args.sourceTool) item.sourceTool = args.sourceTool;
    if (args.source) item.source = args.source;
    const root = repoRoot(args.repo || process.cwd());
    const candidate = {
      sources: [{ tool: item.sourceTool, source: args.file || item.source || "" }],
    };
    const audit = {
      status: args.status,
      evidence: args.evidence,
      topics: args.topics,
      date: args.date || inferPlanDate(root, candidate, args.evidence, args.status),
    };
    const result = archive(root, item, audit);
    console.log(`PASS ${result.state} ${result.digest}${result.file ? ` -> ${result.file}` : ""}`);
    return 0;
  } catch (error) { console.error(`FAIL ${error.message}`); return 2; }
}

if (require.main === module) process.exit(main());
module.exports = { parse, archive, fromArgs, validateArchiveInput, validDate, STATUSES };
