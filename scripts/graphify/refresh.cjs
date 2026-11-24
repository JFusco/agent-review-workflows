'use strict';

const { execFileSync } = require('node:child_process');
const { appendFileSync, readFileSync } = require('node:fs');
const { changedPaths, isMapInput, mapOnly, manifest } = require('./map-files.cjs');

function refreshNeeded(source, head, git = execFileSync) {
  if (source === head) return false;
  if (!/^[a-f0-9]{40}$/.test(source || '')) return true;
  try {
    git('git', ['merge-base', '--is-ancestor', source, head], { stdio: 'ignore' });
  } catch (error) {
    if (error.status === 1 || error.status === 128) return true;
    throw error;
  }
  return changedPaths(source + '..' + head, git).some(isMapInput);
}

function mappedCommit() {
  return JSON.parse(readFileSync('graphify-out/graph.json', 'utf8')).built_at_commit;
}

function refresh(head) {
  if (!refreshNeeded(mappedCommit(), head)) {
    console.log('The tracked Graphify map covers the current source.');
    return false;
  }

  execFileSync('graphify', ['update', '.', '--force'], { stdio: 'inherit' });
  const paths = changedPaths('HEAD');
  if (paths.every(file => file === manifest)) {
    console.log('Graphify found no topology or artifact changes.');
    return false;
  }
  if (!mapOnly(paths) || mappedCommit() !== head) {
    throw new Error('Graphify output must be confined to tracked map files and identify the checked-out revision.');
  }
  return true;
}

if (require.main === module) {
  const head = execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim();
  const checking = process.argv[2] === '--check';
  const result = checking ? refreshNeeded(mappedCommit(), head) : refresh(head);
  const output = (checking ? 'needed=' : 'changed=') + result + '\n';
  if (process.env.GITHUB_OUTPUT) appendFileSync(process.env.GITHUB_OUTPUT, output);
  else process.stdout.write(output);
}

module.exports = { refreshNeeded };
