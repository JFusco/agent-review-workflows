"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { walk, slash, digest, ensureInside, remoteSlug } = require("./common.cjs");
const { splitFrontmatter, list, titleFromBody } = require("./frontmatter.cjs");
const { githubRefs, withoutFencedCode } = require("./github-refs.cjs");

function normalizeWikiRoot(value = "wiki") {
  const normalized = slash(path.normalize(String(value || "wiki"))).replace(/^\.\//, "").replace(/\/$/, "");
  if (!normalized || normalized === "." || path.isAbsolute(normalized) || normalized === ".." || normalized.startsWith("../") || normalized === ".git" || normalized.startsWith(".git/")) {
    throw new Error("wiki root must be a safe repository-relative directory");
  }
  return normalized;
}

function kind(id, wikiRoot = "wiki") {
  const prefix = `${normalizeWikiRoot(wikiRoot)}/`;
  if (id.startsWith(`${prefix}topics/`)) return "topic";
  if (id.startsWith(`${prefix}journal/`)) return "journal";
  if (id.startsWith(`${prefix}plans/`) && id !== `${prefix}plans/INDEX.md`) return "plan";
  return "index";
}

function scanForSymlinks(root, directory) {
  const found = [];
  (function scan(current) {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const absolute = path.join(current, entry.name);
      if (entry.isSymbolicLink()) found.push(slash(path.relative(root, absolute)));
      else if (entry.isDirectory()) scan(absolute);
    }
  })(directory);
  return found;
}

function resolveWikiLink(root, wikiRootRelative, source, href) {
  const clean = String(href || "").split("#")[0].split("?")[0];
  if (!clean || /^(?:[a-z][a-z0-9+.-]*:|#)/i.test(href)) return null;
  const wikiRoot = path.join(root, wikiRootRelative);
  let target;
  try {
    target = clean.startsWith("/") ? path.join(root, decodeURIComponent(clean.slice(1))) : path.resolve(path.dirname(source), decodeURIComponent(clean));
  } catch {
    return null;
  }
  if (!path.extname(target)) target += ".md";
  else if (path.extname(target).toLowerCase() !== ".md") return null;
  if (!ensureInside(wikiRoot, target)) return null;
  if (slash(path.relative(root, target)) === `${wikiRootRelative}/connections.md`) return null;
  return target;
}

function frontmatterTarget(root, wikiRoot, type, value) {
  if (!value) return null;
  if (value.startsWith(`${wikiRoot}/`)) {
    const target = path.join(root, value);
    return path.extname(target) ? target : `${target}.md`;
  }
  const directory = type === "topic" ? "topics" : "plans";
  return path.join(root, wikiRoot, directory, value.endsWith(".md") ? value : `${value}.md`);
}

function collect(root, { wikiRoot = "wiki" } = {}) {
  const wikiRootRelative = normalizeWikiRoot(wikiRoot);
  const absoluteWikiRoot = path.join(root, wikiRootRelative);
  if (!ensureInside(root, absoluteWikiRoot)) throw new Error("wiki root escapes the repository");
  if (!fs.existsSync(absoluteWikiRoot) || !fs.statSync(absoluteWikiRoot).isDirectory()) throw new Error(`${wikiRootRelative}/ is missing`);
  if (fs.lstatSync(absoluteWikiRoot).isSymbolicLink()) throw new Error(`${wikiRootRelative}/ must not be a symbolic link`);
  const symlinks = scanForSymlinks(root, absoluteWikiRoot);
  if (symlinks.length) throw new Error(`symbolic links are not allowed under ${wikiRootRelative}/: ${symlinks.join(", ")}`);

  const connectionsId = `${wikiRootRelative}/connections.md`;
  const files = walk(absoluteWikiRoot, (file) => file.endsWith(".md") && slash(path.relative(root, file)) !== connectionsId);
  const idFor = new Map(files.map((file) => [path.resolve(file), slash(path.relative(root, file))]));
  const repository = remoteSlug(root);
  const textFor = new Map();
  const nodes = files.map((file, index) => {
    const text = fs.readFileSync(file, "utf8");
    textFor.set(file, text);
    const parsed = splitFrontmatter(text);
    const id = idFor.get(path.resolve(file));
    const type = kind(id, wikiRootRelative);
    const angle = files.length ? 2 * Math.PI * index / files.length : 0;
    return {
      id,
      label: titleFromBody(parsed.body, path.basename(file, ".md")),
      type,
      aliases: list(parsed.raw, "aliases"),
      githubRefs: githubRefs(text, { repository }),
      bytes: Buffer.byteLength(text, "utf8"),
      degree: 0,
      x: Number(Math.cos(angle).toFixed(6)),
      y: Number(Math.sin(angle).toFixed(6)),
      size: type === "index" ? 12 : 8,
    };
  });
  const edges = [];
  const edgeKeys = new Set();
  function add(sourceId, absoluteTarget, relation) {
    const targetId = absoluteTarget && idFor.get(path.resolve(absoluteTarget));
    if (!targetId) {
      if (sourceId.startsWith(`${wikiRootRelative}/plans/`) && sourceId !== `${wikiRootRelative}/plans/INDEX.md`) return;
      throw new Error(`dangling ${relation}: ${sourceId} -> ${absoluteTarget ? slash(path.relative(root, absoluteTarget)) : "missing target"}`);
    }
    const edgeIdentity = `${sourceId}\0${targetId}\0${relation}`;
    if (sourceId === targetId || edgeKeys.has(edgeIdentity)) return;
    edgeKeys.add(edgeIdentity);
    edges.push({ id: digest(edgeIdentity).slice(0, 16), source: sourceId, target: targetId, type: relation, relation });
  }
  for (const file of files) {
    const text = textFor.get(file);
    const parsed = splitFrontmatter(text);
    const sourceId = idFor.get(path.resolve(file));
    for (const match of withoutFencedCode(parsed.body).matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
      const target = resolveWikiLink(root, wikiRootRelative, file, match[1]);
      if (target) add(sourceId, target, "link");
    }
    for (const topic of list(parsed.raw, "topics")) add(sourceId, frontmatterTarget(root, wikiRootRelative, "topic", topic), "topic");
    if (sourceId.startsWith(`${wikiRootRelative}/journal/`)) {
      for (const plan of [...list(parsed.raw, "plans"), ...list(parsed.raw, "plan")]) add(sourceId, frontmatterTarget(root, wikiRootRelative, "plan", plan), "plan");
    }
  }
  const byId = new Map(nodes.map((node) => [node.id, node]));
  for (const edge of edges) {
    byId.get(edge.source).degree += 1;
    byId.get(edge.target).degree += 1;
  }
  nodes.sort((a, b) => a.id.localeCompare(b.id));
  edges.sort((a, b) => a.id.localeCompare(b.id));
  if (nodes.some((node) => !node.id.startsWith(`${wikiRootRelative}/`))) throw new Error(`graph contains a node outside ${wikiRootRelative}/`);
  const byType = {};
  for (const node of nodes) byType[node.type] = (byType[node.type] || 0) + 1;
  return { version: 1, wikiRoot: wikiRootRelative, counts: { nodes: nodes.length, edges: edges.length, byType }, nodes, edges };
}

module.exports = { collect, normalizeWikiRoot, resolveWikiLink, kind };
