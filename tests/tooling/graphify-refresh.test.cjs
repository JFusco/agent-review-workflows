"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
const { refreshNeeded } = require("../../scripts/graphify/refresh.cjs");
const { isMapInput, mapOnly, manifest } = require("../../scripts/graphify/map-files.cjs");
const { branch, title, body, isRefreshPR } = require("../../scripts/graphify/refresh-pr.cjs");
const { mergeCheckState } = require("../../scripts/graphify/refresh-checks.cjs");
const { publish } = require("../../scripts/graphify/publish-refresh.cjs");

const source = "a".repeat(40);
const head = "b".repeat(40);
const generated = ["graphify-out/graph.json", "graphify-out/GRAPH_REPORT.md", manifest];

function check(workflowName, name, conclusion = "SUCCESS", startedAt = "2026-11-24T17:30:00Z") {
  return { workflowName, name, status: "COMPLETED", conclusion, startedAt };
}

function passingChecks() {
  return [
    check("Quality", "quality (Python 3.11)"),
    check("Commit message lint", "commitlint"),
    check("Wiki integrity", "check"),
  ];
}

function event() {
  const repository = { full_name: "JFusco/agent-review-workflows" };
  return {
    repository,
    pull_request: {
      user: { id: 486049, login: "JFusco" },
      base: { ref: "main", sha: source },
      head: { ref: branch, sha: head, repo: { ...repository } },
      title,
      body,
    },
  };
}

function publication({ checks = passingChecks(), prHead = head, advanced = false } = {}) {
  const snapshot = {
    state: "OPEN", headRefOid: prHead, headRefName: branch, baseRefName: "main",
    isCrossRepository: false, title, body, statusCheckRollup: checks,
  };
  const revisions = [source, head];
  const gitCalls = [];
  const ghCalls = [];
  let comparisons = 0;
  return {
    git(...args) {
      gitCalls.push(args);
      if (args[0] === "rev-parse") return revisions.shift();
      if (args[0] === "ls-remote") return source + "\trefs/heads/" + branch;
      return "";
    },
    gh(...args) {
      ghCalls.push(args);
      if (args[1] === "list") return '[{"number":12,"isCrossRepository":false}]';
      if (args[1] === "view") return JSON.stringify(snapshot);
      return "";
    },
    paths(range) {
      if (range === "HEAD") return generated;
      comparisons++;
      return advanced && comparisons === 2 ? ["scripts/review_cli.py"] : [];
    },
    wait: async () => {},
    gitCalls,
    ghCalls,
  };
}

test("freshness checks the mapped ancestor and limits inputs to tracked script scope", () => {
  const calls = [];
  const git = (_, args) => {
    calls.push(args);
    return "graphify-out/graph.json\0wiki/INDEX.md\0";
  };
  assert.equal(refreshNeeded(source, head, git), false);
  assert.deepEqual(calls[1], ["diff", "--name-only", "--no-renames", "-z", source + ".." + head]);
  for (const file of ["scripts/review_cli.py", "scripts/deleted.cjs", ".graphifyignore", ".gitignore"]) {
    assert.equal(refreshNeeded(source, head, () => file + "\0"), true);
  }
  for (const file of ["tests/test_review_cli.py", "scripts/wiki/graph/viewer/vendor/sigma.js", "scripts/wiki/graph/data/graph.json"]) {
    assert.equal(isMapInput(file), false);
  }
  assert.equal(refreshNeeded(undefined, head), true);
  assert.equal(refreshNeeded(source, head, () => { throw Object.assign(new Error("unreachable"), { status: 1 }); }), true);
});

test("only the canonical same-repo automation PR qualifies for the body exception", () => {
  assert.equal(isRefreshPR(event(), () => generated), true);
  const fork = event();
  fork.pull_request.head.repo.full_name = "other/agent-review-workflows";
  assert.equal(isRefreshPR(fork, () => generated), false);
  const otherAuthor = event();
  otherAuthor.pull_request.user.id = 123;
  assert.equal(isRefreshPR(otherAuthor, () => generated), false);
  assert.equal(isRefreshPR(event(), () => [...generated, "scripts/review_cli.py"]), false);
  assert.equal(mapOnly([manifest]), false);
  assert.equal(mapOnly([]), false);
});

test("waits for the repository's exact check set and uses the most recent attempt", () => {
  assert.equal(mergeCheckState([]), "pending");
  assert.equal(mergeCheckState(passingChecks().slice(0, 2)), "pending");
  assert.equal(mergeCheckState([
    check("Commit message lint", "commitlint", "CANCELLED", "2026-11-24T17:29:00Z"),
    ...passingChecks(),
  ]), "passed");
  assert.equal(mergeCheckState([...passingChecks(), check("Other", "unexpected", "FAILURE")]), "failed");
});

test("reuses the bot PR and merges only the CI-confirmed generated commit", async () => {
  const fixture = publication();
  await publish(fixture);
  assert.deepEqual(fixture.gitCalls.find(args => args[0] === "push"), [
    "push", "--force-with-lease=refs/heads/" + branch + ":" + source,
    "origin", "HEAD:refs/heads/" + branch,
  ]);
  assert.deepEqual(fixture.ghCalls.find(args => args[1] === "merge"),
    ["pr", "merge", "12", "--merge", "--match-head-commit", head]);
  assert.equal(fixture.ghCalls.some(args => args[1] === "create"), false);
});

test("leaves the generated PR unmerged if checks fail, the head changes, or source advances", async () => {
  for (const [fixture, error] of [
    [publication({ checks: [check("Quality", "quality (Python 3.11)", "FAILURE")] }), /checks did not pass/],
    [publication({ prHead: source }), /no longer matches/],
    [publication({ advanced: true }), /source advanced/],
  ]) {
    await assert.rejects(publish(fixture), error);
    assert.equal(fixture.ghCalls.some(args => args[1] === "merge"), false);
  }
});
