"use strict";

(function () {
  const TYPE_COLORS = {
    index: "#7a8296",
    journal: "#5bd0d0",
    topic: "#8fd14f",
    plan: "#b0b6c4",
  };
  const TYPE_LABELS = {
    index: "Wiki index",
    journal: "Wiki journal",
    topic: "Wiki topic",
    plan: "Wiki plan",
  };
  const EDGE_COLORS = {
    link: "rgba(150,156,170,0.22)",
    topic: "rgba(143,209,79,0.4)",
    plan: "rgba(91,208,208,0.45)",
  };
  const DIM_NODE = "rgba(120,126,140,0.16)";
  const DIM_EDGE = "rgba(120,126,140,0.05)";

  const state = {
    graph: null,
    model: null,
    renderer: null,
    raw: new Map(),
    adjacency: new Map(),
    relationships: new Map(),
    counts: new Map(),
    hiddenTypes: new Set(),
    visible: new Set(),
    matched: null,
    focus: null,
    focusSet: null,
    query: "",
    policy: null,
    route: null,
    routeNodes: null,
    routeEdges: null,
  };

  const $ = (selector) => document.querySelector(selector);

  async function init() {
    try {
      const response = await fetch("../data/graph.json", { cache: "no-store" });
      if (!response.ok) throw new Error(`graph load failed: ${response.status}`);
      state.graph = await response.json();
      if (!Array.isArray(state.graph.nodes) || !Array.isArray(state.graph.edges)) throw new Error("graph data is invalid");
      if (state.graph.nodes.some((node) => !node.id.startsWith("wiki/"))) throw new Error("graph contains non-wiki nodes");
      const policyResponse = await fetch("../routing-policy.json", { cache: "no-store" });
      if (!policyResponse.ok) throw new Error(`routing policy load failed: ${policyResponse.status}`);
      state.policy = await policyResponse.json();
      buildIndexes();
      buildModel();
      buildRenderer();
      buildLegend();
      populateRouteSelects();
      wireControls();
      applyView();
      $("#stats").textContent = `${state.graph.nodes.length} nodes · ${state.graph.edges.length} edges`;
    } catch (error) {
      $("#stats").textContent = `Could not load the wiki graph: ${error.message}`;
      console.error(error);
    }
  }

  function buildIndexes() {
    for (const node of state.graph.nodes) {
      state.raw.set(node.id, node);
      state.adjacency.set(node.id, new Set());
      state.relationships.set(node.id, new Map());
      state.counts.set(node.type, (state.counts.get(node.type) || 0) + 1);
      state.visible.add(node.id);
    }
    for (const edge of state.graph.edges) {
      if (!state.raw.has(edge.source) || !state.raw.has(edge.target)) continue;
      state.adjacency.get(edge.source).add(edge.target);
      state.adjacency.get(edge.target).add(edge.source);
      addRelationship(edge.source, edge.target, edge.relation);
      addRelationship(edge.target, edge.source, edge.relation);
    }
  }

  function addRelationship(source, target, relation) {
    const relations = state.relationships.get(source);
    if (!relations.has(target)) relations.set(target, new Set());
    relations.get(target).add(relation);
  }

  function nodeSize(degree) {
    return 3 + Math.sqrt(degree) * 1.7;
  }

  function githubRefText(node) {
    return (node.githubRefs || []).flatMap((item) => [
      item.url,
      item.repository,
      `${item.repository}#${item.number}`,
      `${item.repository} ${item.kind === "pull-request" ? "PR pull request" : "issue"} #${item.number}`,
    ]).join(" ");
  }

  function nodeSearchKey(node) {
    return `${node.label} ${node.id} ${(node.aliases || []).join(" ")} ${githubRefText(node)}`.toLowerCase();
  }

  function buildModel() {
    const graph = new graphology.MultiGraph();
    for (const node of state.graph.nodes) {
      graph.addNode(node.id, {
        label: node.label,
        size: nodeSize(0),
        color: TYPE_COLORS[node.type] || "#888",
        nodeType: node.type,
        searchKey: nodeSearchKey(node),
        x: 0,
        y: 0,
      });
    }
    for (const edge of state.graph.edges) {
      if (!graph.hasNode(edge.source) || !graph.hasNode(edge.target)) continue;
      graph.addEdgeWithKey(edge.id, edge.source, edge.target, {
        edgeType: edge.relation,
        size: edge.relation === "link" ? 0.6 : 0.8,
        color: EDGE_COLORS[edge.relation] || DIM_EDGE,
        routeKey: window.WikiRouting.edgeKey(edge),
      });
    }
    graph.forEachNode((node) => graph.setNodeAttribute(node, "size", nodeSize(graph.degree(node))));

    if (graph.order > 1) {
      graphologyLibrary.layout.circular.assign(graph);
      const settings = graphologyLibrary.layoutForceAtlas2.inferSettings(graph);
      graphologyLibrary.layoutForceAtlas2.assign(graph, { iterations: 300, settings });
    }
    state.model = graph;
  }

  function buildRenderer() {
    state.renderer = new Sigma(state.model, $("#graph"), {
      labelColor: { color: "#c9cede" },
      labelSize: 12,
      labelWeight: "500",
      labelDensity: 0.5,
      labelGridCellSize: 70,
      labelRenderedSizeThreshold: 7,
      defaultEdgeType: "line",
      zIndex: true,
      nodeReducer,
      edgeReducer,
    });
    state.renderer.on("clickNode", ({ node }) => selectNode(node));
    state.renderer.on("clickStage", clearFocus);
  }

  function nodeReducer(node, data) {
    if (state.routeNodes?.has(node)) return { ...data, size: data.size + 2, zIndex: 2 };
    if (!state.visible.has(node)) return { ...data, hidden: true };
    if (state.routeNodes && !state.routeNodes.has(node)) return { ...data, color: DIM_NODE, label: "", zIndex: 0 };
    const active = (!state.matched || state.matched.has(node)) && (!state.focusSet || state.focusSet.has(node));
    return active ? { ...data, zIndex: 1 } : { ...data, color: DIM_NODE, label: "", zIndex: 0 };
  }

  function edgeReducer(edge, data) {
    const [source, target] = state.model.extremities(edge);
    if (state.routeEdges?.has(data.routeKey)) return { ...data, size: 2.5, color: "rgba(255,196,80,0.95)", zIndex: 2 };
    if (!state.visible.has(source) || !state.visible.has(target)) return { ...data, hidden: true };
    if (state.routeEdges) return { ...data, hidden: true };
    const inFocus = !state.focusSet || state.focusSet.has(source) || state.focusSet.has(target);
    const inSearch = !state.matched || state.matched.has(source) || state.matched.has(target);
    return inFocus && inSearch ? data : { ...data, color: DIM_EDGE, zIndex: 0 };
  }

  function applyView() {
    state.visible = new Set();
    for (const node of state.graph.nodes) if (!state.hiddenTypes.has(node.type)) state.visible.add(node.id);

    if (state.query) {
      state.matched = new Set();
      for (const node of state.graph.nodes) {
        if (nodeSearchKey(node).includes(state.query)) state.matched.add(node.id);
      }
    } else {
      state.matched = null;
    }

    const neighbors = state.adjacency.get(state.focus) || [];
    state.focusSet = state.focus ? new Set([state.focus, ...neighbors]) : null;
    state.renderer.refresh();
  }

  function buildLegend() {
    const legend = $("#legend");
    legend.replaceChildren();
    for (const type of Object.keys(TYPE_LABELS)) {
      const count = state.counts.get(type) || 0;
      if (!count) continue;
      const item = document.createElement("div");
      item.className = "legend-item";
      item.dataset.type = type;
      item.tabIndex = 0;
      item.setAttribute("role", "button");
      item.setAttribute("aria-pressed", "true");

      const swatch = document.createElement("span");
      swatch.className = "swatch";
      swatch.style.background = TYPE_COLORS[type];
      const label = document.createElement("span");
      label.textContent = TYPE_LABELS[type];
      const countNode = document.createElement("span");
      countNode.className = "count";
      countNode.textContent = String(count);
      item.append(swatch, label, countNode);

      item.addEventListener("click", () => toggleType(type, item));
      item.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        toggleType(type, item);
      });
      legend.appendChild(item);
    }
  }

  function toggleType(type, item) {
    const hidden = !state.hiddenTypes.has(type);
    if (hidden) state.hiddenTypes.add(type);
    else state.hiddenTypes.delete(type);
    item.classList.toggle("off", hidden);
    item.setAttribute("aria-pressed", String(!hidden));
    applyView();
  }

  function populateRouteSelects() {
    const nodes = [...state.graph.nodes].sort((a, b) => a.label.localeCompare(b.label) || a.id.localeCompare(b.id));
    for (const selector of ["#route-from", "#route-to"]) {
      const select = $(selector);
      const prompt = document.createElement("option");
      prompt.value = "";
      prompt.textContent = selector === "#route-from" ? "Source…" : "Target…";
      select.replaceChildren(prompt);
      for (const node of nodes) {
        const option = document.createElement("option");
        option.value = node.id;
        option.textContent = `${node.label} — ${node.id}`;
        select.appendChild(option);
      }
    }
  }

  function formatBytes(bytes) { return bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KiB`; }

  function showRoute() {
    const source = $("#route-from").value;
    const target = $("#route-to").value;
    if (!source || !target) { $("#route-status").textContent = "Choose a source and target."; return; }
    const route = window.WikiRouting.shortestPath(state.graph, source, target, state.policy);
    if (!route) { clearRoute("No permitted route found."); return; }
    state.route = route;
    state.routeNodes = new Set(route.nodes);
    state.routeEdges = new Set(route.steps.map((step) => window.WikiRouting.edgeKey(step.edge)));
    $("#route-status").textContent = `Authority: ${route.routeAuthority} · ${route.nodes.length} file(s) · Total bytes: ${formatBytes(route.totalBytes)} · cost ${route.cost}`;
    renderRoutePanel();
    applyView();
  }

  function renderRoutePanel() {
    $("#p-label").textContent = "Shortest route";
    $("#node-panel").classList.add("hidden");
    const list = $("#p-route");
    list.replaceChildren();
    state.route.itinerary.forEach((routeItem) => {
      const id = routeItem.id;
      const node = state.raw.get(id);
      const item = document.createElement("li");
      item.tabIndex = 0;
      item.textContent = `${node.label} — ${routeItem.relation} — ${routeItem.authority} · ${formatBytes(routeItem.bytes)}`;
      item.addEventListener("click", () => selectNode(id));
      item.addEventListener("keydown", (event) => { if (event.key === "Enter" || event.key === " ") selectNode(id); });
      list.appendChild(item);
    });
    $("#route-panel").classList.remove("hidden");
    $("#panel").classList.remove("hidden");
  }

  function clearRoute(message = "") {
    state.route = null;
    state.routeNodes = null;
    state.routeEdges = null;
    $("#route-status").textContent = message;
    $("#route-panel").classList.add("hidden");
    applyView();
  }

  function wireControls() {
    $("#search").addEventListener("input", (event) => {
      state.query = window.WikiRouting.normalizeGithubQuery(event.target.value);
      applyView();
    });
    $("#reset").addEventListener("click", resetView);
    $("#show-route").addEventListener("click", showRoute);
    $("#toggle-all").addEventListener("click", () => {
      const items = [...document.querySelectorAll(".legend-item")];
      const hide = items.some((item) => !state.hiddenTypes.has(item.dataset.type));
      for (const item of items) {
        const type = item.dataset.type;
        if (hide) state.hiddenTypes.add(type);
        else state.hiddenTypes.delete(type);
        item.classList.toggle("off", hide);
        item.setAttribute("aria-pressed", String(!hide));
      }
      applyView();
    });
    $("#panel-close").addEventListener("click", clearFocus);
  }

  function resetView() {
    state.query = "";
    $("#search").value = "";
    state.hiddenTypes.clear();
    for (const item of document.querySelectorAll(".legend-item")) {
      item.classList.remove("off");
      item.setAttribute("aria-pressed", "true");
    }
    state.focus = null;
    state.route = null;
    state.routeNodes = null;
    state.routeEdges = null;
    $("#route-from").value = "";
    $("#route-to").value = "";
    $("#route-status").textContent = "";
    $("#panel").classList.add("hidden");
    applyView();
    state.renderer.getCamera().animatedReset();
  }

  function selectNode(id) {
    if (!state.raw.has(id)) return;
    state.focus = id;
    applyView();
    renderPanel(id);
    state.renderer.getCamera().animate(state.renderer.getNodeDisplayData(id), { duration: 500 });
  }

  function clearFocus() {
    state.focus = null;
    $("#panel").classList.add("hidden");
    applyView();
  }

  function addMetaRow(label, value, code = false) {
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");
    if (code) {
      const codeNode = document.createElement("code");
      codeNode.textContent = value;
      detail.appendChild(codeNode);
    } else {
      detail.textContent = value;
    }
    $("#p-meta").append(term, detail);
  }

  function renderPanel(id) {
    const node = state.raw.get(id);
    $("#p-label").textContent = node.label;
    $("#route-panel").classList.add("hidden");
    $("#node-panel").classList.remove("hidden");
    const typeBadge = $("#p-type");
    typeBadge.textContent = TYPE_LABELS[node.type] || node.type;
    typeBadge.style.background = TYPE_COLORS[node.type] || "#888";
    typeBadge.style.color = "#14161b";
    typeBadge.style.borderColor = "transparent";

    $("#p-meta").replaceChildren();
    addMetaRow("Path", node.id, true);
    addMetaRow("Connections", String(state.adjacency.get(id).size));
    addMetaRow("Size", formatBytes(node.bytes || 0));
    for (const ref of node.githubRefs || []) addMetaLink(ref.kind === "pull-request" ? "Pull request" : "Issue", `${ref.repository}#${ref.number}`, ref.url);

    const neighbors = [...state.adjacency.get(id)]
      .map((neighborId) => state.raw.get(neighborId))
      .filter(Boolean)
      .sort((a, b) => state.adjacency.get(b.id).size - state.adjacency.get(a.id).size || a.label.localeCompare(b.label));
    const list = $("#p-neighbors");
    list.replaceChildren();
    for (const neighbor of neighbors) {
      const item = document.createElement("li");
      item.tabIndex = 0;
      const swatch = document.createElement("span");
      swatch.className = "swatch";
      swatch.style.background = TYPE_COLORS[neighbor.type] || "#888";
      const label = document.createElement("span");
      label.textContent = neighbor.label;
      const relation = document.createElement("span");
      relation.className = "rel";
      relation.textContent = [...state.relationships.get(id).get(neighbor.id)].sort().join(", ");
      item.append(swatch, label, relation);
      item.addEventListener("click", () => selectNode(neighbor.id));
      item.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        selectNode(neighbor.id);
      });
      list.appendChild(item);
    }
    $("#panel").classList.remove("hidden");
  }

  function addMetaLink(label, value, href) {
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");
    const link = document.createElement("a");
    link.href = href;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = value;
    detail.appendChild(link);
    $("#p-meta").append(term, detail);
  }

  window.WikiGraph = { select: selectNode, reset: resetView, state, nodeSearchKey };
  init();
})();
