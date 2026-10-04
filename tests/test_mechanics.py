"""Deterministic boundaries: temporary Git projects and synthetic provider/GitHub records."""
import copy
import io
import json
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_review_cli as fixtures

r = fixtures.r
PR = 'https://github.com/example/project/pull/12'
ISSUE = 'https://github.com/example/project/issues/8'
OTHER_ISSUE = 'https://github.com/other/repo/issues/3'


class MechanicsFixture:
    response = fixtures.ReviewTests.response
    repair_response = fixtures.ReviewTests.repair_response
    accept = fixtures.ReviewTests.accept
    commit_fixture = fixtures.ReviewTests.commit_fixture
    to_repair = fixtures.ReviewTests.to_repair

    def use_passing_check(self):
        fixtures.ReviewTests.use_passing_check(self)
        r.save(self.run, self.state)

    def setUp(self):
        fixtures.ReviewTests.setUp(self)
        self.state['schema_version'] = 3
        r.save(self.run, self.state)

    def cli(self, action, *extra):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['review_cli.py', action, str(self.run), *extra]), patch('sys.stdout', output):
            try:
                r.main()
            except SystemExit as exc:
                if exc.code != 0:
                    raise
        return output.getvalue()

    def fake_dispatch(self, path='empty'):
        execute = r.execute_process
        def process(argv, cwd, content, call_dir, timeout, require_success=True):
            if call_dir.parent.name != 'calls':
                return execute(argv, cwd, content, call_dir, timeout, require_success)
            r.write_new(call_dir/'invocation.json', {'argv': argv})
            if self.state['stage'] == 'repair':
                source = self.project/'calculator.py'
                source.write_text(source.read_text().replace('(len(values) + 1)', 'len(values)'))
            return 0
        def extract(state, call_dir):
            self.state = state
            data = self.response([] if path == 'empty' else [fixtures.finding()] if state['stage'] == 'review' else None)
            if state['stage'] == 'adjudicate':
                data['findings'][0].update(disposition='REJECTED' if path == 'rejected' else 'ACCEPTED', rationale='Evidence-backed disposition.')
            elif state['stage'] == 'repair':
                data = self.repair_response()
            elif state['stage'] == 'recheck':
                data['findings'][0].update(verification_status='PASSED', verification_evidence=['SOURCE:calculator.py'], rationale='Corrected source satisfies the acceptance check.')
            model, effort = r.agent_settings(state, r.role(state))
            return data, None, {'model': model, 'effort': effort, 'observed': {'source': 'not exposed by CLI output'}}
        return patch.object(r, 'execute_process', side_effect=process), patch.object(r, 'extract_response', side_effect=extract)

    def terminal(self):
        self.use_passing_check()
        self.accept(self.response([]))
        r.finish_local(self.run, self.state)
        return self.commit_fixture('calculator.py')


