"use strict";

// Browser counterpart to scripts/wiki/routing.cjs. Both consume the same
// declarative policy and use identical edge, hub, byte, and tie-break costs.
window.WikiRouting = (() => {
  const edgeType = (edge) => edge.type || edge.relation;
  const edgeKey = (edge) => `${edge.source}\u0000${edge.target}\u0000${edgeType(edge)}`;
  function normalizeGithubQuery(value) {
    const source = String(value || "").trim().toLowerCase();
    const match = source.match(/^https?:\/\/(?:www\.)?github\.com\/([a-z0-9_.-]+)\/([a-z0-9_.-]+)\/(pull|issues)\/(\d+)(?:[?#].*)?$/i);
    if (!match) return source;
    const number = Number(match[4]);
    if (!Number.isSafeInteger(number) || number < 1) return source;
    return `https://github.com/${match[1].toLowerCase()}/${match[2].toLowerCase()}/${match[3].toLowerCase()}/${number}`;
  }
  function validPolicy(policy, graph = null) {
    const intrinsicallyValid = Boolean(policy && policy.edgeCosts && Object.values(policy.edgeCosts).every((value) => Number.isFinite(value) && value > 0)
      && Number.isFinite(policy.hubPenalty) && policy.hubPenalty >= 0
      && Number.isFinite(policy.bytePenaltyPerKiB) && policy.bytePenaltyPerKiB >= 0
      && Array.isArray(policy.excludedIntermediateTypes)
      && policy.excludedIntermediateTypes.every((type) => typeof type === "string" && type));
    if (!intrinsicallyValid) return false;
    return !graph || (graph.edges || []).every((edge) => {
      const cost = policy.edgeCosts[edgeType(edge)];
      return Number.isFinite(cost) && cost > 0;
    });
  }
  function shortestPath(graph, source, target, policy) {
    if (!validPolicy(policy, graph)) return null;
    const byId = new Map(graph.nodes.map((node) => [node.id, node]));
    const adjacency = new Map(graph.nodes.map((node) => [node.id, []]));
    for (const edge of graph.edges) {
      adjacency.get(edge.source)?.push({ to: edge.target, edge, direction: "forward" });
      adjacency.get(edge.target)?.push({ to: edge.source, edge, direction: "reverse" });
    }
    for (const steps of adjacency.values()) steps.sort((a, b) => edgeKey(a.edge).localeCompare(edgeKey(b.edge)) || a.to.localeCompare(b.to));
    const excluded = new Set(policy.excludedIntermediateTypes);
    const distances = new Map([[source, 0]]);
    const previous = new Map();
    const pending = new Set([source]);
    while (pending.size) {
      let current;
      for (const id of pending) if (!current || distances.get(id) < distances.get(current) || (distances.get(id) === distances.get(current) && id < current)) current = id;
      pending.delete(current);
      for (const step of adjacency.get(current) || []) {
        if (step.to !== target && step.to !== source && excluded.has(byId.get(step.to)?.type)) continue;
        const node = byId.get(step.to);
        const base = policy.edgeCosts[edgeType(step.edge)];
        const next = distances.get(current) + base + policy.hubPenalty * Math.log2((node?.degree || 0) + 1) + policy.bytePenaltyPerKiB * ((node?.bytes || 0) / 1024);
        const known = distances.get(step.to);
        const priorKey = previous.get(step.to) ? edgeKey(previous.get(step.to).edge) : "";
        if (known == null || next < known || (next === known && edgeKey(step.edge) < priorKey)) {
          distances.set(step.to, next);
          previous.set(step.to, { from: current, edge: step.edge, direction: step.direction });
          pending.add(step.to);
        }
      }
    }
    if (!distances.has(target)) return null;
    const nodes = [target];
    const steps = [];
    let current = target;
    while (current !== source) {
      const step = previous.get(current);
      if (!step) return null;
      steps.unshift({ ...step, to: current });
      current = step.from;
      nodes.unshift(current);
    }
    const itinerary = nodes.map((id, index) => {
      const step = steps[index - 1];
      const relation = index === 0 ? "query match" : `${step.direction === "forward" ? "→" : "←"} ${edgeType(step.edge)}`;
      let authority = `route step from ${step?.from || id}`;
      if (nodes.length === 1) authority = `source and target: ${id}`;
      else if (index === 0) authority = `source: ${id}`;
      else if (index === nodes.length - 1) authority = `target: ${id}`;
      return { id, relation, authority, bytes: byId.get(id)?.bytes || 0 };
    });
    return { nodes, steps, itinerary, routeAuthority: `${source} → ${target}`, cost: Number(distances.get(target).toFixed(3)), totalBytes: itinerary.reduce((sum, item) => sum + item.bytes, 0) };
  }
  return { shortestPath, edgeKey, edgeType, validPolicy, normalizeGithubQuery };
})();
