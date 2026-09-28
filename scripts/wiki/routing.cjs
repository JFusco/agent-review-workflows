"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { normalizeGithubQuery, parseGithubQuery } = require("./lib/github-refs.cjs");

const POLICY_PATH = path.join(__dirname, "routing-policy.json");
const REQUIRED_INTENTS = ["why", "wiring", "impact"];
const STOP_WORDS = new Set(["a", "an", "and", "are", "as", "at", "does", "for", "from", "how", "i", "in", "is", "it", "of", "on", "or", "the", "this", "to", "what", "when", "where", "why", "with"]);
const EVIDENCE_TYPE_PRIORITY = new Map([["journal", 4], ["topic", 3], ["plan", 2], ["index", 1]]);

function loadPolicy(policyPath = POLICY_PATH) { return JSON.parse(fs.readFileSync(policyPath, "utf8")); }
function tokenize(value) { return String(value || "").toLowerCase().split(/[^a-z0-9]+/).filter((term) => term.length > 1 && !STOP_WORDS.has(term)); }
function githubRefText(node) {
  return (node.githubRefs || []).flatMap((item) => [
    item.url,
    item.repository,
    `${item.repository}#${item.number}`,
    `${item.repository} ${item.kind === "pull-request" ? "PR pull request" : "issue"} #${item.number}`,
  ]).join(" ");
}
function nodeHaystack(node) { return [node.label, node.id, ...(node.aliases || []), githubRefText(node)].join(" ").toLowerCase(); }
function scoreNode(node, query) {
  const normalized = normalizeGithubQuery(query).toLowerCase();
  if (!normalized) return 0;
  const haystack = nodeHaystack(node);
  if (node.id.toLowerCase() === normalized) return 1000;
  if (node.label.toLowerCase() === normalized) return 900;
  const tokens = tokenize(normalized);
  if (!tokens.length || !tokens.every((token) => haystack.includes(token))) return 0;
  return tokens.length * 20 + (haystack.includes(normalized) ? 100 : 0) + (node.label.toLowerCase().includes(normalized) ? 30 : 0) + (node.id.toLowerCase().includes(normalized) ? 20 : 0);
}

function formatGithubRef(item) { return `${item.repository} ${item.kind === "pull-request" ? "PR" : "issue"} #${item.number}`; }
function resolveEvidenceNode(graph, query) {
  const evidence = parseGithubQuery(query);
  if (!evidence) return null;
  const matchingRefs = graph.nodes.flatMap((node) => (node.githubRefs || [])
    .filter((item) => item.repository === evidence.repository && item.number === evidence.number && (!evidence.kind || item.kind === evidence.kind))
    .map((item) => ({ node, item })));
  const kinds = new Set(matchingRefs.map(({ item }) => item.kind));
  const matchedEvidence = evidence.kind ? evidence : kinds.size === 1 ? matchingRefs[0]?.item || evidence : evidence;
  const matches = [...new Map(matchingRefs.map(({ node }) => [node.id, node])).values()]
    .sort((a, b) => (EVIDENCE_TYPE_PRIORITY.get(b.type) || 0) - (EVIDENCE_TYPE_PRIORITY.get(a.type) || 0) || a.id.localeCompare(b.id));
  if (!matches.length) return { node: null, candidates: [], matchedEvidence, resolvedBy: "github-evidence" };
  if (!evidence.kind && kinds.size > 1) return { node: null, candidates: matches, matchedEvidence, resolvedBy: "github-evidence" };
  const priority = EVIDENCE_TYPE_PRIORITY.get(matches[0].type) || 0;
  const top = matches.filter((node) => (EVIDENCE_TYPE_PRIORITY.get(node.type) || 0) === priority);
  return { node: top.length === 1 ? top[0] : null, candidates: top, matchedEvidence, resolvedBy: "github-evidence" };
}

function edgeType(edge) { return edge.type || edge.relation; }
function policyProblems(policy, graph = null) {
  const problems = [];
  if (!policy || typeof policy !== "object") return ["policy must be an object"];
  if (!policy.edgeCosts || typeof policy.edgeCosts !== "object" || Array.isArray(policy.edgeCosts)) problems.push("edgeCosts must be an object");
  else for (const [type, cost] of Object.entries(policy.edgeCosts)) if (!Number.isFinite(cost) || cost <= 0) problems.push(`edge cost for ${type} must be positive`);
  if (!Number.isFinite(policy.hubPenalty) || policy.hubPenalty < 0) problems.push("hubPenalty must be non-negative");
  if (!Number.isFinite(policy.bytePenaltyPerKiB) || policy.bytePenaltyPerKiB < 0) problems.push("bytePenaltyPerKiB must be non-negative");
  if (!Array.isArray(policy.excludedIntermediateTypes)) problems.push("excludedIntermediateTypes must be an array");
  else if (policy.excludedIntermediateTypes.some((type) => typeof type !== "string" || !type)) problems.push("excludedIntermediateTypes must contain non-empty strings");
  for (const intent of REQUIRED_INTENTS) {
    const definition = policy.intents?.[intent];
    if (!definition) problems.push(`missing ${intent} intent`);
    else for (const field of ["preferredSourceTypes", "preferredTargetTypes"]) if (!Array.isArray(definition[field]) || !definition[field].length || definition[field].some((type) => typeof type !== "string" || !type)) problems.push(`${intent} ${field} must be a non-empty string array`);
  }
  if (graph) for (const type of new Set(graph.edges.map(edgeType))) if (!Number.isFinite(policy.edgeCosts?.[type])) problems.push(`missing edge cost for ${type}`);
  return problems;
}

