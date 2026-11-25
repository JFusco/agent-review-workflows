'use strict';

const required = [
  ['Quality', 'quality (Python 3.11)'],
  ['Commit message lint', 'commitlint'],
  ['Wiki integrity', 'check'],
];

function mergeCheckState(checks) {
  const latest = new Map();
  for (const result of checks) {
    const check = result.context ? {
      name: result.context,
      status: result.state === 'PENDING' || result.state === 'EXPECTED' ? 'IN_PROGRESS' : 'COMPLETED',
      conclusion: result.state,
      startedAt: result.startedAt,
    } : result;
    const key = JSON.stringify([check.workflowName, check.name]);
    if (!latest.has(key) || (check.startedAt || '') >= (latest.get(key).startedAt || '')) {
      latest.set(key, check);
    }
  }
  const finished = check => check?.status === 'COMPLETED';
  const successful = check => check?.conclusion === 'SUCCESS';
  const requiredChecks = required.map(([workflow, name]) => latest.get(JSON.stringify([workflow, name])));
  if (requiredChecks.some(check => finished(check) && !successful(check))) return 'failed';
  const other = [...latest.values()].filter(check => !requiredChecks.includes(check));
  if (other.some(check => finished(check) && !['SUCCESS', 'SKIPPED', 'NEUTRAL'].includes(check.conclusion))) {
    return 'failed';
  }
  return requiredChecks.every(check => finished(check) && successful(check)) && other.every(finished)
    ? 'passed' : 'pending';
}

module.exports = { mergeCheckState };
