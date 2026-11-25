'use strict';

const { execFileSync } = require('node:child_process');

const manifest = 'graphify-out/manifest.json';
const files = new Set([
  manifest,
  'graphify-out/graph.json',
  'graphify-out/graph.html',
  'graphify-out/GRAPH_REPORT.md',
  'graphify-out/.graphify_analysis.json',
  'graphify-out/.graphify_labels.json',
  'graphify-out/.graphify_labels.json.sig',
]);

function changedPaths(range, run = execFileSync) {
  return run('git', ['diff', '--name-only', '--no-renames', '-z', range], { encoding: 'utf8' })
    .split('\0').filter(Boolean);
}

function isMapInput(file) {
  return ['.graphifyignore', '.gitignore'].includes(file) || (
    file.startsWith('scripts/')
    && !/\.(md|mdx|json|css)$/.test(file)
    && !file.includes('/viewer/vendor/')
  );
}

function mapOnly(paths) {
  return paths.some(file => file !== manifest) && paths.every(file => files.has(file));
}

module.exports = { changedPaths, isMapInput, mapOnly, manifest };
