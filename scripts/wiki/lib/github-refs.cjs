"use strict";

// GitHub evidence is keyed by repository as well as number. Issue #7 in one
// repository must never collide with issue #7 in another repository.

const URL_RE = /(?<![A-Za-z0-9_./:=?&%+-])https:\/\/github\.com\/([A-Za-z0-9_.-]+)\/([A-Za-z0-9_.-]+)\/(pull|issues)\/(\d+)\b[^\s<>"'`)\]]*/gi;
const LABELED_RE = /\b(PR|pull request|issue)\s+#(\d+)\b/gi;
const REPOSITORY_RE = "[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+";

function normalizeRepository(value) {
  const parts = String(value || "").trim().replace(/^https:\/\/github\.com\//i, "").replace(/\.git$/i, "").replace(/^\/+|\/+$/g, "").split("/");
  return parts.length === 2 && parts.every((part) => /^[A-Za-z0-9_.-]+$/.test(part))
    ? parts.join("/").toLowerCase()
    : "";
}

function ref(repository, kind, number) {
  const normalized = normalizeRepository(repository);
  const numeric = Number(number);
  if (!normalized || !Number.isSafeInteger(numeric) || numeric < 1) return null;
  const normalizedKind = ["pull", "pr", "pull-request"].includes(kind) ? "pull-request" : ["issue", "issues"].includes(kind) ? "issue" : "";
  if (!normalizedKind) return null;
  const segment = normalizedKind === "pull-request" ? "pull" : "issues";
  return {
    repository: normalized,
    kind: normalizedKind,
    number: numeric,
    url: `https://github.com/${normalized}/${segment}/${numeric}`,
  };
}

function advanceFence(line, fence = null) {
  const match = String(line).match(/^\s*(`{3,}|~{3,})(.*)$/);
  if (!match) return { fence, marker: false };
  const marker = match[1];
  if (!fence) return { fence: { character: marker[0], length: marker.length }, marker: true };
  const closes = marker[0] === fence.character && marker.length >= fence.length && /^\s*$/.test(match[2]);
  return { fence: closes ? null : fence, marker: true };
}

function withoutFencedCode(text) {
  const kept = [];
  let fence = null;
  for (const line of String(text || "").split(/\r?\n/)) {
    const state = advanceFence(line, fence);
    fence = state.fence;
    if (state.marker) continue;
    if (!fence) kept.push(line);
  }
  return kept.join("\n");
}

function key(item) {
  return `${item.repository}\u0000${item.kind}\u0000${item.number}`;
}

function normalizeGithubQuery(value) {
  const source = String(value || "").trim();
  const match = source.match(new RegExp(
    `^https?:\\/\\/(?:www\\.)?github\\.com\\/(${REPOSITORY_RE})\\/(pull|issues)\\/(\\d+)(?:[?#].*)?$`,
    "i",
  ));
  if (!match) return source;
  return ref(match[1], match[2], match[3])?.url || source;
}

function parseGithubQuery(value) {
  const source = String(value || "").trim();
  if (!source || /^#\d+$/.test(source)) return null;
  const normalized = normalizeGithubQuery(source);
  let match = normalized.match(new RegExp(
    `^https:\\/\\/github\\.com\\/(${REPOSITORY_RE})\\/(pull|issues)\\/(\\d+)$`,
    "i",
  ));
  if (match) return ref(match[1], match[2], match[3]);
  match = source.match(new RegExp(`^(${REPOSITORY_RE})\\s+(PR|pull(?:\\s+request)?|issue)\\s*#?(\\d+)$`, "i"));
  if (match) return ref(match[1], /^issue$/i.test(match[2]) ? "issue" : "pull-request", match[3]);
  match = source.match(new RegExp(`^(${REPOSITORY_RE})#(\\d+)$`, "i"));
  if (!match) return null;
  const repository = normalizeRepository(match[1]);
  const number = Number(match[2]);
  return repository && Number.isSafeInteger(number) && number > 0
    ? { repository, kind: null, number, url: null }
    : null;
}

function githubRefs(text, { repository = "", includeLabeled = true, includeFencedCode = false } = {}) {
  const source = includeFencedCode ? String(text || "") : withoutFencedCode(text);
  const found = [];
  for (const match of source.matchAll(URL_RE)) {
    const item = ref(`${match[1]}/${match[2]}`, match[3].toLowerCase(), match[4]);
    if (item) found.push(item);
  }
  const fallback = normalizeRepository(repository);
  if (includeLabeled && fallback) {
    for (const match of source.matchAll(LABELED_RE)) {
      const item = ref(fallback, /^issue$/i.test(match[1]) ? "issue" : "pull-request", match[2]);
      if (item) found.push(item);
    }
  }
  return [...new Map(found.map((item) => [key(item), item])).values()]
    .sort((a, b) => a.repository.localeCompare(b.repository) || a.kind.localeCompare(b.kind) || a.number - b.number);
}

function closingIssues(text, repository = "") {
  const fallback = normalizeRepository(repository);
  const source = withoutFencedCode(text);
  const found = [];
  const seen = new Set();
  const keyword = /\b(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?)\s*:?\s+/gi;
  const token = /^(?:https:\/\/github\.com\/([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)\/issues\/(\d+)\b|([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+)#(\d+)\b|#(\d+)\b)/i;
  while (keyword.exec(source) !== null) {
    let cursor = keyword.lastIndex;
    let first = true;
    while (cursor < source.length) {
      if (!first) {
        const separator = source.slice(cursor).match(/^(?:\s*,\s*(?:and\s+)?|\s+(?:and|&)\s+|\s+)/i);
        if (!separator) break;
        cursor += separator[0].length;
      }
      const match = source.slice(cursor).match(token);
      if (!match) break;
      const item = ref(match[1] || match[3] || fallback, "issue", match[2] || match[4] || match[5]);
      if (item && !seen.has(key(item))) {
        seen.add(key(item));
        found.push(item);
      }
      cursor += match[0].length;
      first = false;
      if (/^[.!?;]/.test(source.slice(cursor))) break;
    }
    keyword.lastIndex = Math.max(keyword.lastIndex, cursor);
  }
  return found;
}

module.exports = { githubRefs, closingIssues, withoutFencedCode, advanceFence, normalizeGithubQuery, parseGithubQuery, normalizeRepository, ref, key };
