"use strict";

const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");
const { ROOT, environment, run, must, write, repository, fixture } = require("./support.cjs");

test("Husky activates locally and leaves disabled CI hooks untouched", (t) => {
  const root = repository(t);
  write(root, "package.json", JSON.stringify({ scripts: { prepare: "husky" } }));
  fs.symlinkSync(path.join(ROOT, "node_modules"), path.join(root, "node_modules"), "junction");
  must(root, "pnpm", ["run", "prepare"], { env: environment({ HUSKY: "0" }) });
  assert.equal(must(root, "git", ["config", "--get", "core.hooksPath"]).stdout.trim(), ".disabled-hooks");
  assert.equal(fs.existsSync(path.join(root, ".husky/_")), false);
  must(root, "pnpm", ["run", "prepare"]);
  assert.equal(must(root, "git", ["config", "--get", "core.hooksPath"]).stdout.trim(), ".husky/_");
});

test("staged fixes preserve unstaged content and lint errors block commits", (t) => {
  const root = fixture(t);
  const staged = '"use strict";\nif (!!process.env.QUALITY_TEST) module.exports = 1;\n';
  write(root, "sample.cjs", staged);
  must(root, "git", ["add", "sample.cjs"]);
  write(root, "sample.cjs", staged + "// Keep this unstaged.\n");
  must(root, "git", ["commit", "-m", "fix(test): Remove redundant boolean cast"]);
  assert.equal(must(root, "git", ["show", "HEAD:sample.cjs"]).stdout, '"use strict";\nif (process.env.QUALITY_TEST) module.exports = 1;\n');
  assert.equal(fs.readFileSync(path.join(root, "sample.cjs"), "utf8"), '"use strict";\nif (process.env.QUALITY_TEST) module.exports = 1;\n// Keep this unstaged.\n');
  const before = must(root, "git", ["rev-parse", "HEAD"]).stdout;
  write(root, "sample.cjs", "module.exports = undefinedVariable;\n");
  must(root, "git", ["add", "sample.cjs"]);
  const rejected = run(root, "git", ["commit", "-m", "fix(test): Reject undefined names"]);
  assert.notEqual(rejected.status, 0, rejected.stdout + rejected.stderr);
  assert.equal(must(root, "git", ["rev-parse", "HEAD"]).stdout, before);
});

test("Ruff fixes only the staged Python content", (t) => {
  const root = fixture(t);
  const python = must(ROOT, "node", ["scripts/python.cjs", "-c", "import sys; print(sys.executable)"]).stdout.trim();
  const local = path.join(root, ".venv/bin/python");
  fs.mkdirSync(path.dirname(local), { recursive: true });
  write(root, ".venv/bin/python", `#!/bin/sh\nexec '${python.replaceAll("'", "'\\''")}' "$@"\n`, 0o755);
  write(root, "sample.py", "value = 1\n");
  must(root, "git", ["add", "sample.py"]);
  must(root, "git", ["commit", "-m", "test(python): Seed Python fixture"]);
  const staged = "import os\nvalue = 2\n";
  write(root, "sample.py", staged);
  must(root, "git", ["add", "sample.py"]);
  write(root, "sample.py", staged + "# Keep this unstaged.\n");
  must(root, "git", ["commit", "-m", "test(python): Check staged fixes"]);
  assert.equal(must(root, "git", ["show", "HEAD:sample.py"]).stdout, "value = 2\n");
  assert.equal(fs.readFileSync(path.join(root, "sample.py"), "utf8"), "value = 2\n# Keep this unstaged.\n");
});

test("legacy hook failures block while wiki lifecycle failures stay advisory", (t) => {
  const root = fixture(t);
  write(root, ".git/hooks/pre-commit", "#!/bin/sh\nexit 23\n", 0o755);
  const rejected = run(root, "git", ["commit", "--allow-empty", "-m", "test(hooks): Check legacy failure"]);
  assert.notEqual(rejected.status, 0, rejected.stdout + rejected.stderr);
  assert.equal(fs.existsSync(path.join(root, ".git/wiki-called")), false);
  write(root, ".git/hooks/pre-commit", "#!/bin/sh\nprintf 'legacy\\n' >> .git/legacy-called\n", 0o755);
  const accepted = must(root, "git", ["commit", "--allow-empty", "-m", "test(hooks): Keep wiki advisory"], { env: environment({ QUALITY_TEST_WIKI_EXIT: "23" }) });
  assert.match(accepted.stdout + accepted.stderr, /wiki lifecycle failed; continuing/);
  assert.equal(fs.readFileSync(path.join(root, ".git/legacy-called"), "utf8"), "legacy\n");
  assert.equal(fs.readFileSync(path.join(root, ".git/wiki-called"), "utf8"), "wiki\n");
});

test("the real wiki hook skips output derived from unstaged wiki inputs", (t) => {
  const root = repository(t);
  write(root, "wiki/topic.md", "# Original topic\n");
  write(root, "scripts/wiki/graph/data/graph.json", "unchanged graph\n");
  must(root, "git", ["add", "."]);
  must(root, "git", ["commit", "-m", "docs(wiki): Seed wiki fixture"]);
  write(root, "wiki/topic.md", "# Staged topic\n");
  must(root, "git", ["add", "wiki/topic.md"]);
  write(root, "wiki/topic.md", "# Staged topic\nUnstaged text.\n");
  const before = must(root, "git", ["diff", "--cached"]).stdout;
  const result = must(root, process.execPath, [path.join(ROOT, "scripts/wiki/pre-commit.cjs")]);
  assert.match(result.stderr, /rebuild skipped to avoid staging output derived from uncommitted content/);
  assert.equal(must(root, "git", ["diff", "--cached"]).stdout, before);
  assert.equal(fs.readFileSync(path.join(root, "scripts/wiki/graph/data/graph.json"), "utf8"), "unchanged graph\n");
});

test("pre-push clears Git-local variables and propagates verification failure", (t) => {
  const root = fixture(t);
  const pkg = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
  pkg.scripts["verify:push"] = "node verify-push.cjs";
  write(root, "package.json", JSON.stringify(pkg));
  write(root, "verify-push.cjs", "const selected = Object.fromEntries(['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'].map(key => [key, process.env[key]])); require('node:fs').writeFileSync('.git/push-env.json', JSON.stringify(selected)); process.exit(19);\n");
  const result = run(root, "sh", [".husky/_/pre-push", "origin", "unused"], { env: environment({ GIT_DIR: path.join(root, ".git"), GIT_WORK_TREE: root, GIT_INDEX_FILE: path.join(root, ".git/index") }) });
  assert.equal(result.status, 19, result.stdout + result.stderr);
  const env = JSON.parse(fs.readFileSync(path.join(root, ".git/push-env.json"), "utf8"));
  for (const name of ["GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"]) assert.equal(env[name], undefined);
});
