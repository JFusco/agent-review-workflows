"""Writer startup recovery through public commands; local children, no providers."""
import copy
import io
import json
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from test_codex_launch import STARTUP
from test_mechanics import MechanicsFixture
import test_review_cli as fixtures

r = fixtures.r


class RepairLaunchTests(MechanicsFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        binary = self.root / 'codex-fixture'
        binary.write_text('#!' + sys.executable + '\nimport sys\nsys.stdin.read()\n'
                          'print(' + repr(STARTUP) + ',file=sys.stderr)\nsys.exit(1)\n')
        binary.chmod(0o700)
        self.state['codex_binary'] = str(binary)
        self.use_passing_check()
        self.to_repair()
        self.ready = copy.deepcopy(self.state)

    def command(self, action, *extra, failed=False):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['review_cli.py', action, str(self.run), *extra]), \
                patch('sys.stdout', output), patch('sys.stderr', output):
            if failed:
                with self.assertRaises(SystemExit) as exc:
                    r.main()
                self.assertEqual(exc.exception.code, 2)
            else:
                r.main()
        return output.getvalue()

    def fail_startup(self):
        self.command('step', failed=True)
        self.state = r.read_json(self.run / 'state.json')
        self.assertEqual((self.state['stage'], self.state['status']), ('repair', 'interrupted'))
        return self.run / 'calls/001-repair'

    def test_recover_preserves_lock_checks_profiles_and_failure_receipts(self):
        call = self.fail_startup()
        old = {p: p.read_bytes() for p in call.rglob('*') if p.is_file()}
        with patch.object(r, 'execute_process') as execute, patch.object(r, 'perform_checks') as checks:
            self.command('recover-startup')
        execute.assert_not_called(); checks.assert_not_called()
        after = r.read_json(self.run / 'state.json')
        for key in ('ledger', 'checks', 'agent_profile', 'handoff_revision', 'target_fingerprint', 'round', 'sessions'):
            self.assertEqual(after[key], self.ready[key])
        self.assertEqual(after['status'], 'ready')
        self.assertEqual(len(after['startup_recoveries']), 1)
        self.assertIn(f'- Startup recovery at revision {after["handoff_revision"]}: {call}; '
                      'no dispatch or repair pass consumed.', (self.run / 'handoff.md').read_text())
        for path, content in old.items():
            self.assertEqual(path.read_bytes(), content)
        before = (self.run / 'state.json').read_bytes()
        self.command('recover-startup', failed=True)
        self.assertEqual((self.run / 'state.json').read_bytes(), before)

    def test_recovery_rejects_missing_changed_or_ambiguous_call_receipts(self):
        call = self.fail_startup()
        cases = {
            'stderr.log': b'unknown failure\n', 'stdout.log': b'model output\n',
            'invocation.json': b'{}', 'agent.json': b'{}', 'provider-schema.json': b'{}',
            'input-transport.json': b'{}', 'prompt.txt': b'changed', 'stdin.txt': b'changed',
            'process.json': json.dumps({'exit_code': 1, 'interruption': 'TimeoutExpired'}).encode(),
            'started.json': b'{"pid":1,"process_group":1}',
        }
        for name, value in cases.items():
            with self.subTest(name=name):
                path = call / name; original = path.read_bytes()
                path.write_bytes(value)
                before = (self.run / 'state.json').read_bytes()
                self.command('recover-startup', failed=True)
                self.assertEqual((self.run / 'state.json').read_bytes(), before)
                path.write_bytes(original)
        for process in ({'exit_code': 1, 'interruption': 'TimeoutExpired', 'elapsed_seconds': 0.1},
                        {'exit_code': 0, 'interruption': None, 'elapsed_seconds': 0.1}):
            with self.subTest(process=process):
                path = call / 'process.json'; original = path.read_bytes()
                path.write_text(json.dumps(process))
                before = (self.run / 'state.json').read_bytes()
                output = self.command('recover-startup', failed=True)
                self.assertIn('not a recognized startup-only failure', output)
                self.assertEqual((self.run / 'state.json').read_bytes(), before)
                path.write_bytes(original)
        state = r.read_json(self.run / 'state.json')
        malformed = copy.deepcopy(state); malformed['last_call'] = None
        r.save(self.run, malformed)
        self.command('recover-startup', failed=True)
        r.save(self.run, state)
        path = call / 'last-message.json'; path.write_text('{}')
        self.command('recover-startup', failed=True)

    def test_recovery_rejects_receipt_symlinks_and_live_groups(self):
        call = self.fail_startup()
        path = call / 'stderr.log'; original = path.read_bytes()
        other = self.root / 'saved-stderr'; other.write_bytes(original)
        path.unlink(); path.symlink_to(other)
        self.command('recover-startup', failed=True)
        path.unlink(); path.write_bytes(original)
        lock = self.lock_root / f'agent-review-locks-{os.getuid()}' / (r.digest(str(self.project)) + '.lock')
        lock.write_text('')
        with patch.object(r, 'group_alive', return_value=True):
            output = self.command('recover-startup', failed=True)
        self.assertIn('Startup recovery requires a stopped original process group', output)
        self.assertFalse(list(self.run.glob('startup-recovery-*')))
        event = self.run / 'startup-recovery-001-repair.json'
        event.symlink_to(other)
        self.command('recover-startup', failed=True)
        self.assertTrue(event.is_symlink())
        self.assertEqual(other.read_bytes(), original)

    def test_recovery_rejects_scoped_or_unscoped_content_drift(self):
        self.fail_startup()
        for name in ('calculator.py', 'unrelated.txt'):
            with self.subTest(name=name):
                path = self.project / name; old = path.read_bytes() if path.exists() else None
                path.write_text('changed')
                self.command('recover-startup', failed=True)
                if old is None:
                    path.unlink()
                else:
                    path.write_bytes(old)
        self.assertFalse(list(self.run.glob('startup-recovery-*')))

    def test_recovery_rejects_index_drift(self):
        self.fail_startup()
        subprocess.run(['git', '-C', str(self.project), 'add', 'calculator.py'], check=True)
        self.command('recover-startup', failed=True)

    def test_recovery_rejects_head_drift(self):
        self.fail_startup()
        self.commit_fixture('calculator.py')
        self.command('recover-startup', failed=True)

    def test_recovery_and_launch_reject_invalid_locks_checks_and_sessions(self):
        self.fail_startup()
        original = r.read_json(self.run / 'state.json')
        for key, value in [('checks', []), ('checks', [None]), ('round', 1),
                           ('sessions', {'sol': 'uncertain-session'}), ('ledger', [])]:
            with self.subTest(key=key, value=value):
                state = copy.deepcopy(original); state[key] = value
                r.save(self.run, state)
                with patch.object(r, 'execute_process') as execute:
                    self.command('recover-startup', failed=True)
                    state['status'] = 'ready'; r.save(self.run, state)
                    self.command('step', '--codex-repair-only', failed=True)
                execute.assert_not_called()
        r.save(self.run, original)

    def test_guard_rejects_other_stages_external_coordination_and_combined_flags(self):
        for stage in ('review', 'adjudicate', 'recheck', 'finalize'):
            state = copy.deepcopy(self.ready); state['stage'] = stage
            r.save(self.run, state)
            with patch.object(r, 'execute_process') as execute:
                self.command('step', '--codex-repair-only', failed=True)
            execute.assert_not_called()
        r.save(self.run, self.ready)
        for extra in ('--external-coordinator', '--codex-read-only', '--reviewer-only'):
            with patch.object(r, 'execute_process') as execute:
                self.command('step', '--codex-repair-only', extra, failed=True)
            execute.assert_not_called()

    def test_guard_accepts_one_repair_defers_checks_and_retains_independent_recheck(self):
        self.fail_startup(); self.command('recover-startup')
        with self.fake_dispatch()[0] as execute, self.fake_dispatch()[1], \
                patch.object(r, 'perform_checks') as checks, patch.object(r, 'finish_local') as finish:
            self.command('step', '--codex-repair-only')
        execute.assert_called_once(); checks.assert_not_called(); finish.assert_not_called()
        argv = execute.call_args.args[0]
        for setting in ('--ignore-user-config', 'model_reasoning_effort="xhigh"',
                        'sandbox_mode="workspace-write"', 'approval_policy="never"', 'agents.enabled=false',
                        'sandbox_workspace_write.network_access=false',
                        'sandbox_workspace_write.exclude_slash_tmp=true',
                        'sandbox_workspace_write.exclude_tmpdir_env_var=true',
                        'sandbox_workspace_write.writable_roots=' + json.dumps([str(self.project)])):
            self.assertIn(setting, argv)
        self.assertEqual(argv[argv.index('--model') + 1], 'gpt-6.1-sol')
        self.assertNotIn('resume', argv)
        self.state = r.read_json(self.run / 'state.json')
        self.assertEqual((self.state['stage'], self.state['status'], self.state['round']), ('recheck', 'blocked', 1))
        self.assertFalse(self.state['checks'])
        self.command('step', '--codex-repair-only', failed=True)
        self.command('retry')
        self.state = r.read_json(self.run / 'state.json')
        self.assertTrue(r.checks_pass(self.state))
        self.assertEqual(self.state['stage'], 'recheck')
        boundary = r.read_json(self.run / 'calls/002-repair/launch-boundary.json')
        self.assertEqual(boundary['boundary'], 'codex-repair-only')
        self.assertTrue(boundary['single_attempt'])

    def test_guard_does_not_retry_failed_writer_or_run_checks(self):
        with patch.object(r, 'execute_process', side_effect=r.ProviderCallError('rate_limit')) as execute, \
                patch.object(r, 'request_correction') as correction, patch.object(r, 'select_fallback') as fallback, \
                patch.object(r, 'perform_checks') as checks:
            self.command('step', '--codex-repair-only', failed=True)
        execute.assert_called_once(); correction.assert_not_called(); fallback.assert_not_called(); checks.assert_not_called()
        self.command('recover-startup', failed=True)

    def test_initial_failing_check_does_not_prevent_its_locked_repair(self):
        self.state['check_commands'] = [[sys.executable, '-c', 'raise SystemExit(1)']]
        r.perform_checks(self.run, self.state)
        # The changed check contract must be freshly adjudicated, not edited under a lock.
        self.state['stage'] = 'adjudicate'
        self.accept(self.response())
        with self.fake_dispatch()[0] as execute, self.fake_dispatch()[1]:
            self.command('step', '--codex-repair-only')
        execute.assert_called_once()
        self.assertEqual(r.read_json(self.run / 'state.json')['status'], 'blocked')

    def test_guard_keeps_existing_postwrite_scope_protection(self):
        def write_outside_scope(*_args, **_kwargs):
            (self.project / 'unrelated.txt').write_text('unauthorized')
        def extract(state, _call):
            self.state = state
            model, effort = r.agent_settings(state, 'sol')
            return self.repair_response(), None, {'model': model, 'effort': effort}
        with patch.object(r, 'execute_process', side_effect=write_outside_scope), \
                patch.object(r, 'extract_response', side_effect=extract):
            self.command('step', '--codex-repair-only', failed=True)
        after = r.read_json(self.run / 'state.json')
        self.assertEqual((after['stage'], after['status'], after['round']), ('repair', 'interrupted', 0))
        self.command('recover-startup', failed=True)