function resolveNode(graph, query, preferredTypes = []) {
  const evidence = resolveEvidenceNode(graph, query);
  if (evidence) return evidence;
  const exact = graph.nodes.find((node) => node.id === query);
  if (exact) return { node: exact, candidates: [exact], resolvedBy: "node-id" };
  const preference = new Map(preferredTypes.map((type, index) => [type, preferredTypes.length - index]));
  const scored = graph.nodes.map((node) => ({ node, score: scoreNode(node, query) })).filter((entry) => entry.score > 0)
    .sort((a, b) => b.score - a.score || a.node.id.localeCompare(b.node.id));
  if (!scored.length) return { node: null, candidates: [], resolvedBy: "text" };
  const textScore = scored[0].score;
  const topText = scored.filter((entry) => entry.score === textScore);
  const preferred = Math.max(...topText.map((entry) => preference.get(entry.node.type) || 0));
  const candidates = topText.filter((entry) => (preference.get(entry.node.type) || 0) === preferred).map((entry) => entry.node).sort((a, b) => a.id.localeCompare(b.id));
  return { node: candidates.length === 1 ? candidates[0] : null, candidates, resolvedBy: "text" };
}

function edgeKey(edge) { return `${edge.source}\u0000${edge.target}\u0000${edgeType(edge)}`; }
function adjacency(graph) {
  const result = new Map(graph.nodes.map((node) => [node.id, []]));
  for (const edge of graph.edges) {
    result.get(edge.source)?.push({ node: edge.target, edge, direction: "forward" });
    result.get(edge.target)?.push({ node: edge.source, edge, direction: "reverse" });
  }
  for (const steps of result.values()) steps.sort((a, b) => edgeKey(a.edge).localeCompare(edgeKey(b.edge)) || a.node.localeCompare(b.node));
  return result;
}
function edgeCost(edge, destination, byId, policy) {
  const node = byId.get(destination);
  return policy.edgeCosts[edgeType(edge)]
    + policy.hubPenalty * Math.log2((node?.degree || 0) + 1)
    + policy.bytePenaltyPerKiB * ((node?.bytes || 0) / 1024);
}
function shortestPaths(graph, sourceId, policy, targetId = null) {
  const errors = policyProblems(policy, graph);
  if (errors.length) throw new Error(`Invalid routing policy: ${errors.join("; ")}`);
  const byId = new Map(graph.nodes.map((node) => [node.id, node]));
  const links = adjacency(graph);
  const excluded = new Set(policy.excludedIntermediateTypes);
  const distances = new Map([[sourceId, 0]]);
  const previous = new Map();
  const pending = new Set([sourceId]);
  while (pending.size) {
    let current;
    for (const id of pending) if (!current || distances.get(id) < distances.get(current) || (distances.get(id) === distances.get(current) && id < current)) current = id;
    pending.delete(current);
    for (const step of links.get(current) || []) {
      if (step.node !== sourceId && step.node !== targetId && excluded.has(byId.get(step.node)?.type)) continue;
      const next = distances.get(current) + edgeCost(step.edge, step.node, byId, policy);
      const known = distances.get(step.node);
      const candidateKey = edgeKey(step.edge);
      const previousKey = previous.get(step.node) ? edgeKey(previous.get(step.node).edge) : "";
      if (known == null || next < known || (next === known && candidateKey < previousKey)) {
        distances.set(step.node, next);
        previous.set(step.node, { from: current, edge: step.edge, direction: step.direction });
        pending.add(step.node);
      }
    }
  }
  return { distances, previous };
}
function reconstructRoute(sourceId, targetId, previous) {
  if (sourceId === targetId) return { nodes: [sourceId], steps: [] };
  const nodes = [targetId];
  const steps = [];
  let current = targetId;
  while (current !== sourceId) {
    const item = previous.get(current);
    if (!item) return null;
    steps.unshift({ ...item, to: current });
    current = item.from;
    nodes.unshift(current);
  }
  return { nodes, steps };
}
function targetForIntent(graph, source, intentPolicy, distances) {
  if (intentPolicy.allowSourceAsTarget && intentPolicy.preferredTargetTypes.includes(source.type)) return source;
  const order = new Map(intentPolicy.preferredTargetTypes.map((type, index) => [type, index]));
  return graph.nodes.filter((node) => node.id !== source.id && order.has(node.type) && distances.has(node.id)).sort((a, b) => distances.get(a.id) - distances.get(b.id) || order.get(a.type) - order.get(b.type) || a.id.localeCompare(b.id))[0] || null;
}
function route(graph, { intent, query, from, to, maxBytes = null, policy = loadPolicy() }) {
  const errors = policyProblems(policy, graph);
  if (errors.length) return { status: "invalid-policy", intent, candidates: [], problems: errors };
  const intentPolicy = policy.intents[intent];
  if (!intentPolicy) return { status: "invalid-intent", intent, candidates: [] };
  const resolvedSource = resolveNode(graph, from || query, intentPolicy.preferredSourceTypes);
  if (!resolvedSource.node) return { status: resolvedSource.candidates.length ? "ambiguous-source" : "missing-source", intent, candidates: resolvedSource.candidates };
  const source = resolvedSource.node;
  let target = null;
  if (to) {
    const resolvedTarget = resolveNode(graph, to, intentPolicy.preferredTargetTypes);
    if (!resolvedTarget.node) return { status: resolvedTarget.candidates.length ? "ambiguous-target" : "missing-target", intent, source, candidates: resolvedTarget.candidates };
    target = resolvedTarget.node;
  }
  const paths = shortestPaths(graph, source.id, policy, target?.id || null);
  if (!target) target = targetForIntent(graph, source, intentPolicy, paths.distances);
  if (!target) return { status: "no-route", intent, source, candidates: [] };
  const reconstructed = reconstructRoute(source.id, target.id, paths.previous);
  if (!reconstructed) return { status: "no-route", intent, source, target, candidates: [] };
  const byId = new Map(graph.nodes.map((node) => [node.id, node]));
  const itinerary = reconstructed.nodes.map((id, index) => {
    const node = byId.get(id);
    const step = reconstructed.steps[index - 1];
    const relation = index === 0 ? resolvedSource.resolvedBy === "github-evidence" ? "evidence citation" : "query match" : `${step.direction === "forward" ? "→" : "←"} ${edgeType(step.edge)}`;
    let authority = `route step from ${step?.from || id}`;
    if (reconstructed.nodes.length === 1) authority = `source and target: ${id}`;
    else if (index === 0) authority = resolvedSource.resolvedBy === "github-evidence" ? `source: ${id}; cites ${formatGithubRef(resolvedSource.matchedEvidence)}` : `source: ${id}`;
    else if (index === reconstructed.nodes.length - 1) authority = `target: ${id}`;
    return { id, label: node.label, type: node.type, authority, bytes: node.bytes || 0, relation };
  });
  const totalBytes = itinerary.reduce((sum, item) => sum + item.bytes, 0);
  return { status: "ok", intent, source, target, cost: Number((paths.distances.get(target.id) || 0).toFixed(3)), matchedEvidence: resolvedSource.matchedEvidence || null, routeAuthority: `${source.id} → ${target.id}`, totalBytes, maxBytes, overBudget: Number.isFinite(maxBytes) && totalBytes > maxBytes, candidates: [], itinerary, steps: reconstructed.steps };
}

