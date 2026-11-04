"""Public-command launch boundaries with controlled children, never provider calls."""
import copy
import io
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_review_cli as fixtures
from test_mechanics import MechanicsFixture

r = fixtures.r
STARTUP = 'Error: failed to initialize in-process app-server client: Operation not permitted (os error 1)'


class CodexLaunchTests(MechanicsFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        fixtures.ReviewTests.start_diff(self)
        self.use_passing_check()
        self.accept(self.response([]))

    def command(self, *args, failed=False):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['review_cli.py', *args[:1], str(self.run), *args[1:]]), \
                patch('sys.stdout', output), patch('sys.stderr', output):
            if failed:
                with self.assertRaises(SystemExit) as exc:
                    r.main()
                self.assertEqual(exc.exception.code, 2)
            else:
                r.main()
        return output.getvalue()

    def controlled_failure(self, message=STARTUP):
        execute = r.execute_process
        def child(argv, cwd, content, call_dir, timeout, require_success=True):
            return execute([sys.executable, '-c',
                            'import sys; sys.stdin.read(); print(' + repr(message) +
                            ', file=sys.stderr); sys.exit(1)'], cwd, content, call_dir, timeout)
        return patch.object(r, 'execute_process', side_effect=child)

    def test_startup_diagnostic_preserves_review_and_never_falls_back(self):
        before = copy.deepcopy(self.state)
        receipts = {p: p.read_bytes() for folder in ('checks', 'artifacts')
                    for p in (self.run/folder).rglob('*') if p.is_file()}
        with self.controlled_failure() as execute:
            output = self.command('step', failed=True)
        self.assertEqual(execute.call_count, 1)
        self.assertIn('Codex could not start in the current execution context at adjudicate', output)
        self.assertIn('no stage response accepted', output)
        after = r.read_json(self.run/'state.json')
        self.assertEqual((after['stage'], after['status']), ('adjudicate', 'blocked'))
        for key in ('ledger', 'agent_profile', 'agent_selections', 'fallback_history', 'checks',
                    'target_fingerprint', 'handoff_revision', 'sessions'):
            self.assertEqual(after[key], before[key])
        for path, content in receipts.items():
            self.assertEqual(path.read_bytes(), content)
        call = self.run/'calls/001-adjudicate'
        self.assertEqual((call/'stderr.log').read_text().strip(), STARTUP)
        self.assertEqual(r.read_json(call/'process.json')['exit_code'], 1)
        failed_receipts = {p: p.read_bytes() for p in call.rglob('*') if p.is_file()}
        self.command('retry')
        with self.controlled_failure() as execute:
            self.command('step', '--codex-read-only', failed=True)
        self.assertEqual(execute.call_count, 1)
        self.assertEqual(len(list((self.run/'calls').iterdir())), 2)
        for path, content in failed_receipts.items():
            self.assertEqual(path.read_bytes(), content)

    def test_diagnostic_is_exact_and_does_not_expose_arbitrary_stderr(self):
        with self.controlled_failure('private detail: unrelated failure'):
            output = self.command('step', failed=True)
        self.assertIn('Agent exited 1', output)
        self.assertNotIn('private detail', output)
        self.assertNotIn('Codex could not start', output)

    def test_exact_startup_precedes_capacity_matching(self):
        with self.controlled_failure('rate_limit\n' + STARTUP) as execute:
            self.command('step', failed=True)
        self.assertEqual(execute.call_count, 1)
        self.assertFalse(r.read_json(self.run/'state.json')['fallback_history'])

    def test_guard_rejects_nonready_and_claude_stages_without_mutation(self):
        for status, stage in [('blocked', 'adjudicate'), ('running', 'adjudicate'),
                              ('reported', 'adjudicate'), ('awaiting_coordinator', 'adjudicate'),
                              ('ready', 'review')]:
            with self.subTest(status=status, stage=stage):
                state = copy.deepcopy(self.state)
                state.update(status=status, stage=stage)
                r.save(self.run, state)
                before = (self.run/'state.json').read_bytes()
                with patch.object(r, 'execute_process') as execute, patch.object(r, 'perform_checks') as checks:
                    self.command('step', '--codex-read-only', failed=True)
                execute.assert_not_called()
                checks.assert_not_called()
                self.assertEqual((self.run/'state.json').read_bytes(), before)

    def test_guard_rejects_valid_writer_research_and_finalizer_states(self):
        for mode, stage in [('implementation', 'repair'), ('implementation', 'finalize'), ('plan', 'research')]:
            with self.subTest(mode=mode, stage=stage):
                args = copy.deepcopy(self.args)
                args.mode = mode
                if mode == 'plan':
                    draft = self.root/'draft.md'
                    draft.write_text('Review the calculator requirements without implementing them.')
                    args.plan, args.base, args.check = str(draft), None, []
                self.run, self.state = r.initialize(args)
                self.state['stage'] = stage
                r.require_current_protocol(self.state)
                r.save(self.run, self.state)
                before = (self.run/'state.json').read_bytes()
                with patch.object(r, 'execute_process') as execute, patch.object(r, 'perform_checks') as checks, \
                        patch.object(r, 'finish_local') as finish:
                    output = self.command('step', '--codex-read-only', failed=True)
                self.assertIn('Codex read-only step requires a ready Codex review, adjudicate, or recheck stage', output)
                execute.assert_not_called()
                checks.assert_not_called()
                finish.assert_not_called()
                self.assertEqual((self.run/'state.json').read_bytes(), before)

    def test_guard_rejects_missing_malformed_and_stale_checks(self):
        for checks in ([], None, [None], [{}], [{**self.state['checks'][0], 'exit_code': True}],
                       [{**self.state['checks'][0], 'target_fingerprint': 'stale'}]):
            with self.subTest(checks=checks):
                state = copy.deepcopy(self.state)
                state['checks'] = checks
                r.save(self.run, state)
                with patch.object(r, 'execute_process') as execute, patch.object(r, 'perform_checks') as perform:
                    self.command('step', '--codex-read-only', failed=True)
                execute.assert_not_called()
                perform.assert_not_called()

    def test_guard_rejects_external_and_combined_boundaries(self):
        for extra in ('--external-coordinator', '--reviewer-only'):
            with patch.object(r, 'execute_process') as execute:
                self.command('step', '--codex-read-only', extra, failed=True)
            execute.assert_not_called()

    def test_guard_rejects_stale_source(self):
        (self.project/'calculator.py').write_text('changed\n')
        with patch.object(r, 'execute_process') as execute:
            self.assertIn('changed', self.command('step', '--codex-read-only', failed=True).lower())
        execute.assert_not_called()

    def test_guard_rejects_active_owned_process(self):
        proc = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], start_new_session=True)
        try:
            locks = self.lock_root/f'agent-review-locks-{r.os.getuid()}'
            locks.mkdir(mode=0o700, exist_ok=True)
            (locks/(r.digest(str(self.project))+'.lock')).write_text(r.dumps({'process_group': proc.pid}))
            with patch.object(r, 'execute_process') as execute:
                self.assertIn('still active', self.command('step', '--codex-read-only', failed=True))
            execute.assert_not_called()
        finally:
            proc.terminate()
            proc.wait()

    def test_guard_never_retries_capacity_or_contract_failures(self):
        for error in (r.ProviderCallError('rate_limit'), r.ContractResponseError('invalid response')):
            r.save(self.run, self.state)
            with patch.object(r, 'execute_process', side_effect=error) as execute, \
                    patch.object(r, 'request_correction') as correct, patch.object(r, 'select_fallback') as fallback:
                self.command('step', '--codex-read-only', failed=True)
            self.assertEqual(execute.call_count, 1)
            correct.assert_not_called()
            fallback.assert_not_called()

    def test_guard_dispatches_selected_readonly_role_once_without_tail(self):
        def extract(state, call_dir):
            self.state = state
            return self.response([]), None, {'model': 'gpt-6-astra', 'effort': 'max', 'observed': {'source': 'fixture'}}
        with patch.object(r, 'execute_process') as execute, patch.object(r, 'extract_response', side_effect=extract), \
                patch.object(r, 'finish_local') as finish, patch.object(r, 'perform_checks') as checks:
            self.command('step', '--codex-read-only')
        self.assertEqual(execute.call_count, 1)
        argv = execute.call_args.args[0]
        for setting in ('sandbox_mode="read-only"', 'approval_policy="never"', 'agents.enabled=false',
                        'sandbox_workspace_write.network_access=false', 'sandbox_workspace_write.writable_roots=[]'):
            self.assertIn(setting, argv)
        self.assertEqual(argv[argv.index('--model')+1], 'gpt-6-astra')
        self.assertIn('model_reasoning_effort="max"', argv)
        finish.assert_not_called()
        checks.assert_not_called()
        self.assertEqual(r.read_json(self.run/'state.json')['status'], 'reported')
        boundary = r.read_json(self.run/'calls/001-adjudicate/launch-boundary.json')
        self.assertEqual(boundary['boundary'], 'codex-read-only')
        self.assertTrue(boundary['single_attempt'])
        with patch.object(r, 'execute_process') as replay:
            self.command('step', '--codex-read-only', failed=True)
        replay.assert_not_called()
