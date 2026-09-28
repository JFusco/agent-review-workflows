'use strict';

function splitFrontmatter(text) {
  const normalized = String(text).replace(/^\uFEFF/, '');
  const match = normalized.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);

  return match
    ? { raw: match[1], body: normalized.slice(match[0].length), full: match[0] }
    : { raw: '', body: normalized, full: '' };
}

function keyPattern(key) {
  return new RegExp(`^${key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}:\\s*`);
}

function scalar(raw, key) {
  const match = raw.match(
    new RegExp(`${keyPattern(key).source}(.*?)\\s*$`, 'm'),
  );
  if (!match) return '';
  return match[1].replace(/^['"]|['"]$/g, '');
}

function parseListLiteral(value) {
  const literal = String(value).trim();
  if (!literal.startsWith('[') || !literal.endsWith(']')) return [];
  try {
    const parsed = JSON.parse(literal.replace(/,\s*]/g, ']'));
    if (Array.isArray(parsed))
      return parsed
        .map(String)
        .map(item => item.trim())
        .filter(Boolean);
  } catch {
    // Fall back to the permissive comma-separated parser below.
  }
  return literal
    .slice(1, -1)
    .split(',')
    .map(item => item.trim().replace(/^['"]|['"]$/g, ''))
    .filter(Boolean);
}

function fieldSpan(raw, key) {
  const lines = String(raw).split(/\r?\n/);
  const pattern = keyPattern(key);
  const start = lines.findIndex(line => pattern.test(line));
  if (start < 0) return null;
  if (lines[start].replace(pattern, '').trim())
    return { start, end: start + 1, kind: 'inline', valid: true };

  let end = start + 1;
  if (/^\s*\[\s*$/.test(lines[end] || '')) {
    const opening = end;
    while (++end < lines.length && !/^\s*\]\s*,?\s*$/.test(lines[end])) {
      // Keep scanning until the bracketed list closes.
    }
    return {
      start,
      end: end < lines.length ? end + 1 : end,
      opening,
      kind: 'bracket-list',
      valid: end < lines.length,
    };
  }
  while (end < lines.length && /^\s+-\s+/.test(lines[end])) end++;
  return { start, end, kind: 'dash-list', valid: true };
}

function list(raw, key) {
  const lines = String(raw).split(/\r?\n/);
  const span = fieldSpan(raw, key);
  if (!span) return [];
  if (span.kind === 'inline') {
    const inline = lines[span.start].replace(keyPattern(key), '').trim();
    if (inline.startsWith('[') && inline.endsWith(']'))
      return parseListLiteral(inline);
    return inline ? [inline.replace(/^['"]|['"]$/g, '')] : [];
  }
  if (span.kind === 'bracket-list') {
    return span.valid
      ? parseListLiteral(lines.slice(span.opening, span.end).join('\n'))
      : [];
  }
  return lines
    .slice(span.start + 1, span.end)
    .map(line =>
      line
        .replace(/^\s+-\s+/, '')
        .trim()
        .replace(/^['"]|['"]$/g, ''),
    )
    .filter(Boolean);
}

function frontmatterProblems(raw) {
  const lines = String(raw).split(/\r?\n/);
  const seen = new Set();
  const problems = [];
  for (let index = 0; index < lines.length; index++) {
    const key = lines[index].match(/^([A-Za-z][A-Za-z0-9_-]*):(?:\s|$)/);
    if (key) {
      if (seen.has(key[1]))
        problems.push(`duplicate frontmatter field "${key[1]}"`);
      seen.add(key[1]);
    }
    if (!/^\s*\[\s*$/.test(lines[index])) continue;
    const owner = lines[index - 1]?.match(/^([A-Za-z][A-Za-z0-9_-]*):\s*$/);
    let closing = index + 1;
    while (closing < lines.length && !/^\s*\]\s*,?\s*$/.test(lines[closing]))
      closing++;
    if (!owner) problems.push(`orphaned bracket list at line ${index + 1}`);
    else if (closing === lines.length)
      problems.push(`unterminated bracket list for "${owner[1]}"`);
    if (closing < lines.length) index = closing;
  }
  return problems;
}

function titleFromBody(body, fallback = 'Untitled') {
  const match = body.match(/^#\s+(.+)$/m);

  return match ? match[1].trim() : fallback;
}

function quote(value) {
  return JSON.stringify(String(value));
}

function render(fields, body) {
  const lines = ['---'];
  for (const [key, value] of Object.entries(fields)) {
    if (Array.isArray(value))
      lines.push(`${key}: [${value.map(quote).join(', ')}]`);
    else if (typeof value === 'boolean') lines.push(`${key}: ${value}`);
    else lines.push(`${key}: ${quote(value)}`);
  }
  return `${lines.join('\n')}\n---\n\n${String(body).replace(/^\s+/, '').replace(/\s+$/, '')}\n`;
}

module.exports = {
  splitFrontmatter,
  scalar,
  list,
  fieldSpan,
  frontmatterProblems,
  titleFromBody,
  render,
};