class MechanicsTests(MechanicsFixture, unittest.TestCase):
    def test_new_version_and_exact_matrix(self):
        _, state = r.initialize(copy.deepcopy(self.args))
        self.assertEqual(state['schema_version'], 3)
        self.assertEqual(r.read_json(self.run/'original.json')['schema_version'], 3)
        self.assertEqual(r.packet(state)['schema_version'], 3)
        self.assertEqual(r.status_payload(self.run, state)['schema_version'], 3)
        for mode, version, marker in [('implementation', 2, 'implementation_evidence_version'), ('implementation', 3, 'implementation_response_version'), ('diff', 2, 'implementation_evidence_version'), ('plan', 2, 'plan_protocol_version')]:
            candidate = copy.deepcopy(state)
            candidate.update(mode=mode, schema_version=version)
            candidate[marker] = 2
            r.require_current_protocol(candidate)
        for mode, version in [('plan', 3), ('diff', 3), ('implementation', 1), ('implementation', True), ('implementation', 3.0), ('implementation', '3'), ('implementation', 4)]:
            candidate = copy.deepcopy(state)
            candidate.update(mode=mode, schema_version=version)
            with self.subTest(mode=mode, version=version), self.assertRaises(r.ReviewError):
                r.require_current_protocol(candidate)
        for field in ('implementation_evidence_version', 'implementation_response_version'):
            for value in (None, True, 2.0, '2', 1, 3):
                candidate = copy.deepcopy(state)
                candidate[field] = value
                with self.assertRaises(r.ReviewError):
                    r.require_current_protocol(candidate)

    def test_provider_paths_remove_only_finalizer(self):
        for path, count in [('empty', 1), ('rejected', 2), ('repair', 4)]:
            with self.subTest(path=path):
                self.run, self.state = r.initialize(copy.deepcopy(self.args))
                self.use_passing_check()
                a, b = self.fake_dispatch(path)
                with a, b, patch.object(r, 'assert_claude_auth'):
                    output = self.cli('run')
                self.state = r.read_json(self.run/'state.json')
                self.assertEqual(self.state['status'], 'complete')
                self.assertEqual(len(list((self.run/'calls').glob('*/invocation.json'))), count)
                self.assertEqual(self.state['ledger'][-1]['agent'], {'model': 'local-finalizer', 'effort': 'deterministic'})
                self.assertIn('finalize: local-finalizer (deterministic)', output)
                artifact = r.read_json(self.run/'artifacts'/f'{self.state["ledger"][-1]["artifact_id"]}.json')
                self.assertEqual(artifact['response']['findings'], self.state['findings'])
                self.assertIsNone(artifact['response']['plan_markdown'])
                (self.project/'calculator.py').write_text((fixtures.ROOT/'tests/fixtures/calculator.py').read_text())

    def test_step_local_tail_and_reviewer_only_boundary(self):
        self.use_passing_check()
        a, b = self.fake_dispatch()
        with a, b, patch.object(r, 'assert_claude_auth'):
            self.cli('step', '--reviewer-only')
        state = r.read_json(self.run/'state.json')
        self.assertEqual((state['stage'], state['status']), ('finalize', 'ready'))
        with self.assertRaises(SystemExit) as stopped:
            self.cli('step', '--reviewer-only')
        self.assertEqual(stopped.exception.code, 2)
        with patch.object(r, 'execute_process') as execute, patch.object(r, 'assert_claude_auth') as auth, patch.object(r, 'cli_argv') as argv:
            self.cli('step')
        execute.assert_not_called()
        auth.assert_not_called()
        argv.assert_not_called()
        self.assertEqual(r.read_json(self.run/'state.json')['status'], 'complete')

    def test_ordinary_step_completes_clean_reviewer(self):
        self.use_passing_check()
        a, b = self.fake_dispatch()
        with a, b, patch.object(r, 'assert_claude_auth'):
            self.cli('step')
        self.assertEqual(r.read_json(self.run/'state.json')['status'], 'complete')

    def test_external_run_does_not_yield_local_tail(self):
        self.use_passing_check()
        a, b = self.fake_dispatch()
        with a, b, patch.object(r, 'assert_claude_auth'):
            self.cli('run', '--external-coordinator')
        self.assertFalse((self.run/'external-request.json').exists())
        self.assertEqual(r.read_json(self.run/'state.json')['status'], 'complete')

    def test_external_adjudication_submission_local_tail(self):
        self.use_passing_check()
        self.accept(self.response([fixtures.finding()]))
        r.advance(self.run, self.state, external_coordinator=True)
        data = self.response()
        data['findings'][0].update(disposition='REJECTED', rationale='Observed fixture does not require repair.')
        response_path = self.root/'response.json'
        r.write_new(response_path, data)
        request_bytes = (self.run/'external-request.json').read_bytes()
        with patch.object(r, 'execute_process') as execute:
            self.cli('submit', '--response', str(response_path), '--model', 'gpt-6-astra', '--effort', 'max')
        execute.assert_not_called()
        self.assertEqual(r.read_json(self.run/'state.json')['status'], 'complete')
        self.assertEqual((self.run/'external-request.json').read_bytes(), request_bytes)

    def test_local_gates_and_check_recovery(self):
        self.state['check_commands'] = [[sys.executable, '-c', 'raise SystemExit(1)']]
        r.perform_checks(self.run, self.state)
        self.accept(self.response([]))
        self.assertEqual(self.state['status'], 'unresolved')
        self.state['check_commands'] = [[sys.executable, '-c', 'pass']]
        # Fixture configuration sets up a transient-failure receipt with the same authorized command.
        r.perform_checks(self.run, self.state)
        self.state['checks'][0]['exit_code'] = 1
        r.save(self.run, self.state)
        r.rerun_checks(self.run, self.state)
        self.assertEqual(self.state['status'], 'complete')
        self.assertEqual([e['stage'] for e in self.state['ledger']], ['review', 'rerun-checks', 'finalize'])
        self.run, self.state = r.initialize(copy.deepcopy(self.args))
        self.use_passing_check()
        self.accept(self.response([]))
        self.state['checks'][0]['exit_code'] = 1
        r.save(self.run, self.state)
        r.finish_local(self.run, self.state)
        self.assertEqual(self.state['status'], 'unresolved')

    def test_local_stale_scope_and_incomplete_findings_reject(self):
        self.use_passing_check()
        self.accept(self.response([]))
        self.state['findings'] = [fixtures.finding()]
        r.finish_local(self.run, self.state)
        self.assertEqual(self.state['status'], 'unresolved')
        self.state.update(status='ready', findings=[])
        (self.project/'test_calculator.py').write_text('unexpected change')
        with self.assertRaises(r.ReviewError):
            r.finish_local(self.run, self.state)
        self.assertEqual(self.state['status'], 'ready')

    def test_completion_save_failure_records_orphan_then_accepts_once(self):
        self.use_passing_check()
        self.accept(self.response([]))
        save = r.save
        def fail(run, state):
            if state['status'] == 'complete':
                raise OSError('injected completion save failure')
            save(run, state)
        with patch.object(r, 'save', side_effect=fail), self.assertRaises(OSError):
            r.finish_local(self.run, self.state)
        self.assertEqual(r.read_json(self.run/'state.json')['status'], 'ready')
        r.finish_local(self.run, self.state)
        self.assertEqual(len([e for e in self.state['ledger'] if e['stage'] == 'finalize']), 1)
        self.assertEqual(self.state['ledger'][-1]['orphaned_artifacts'], ['revision-002'])

    def test_completion_render_failure_is_durable_and_historical(self):
        self.use_passing_check()
        self.accept(self.response([]))
        with patch.object(r, 'render', side_effect=KeyboardInterrupt('injected view failure')), self.assertRaises(r.DerivedViewError) as error:
            r.advance(self.run, self.state)
        self.assertIsInstance(error.exception.__cause__, KeyboardInterrupt)
        self.assertEqual(r.read_json(self.run/'state.json')['status'], 'complete')
        saved = (self.run/'state.json').read_bytes()
        artifacts = list((self.run/'artifacts').glob('*'))
        shutil.rmtree(self.project)
        with patch.object(r, 'target', side_effect=AssertionError('historical views must not read checkout')), patch.object(r, 'execute_process') as execute:
            self.cli('step')
            self.cli('run')
        execute.assert_not_called()
        self.assertEqual(saved, (self.run/'state.json').read_bytes())
        self.assertEqual(artifacts, list((self.run/'artifacts').glob('*')))
        self.assertIn('Scoped diff', (self.run/'handoff.md').read_text())
        self.assertIn('No findings', (self.run/'final.md').read_text())
        for action in ('retry', 'rerun-checks', 'reconcile', 'decide', 'submit'):
            extra = {'reconcile': ['--note', 'Inspected'], 'decide': ['--instruction', 'Actual decision'],
                     'submit': ['--response', str(self.root/'missing'), '--model', 'gpt-6-astra', '--effort', 'max']}.get(action, [])
            with self.subTest(action=action), self.assertRaises(SystemExit):
                self.cli(action, *extra)
        self.assertEqual(saved, (self.run/'state.json').read_bytes())

    def test_completed_v3_verify_target(self):
        head = self.terminal()
        self.assertEqual(r.verify_target(self.run, head, self.state['base'])['status'], 'PASS')

    def test_post_repair_failure_and_retry_do_not_replay_writer(self):
        for failure in ('execution', 'receipt', 'render'):
            with self.subTest(failure=failure):
                (self.project/'calculator.py').write_text((fixtures.ROOT/'tests/fixtures/calculator.py').read_text())
                self.run, self.state = r.initialize(copy.deepcopy(self.args))
                self.use_passing_check()
                self.to_repair()
                a, b = self.fake_dispatch('repair')
                perform, write = r.perform_checks, r.write_new
                def checks(run, state, rerun_attempt=None):
                    if failure == 'execution':
                        raise KeyboardInterrupt('post-repair check interrupted')
                    perform(run, state, rerun_attempt)
                def write_receipt(path, value):
                    if failure == 'receipt' and path.parent.name == 'checks':
                        raise OSError('receipt write failed')
                    write(path, value)
                with a, b, patch.object(r, 'perform_checks', side_effect=checks), patch.object(r, 'write_new', side_effect=write_receipt):
                    if failure == 'render':
                        with patch.object(r, 'render', side_effect=OSError('view failed')), self.assertRaises(r.DerivedViewError):
                            r.advance(self.run, self.state)
                    else:
                        with self.assertRaises((OSError, KeyboardInterrupt)):
                            r.advance(self.run, self.state)
                saved = r.read_json(self.run/'state.json')
                self.assertEqual((saved['stage'], saved['status']), ('recheck', 'ready' if failure == 'render' else 'blocked'))
                self.assertEqual(saved['round'], 1)
                self.assertEqual(len([e for e in saved['ledger'] if e['stage'] == 'repair']), 1)
                if failure != 'render':
                    with patch.object(r, 'execute_process') as execute:
                        self.cli('step')
                    execute.assert_not_called()
                    self.cli('retry')
                    saved = r.read_json(self.run/'state.json')
                    self.assertEqual(saved['status'], 'ready')
                self.assertTrue(r.checks_pass(saved))

    def test_version_two_external_finalize_keeps_original_and_profile(self):
        self.state['schema_version'] = 2
        original = r.read_json(self.run/'original.json')
        original.pop('schema_version')
        (self.run/'original.json').write_text(r.dumps(original))
        saved_original = (self.run/'original.json').read_bytes()
        self.use_passing_check()
        self.accept(self.response([]))
        with patch.object(r, 'execute_process') as execute:
            r.advance(self.run, self.state, external_coordinator=True)
        execute.assert_not_called()
        self.assertEqual(self.state['status'], 'awaiting_coordinator')
        data = self.response()
        response = self.root/'external-finalize.json'
        r.write_new(response, data)
        self.cli('submit', '--response', str(response), '--model', 'gpt-6-astra', '--effort', 'max')
        self.assertEqual(r.read_json(self.run/'state.json')['ledger'][-1]['agent']['model'], 'gpt-6-astra')
        self.assertEqual(saved_original, (self.run/'original.json').read_bytes())

    def test_render_failure_after_provider_keeps_local_tail_ready(self):
        self.use_passing_check()
        a, b = self.fake_dispatch()
        with a, b, patch.object(r, 'assert_claude_auth'), patch.object(r, 'render', side_effect=OSError('derived view')), self.assertRaises(r.DerivedViewError):
            r.advance(self.run, self.state)
        self.assertEqual((self.state['stage'], self.state['status']), ('finalize', 'ready'))
        with patch.object(r, 'execute_process') as execute:
            self.cli('run')
        execute.assert_not_called()
        self.assertEqual(r.read_json(self.run/'state.json')['status'], 'complete')

    def test_failing_check_rerun_does_not_leave_ready_finalization(self):
        self.use_passing_check()
        self.accept(self.response([]))
        self.state['check_commands'] = [[sys.executable, '-c', 'raise SystemExit(1)']]
        r.save(self.run, self.state)
        r.rerun_checks(self.run, self.state)
        self.assertEqual(self.state['status'], 'unresolved')
        self.assertEqual(self.state['ledger'][-1]['stage'], 'rerun-checks')


