'use strict';

const { execFileSync } = require('node:child_process');
const { setTimeout: delay } = require('node:timers/promises');
const { changedPaths, isMapInput, mapOnly } = require('./map-files.cjs');
const { branch, title, body } = require('./refresh-pr.cjs');
const { mergeCheckState } = require('./refresh-checks.cjs');

const git = (...args) => execFileSync('git', args, { encoding: 'utf8' }).trim();
const gh = (...args) => execFileSync('gh', args, { encoding: 'utf8' }).trim();

function verifyBase(source, git, paths) {
  git('fetch', '--no-tags', 'origin', 'main');
  if (paths(source + '..origin/main').some(isMapInput)) {
    throw new Error('Mapped source advanced while refreshing. The newer main run can refresh it.');
  }
}

async function publish({ git: runGit = git, gh: runGh = gh, paths: diff = changedPaths, wait = delay } = {}) {
  const source = runGit('rev-parse', 'HEAD');
  const paths = diff('HEAD');
  if (!mapOnly(paths)) throw new Error('Only tracked Graphify map changes can be published.');
  verifyBase(source, runGit, diff);

  runGit('add', '--', ...paths);
  runGit('-c', 'user.name=github-actions[bot]',
    '-c', 'user.email=41898282+github-actions[bot]@users.noreply.github.com',
    'commit', '-m', title);
  const head = runGit('rev-parse', 'HEAD');
  const ref = 'refs/heads/' + branch;
  const tip = runGit('ls-remote', '--heads', 'origin', ref).split(/\s+/)[0];
  runGit('push', '--force-with-lease=' + ref + ':' + tip, 'origin', 'HEAD:' + ref);

  const open = JSON.parse(runGh('pr', 'list', '--state', 'open', '--head', branch, '--base', 'main',
    '--json', 'number,isCrossRepository'));
  if (open.length > 1 || open.some(pr => pr.isCrossRepository)) {
    throw new Error('Expected at most one review-workflows Graphify branch pull request.');
  }
  const pr = open.length ? String(open[0].number) :
    runGh('pr', 'create', '--base', 'main', '--head', branch, '--title', title, '--body', body);
  console.log('Graphify pull request: ' + pr);

  for (let attempt = 0; attempt < 48; attempt++) {
    const snapshot = JSON.parse(runGh('pr', 'view', pr, '--json',
      'state,headRefOid,headRefName,baseRefName,isCrossRepository,title,body,statusCheckRollup'));
    if (snapshot.headRefOid !== head || snapshot.headRefName !== branch ||
        snapshot.baseRefName !== 'main' || snapshot.isCrossRepository ||
        snapshot.title !== title || snapshot.body.trim() !== body) {
      throw new Error('The Graphify pull request no longer matches the generated commit.');
    }
    if (snapshot.state === 'MERGED') return;
    if (snapshot.state !== 'OPEN') throw new Error('The Graphify pull request was closed.');
    const checks = mergeCheckState(snapshot.statusCheckRollup);
    if (checks === 'failed') throw new Error('Graphify pull request checks did not pass.');
    if (checks === 'passed') {
      verifyBase(source, runGit, diff);
      console.log(runGh('pr', 'merge', pr, '--merge', '--match-head-commit', head));
      return;
    }
    await wait(10_000);
  }
  throw new Error('Timed out waiting for Graphify pull request checks.');
}

if (require.main === module) {
  publish().catch(error => {
    console.error(error.message);
    process.exitCode = 1;
  });
}

module.exports = { publish };
