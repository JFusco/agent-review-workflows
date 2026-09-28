"use strict";

const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");

function digest(value) { return crypto.createHash("sha256").update(value).digest("hex"); }
function slash(value) { return value.split(path.sep).join("/"); }
function slugify(value) {
  return String(value).toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 72) || "plan";
}
function git(args, cwd) {
  try { return execFileSync("git", args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim(); }
  catch { return ""; }
}
function repoRoot(start = process.cwd()) { return path.resolve(git(["rev-parse", "--show-toplevel"], start) || start); }
function remoteSlug(root) {
  const url = git(["remote", "get-url", "origin"], root);
  const match = url.match(/(?:^|@|:\/\/)github\.com[/:]([^?#\s]+)$/i);
  if (!match) return "";
  const slug = match[1].replace(/\.git$/i, "");
  return slug.split("/").length === 2 ? slug.toLowerCase() : "";
}
function walk(dir, predicate = () => true) {
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const absolute = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(absolute, predicate));
    else if (entry.isFile() && predicate(absolute)) out.push(absolute);
  }
  return out.sort();
}
function wikiPath(root, absolute) { return slash(path.relative(root, absolute)); }
function ensureInside(root, target) {
  const rel = path.relative(root, target);
  return rel === "" || (rel !== ".." && !rel.startsWith(`..${path.sep}`));
}
function hasSymlinkComponent(root, target) {
  if (!ensureInside(root, target)) return true;
  let current = path.resolve(root);
  for (const part of path.relative(root, target).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    try {
      if (fs.lstatSync(current).isSymbolicLink()) return true;
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
  }
  return false;
}
function atomicWrite(file, bytes, options = {}) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = path.join(path.dirname(file), `.${path.basename(file)}.wiki-tmp-${process.pid}-${crypto.randomBytes(6).toString("hex")}`);
  try {
    fs.writeFileSync(temporary, bytes, options);
    fs.renameSync(temporary, file);
  } finally {
    try { fs.unlinkSync(temporary); } catch (error) { if (error.code !== "ENOENT") throw error; }
  }
}
function substantive(paths) {
  const ignored = /^(wiki\/|scripts\/wiki\/|\.github\/workflows\/wiki-|CHANGELOG|.*lock(?:\.yaml|\.json)?$)/i;
  return paths.some((item) => !ignored.test(slash(item)) && (!/\.(md|txt)$/i.test(item) || /^(AGENTS|CLAUDE)\.md$/i.test(item)));
}
function today() { return new Date().toISOString().slice(0, 10); }

module.exports = { digest, slash, slugify, git, repoRoot, remoteSlug, walk, wikiPath, ensureInside, hasSymlinkComponent, atomicWrite, substantive, today };