class CollectionTests(MechanicsFixture, unittest.TestCase):
    # Reuse setup and fixture utilities without rerunning the completion suite.
    def pr_record(self, **overrides):
        return {'url': PR, 'title': 'Reviewed change', 'body': 'Acceptance criteria', 'state': 'OPEN', 'isDraft': False,
                'headRefOid': self.head, 'baseRefOid': self.state['base'], 'updatedAt': '2026-10-04T10:00:00Z',
                'closingIssuesReferences': [{'url': ISSUE}], 'mergeable': 'MERGEABLE', 'reviewDecision': 'APPROVED', **overrides}

    def hosted(self, pr=None, checks=None, code=0, second_pr=None, second_checks=None, mutate=None):
        counts = {'pr': 0, 'checks': 0}
        real_command = r.command
        def command(argv, cwd, timeout=30):
            if argv[0] == 'git':
                return real_command(argv, cwd, timeout)
            self.assertEqual(argv[0], 'gh')
            if argv[1:3] == ['pr', 'view']:
                counts['pr'] += 1
                value = second_pr if counts['pr'] == 2 and second_pr is not None else pr or self.pr_record()
                if counts['pr'] == 2 and mutate:
                    mutate()
                return subprocess.CompletedProcess(argv, 0, json.dumps(value), '')
            if argv[1:3] == ['issue', 'view']:
                return subprocess.CompletedProcess(argv, 0, json.dumps({'url': argv[3], 'title': 'Expected change', 'body': 'Requirement', 'state': 'OPEN'}), '')
            self.assertEqual(argv[1:3], ['pr', 'checks'])
            counts['checks'] += 1
            value = second_checks if counts['checks'] == 2 and second_checks is not None else checks if checks is not None else [
                {'name': 'test', 'state': 'SUCCESS', 'bucket': 'pass', 'link': 'https://example.invalid/check/1'}]
            return subprocess.CompletedProcess(argv, code, json.dumps(value), '')
        return patch.object(r, 'command', side_effect=command)

    def setUp(self):
        super().setUp()
        self.head = self.terminal()

    def test_delivery_pass_readonly_and_multiple_issue_urls(self):
        pr = self.pr_record(closingIssuesReferences=[{'url': ISSUE}, {'url': OTHER_ISSUE}])
        before = r.evidence_snapshot(self.run)
        project_before = r.inventory(self.project)
        with self.hosted(pr=pr) as gh, patch.object(r, 'execute_process') as execute, patch.object(r, 'resolve_cli') as resolve, patch.object(r, 'render') as render, patch.object(r, 'project_lock') as lock:
            output = self.cli('delivery-evidence', '--pr', PR)
        report = json.loads(output)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['evidence']['semantic_coverage'], 'not_assessed')
        self.assertEqual(report['conditions']['identity']['report']['conditions']['eligible_run']['status'], 'PASS')
        self.assertEqual(len([c for c in gh.call_args_list if c.args[0][0] == 'gh']), 8)
        for mock in (execute, resolve, render, lock):
            mock.assert_not_called()
        self.assertEqual(before, r.evidence_snapshot(self.run))
        self.assertEqual(project_before, r.inventory(self.project))

    def test_hosted_conditions_matrix(self):
        for field, value, expected in [('state', 'CLOSED', 'BLOCKED'), ('state', 'MERGED', 'BLOCKED'),
                ('isDraft', True, 'BLOCKED'), ('isDraft', None, 'UNKNOWN'), ('mergeable', 'CONFLICTING', 'BLOCKED'),
                ('mergeable', 'UNKNOWN', 'UNKNOWN'), ('mergeable', '', 'UNKNOWN'),
                ('reviewDecision', 'REVIEW_REQUIRED', 'BLOCKED'), ('reviewDecision', 'CHANGES_REQUESTED', 'BLOCKED'),
                ('reviewDecision', '', 'UNKNOWN'), ('closingIssuesReferences', [], 'UNKNOWN'),
                ('closingIssuesReferences', [{'number': 8}], 'UNKNOWN'),
                ('headRefOid', None, 'UNKNOWN'), ('body', None, 'UNKNOWN'), ('url', 'https://github.com/example/project/pull/99', 'BLOCKED')]:
            with self.subTest(field=field, value=value), self.hosted(pr=self.pr_record(**{field: value})):
                self.assertEqual(r.delivery_evidence(self.run, PR)['status'], expected)

    def test_required_check_state_exit_matrix(self):
        for state, bucket, code, expected in [('SUCCESS', 'pass', 0, 'PASS'), ('SUCCESS', 'pass', 1, 'UNKNOWN'),
            ('FAILURE', 'fail', 1, 'BLOCKED'), ('PENDING', 'pending', 8, 'BLOCKED'),
            ('CANCELLED', 'cancel', 1, 'BLOCKED'), ('SKIPPED', 'skipping', 0, 'UNKNOWN'),
            ('NEUTRAL', 'pass', 0, 'UNKNOWN'), ('FAILURE', 'pass', 0, 'BLOCKED'), ('SUCCESS', 'pending', 8, 'BLOCKED')]:
            with self.subTest(state=state, bucket=bucket), self.hosted(checks=[{'name': 'test', 'state': state, 'bucket': bucket, 'link': ''}], code=code):
                self.assertEqual(r.delivery_evidence(self.run, PR)['status'], expected)
        for rows in ([], [{}], [{'name': 'test', 'bucket': 'pass'}], [{'name': 'test', 'bucket': 'pass', 'state': 'SUCCESS', 'link': None}]):
            with self.hosted(checks=rows):
                self.assertEqual(r.delivery_evidence(self.run, PR)['conditions']['required_checks']['status'], 'UNKNOWN')

    def test_changed_hosted_or_local_overrides_blocker(self):
        for local in (False, True):
            with self.subTest(local=local), self.hosted(pr=self.pr_record(isDraft=True),
                 second_pr=None if local else self.pr_record(isDraft=True, updatedAt='changed'),
                 mutate=(lambda: (self.run/'calls'/'new').mkdir()) if local else None):
                report = r.delivery_evidence(self.run, PR)
            self.assertEqual(report['status'], 'UNKNOWN')
            self.assertEqual(report['conditions']['pr_state']['status'], 'BLOCKED')
        with self.hosted(second_checks=[{'name': 'test', 'state': 'PENDING', 'bucket': 'pending', 'link': ''}]):
            self.assertEqual(r.delivery_evidence(self.run, PR)['status'], 'UNKNOWN')

    def test_missing_network_malformed_and_identity_blocker(self):
        with patch.object(r, 'command', side_effect=r.ReviewError('gh unavailable')):
            self.assertEqual(r.delivery_evidence(self.run, PR)['status'], 'UNKNOWN')
        with patch.object(r, 'command', return_value=subprocess.CompletedProcess([], 1, 'not JSON', 'access unavailable')):
            self.assertEqual(r.delivery_evidence(self.run, PR)['status'], 'UNKNOWN')
        (self.project/'test_calculator.py').write_text('changed context')
        with self.hosted(pr=self.pr_record(reviewDecision='')):
            report = r.delivery_evidence(self.run, PR)
        self.assertEqual(report['status'], 'BLOCKED')
        self.assertEqual(report['conditions']['identity']['status'], 'BLOCKED')

    def test_local_checks_and_verification_conditions(self):
        receipts = [x for x in r.snapshot_records(r.evidence_snapshot(self.run), 'checks/') if '/' not in x['source'][7:]]
        self.assertEqual(r.local_check_condition(self.state, receipts)['status'], 'PASS')
        self.assertEqual(r.local_check_condition(self.state, [])['status'], 'UNKNOWN')
        self.state['checks'][0]['target_fingerprint'] = 'stale'
        self.assertEqual(r.local_check_condition(self.state, receipts)['status'], 'BLOCKED')
        self.state['findings'] = [fixtures.finding()]
        self.assertEqual(r.finding_condition(self.state, [], [])['status'], 'BLOCKED')
        self.state['findings'][0].update(disposition='ACCEPTED', verification_status='PASSED', verification_evidence=['SOURCE:calculator.py'])
        self.assertEqual(r.finding_condition(self.state, [], [])['status'], 'UNKNOWN')
        self.state['findings'][0].update(disposition='REJECTED')
        self.assertEqual(r.finding_condition(self.state, [], [])['status'], 'PASS')


    def test_independent_recheck_support_and_stale_references(self):
        (self.project/'calculator.py').write_text((fixtures.ROOT/'tests/fixtures/calculator.py').read_text())
        self.args.base = self.state['base']
        self.run, self.state = r.initialize(copy.deepcopy(self.args))
        self.use_passing_check()
        a, b = self.fake_dispatch('repair')
        with a, b, patch.object(r, 'assert_claude_auth'):
            self.cli('run')
        self.state = r.read_json(self.run/'state.json')
        snapshot = r.evidence_snapshot(self.run)
        artifacts = r.snapshot_records(snapshot, 'artifacts/')
        receipts = [x for x in r.snapshot_records(snapshot, 'checks/') if '/' not in x['source'][7:]]
        self.assertEqual(r.finding_condition(self.state, artifacts, receipts)['status'], 'PASS')
        self.assertEqual(r.finding_condition(self.state, [], receipts)['status'], 'UNKNOWN')
        malformed = copy.deepcopy(self.state)
        malformed['findings'][0].pop('id')
        self.assertEqual(r.finding_condition(malformed, artifacts, receipts)['status'], 'UNKNOWN')
        stale = copy.deepcopy(self.state)
        stale['findings'][0]['verification_evidence'] = ['SOURCE:missing.py']
        self.assertEqual(r.finding_condition(stale, artifacts, receipts)['status'], 'BLOCKED')
        stale['findings'][0]['verification_evidence'] = ['CHECK-old']
        stale['cited_check_receipts'] = {'CHECK-old': {'id': 'CHECK-old', 'target_fingerprint': 'old'}}
        self.assertEqual(r.finding_condition(stale, artifacts, receipts + [{'source': 'checks/old.json', 'value': stale['cited_check_receipts']['CHECK-old']}])['status'], 'BLOCKED')

    def test_hosted_order_and_issue_rereads(self):
        real = r.command
        pr = self.pr_record(closingIssuesReferences=[{'url': ISSUE}, {'url': OTHER_ISSUE}])
        second = self.pr_record(closingIssuesReferences=[{'url': OTHER_ISSUE}, {'url': ISSUE}])
        with self.hosted(pr=pr, second_pr=second):
            self.assertEqual(r.delivery_evidence(self.run, PR)['status'], 'PASS')
        for failure in ('unavailable', 'changed', 'malformed'):
            seen = {}
            with self.hosted(pr=pr):
                hosted_command = r.command
                def issues(argv, cwd, timeout=30):
                    if argv[0] == 'git':
                        return real(argv, cwd, timeout)
                    if argv[1:3] == ['issue', 'view']:
                        seen[argv[3]] = seen.get(argv[3], 0) + 1
                        if failure == 'unavailable':
                            raise r.ReviewError('Issue inaccessible')
                        if failure == 'malformed':
                            return subprocess.CompletedProcess(argv, 0, '{}', '')
                        if seen[argv[3]] == 2:
                            return subprocess.CompletedProcess(argv, 0, json.dumps({'url': argv[3], 'title': 'changed', 'body': 'Requirement', 'state': 'OPEN'}), '')
                    return hosted_command(argv, cwd, timeout)
                with patch.object(r, 'command', side_effect=issues):
                    self.assertEqual(r.delivery_evidence(self.run, PR)['status'], 'UNKNOWN')

    def comparison(self):
        candidate = self.root/'candidate'
        shutil.copytree(self.run, candidate)
        return candidate

    def test_comparison_historical_exact_inputs_and_context(self):
        candidate = self.comparison()
        state = r.read_json(candidate/'state.json')
        state.update(schema_version=1, agent_profile=None)
        r.save(candidate, state)
        before = r.evidence_snapshot(self.run), r.evidence_snapshot(candidate)
        with patch.object(r, 'command') as command, patch.object(r, 'execute_process') as execute, patch.object(r, 'project_lock') as lock, patch.object(r, 'render') as render:
            report = r.compare_runs(self.run, candidate)
        self.assertEqual(report['status'], 'COMPARABLE')
        self.assertIn('protocol', report['comparability']['context_differences'])
        for mock in (command, execute, lock, render):
            mock.assert_not_called()
        self.assertEqual(before, (r.evidence_snapshot(self.run), r.evidence_snapshot(candidate)))
        original = r.read_json(candidate/'original.json')
        original['requirements'] += '\n'
        (candidate/'original.json').write_text(r.dumps(original))
        self.assertEqual(r.compare_runs(self.run, candidate)['status'], 'NOT_COMPARABLE')
        (candidate/'original.json').unlink()
        self.assertEqual(r.compare_runs(self.run, candidate)['status'], 'UNKNOWN')

    def test_attempts_acceptance_provenance_and_individual_usage(self):
        agents = [{'model': 'claude-opus-5-5', 'effort': 'high', 'observed': {'source': 'Claude modelUsage', 'model': 'different'}},
                  {'model': 'gpt-6-astra', 'effort': 'max', 'observed': {'source': 'not exposed by CLI output', 'model': None}},
                  {'model': 'gpt-6-astra', 'effort': 'max', 'observed': {'source': 'caller attestation; not provider-verified'}},
                  {'model': 'local-finalizer'}, {'model': 'local-checks'}, {'model': 'operator'},
                  {'model': 'fixture', 'observed': {'source': 'fixture'}}, {'model': 'unknown'}]
        self.state['ledger'] = [{'stage': 'same-stage', 'agent': a} for a in agents]
        r.save(self.run, self.state)
        for name, argv, output in [('001', ['claude', '--model', 'requested', '--effort', 'high'], {'usage': {'input_tokens': 5, 'output_tokens': 2}, 'total_cost_usd': 0.2, 'modelUsage': {'observed': {'inputTokens': 5, 'costUSD': 0.2}}}),
                 ('002', ['claude', '--resume', 'session', '--model', 'requested'], {'usage': {'input_tokens': 20}, 'total_cost_usd': 0.8}),
                 ('003', ['codex', 'exec', 'resume', '--model', 'gpt-6-astra', '-c', 'model_reasoning_effort="max"'], None)]:
            call = self.run/'calls'/name
            r.write_new(call/'invocation.json', {'argv': argv})
            if name != '002':
                r.write_new(call/'process.json', {'elapsed_seconds': 2, 'exit_code': 1 if name == '003' else 0, 'interruption': None})
            r.write_new(call/'stdout.log', output if output is not None else
                        '{"type":"thread.started","thread_id":"thread"}\n{"type":"turn.completed","usage":{"input_tokens":8,"cached_input_tokens":4,"output_tokens":2,"reasoning_output_tokens":1}}\n')
        (self.run/'calls'/'empty').mkdir()
        report = r.compare_runs(self.run, self.comparison())['baseline']
        self.assertEqual(report['accepted_counts'], {'total': 8, 'cli': 2, 'external': 1, 'deterministic': 2, 'operator': 1, 'synthetic': 1, 'unclassified': 1})
        self.assertEqual(report['launch_attempt_count'], 3)
        self.assertEqual(report['provider_cli_time']['measured_count'], 2)
        self.assertEqual(report['provider_cli_time']['measured_elapsed_seconds'], 4)
        self.assertEqual(len(report['incomplete_calls']), 1)
        self.assertTrue(report['launch_attempts'][0]['settings_discrepancy'])
        self.assertEqual(len(report['telemetry']), 3)
        self.assertEqual(report['telemetry'][1]['incremental_accounting_scope'], 'unknown for resumed session')
        self.assertEqual(report['telemetry'][2]['thread_id'], 'thread')
        self.assertEqual(report['telemetry'][2]['event_position'], 2)
        self.assertIsNone(report['telemetry'][2]['total_cost_usd'])
        self.assertEqual(report['check_time']['recorded_count'], 1)
        self.assertNotIn('total_cost_usd', report)

    def test_malformed_optional_usage_stays_unavailable_and_json_valid(self):
        for value in ('NaN', 'Infinity', '1e999', '2,"input_tokens":3'):
            source = self.run/'calls'/'malformed'
            source.mkdir(parents=True, exist_ok=True)
            (source/'invocation.json').write_text(r.dumps({'argv': ['codex', 'exec']}))
            (source/'stdout.log').write_text('{"type":"turn.completed","usage":{"input_tokens":' + value + '}}\n')
            report = r.compare_runs(self.run, self.run)
            self.assertEqual(report['status'], 'COMPARABLE')
            self.assertEqual(report['baseline']['telemetry'], [])
            self.assertIsNotNone(report['baseline']['launch_attempts'][0]['usage_unavailable_reason'])
            r.parse_json(r.dumps(report))
        with self.assertRaises(r.ReviewError):
            r.parse_json('{"cost":1e999}')

    def test_comparison_changing_evidence_unknown(self):
        candidate = self.comparison()
        collect = r.run_comparison_evidence
        def change(run, snapshot):
            value = collect(run, snapshot)
            if run == candidate:
                r.write_new(run/'calls'/'added'/'invocation.json', {'argv': []})
            return value
        with patch.object(r, 'run_comparison_evidence', side_effect=change):
            self.assertEqual(r.compare_runs(self.run, candidate)['status'], 'UNKNOWN')

    def test_collectors_single_json_and_exit_codes(self):
        for status, code in [('PASS', 0), ('BLOCKED', 1), ('UNKNOWN', 2)]:
            with patch.object(r, 'delivery_evidence', return_value={'status': status}), patch.object(sys, 'argv', ['review_cli.py', 'delivery-evidence', str(self.run), '--pr', PR]), patch('sys.stdout', io.StringIO()) as output, self.assertRaises(SystemExit) as result:
                r.main()
            self.assertEqual(result.exception.code, code)
            self.assertEqual(json.loads(output.getvalue())['status'], status)
        candidate = self.comparison()
        for status, code in [('COMPARABLE', 0), ('NOT_COMPARABLE', 1), ('UNKNOWN', 2)]:
            with patch.object(r, 'compare_runs', return_value={'status': status}), patch.object(sys, 'argv', ['review_cli.py', 'compare-runs', str(self.run), str(candidate)]), patch('sys.stdout', io.StringIO()) as output, self.assertRaises(SystemExit) as result:
                r.main()
            self.assertEqual(result.exception.code, code)
            self.assertEqual(json.loads(output.getvalue())['status'], status)
