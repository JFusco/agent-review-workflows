#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const {
  repoRoot,
  walk,
  slash,
  digest,
  hasSymlinkComponent,
} = require('./lib/common.cjs');
const {
  splitFrontmatter,
  scalar,
  list,
  frontmatterProblems,
} = require('./lib/frontmatter.cjs');
const { key: githubRefKey } = require('./lib/github-refs.cjs');
const { loadPolicy, policyProblems } = require('./routing.cjs');

function main() {
  const repoAt = process.argv.indexOf('--repo');
  const root = repoRoot(repoAt >= 0 ? process.argv[repoAt + 1] : process.cwd());
  const errors = [];
  const ledgerFile = path.join(root, 'wiki', 'plans', 'INDEX.md');
  const ledger = fs.existsSync(ledgerFile)
    ? fs.readFileSync(ledgerFile, 'utf8')
    : '';
  if (ledger && !ledger.includes('<!-- wiki-plan-rows -->'))
    errors.push('wiki/plans/INDEX.md: missing wiki-plan-rows marker');
  const ledgerDigests = [
    ...ledger.matchAll(/<!--\s*plan:([a-f0-9]{64})\s*-->/gi),
  ].map(match => match[1].toLowerCase());
  const duplicateLedger = ledgerDigests.filter(
    (value, index) => ledgerDigests.indexOf(value) !== index,
  );
  if (duplicateLedger.length)
    errors.push(
      `duplicate plan ledger digests: ${[...new Set(duplicateLedger)].join(', ')}`,
    );
  const archiveDigests = new Set();
  for (const required of [
    'wiki/INDEX.md',
    'wiki/MECHANICS.md',
    'wiki/plans/INDEX.md',
    'scripts/wiki/graph/data/graph.json',
    'scripts/wiki/navigate.cjs',
    'scripts/wiki/routing.cjs',
    'scripts/wiki/routing-policy.json',
    'scripts/wiki/reconcile-merges.cjs',
    'scripts/wiki/graph/viewer/routing.js',
  ]) {
    if (!fs.existsSync(path.join(root, required)))
      errors.push(`missing ${required}`);
  }
  const syncWorkflow = path.join(root, '.github', 'workflows', 'wiki-sync.yml');
  if (fs.existsSync(syncWorkflow)) {
    const source = fs.readFileSync(syncWorkflow, 'utf8');
    if (
      !source.includes('scripts/wiki/reconcile-merges.cjs') ||
      !source.includes('pr_number:') ||
      !source.includes('since:') ||
      !source.includes('gh api --method PATCH')
    )
      errors.push(
        'Sync context wiki does not provide REST-based single and batch merge reconciliation',
      );
  }
  for (const file of walk(path.join(root, 'wiki'), item =>
    item.endsWith('.md'),
  )) {
    const parsed = splitFrontmatter(fs.readFileSync(file, 'utf8'));
    for (const problem of frontmatterProblems(parsed.raw)) {
      errors.push(`${slash(path.relative(root, file))}: ${problem}`);
    }
  }
  for (const file of walk(
    path.join(root, 'wiki', 'plans'),
    item => item.endsWith('.md') && path.basename(item) !== 'INDEX.md',
  )) {
    if (hasSymlinkComponent(root, file)) {
      errors.push(
        `${slash(path.relative(root, file))}: symbolic links are not allowed`,
      );
      continue;
    }
    const parsed = splitFrontmatter(fs.readFileSync(file, 'utf8'));
    const status = scalar(parsed.raw, 'status');
    const executed = scalar(parsed.raw, 'executed');
    const evidence = list(parsed.raw, 'evidence');
    const topics = list(parsed.raw, 'topics');
    const recordedDigest = scalar(parsed.raw, 'digest').toLowerCase();
    const computedDigest = digest(parsed.body.trim() + '\n');
    for (const key of [
      'status',
      'executed',
      'source_tool',
      'source',
      'topics',
      'digest',
    ])
      if (!new RegExp(`^${key}:`, 'm').test(parsed.raw))
        errors.push(`${slash(path.relative(root, file))}: missing ${key}`);
    if (!['implemented', 'partial'].includes(status))
      errors.push(
        `${slash(path.relative(root, file))}: archived bodies must be implemented or partial`,
      );
    if (executed !== 'true')
      errors.push(`${slash(path.relative(root, file))}: executed must be true`);
    if (!evidence.length)
      errors.push(
        `${slash(path.relative(root, file))}: implementation evidence is required`,
      );
    if (!topics.length)
      errors.push(
        `${slash(path.relative(root, file))}: at least one topic is required`,
      );
    if (
      !/^[a-f0-9]{64}$/.test(recordedDigest) ||
      recordedDigest !== computedDigest
    )
      errors.push(
        `${slash(path.relative(root, file))}: digest does not match the archived body`,
      );
    else {
      if (archiveDigests.has(recordedDigest))
        errors.push(
          `${slash(path.relative(root, file))}: duplicate archived digest`,
        );
      archiveDigests.add(recordedDigest);
      if (!ledgerDigests.includes(recordedDigest))
        errors.push(
          `${slash(path.relative(root, file))}: missing plan ledger row`,
        );
    }
    if (!scalar(parsed.raw, 'source_tool'))
      errors.push(
        `${slash(path.relative(root, file))}: source_tool must not be empty`,
      );
    if (!scalar(parsed.raw, 'source'))
      errors.push(
        `${slash(path.relative(root, file))}: source must not be empty`,
      );
  }
  if (fs.existsSync(path.join(root, 'scripts/wiki/graph/data/graph.json'))) {
    try {
      const graph = JSON.parse(
        fs.readFileSync(
          path.join(root, 'scripts/wiki/graph/data/graph.json'),
          'utf8',
        ),
      );
      if (graph.version !== 1 || graph.wikiRoot !== 'wiki')
        errors.push('graph schema/root metadata is not current');
      if (graph.nodes.some(node => !node.id.startsWith('wiki/')))
        errors.push('graph contains a node outside wiki/');
      for (const node of graph.nodes) {
        if (!Number.isInteger(node.bytes) || node.bytes < 0)
          errors.push(`${node.id}: byte metadata is invalid`);
        if (!Number.isInteger(node.degree) || node.degree < 0)
          errors.push(`${node.id}: degree metadata is invalid`);
        if (!Array.isArray(node.githubRefs))
          errors.push(`${node.id}: githubRefs metadata is missing`);
        else {
          const keys = node.githubRefs.map(githubRefKey);
          if (new Set(keys).size !== keys.length)
            errors.push(`${node.id}: duplicate GitHub evidence metadata`);
          for (const ref of node.githubRefs)
            if (
              !/^[a-z0-9_.-]+\/[a-z0-9_.-]+$/.test(ref.repository) ||
              !['pull-request', 'issue'].includes(ref.kind) ||
              !Number.isSafeInteger(ref.number) ||
              ref.number < 1 ||
              ref.url !==
                `https://github.com/${ref.repository}/${ref.kind === 'pull-request' ? 'pull' : 'issues'}/${ref.number}`
            )
              errors.push(`${node.id}: invalid repo-qualified GitHub evidence`);
        }
      }
      for (const problem of policyProblems(loadPolicy(), graph))
        errors.push(`routing policy: ${problem}`);
    } catch (error) {
      errors.push(`invalid graph JSON: ${error.message}`);
    }
  }
  const graph = spawnSync(
    process.execPath,
    [
      path.join(root, 'scripts/wiki/build-graph.cjs'),
      '--check',
      '--repo',
      root,
    ],
    { cwd: root, encoding: 'utf8' },
  );
  if (graph.status !== 0) errors.push((graph.stderr || graph.stdout).trim());
  if (errors.length) {
    for (const error of errors) console.error(`FAIL ${error}`);
    return 2;
  }
  console.log('PASS wiki integrity');
  return 0;
}

if (require.main === module) process.exit(main());
module.exports = { main };
