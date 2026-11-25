'use strict';

const { changedPaths, mapOnly } = require('./map-files.cjs');

const branch = 'bot/graphify-refresh';
const title = 'chore(graphify): refresh shared code map';
const body = 'Automated Graphify refresh from merged review-workflows source. The graph report identifies the source revision.';

function isRefreshPR(event, paths = (base, head) => changedPaths(base + '...' + head)) {
  const pull = event?.pull_request;
  return Boolean(event?.repository?.full_name
    && pull?.base?.ref === 'main'
    && pull.head?.repo?.full_name === event.repository.full_name
    && pull.head.ref === branch
    && pull.user?.id === 486049
    && pull.user.login === 'JFusco'
    && pull.title === title
    && pull.body?.trim() === body
    && /^[a-f0-9]{40}$/.test(pull.base.sha)
    && /^[a-f0-9]{40}$/.test(pull.head.sha)
    && mapOnly(paths(pull.base.sha, pull.head.sha)));
}

if (require.main === module) {
  const { readFileSync } = require('node:fs');
  const event = JSON.parse(readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8'));
  if (isRefreshPR(event)) console.log('PASS canonical Graphify pull request body and scope');
  else process.exitCode = 1;
}

module.exports = { branch, title, body, isRefreshPR };