function formatBytes(value) { return value < 1024 ? `${value} B` : `${(value / 1024).toFixed(1)} KiB`; }
function formatRoute(result) {
  if (result.status !== "ok") {
    const lines = [`Route unavailable: ${result.status}.`];
    for (const problem of result.problems || []) lines.push(`- ${problem}`);
    for (const node of result.candidates || []) lines.push(`- ${node.id}`);
    return `${lines.join("\n")}\n`;
  }
  const budget = result.overBudget ? ` · exceeds ${formatBytes(result.maxBytes)}` : "";
  const lines = [`Route ${result.intent} · cost ${result.cost} · ${result.itinerary.length} file(s) · ${formatBytes(result.totalBytes)}${budget}`];
  lines.push(`Authority: ${result.routeAuthority}`);
  result.itinerary.forEach((item, index) => lines.push(`${index + 1}. ${item.id} — ${item.relation} — ${item.authority} — ${formatBytes(item.bytes)}`));
  lines.push(`Total bytes: ${formatBytes(result.totalBytes)}`);
  return `${lines.join("\n")}\n`;
}

module.exports = { POLICY_PATH, REQUIRED_INTENTS, loadPolicy, policyProblems, tokenize, githubRefText, nodeHaystack, scoreNode, resolveEvidenceNode, resolveNode, shortestPaths, reconstructRoute, route, formatRoute, formatBytes, edgeKey, edgeType };
