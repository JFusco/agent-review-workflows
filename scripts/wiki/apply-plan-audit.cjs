#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { archive, validateArchiveInput, STATUSES } = require("./archive-plan.cjs");
const { repoRoot } = require("./lib/common.cjs");
const { inferPlanDate } = require("./lib/dates.cjs");

function parse(argv) {
  const out = { manifest: "", audit: "", repo: process.cwd() };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--manifest") out.manifest = argv[++i];
    else if (argv[i] === "--audit") out.audit = argv[++i];
    else if (argv[i] === "--repo") out.repo = argv[++i];
    else if (argv[i] === "--help") out.help = true;
    else throw new Error(`unknown argument: ${argv[i]}`);
  }
  return out;
}

function main() {
  try {
    const args = parse(process.argv.slice(2));
    if (args.help) { console.log("Usage: apply-plan-audit.cjs --manifest <file> --audit <file> [--repo <path>]"); return 0; }
    if (!args.manifest || !args.audit) throw new Error("--manifest and --audit are required");
    const manifest = JSON.parse(fs.readFileSync(path.resolve(args.manifest), "utf8"));
    const audit = JSON.parse(fs.readFileSync(path.resolve(args.audit), "utf8"));
    if (!Array.isArray(audit.entries)) throw new Error("audit.entries must be an array");
    if (!Array.isArray(manifest.candidates)) throw new Error("manifest.candidates must be an array");
    const candidates = new Map();
    const candidateIds = new Set();
    const candidateDigests = new Set();
    for (const item of manifest.candidates) {
      if (!item || typeof item.id !== "string" || !item.id || typeof item.digest !== "string" || !item.digest) throw new Error("manifest candidate id and digest are required");
      if (candidateIds.has(item.id) || candidateDigests.has(item.digest)) throw new Error(`duplicate manifest candidate: ${item.id}`);
      candidateIds.add(item.id); candidateDigests.add(item.digest);
      candidates.set(item.id, item); candidates.set(item.digest, item);
    }
    const root = repoRoot(args.repo);
    const seen = new Set();
    const seenDigests = new Set();
    const totals = {};
    const prepared = [];
    for (const entry of audit.entries) {
      const item = candidates.get(entry.id);
      if (!item) throw new Error(`audit candidate not found: ${entry.id}`);
      if (seen.has(item.id) || seenDigests.has(item.digest)) throw new Error(`duplicate audit candidate: ${entry.id}`);
      seen.add(item.id); seenDigests.add(item.digest);
      if (!STATUSES.has(entry.status)) throw new Error(`invalid status for ${entry.id}: ${entry.status}`);
      const archiveItem = {
        body: item.body, title: item.title, digest: item.digest, sourceTool: item.source_tool,
        source: Array.isArray(item.sources) && item.sources.every((source) => source && typeof source.source === "string" && source.source.trim() && (source.tool === undefined || typeof source.tool === "string")) ? item.sources.map((source) => `${source.tool || item.source_tool}:${source.source}`).join(", ") : "",
      };
      const archiveAudit = {
        status: entry.status,
        evidence: entry.evidence || [],
        topics: entry.topics || [],
        date: entry.date || inferPlanDate(root, item, entry.evidence || [], entry.status),
      };
      validateArchiveInput(root, archiveItem, archiveAudit);
      prepared.push({ item: archiveItem, audit: archiveAudit });
    }
    for (const entry of prepared) {
      archive(root, entry.item, entry.audit);
      const status = entry.audit.status;
      totals[status] = (totals[status] || 0) + 1;
    }
    const remaining = manifest.candidates.filter((item) => item.association !== "unmatched" && !seen.has(item.id));
    if (remaining.length) console.warn(`warning: ${remaining.length} matched or ambiguous candidates remain unaudited`);
    console.log(`PASS applied ${seen.size} plan audits ${JSON.stringify(totals)}`);
    return 0;
  } catch (error) { console.error(`FAIL ${error.message}`); return 2; }
}

if (require.main === module) process.exit(main());
module.exports = { parse, main };
