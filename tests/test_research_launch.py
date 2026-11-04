"""Guarded researcher launches use controlled children and synthetic briefs only."""
import copy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_codex_launch as launch_fixtures
import test_plan_research as research_fixtures

r = research_fixtures.r


class ResearchLaunchTests(unittest.TestCase):
    setUp = research_fixtures.PlanResearchTests.setUp
    brief = research_fixtures.PlanResearchTests.brief
    command = launch_fixtures.CodexLaunchTests.command
    controlled_failure = launch_fixtures.CodexLaunchTests.controlled_failure

    def extracted(self, state, call_dir):
        self.state = state
        return self.brief(), 'fixture-research', {
            **r.agent_candidate(state, 'researcher'), 'observed': {'source': 'fixture'}}

    def assert_no_dispatch(self, *extra):
        before = (self.run / 'state.json').read_bytes()
        calls = list((self.run / 'calls').iterdir())
        with patch.object(r, 'execute_process') as execute, patch.object(r, 'perform_checks') as checks, \
                patch.object(r, 'finish_local') as finish:
            self.command('step', '--codex-research-only', *extra, failed=True)
        execute.assert_not_called()
        checks.assert_not_called()
        finish.assert_not_called()
        self.assertEqual((self.run / 'state.json').read_bytes(), before)
        self.assertEqual(list((self.run / 'calls').iterdir()), calls)

    def test_startup_recovery_preserves_receipts_and_accepts_one_brief(self):
        with self.controlled_failure() as execute:
            self.command('step', failed=True)
        execute.assert_called_once()
        failed = {p: p.read_bytes() for p in (self.run / 'calls/001-research').iterdir()}
        self.command('retry')
        with patch.object(r, 'execute_process') as execute, \
                patch.object(r, 'extract_response', side_effect=self.extracted), \
                patch.object(r, 'perform_checks') as checks, patch.object(r, 'finish_local') as finish:
            self.command('step', '--codex-research-only')
        execute.assert_called_once()
        checks.assert_not_called()
        finish.assert_not_called()
        argv, cwd, *_ = execute.call_args.args
        self.assertEqual(cwd, Path(self.state['research_access']['scratch']))
        for value in ('--ignore-user-config', 'gpt-6-astra', 'model_reasoning_effort="high"',
                      'approval_policy="never"', 'default_permissions="plan-research"',
                      'permissions.plan-research.extends=":read-only"',
                      'permissions.plan-research.network.enabled=false', 'web_search="live"',
                      'agents.enabled=false', 'features.multi_agent=false', 'features.multi_agent_v2=false'):
            self.assertIn(value, argv)
        self.assertNotIn('--resume', argv)
        saved = r.read_json(self.run / 'state.json')
        self.assertEqual((saved['stage'], saved['status'], saved['round']), ('review', 'ready', 0))
        self.assertEqual([entry['stage'] for entry in saved['ledger']], ['research'])
        self.assertEqual(saved['agent_profile'], self.state['agent_profile'])
        self.assertEqual(saved['fallback_history'], [])
        self.assertIsNotNone(r.accepted_research(saved))
        boundary = r.read_json(self.run / 'calls/002-research/launch-boundary.json')
        self.assertEqual(boundary['boundary'], 'codex-research-only')
        self.assertTrue(boundary['single_attempt'])
        for path, content in failed.items():
            self.assertEqual(path.read_bytes(), content)
        self.assert_no_dispatch()
        # Ordinary continuation, not the guarded launch, owns the independent reviewer.
        def review(state, call_dir):
            return {**{key: state[key] for key in ('run_id', 'stage', 'handoff_revision', 'target_fingerprint')},
                    'plan_protocol_version': 2, 'summary': 'Synthetic independent review.', 'new_findings': []}, \
                'fixture-review', {**r.agent_candidate(state, 'opus'), 'observed': {'source': 'fixture'}}
        with patch.object(r, 'execute_process') as execute, patch.object(r, 'assert_claude_auth'), \
                patch.object(r, 'extract_response', side_effect=review):
            self.command('step')
        execute.assert_called_once()
        self.assertEqual(r.read_json(self.run / 'state.json')['stage'], 'adjudicate')

    def test_rejects_nonready_and_other_plan_stages(self):
        for status, stage in [('blocked', 'research'), ('running', 'research'), ('complete', 'research'),
                              ('awaiting_coordinator', 'research'), ('ready', 'review'),
                              ('ready', 'adjudicate'), ('ready', 'recheck'), ('ready', 'finalize')]:
            with self.subTest(status=status, stage=stage):
                state = copy.deepcopy(self.state)
                state.update(status=status, stage=stage)
                r.save(self.run, state)
                self.assert_no_dispatch()

    def test_rejects_other_modes_legacy_contract_and_accepted_research(self):
        for mode in ('implementation', 'diff'):
            with self.subTest(mode=mode):
                args = copy.deepcopy(self.args)
                args.mode, args.plan, args.base, args.check = mode, None, 'HEAD', [f'{sys.executable} -c pass']
                run, state = r.initialize(args)
                with self.assertRaises(r.ReviewError):
                    r.guard_codex_research(run, state)
        for changes in ({'schema_version': 2}, {'research_contract_version': 0}, {'research': {'artifact': 'old'}}):
            with self.subTest(changes=changes):
                state = {**self.state, **changes}
                r.save(self.run, state)
                self.assert_no_dispatch()

    def test_rejects_external_coordination_and_combined_boundaries(self):
        for flag in ('--external-coordinator', '--codex-read-only', '--codex-repair-only', '--reviewer-only'):
            self.assert_no_dispatch(flag)

    def test_rejects_stale_source_or_draft(self):
        for path in (self.project / 'calculator.py', self.draft):
            with self.subTest(path=path):
                original = path.read_text()
                path.write_text(original + '\nChanged input.\n')
                self.assert_no_dispatch()
                path.write_text(original)

    def test_rejects_changed_missing_and_symlinked_permission_roots(self):
        for field, value in [('scratch', str(self.project)), ('brain_metadata', str(self.project)),
                             ('brain_root', str(self.project))]:
            state = copy.deepcopy(self.state)
            state['research_access'][field] = value
            r.save(self.run, state)
            self.assert_no_dispatch()
        r.save(self.run, self.state)
        scratch = Path(self.state['research_access']['scratch'])
        scratch.rmdir()
        self.assert_no_dispatch()
        scratch.symlink_to(self.project, target_is_directory=True)
        self.assert_no_dispatch()

    def test_rejects_invalid_frozen_researcher(self):
        state = copy.deepcopy(self.state)
        state['agent_profile']['researcher']['model'] = 'invalid model'
        r.save(self.run, state)
        self.assert_no_dispatch()

    def test_rejects_active_process_group(self):
        proc = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], start_new_session=True)
        try:
            locks = self.lock_root / f'agent-review-locks-{r.os.getuid()}'
            locks.mkdir(mode=0o700, exist_ok=True)
            (locks / (r.digest(str(self.project)) + '.lock')).write_text(r.dumps({'process_group': proc.pid}))
            self.assert_no_dispatch()
        finally:
            proc.terminate()
            proc.wait()

    def test_single_attempt_on_capacity_or_contract_failure(self):
        for error in (r.ProviderCallError('rate_limit'), r.ContractResponseError('invalid brief')):
            r.save(self.run, self.state)
            with patch.object(r, 'execute_process', side_effect=error) as execute, \
                    patch.object(r, 'request_correction') as correct, patch.object(r, 'select_fallback') as fallback:
                self.command('step', '--codex-research-only', failed=True)
            execute.assert_called_once()
            correct.assert_not_called()
            fallback.assert_not_called()
            self.assertEqual(r.read_json(self.run / 'state.json')['status'], 'blocked')

    def test_malformed_brief_is_not_accepted_or_retried(self):
        config = {**r.agent_candidate(self.state, 'researcher'), 'observed': {'source': 'fixture'}}
        with patch.object(r, 'execute_process') as execute, \
                patch.object(r, 'extract_response', return_value=({}, 'fixture-research', config)), \
                patch.object(r, 'request_correction') as correct, patch.object(r, 'select_fallback') as fallback:
            self.command('step', '--codex-research-only', failed=True)
        execute.assert_called_once()
        correct.assert_not_called()
        fallback.assert_not_called()
        saved = r.read_json(self.run / 'state.json')
        self.assertIsNone(saved['research'])
        self.assertEqual(saved['ledger'], [])
