#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const http = require("node:http");
const path = require("node:path");
const { repoRoot, ensureInside } = require("./lib/common.cjs");

const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
};

function resolveRequest(root, requestUrl) {
  try {
    const pathname = decodeURIComponent(new URL(requestUrl, "http://127.0.0.1").pathname);
    const requested = path.resolve(root, pathname === "/" ? "viewer/index.html" : pathname.slice(1));
    if (!ensureInside(root, requested) || !fs.existsSync(requested)) return null;
    const file = fs.realpathSync(requested);
    return ensureInside(root, file) && fs.statSync(file).isFile() ? file : null;
  } catch {
    return null;
  }
}

function createServer(root, policyFile = path.join(path.dirname(root), "routing-policy.json")) {
  return http.createServer((req, res) => {
    try {
      const pathname = new URL(req.url, "http://127.0.0.1").pathname;
      const file = pathname === "/routing-policy.json" && fs.existsSync(policyFile) ? policyFile : resolveRequest(root, req.url);
      if (!file) throw new Error("not found");
      res.writeHead(200, {
        "Content-Type": types[path.extname(file)] || "application/octet-stream",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      });
      fs.createReadStream(file).pipe(res);
    } catch {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8", "X-Content-Type-Options": "nosniff" });
      res.end("Not found");
    }
  });
}

function listen(root, requestedPort, allowFallback = true, serverFactory = () => createServer(root)) {
  return new Promise((resolve, reject) => {
    function attempt(port) {
      const server = serverFactory();
      server.once("error", (error) => {
        if (allowFallback && error.code === "EADDRINUSE" && port < 65535) {
          attempt(port + 1);
          return;
        }
        reject(error);
      });
      server.listen(port, "127.0.0.1", () => resolve({ server, port }));
    }
    attempt(requestedPort);
  });
}

async function main() {
  const root = fs.realpathSync(path.join(repoRoot(process.cwd()), "scripts", "wiki", "graph"));
  const configuredPort = process.env.GRAPH_PORT || process.env.WIKI_GRAPH_PORT;
  const port = Number(configuredPort || 4173);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error("GRAPH_PORT must be an integer from 1 to 65535");
  }
  const graphJson = path.join(root, "data", "graph.json");
  const result = await listen(root, port, !configuredPort);
  if (!fs.existsSync(graphJson)) {
    console.log("Note: data/graph.json not found — run `node scripts/wiki/build-graph.cjs` first.\n");
  }
  if (result.port !== port) console.log(`Port ${port} is in use; selected ${result.port}.`);
  console.log(`Knowledge graph viewer → http://127.0.0.1:${result.port}/`);
  console.log("Press Ctrl+C to stop.");
}

if (require.main === module) main().catch((error) => {
  console.error(`FAIL ${error.message}`);
  process.exitCode = 1;
});
module.exports = { resolveRequest, createServer, listen, main };
