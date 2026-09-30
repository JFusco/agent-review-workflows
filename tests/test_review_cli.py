import argparse
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import signal
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('review_cli', ROOT / 'scripts/review_cli.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def finding():
    return {'id': 'FIND-001', 'severity': 'WARN', 'location': 'calculator.py:5',
            'evidence': 'For [2,4], dividing 6 by 3 returns 2.', 'correction_recommended': 'Divide by the number of values.',
            'acceptance_check': 'average([2,4]) == 3', 'disposition': 'OPEN', 'rationale': '',
            'verification_status': 'UNVERIFIED', 'verification_evidence': []}


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        runtime_config_patch = patch.object(r, 'RUNTIME_CONFIG', self.root/'runtime.local.json')
        runtime_config_patch.start()
        self.addCleanup(runtime_config_patch.stop)
        self.lock_root = self.root / 'locks'
        self.lock_root.mkdir()
        lock_root_patch = patch.object(r, 'LOCK_ROOT', self.lock_root)
        lock_root_patch.start()
        self.addCleanup(lock_root_patch.stop)
        cli_environment = patch.dict(os.environ, {
            'AGENT_REVIEW_CODEX_BIN': sys.executable,
            'AGENT_REVIEW_CLAUDE_BIN': sys.executable,
        })
        cli_environment.start()
        self.addCleanup(cli_environment.stop)
        self.project = self.root / 'project'
        self.project.mkdir()
        buggy_calculator = (ROOT/'tests/fixtures/calculator.py').read_text()
        (self.project/'calculator.py').write_text(buggy_calculator.replace('(len(values) + 1)', 'len(values)'))
        (self.project/'test_calculator.py').write_text((ROOT/'tests/fixtures/test_calculator.py').read_text())
        (self.project / '.gitignore').write_text('__pycache__/\n')
        subprocess.run(['git', 'init', '-q', str(self.project)], check=True)
        subprocess.run(['git', '-C', str(self.project), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.project), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Fixture'], check=True)
        (self.project/'calculator.py').write_text(buggy_calculator)
        self.args = argparse.Namespace(project=str(self.project), mode='implementation', scope=['calculator.py','test_calculator.py'],
                    requirements=str(ROOT/'tests/fixtures/requirements.md'), plan=None, runs_dir=str(self.root/'runs'),
                    base='HEAD', timeout=60, check=[f'{sys.executable} -m unittest -v'])
        self.run, self.state = r.initialize(self.args)

    def response(self, fs=None):
        findings = copy.deepcopy(self.state['findings'] if fs is None else fs)
        if r.advisory_stage(self.state):
            findings = [
                {key: item[key] for key in ('id', 'disposition', 'rationale')}
                for item in findings
            ]
        return {'run_id': self.state['run_id'], 'target_fingerprint': self.state['target_fingerprint'],
                'handoff_revision': self.state['handoff_revision'],
                'stage': self.state['stage'], 'summary': 'Fixture result, not provider evidence.',
                'findings': findings, 'plan_markdown': None}

    def accept(self, data):
        who = r.role(self.state)
        model, effort = r.agent_settings(self.state, who)
        r.accept(self.run, self.state, data,
                 {'model': model, 'effort': effort, 'observed': {'source': 'fixture'}})

    def use_passing_check(self):
        self.state['check_commands'] = [[sys.executable, '-c', 'pass']]
        r.perform_checks(self.run, self.state)

    def to_repair(self):
        self.accept(self.response([finding()]))
        data=self.response()
        data['findings'][0].update(disposition='ACCEPTED', rationale='Coordinator accepts the defect for repair.')
        self.accept(data)
        self.assertEqual(self.state['stage'], 'repair')

    def test_schema_valid(self):
        r.Draft202012Validator.check_schema(r.SCHEMA)
        r.validate_response(self.state, self.response([finding()]))

    def test_invalid_handoffs_fail(self):
        base=self.response([finding()])
        mutations=[lambda x:x.update(run_id='wrong'), lambda x:x.update(target_fingerprint='0'*64),
                   lambda x:x.update(stage='repair'), lambda x:x.update(unexpected=True),
                   lambda x:x['findings'].append(copy.deepcopy(x['findings'][0])),
                   lambda x:x['findings'][0].update(evidence='   '), lambda x:x['findings'][0].pop('correction_recommended'),
                   lambda x:x['findings'][0].update(verification_status='PASSED'),
                   lambda x:x['findings'][0].update(disposition='ACCEPTED')]
        for mutate in mutations:
            data=copy.deepcopy(base)
            mutate(data)
            with self.subTest(data=data), self.assertRaises(r.ReviewError):
                r.validate_response(self.state, data)
        self.assertEqual(self.state['stage'], 'review')
        self.assertEqual(self.state['ledger'], [])

    def test_new_implementation_findings_require_scoped_locations(self):
        for location in ('calculator.py', 'calculator.py:5', 'calculator.py:5-8'):
            with self.subTest(valid=location):
                item = finding()
                item['location'] = location
                r.validate_response(self.state, self.response([item]))
        for location in ('N/A', 'unrelated.py:1', 'calculator.py:0', 'calculator.py:8-5'):
            with self.subTest(invalid=location):
                item = finding()
                item['location'] = location
                with self.assertRaisesRegex(r.ReviewError, 'scoped project-relative file location'):
                    r.validate_response(self.state, self.response([item]))

    def test_existing_finding_definition_is_immutable(self):
        self.accept(self.response([finding()]))
        data = self.response()
        data['findings'] = copy.deepcopy(self.state['findings'])
        data['findings'][0].update(
            disposition='ACCEPTED', rationale='Recommendation with altered evidence.', evidence='Rewritten evidence.',
        )
        with self.assertRaisesRegex(r.ReviewError, 'definitions are immutable'):
            r.validate_response(self.state, data)

    def test_reviewer_packet_contains_requirements_diff_and_check_receipt(self):
        r.perform_checks(self.run, self.state)
        current = r.packet(self.state)
        self.assertEqual(current['requirements'], (ROOT/'tests/fixtures/requirements.md').read_text())
        self.assertIn('diff --git a/calculator.py b/calculator.py', current['target']['diff'])
        self.assertEqual(current['target']['files']['calculator.py'], (ROOT/'tests/fixtures/calculator.py').read_text())
        self.assertEqual(current['findings'], [])
        self.assertEqual(current['decision_ledger'], [])
        self.assertEqual(len(current['checks']), 1)
        self.assertEqual(current['checks'][0]['argv'], self.state['check_commands'][0])
        self.assertNotEqual(current['checks'][0]['exit_code'], 0)
        self.assertIn('FAILED', current['checks'][0]['output'])
        self.assertEqual(current['checks'][0]['target_fingerprint'], self.state['target_fingerprint'])
        self.assertIn('actual target diff', r.prompt(self.state))

    def test_duplicate_json_keys_rejected(self):
        p=self.root/'duplicate.json'
        p.write_text('{"a":1,"a":2}')
        with self.assertRaises(r.ReviewError): r.read_json(p)

    def test_drift_rejected(self):
        (self.project/'calculator.py').write_text('changed')
        with self.assertRaises(r.ReviewError): r.assert_fresh(self.state)

    def test_implementation_evidence_preflight_fails_before_run_creation(self):
        cases = [
            ('missing-base', {'base': None}, 'explicit --base'),
            ('invalid-base', {'base': 'missing-ref'}, 'local commit'),
            ('missing-check', {'check': []}, 'at least one explicit --check'),
        ]
        for name, changes, message in cases:
            with self.subTest(name=name):
                args = copy.deepcopy(self.args)
                args.runs_dir = str(self.root/f'{name}-runs')
                for field, value in changes.items():
                    setattr(args, field, value)
                with self.assertRaisesRegex(r.ReviewError, message):
                    r.initialize(args)
                self.assertFalse(Path(args.runs_dir).exists())

        clean = subprocess.run(
            ['git', '-C', str(self.project), 'show', 'HEAD:calculator.py'],
            check=True, capture_output=True, text=True,
        ).stdout
        (self.project/'calculator.py').write_text(clean)
        args = copy.deepcopy(self.args)
        args.runs_dir = str(self.root/'empty-diff-runs')
        with self.assertRaisesRegex(r.ReviewError, 'nonempty scoped diff'):
            r.initialize(args)
        self.assertFalse(Path(args.runs_dir).exists())

    def test_plan_start_remains_base_and_check_optional(self):
        args = copy.deepcopy(self.args)
        args.mode = 'plan'
        args.plan = str(ROOT/'tests/fixtures/sound-plan.md')
        args.base = None
        args.check = []
        args.runs_dir = str(self.root/'base-less-plan-runs')
        _, state = r.initialize(args)
        self.assertIsNone(state['base'])
        self.assertEqual(state['check_commands'], [])
        self.assertNotIn('implementation_evidence_version', state)
        original = r.read_json(Path(args.runs_dir)/state['run_id']/'original.json')
        self.assertNotIn('implementation_evidence_version', original)
        self.assertNotIn('check_commands', original)
        self.assertNotIn('actual target diff', r.prompt(state))

    def test_scoped_diff_includes_untracked_empty_and_deleted_files(self):
        (self.project/'added.py').write_text('VALUE = 1\n')
        (self.project/'empty.py').write_text('')
        (self.project/'unrelated.py').write_text('OUTSIDE = True\n')
        (self.project/'test_calculator.py').unlink()
        args = copy.deepcopy(self.args)
        args.scope = ['calculator.py', 'test_calculator.py', 'added.py', 'empty.py']
        args.runs_dir = str(self.root/'complete-diff-runs')
        _, state = r.initialize(args)
        current = r.target(state)
        expected_base = subprocess.run(
            ['git', '-C', str(self.project), 'rev-parse', 'HEAD'],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        self.assertEqual(current['base'], expected_base)
        self.assertIn('diff --git a/calculator.py b/calculator.py', current['diff'])
        self.assertIn('deleted file mode', current['diff'])
        self.assertIn('diff --git a/added.py b/added.py', current['diff'])
        self.assertIn('new file mode', current['diff'])
        self.assertIn('diff --git a/empty.py b/empty.py', current['diff'])
        self.assertNotIn('unrelated.py', current['diff'])
        self.assertIsNone(current['files']['test_calculator.py'])
        self.assertEqual(current['files']['empty.py'], '')
        self.assertEqual(state['requirements'], (ROOT/'tests/fixtures/requirements.md').read_text())

    def test_initialize_rejects_symlinked_scope_parent(self):
        (self.project/'.gitignore').write_text('__pycache__/\nbuild/\n')
        (self.project/'build').mkdir()
        for alias, destination, leaf in (('gitlink', '.git', 'hooks/pre-commit'),
                                          ('buildlink', 'build', 'output.py')):
            with self.subTest(destination=destination):
                (self.project/alias).symlink_to(destination, target_is_directory=True)
                self.args.scope = [f'{alias}/{leaf}']
                with self.assertRaisesRegex(r.ReviewError, 'Scope escapes project or uses symlink'):
                    r.initialize(self.args)

    def test_freshness_rejects_ignored_symlinked_scope_parent(self):
        (self.project/'.gitignore').write_text('__pycache__/\nbuild/\nalias\n')
        (self.project/'build').mkdir()
        self.args.scope = ['calculator.py', 'alias/leaf.py']
        _, state = r.initialize(self.args)
        self.assertIsNotNone(r.target(state)['files']['calculator.py'])
        self.assertIsNone(r.target(state)['files']['alias/leaf.py'])
        r.assert_fresh(state)
        (self.project/'alias').symlink_to('build', target_is_directory=True)
        self.assertEqual(r.inventory(self.project), state['inventory'])
        with self.assertRaisesRegex(r.ReviewError, 'Scope escapes project or uses symlink'):
            r.target(state)
        with self.assertRaisesRegex(r.ReviewError, 'Scope escapes project or uses symlink'):
            r.assert_fresh(state)

    def test_no_readonly_writes(self):
        (self.project/'calculator.py').write_text('changed')
        with self.assertRaises(r.ReviewError): self.accept(self.response([]))

    def test_out_of_scope_writes_rejected(self):
        self.to_repair()
        (self.project/'unrelated.py').write_text('changed')
        with self.assertRaises(r.ReviewError): self.accept(self.response())

    def test_implementation_cycle(self):
        self.to_repair()
        lock = self.state['ledger'][-1]['repair_lock']
        artifact = r.read_json(self.run/'artifacts/revision-002.json')
        self.assertEqual(artifact['repair_lock'], lock)
        self.assertEqual(r.packet(self.state)['repair_lock'], lock)
        self.assertEqual(lock['handoff_revision'], self.state['handoff_revision'])
        self.assertEqual(lock['target_fingerprint'], self.state['target_fingerprint'])
        self.assertEqual(lock['scope'], self.state['scope'])
        self.assertEqual(lock['checks'], self.state['check_commands'])
        self.assertEqual([item['id'] for item in lock['accepted_findings']], ['FIND-001'])
        handoff = (self.run/'handoff.md').read_text()
        self.assertIn('Repair lock:', handoff)
        self.assertIn('## Scoped diff', handoff)
        self.assertIn('```diff', handoff)
        self.assertIn('+    return sum(values) / (len(values) + 1)', handoff)
        p=self.project/'calculator.py'
        p.write_text(p.read_text().replace('(len(values) + 1)', 'len(values)'))
        self.accept(self.response())
        self.assertEqual(self.state['checks'][0]['exit_code'],0)
        data=self.response()
        data['findings'][0].update(verification_status='PASSED', verification_evidence=['SOURCE:calculator.py','CHECK-1-1'], rationale='Current source and actual fixture check agree.')
        self.accept(data)
        self.assertEqual(self.state['stage'],'finalize')
        self.accept(self.response())
        self.assertEqual(self.state['status'],'complete')
        self.assertEqual([entry['stage'] for entry in self.state['ledger']],
                         ['review', 'adjudicate', 'repair', 'recheck', 'finalize'])
        artifacts=list((self.run/'artifacts').glob('*.json'))
        self.assertEqual(len(artifacts),5)
        last=json.loads(sorted(artifacts)[-1].read_text())
        self.assertEqual(last['parent_artifact_id'],'revision-004')
        self.assertTrue((self.run/'final.md').exists())
        self.assertNotIn('repair_lock', r.read_json(self.run/'artifacts/revision-003.json'))

    def test_repair_lock_rejects_missing_stale_or_changed_authority(self):
        self.to_repair()
        original = copy.deepcopy(self.state['ledger'][-1]['repair_lock'])
        for mutation in ('missing', 'stale', 'outside'):
            with self.subTest(mutation=mutation):
                self.state['ledger'][-1]['repair_lock'] = copy.deepcopy(original)
                if mutation == 'missing':
                    del self.state['ledger'][-1]['repair_lock']
                elif mutation == 'stale':
                    self.state['ledger'][-1]['repair_lock']['handoff_revision'] -= 1
                else:
                    self.state['ledger'][-1]['repair_lock']['scope'] = ['outside.py']
                with self.assertRaises(r.ReviewError):
                    r.advance(self.run, self.state)
        self.state['ledger'][-1]['repair_lock'] = original
        artifact_path = self.run/'artifacts/revision-002.json'
        artifact = r.read_json(artifact_path)
        artifact['repair_lock']['scope'] = ['outside.py']
        artifact_path.write_text(r.dumps(artifact))
        with self.assertRaisesRegex(r.ReviewError, 'saved adjudication artifact'):
            r.advance(self.run, self.state)

    def test_pending_decision_locks_only_after_readjudication(self):
        self.accept(self.response([finding()]))
        pending = self.response()
        pending['findings'][0].update(disposition='PENDING_USER', rationale='User must choose the behavior.')
        self.accept(pending)
        self.assertEqual(self.state['status'], 'needs_user')
        self.assertNotIn('repair_lock', self.state['ledger'][-1])
        self.state.update(status='ready', stage='adjudicate')
        self.state['handoff_revision'] += 1
        decided = self.response()
        decided['findings'][0].update(disposition='ACCEPTED', rationale='User authorized the scoped correction.')
        self.accept(decided)
        self.assertEqual(self.state['stage'], 'repair')
        self.assertEqual(self.state['ledger'][-1]['repair_lock']['handoff_revision'],
                         self.state['handoff_revision'])

    def test_new_recheck_finding_ends_unresolved_without_second_repair(self):
        self.to_repair()
        p = self.project/'calculator.py'
        p.write_text(p.read_text().replace('(len(values) + 1)', 'len(values)'))
        self.accept(self.response())
        checked = self.response()
        checked['findings'][0].update(verification_status='PASSED',
                                      verification_evidence=['CHECK-1-1'],
                                      rationale='The corrected average passes its focused test.')
        newly_found = finding()
        newly_found.update(id='FIND-002', location='test_calculator.py:4',
                           evidence='A separate in-scope gap is visible at recheck.')
        checked['findings'].append(newly_found)
        self.accept(checked)
        self.assertEqual(self.state['status'], 'unresolved')
        self.assertEqual([entry['stage'] for entry in self.state['ledger']],
                         ['review', 'adjudicate', 'repair', 'recheck'])

    def test_check_only_failure_recovers_finalization_without_repair(self):
        marker = self.root/'check-ready'
        self.state['check_commands'] = [[
            sys.executable, '-c',
            f'import pathlib,sys; sys.exit(0 if pathlib.Path({str(marker)!r}).exists() else 1)',
        ]]
        self.to_repair()
        p = self.project/'calculator.py'
        p.write_text(p.read_text().replace('(len(values) + 1)', 'len(values)'))
        self.accept(self.response())
        checked = self.response()
        checked['findings'][0].update(verification_status='PASSED',
                                      verification_evidence=['SOURCE:calculator.py'],
                                      rationale='The scoped source uses the actual value count.')
        self.accept(checked)
        self.assertEqual((self.state['stage'], self.state['status']), ('finalize', 'unresolved'))
        marker.write_text('ready')
        r.rerun_checks(self.run, self.state)
        self.assertEqual((self.state['stage'], self.state['status']), ('finalize', 'ready'))
        self.accept(self.response())
        self.assertEqual(self.state['status'], 'complete')

    def test_check_rerun_keeps_cited_receipt_for_finalization(self):
        marker = self.root/'check-ready'
        self.state['check_commands'] = [
            [sys.executable, '-c', 'pass'],
            [sys.executable, '-c',
             f'import pathlib,sys; sys.exit(0 if pathlib.Path({str(marker)!r}).exists() else 1)'],
        ]
        self.to_repair()
        p = self.project/'calculator.py'
        p.write_text(p.read_text().replace('(len(values) + 1)', 'len(values)'))
        self.accept(self.response())
        self.assertEqual([check['exit_code'] for check in self.state['checks']], [0, 1])
        checked = self.response()
        checked['findings'][0].update(verification_status='PASSED',
                                      verification_evidence=['CHECK-1-1'],
                                      rationale='The passing focused check covers the corrected average.')
        self.accept(checked)
        self.assertEqual((self.state['stage'], self.state['status']), ('finalize', 'unresolved'))
        reviewed_findings = copy.deepcopy(self.state['findings'])
        with self.assertRaisesRegex(r.ReviewError, 'all configured checks passing'):
            r.validate_response(self.state, self.response())

        r.rerun_checks(self.run, self.state)
        self.assertEqual(self.state['status'], 'unresolved')
        self.assertFalse(r.checks_pass(self.state))
        marker.write_text('ready')
        r.rerun_checks(self.run, self.state)
        self.assertEqual((self.state['stage'], self.state['status']), ('finalize', 'ready'))
        self.state = r.read_json(self.run/'state.json')
        self.assertEqual(self.state['findings'], reviewed_findings)
        self.assertIn('CHECK-1-1', r.evidence_catalog(self.state))
        self.assertIn('CHECK-1-1', r.provider_schema(self.state)['properties']['findings']
                      ['items']['properties']['verification_evidence']['items']['enum'])
        stale = copy.deepcopy(self.state['cited_check_receipts']['CHECK-1-1'])
        stale.update(id='CHECK-stale', target_fingerprint='0'*64)
        self.state['cited_check_receipts']['CHECK-stale'] = stale
        self.assertNotIn('CHECK-stale', r.evidence_catalog(self.state))
        invalid = self.response()
        invalid['findings'][0]['verification_evidence'] = ['CHECK-stale']
        with self.assertRaisesRegex(r.ReviewError, 'unavailable or stale'):
            r.validate_response(self.state, invalid)
        self.accept(self.response())
        self.assertEqual(self.state['status'], 'complete')
        self.assertEqual(self.state['findings'], reviewed_findings)
        self.assertEqual([entry['stage'] for entry in self.state['ledger'] if entry['stage'] == 'repair'],
                         ['repair'])

    def test_legacy_plan_never_repairs(self):
        self.args.mode='plan'
        self.args.plan=str(ROOT/'tests/fixtures/sound-plan.md')
        self.run,self.state=r.initialize(self.args)
        self.state.pop('plan_protocol_version')
        self.accept(self.response([]))
        self.assertEqual(self.state['stage'],'refine')
        data=self.response([])
        data['plan_markdown']='A complete fixture plan preserving scope and meaningful acceptance checks.'
        self.accept(data)
        self.accept(self.response([]))
        data=self.response([])
        data['plan_markdown']=self.state['current_plan']
        self.accept(data)
        self.assertEqual(self.state['status'],'complete')
        self.assertFalse(any(x['stage']=='repair' for x in self.state['ledger']))
        self.assertEqual(r.inventory(self.project),self.state['inventory'])

    def test_final_plan_cannot_change_after_recheck(self):
        self.args.mode='plan'; self.args.plan=str(ROOT/'tests/fixtures/sound-plan.md')
        self.run,self.state=r.initialize(self.args)
        self.state.pop('plan_protocol_version')
        self.state.update(stage='finalize',current_plan='Reviewed plan')
        data=self.response([]); data['plan_markdown']='Different plan'
        with self.assertRaises(r.ReviewError): r.validate_response(self.state,data)

    def test_missing_findings_and_invented_evidence_rejected(self):
        self.state['findings']=[finding()]; self.state['stage']='recheck'
        with self.assertRaises(r.ReviewError): r.validate_response(self.state,self.response([]))
        data=self.response(); data['findings'][0].update(disposition='ACCEPTED',rationale='Claim', verification_status='PASSED',verification_evidence=['invented'])
        with self.assertRaises(r.ReviewError): r.validate_response(self.state,data)

    def test_closed_dispositions_cannot_be_overridden_by_repair(self):
        self.to_repair()
        data=self.response(); data['findings'][0].update(disposition='REJECTED',rationale='Changed mind')
        with self.assertRaises(r.ReviewError): r.validate_response(self.state,data)

    def test_coordinator_receives_both_advisory_assessments(self):
        self.state['implementation_evidence_version'] = 1
        self.accept(self.response([finding()]))
        implementer = self.response()
        implementer['findings'][0].update(
            disposition='ACCEPTED', rationale='Implementer recommends accepting the reproduced defect.',
        )
        self.accept(implementer)
        self.assertEqual(self.state['findings'][0]['disposition'], 'OPEN')
        reviewer = self.response()
        reviewer['findings'][0].update(
            disposition='ACCEPTED', rationale='Reviewer independently agrees with the recommendation.',
        )
        self.accept(reviewer)
        self.assertEqual(self.state['stage'], 'adjudicate')
        self.assertEqual(self.state['findings'][0]['disposition'], 'OPEN')
        history = r.packet(self.state)['decision_ledger']
        self.assertEqual([entry['stage'] for entry in history], ['review', 'respond', 'reply'])
        self.assertEqual(
            history[1]['finding_assessments'][0]['rationale'],
            'Implementer recommends accepting the reproduced defect.',
        )
        self.assertEqual(
            history[2]['finding_assessments'][0]['rationale'],
            'Reviewer independently agrees with the recommendation.',
        )
        coordinator = self.response()
        coordinator['findings'][0].update(
            disposition='ACCEPTED', rationale='Coordinator authoritatively accepts the finding.',
        )
        self.accept(coordinator)
        self.assertEqual(self.state['stage'], 'repair')
        self.assertEqual(self.state['findings'][0]['disposition'], 'ACCEPTED')
        artifact = r.read_json(self.run/'artifacts/revision-004.json')
        self.assertEqual(artifact['response']['findings'][0]['evidence'], finding()['evidence'])
        self.assertEqual(artifact['response']['findings'][0]['disposition'], 'ACCEPTED')

    def test_only_recheck_can_change_implementation_verification(self):
        self.accept(self.response([finding()]))
        coordinator = self.response()
        coordinator['findings'][0].update(
            disposition='ACCEPTED', rationale='Adjudication cannot set verification.',
            verification_status='FAILED',
        )
        with self.assertRaisesRegex(r.ReviewError, 'Only independent recheck'):
            r.validate_response(self.state, coordinator)

    def test_recheck_preserves_dispositions_and_allows_new_findings(self):
        accepted=finding(); accepted.update(disposition='ACCEPTED',rationale='Adjudicated defect.')
        self.state.update(stage='recheck',findings=[accepted])
        data=self.response()
        data['findings'][0].update(disposition='REJECTED',rationale='Changed mind at recheck.')
        with self.assertRaises(r.ReviewError): r.validate_response(self.state,data)
        new=finding(); new.update(id='FIND-002')
        data=self.response([accepted,new])
        r.validate_response(self.state,data)

    def test_false_positive_retained(self):
        self.use_passing_check()
        self.accept(self.response([finding()]))
        data=self.response(); data['findings'][0].update(disposition='REJECTED',rationale='Coordinator rejects the unsupported finding.')
        self.accept(data)
        self.assertEqual(self.state['stage'],'finalize')
        self.accept(self.response())
        self.assertEqual(self.state['findings'][0]['disposition'],'REJECTED')
        self.assertEqual([entry['stage'] for entry in self.state['ledger']],
                         ['review', 'adjudicate', 'finalize'])

    def test_default_profile_is_frozen_into_new_runs(self):
        expected = {
            'reviewer': {'model': 'claude-opus-5-5', 'effort': 'high'},
            'coordinator': {'model': 'gpt-6-astra', 'effort': 'max'},
            'implementer': {'model': 'gpt-6.1-sol', 'effort': 'xhigh'},
        }
        self.assertEqual(self.state['schema_version'], 2)
        self.assertEqual(self.state['implementation_evidence_version'], 2)
        self.assertEqual(self.state['agent_profile'], expected)
        self.assertEqual(r.read_json(self.run/'state.json')['agent_profile'], expected)
        original = r.read_json(self.run/'original.json')
        self.assertEqual(original['agent_profile'], expected)

    def test_plan_default_profile_is_unchanged(self):
        args = copy.deepcopy(self.args)
        args.mode = 'plan'
        args.plan = str(ROOT/'tests/fixtures/sound-plan.md')
        run, state = r.initialize(args)
        expected = {
            'reviewer': {'model': 'claude-opus-5-5', 'effort': 'high'},
            'coordinator': {'model': 'gpt-6-astra', 'effort': 'max'},
        }
        self.assertEqual(state['agent_profile'], expected)
        self.assertEqual(r.read_json(run/'original.json')['agent_profile'], expected)

    def test_implementer_commands_use_frozen_new_default(self):
        self.to_repair()
        with patch.dict(r.DEFAULT_PROFILES['review-implementation']['implementer'],
                        {'model': 'gpt-future-default', 'effort': 'low'}), patch.object(
                            r, 'load_runtime_config', side_effect=AssertionError('Must use frozen profile')):
            for session in (None, '11111111-1111-4111-8111-111111111111'):
                with self.subTest(session=session):
                    state = r.read_json(self.run/'state.json')
                    state['sessions']['sol'] = session
                    r.save(self.run, state)
                    argv = r.cli_argv(r.read_json(self.run/'state.json'), self.run)
                    self.assertEqual(argv[argv.index('--model')+1], 'gpt-6.1-sol')
                    self.assertIn('model_reasoning_effort="xhigh"', argv)
                    self.assertEqual('resume' in argv, session is not None)
                    if session:
                        self.assertEqual(argv[-2:], [session, '-'])

    def test_version_two_sol_six_runs_keep_frozen_implementer(self):
        with patch.dict(r.DEFAULT_PROFILES['review-implementation']['implementer'],
                        {'model': 'gpt-6-sol', 'effort': 'xhigh'}):
            run, state = r.initialize(copy.deepcopy(self.args))
        self.assertEqual(state['schema_version'], 2)
        self.assertEqual(r.DEFAULT_PROFILES['review-implementation']['implementer']['model'], 'gpt-6.1-sol')
        original_bytes = (run/'original.json').read_bytes()
        for session in (None, '11111111-1111-4111-8111-111111111111'):
            with self.subTest(session=session):
                state['stage'] = 'repair'
                state['sessions']['sol'] = session
                r.save(run, state)
                saved_bytes = (run/'state.json').read_bytes()
                loaded = r.read_json(run/'state.json')
                self.assertEqual(loaded['agent_profile']['implementer'],
                                 {'model': 'gpt-6-sol', 'effort': 'xhigh'})
                argv = r.cli_argv(loaded, run)
                self.assertEqual(argv[argv.index('--model')+1], 'gpt-6-sol')
                self.assertIn('model_reasoning_effort="xhigh"', argv)
                self.assertEqual('resume' in argv, session is not None)
                if session:
                    self.assertEqual(argv[-2:], [session, '-'])
                self.assertEqual((run/'state.json').read_bytes(), saved_bytes)
                self.assertEqual((run/'original.json').read_bytes(), original_bytes)

    def test_explicit_sol_six_implementer_overrides_retain_precedence(self):
        config_path = self.root/'runtime.local.json'
        for configured, override, expected in (
            ({'model': 'gpt-6-sol'}, {}, {'model': 'gpt-6-sol', 'effort': 'xhigh'}),
            ({'model': 'gpt-6.1-sol', 'effort': 'high'}, {'model': 'gpt-6-sol'},
             {'model': 'gpt-6-sol', 'effort': 'high'}),
            ({'model': 'gpt-6.1-sol', 'effort': 'high'}, {'model': 'gpt-6-sol', 'effort': 'xhigh'},
             {'model': 'gpt-6-sol', 'effort': 'xhigh'}),
        ):
            with self.subTest(configured=configured, override=override):
                config_path.write_text(json.dumps({'skills': {'review-implementation': {
                    'implementer': configured,
                }}}))
                args = copy.deepcopy(self.args)
                for field, value in override.items():
                    setattr(args, f'implementer_{field}', value)
                run, state = r.initialize(args)
                self.assertEqual(state['agent_profile']['implementer'], expected)
                self.assertEqual(r.read_json(run/'original.json')['agent_profile']['implementer'], expected)

    def test_per_skill_config_and_run_overrides_resolve_independently(self):
        config_path = self.root/'runtime.local.json'
        config_path.write_text(json.dumps({'skills': {
            'review-plan': {
                'reviewer': {'model': 'claude-plan-reviewer', 'effort': 'medium'},
                'coordinator': {'model': 'gpt-plan-coordinator', 'effort': 'high'},
            },
            'review-implementation': {
                'reviewer': {'model': 'claude-implementation-reviewer', 'effort': 'xhigh'},
                'coordinator': {'model': 'gpt-implementation-coordinator', 'effort': 'ultra'},
                'implementer': {'model': 'gpt-implementation-writer', 'effort': 'low'},
            },
        }}))
        plan_args = copy.deepcopy(self.args)
        plan_args.mode = 'plan'
        plan_args.plan = str(ROOT/'tests/fixtures/sound-plan.md')
        plan_args.coordinator_model = 'gpt-run-override'
        plan_args.coordinator_effort = 'max'
        implementation_args = copy.deepcopy(self.args)
        implementation_args.implementer_effort = 'medium'
        with patch.object(r, 'RUNTIME_CONFIG', config_path):
            _, plan_state = r.initialize(plan_args)
            _, implementation_state = r.initialize(implementation_args)
        self.assertEqual(plan_state['agent_profile'], {
            'reviewer': {'model': 'claude-plan-reviewer', 'effort': 'medium'},
            'coordinator': {'model': 'gpt-run-override', 'effort': 'max'},
        })
        self.assertEqual(implementation_state['agent_profile']['reviewer']['model'],
                         'claude-implementation-reviewer')
        self.assertEqual(implementation_state['agent_profile']['coordinator']['effort'], 'ultra')
        self.assertEqual(implementation_state['agent_profile']['implementer'],
                         {'model': 'gpt-implementation-writer', 'effort': 'medium'})

    def test_run_profile_does_not_drift_with_runtime_config(self):
        config_path = self.root/'runtime.local.json'
        config_path.write_text(json.dumps({'skills': {'review-implementation': {
            'coordinator': {'model': 'gpt-frozen', 'effort': 'high'},
        }}}))
        with patch.object(r, 'RUNTIME_CONFIG', config_path):
            run, state = r.initialize(copy.deepcopy(self.args))
        config_path.write_text(json.dumps({'skills': {'review-implementation': {
            'coordinator': {'model': 'gpt-changed', 'effort': 'max'},
        }}}))
        state['stage'] = 'adjudicate'
        self.assertEqual(r.agent_settings(state, 'astra'), ('gpt-frozen', 'high'))
        self.assertIn('gpt-frozen', r.cli_argv(state, run))
        config_path.unlink()
        self.assertEqual(r.agent_settings(state, 'astra'), ('gpt-frozen', 'high'))

    def test_malformed_runtime_profiles_fail_before_run_creation(self):
        cases = [
            '{',
            json.dumps({'unexpected': True}),
            json.dumps({'skills': {'unknown-skill': {}}}),
            json.dumps({'skills': {'review-plan': {'implementer': {}}}}),
            json.dumps({'skills': {'review-plan': {'reviewer': {'temperature': 'hot'}}}}),
            json.dumps({'skills': {'review-plan': {'reviewer': {'model': '   '}}}}),
            json.dumps({'skills': {'review-plan': {'reviewer': {'effort': 'ultra'}}}}),
        ]
        for index, content in enumerate(cases):
            with self.subTest(content=content):
                config_path = self.root/f'invalid-{index}.json'
                config_path.write_text(content)
                args = copy.deepcopy(self.args)
                args.runs_dir = str(self.root/f'invalid-runs-{index}')
                with patch.object(r, 'RUNTIME_CONFIG', config_path), self.assertRaises(r.ReviewError):
                    r.initialize(args)
                self.assertFalse(Path(args.runs_dir).exists())

    def test_plan_rejects_implementer_override_before_run_creation(self):
        config_path = self.root/'empty-runtime.json'
        config_path.write_text('{}')
        args = copy.deepcopy(self.args)
        args.mode = 'plan'
        args.plan = str(ROOT/'tests/fixtures/sound-plan.md')
        args.implementer_model = 'gpt-6-sol'
        args.runs_dir = str(self.root/'invalid-plan-runs')
        with patch.object(r, 'RUNTIME_CONFIG', config_path), self.assertRaisesRegex(
                r.ReviewError, 'do not have an implementer'):
            r.initialize(args)
        self.assertFalse(Path(args.runs_dir).exists())

    def test_version_one_runs_keep_original_pins(self):
        legacy = copy.deepcopy(self.state)
        legacy['schema_version'] = 1
        legacy.pop('agent_profile')
        expected = {
            'reviewer': {'model': 'claude-opus-5-5', 'effort': 'high'},
            'coordinator': {'model': 'gpt-6-astra', 'effort': 'max'},
            'implementer': {'model': 'gpt-6-sol', 'effort': 'xhigh'},
        }
        with patch.dict(r.DEFAULT_PROFILES['review-implementation']['implementer'],
                        {'model': 'gpt-future-default', 'effort': 'low'}):
            self.assertEqual(r.V1_PROFILES['review-implementation'], expected)
            self.assertEqual(r.V1_PROFILES['review-plan'],
                             {key: value for key, value in expected.items() if key != 'implementer'})
            self.assertEqual(r.effective_profile(legacy), expected)
            for who, stage in [('opus', 'review'), ('astra', 'adjudicate'), ('sol', 'repair')]:
                legacy['stage'] = stage
                model, effort = r.agent_settings(legacy, who)
                settings = expected[r.AGENT_TO_PROFILE_ROLE[who]]
                self.assertEqual((model, effort), (settings['model'], settings['effort']))
                argv = r.cli_argv(legacy, self.run)
                self.assertEqual(argv[argv.index('--model')+1], settings['model'])
                if who == 'opus':
                    self.assertEqual(argv[argv.index('--effort')+1], settings['effort'])
                else:
                    self.assertIn(f'model_reasoning_effort="{settings["effort"]}"', argv)
        legacy['schema_version'] = 2
        with self.assertRaisesRegex(r.ReviewError, 'missing its frozen'):
            r.effective_profile(legacy)

    def test_model_settings_on_resume(self):
        self.state['agent_profile'] = {
            'reviewer': {'model': 'claude-custom-reviewer', 'effort': 'medium'},
            'coordinator': {'model': 'gpt-custom-coordinator', 'effort': 'high'},
            'implementer': {'model': 'gpt-custom-implementer', 'effort': 'max'},
        }
        for who,stage in [('opus','review'),('astra','adjudicate'),('sol','repair')]:
            self.state['stage']=stage; self.state['sessions'][who]='11111111-1111-4111-8111-111111111111'
            argv=r.cli_argv(self.state,self.run)
            model, effort = r.agent_settings(self.state, who)
            self.assertIn(model,argv)
            self.assertNotIn('--last',argv)
            if who=='opus':
                self.assertIn('--safe-mode',argv); self.assertIn('Read,Glob,Grep',argv)
                self.assertIn('--restricted',argv); self.assertIn('mcp__*',argv)
                self.assertEqual(argv[argv.index('--effort')+1],effort)
            else:
                self.assertIn(f'model_reasoning_effort="{effort}"',argv)
                self.assertIn('sandbox_mode="'+('workspace-write' if who=='sol' else 'read-only')+'"',argv)
                if who=='sol': self.assertIn('sandbox_workspace_write.writable_roots='+json.dumps([str(self.project)]),argv)

    def test_plan_cannot_resolve_an_implementation_stage(self):
        self.state.update(mode='plan', stage='repair',
                          agent_profile=copy.deepcopy(r.DEFAULT_PROFILES['review-plan']))
        with self.assertRaisesRegex(r.ReviewError, 'has no implementer role'):
            r.cli_argv(self.state,self.run)

    def test_profile_is_visible_in_status_packet_receipt_and_handoff(self):
        self.state['agent_profile']['reviewer'] = {
            'model': 'claude-visible-reviewer', 'effort': 'medium'}
        payload = r.status_payload(self.run, self.state)
        self.assertEqual(payload['agent_profile'], self.state['agent_profile'])
        self.assertEqual(r.packet(self.state)['agent_profile'], self.state['agent_profile'])
        self.use_passing_check()
        self.accept(self.response([]))
        self.assertEqual(self.state['ledger'][0]['agent']['model'], 'claude-visible-reviewer')
        handoff = (self.run/'handoff.md').read_text()
        self.assertIn('Reviewer (Claude): claude-visible-reviewer (medium)', handoff)
        self.assertIn('By claude-visible-reviewer (medium)', handoff)

    def test_parser_accepts_per_run_profile_flags(self):
        args = r.build_parser().parse_args([
            'start', 'plan', '--requirements', str(ROOT/'tests/fixtures/requirements.md'),
            '--plan', str(ROOT/'tests/fixtures/sound-plan.md'),
            '--reviewer-model', 'claude-custom', '--reviewer-effort', 'xhigh',
            '--coordinator-model', 'gpt-custom', '--coordinator-effort', 'ultra',
        ])
        self.assertEqual(args.reviewer_model, 'claude-custom')
        self.assertEqual(args.reviewer_effort, 'xhigh')
        self.assertEqual(args.coordinator_model, 'gpt-custom')
        self.assertEqual(args.coordinator_effort, 'ultra')

    def test_paths_and_symlink_execution(self):
        with patch.dict(os.environ,{'CODEX_HOME':str(self.root/'codex')},clear=True):
            self.assertEqual(r.runs_root(),self.root/'codex/review-runs')
            with patch.dict(os.environ,{'AGENT_REVIEW_RUNS_DIR':str(self.root/'env')}):
                self.assertEqual(r.runs_root(),self.root/'env')
                self.assertEqual(r.runs_root(str(self.root/'cli')),self.root/'cli')
        link=self.root/'helper.py'; link.symlink_to(ROOT/'scripts/review_cli.py')
        result=subprocess.run([sys.executable,str(link),'--help'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_single_project_lock(self):
        with r.project_lock(self.project):
            with self.assertRaises(r.ReviewError):
                with r.project_lock(self.project): pass

    def test_unsafe_lock_directories_rejected(self):
        lock_root=self.root/'lock-root'; lock_root.mkdir()
        uid=os.getuid()
        locks=lock_root/f'agent-review-locks-{uid}'
        with patch.object(r,'LOCK_ROOT',lock_root):
            locks.mkdir(mode=0o700)
            locks.chmod(0o770)
            with self.assertRaises(r.ReviewError):
                with r.project_lock(self.project): pass
            locks.chmod(0o700)
            locks.rmdir()
            private=self.root/'private'; private.mkdir(mode=0o700)
            locks.symlink_to(private,target_is_directory=True)
            with self.assertRaises(r.ReviewError):
                with r.project_lock(self.project): pass
            locks.unlink()
            foreign=lock_root/f'agent-review-locks-{uid+1}'
            foreign.mkdir(mode=0o700)
            with patch.object(r.os,'getuid',return_value=uid+1):
                with self.assertRaises(r.ReviewError):
                    with r.project_lock(self.project): pass

    def test_symlinked_lock_file_rejected_without_target_write(self):
        lock_root=self.root/'lock-root'; lock_root.mkdir()
        locks=lock_root/f'agent-review-locks-{os.getuid()}'
        locks.mkdir(mode=0o700)
        target=self.root/'untouched.txt'; target.write_text('keep this content')
        (locks/(r.digest(str(self.project))+'.lock')).symlink_to(target)
        with patch.object(r,'LOCK_ROOT',lock_root):
            with self.assertRaises(r.ReviewError):
                with r.project_lock(self.project): pass
        self.assertEqual(target.read_text(),'keep this content')

    def test_one_repair_pass_limit(self):
        self.to_repair()
        self.state['round'] = 1
        with self.assertRaisesRegex(r.ReviewError, 'one repair pass'):
            r.advance(self.run,self.state)

    def test_check_failure_does_not_complete(self):
        self.to_repair(); self.accept(self.response())
        self.assertNotEqual(self.state['checks'][0]['exit_code'],0)
        data=self.response(); data['findings'][0].update(verification_status='FAILED',rationale='Acceptance test still fails.')
        self.accept(data)
        self.assertEqual(self.state['stage'],'recheck')
        self.assertEqual(self.state['status'],'unresolved')
        self.assertEqual(self.state['ledger'][-1]['stage'], 'recheck')

    def test_version_one_failed_recheck_and_two_pass_limit(self):
        self.state['implementation_evidence_version'] = 1
        self.accept(self.response([finding()]))
        for rationale in ('Implementer recommends repair.', 'Reviewer agrees with repair.'):
            advisory = self.response()
            advisory['findings'][0].update(disposition='ACCEPTED', rationale=rationale)
            self.accept(advisory)
        decision = self.response()
        decision['findings'][0].update(disposition='ACCEPTED', rationale='Coordinator accepts repair.')
        self.accept(decision)
        self.assertEqual(self.state['stage'], 'repair')
        self.accept(self.response())
        recheck = self.response()
        recheck['findings'][0].update(verification_status='FAILED',
                                     rationale='The configured acceptance check still fails.')
        self.accept(recheck)
        self.assertEqual(self.state['stage'], 'respond')
        self.state.update(stage='repair', round=2)
        with self.assertRaisesRegex(r.ReviewError, 'Two-pass limit reached'):
            r.advance(self.run, self.state)

    def test_external_coordinator_yield(self):
        self.state['stage']='adjudicate'
        self.state['agent_profile']['coordinator'] = {'model': 'gpt-6-luna', 'effort': 'high'}
        r.advance(self.run,self.state,external_coordinator=True)
        self.assertEqual(self.state['status'],'awaiting_coordinator')
        request=r.read_json(self.run/'external-request.json')
        self.assertEqual(request['required_model'],'gpt-6-luna')
        self.assertEqual(request['required_effort'],'high')
        self.assertEqual(request['packet']['run_id'],self.state['run_id'])

    def test_external_submission_must_match_frozen_profile(self):
        self.state['agent_profile']['coordinator'] = {'model': 'gpt-6-luna', 'effort': 'high'}
        with self.assertRaisesRegex(r.ReviewError, 'exactly match'):
            r.external_submission_config(self.state, 'gpt-6-astra', 'max')
        config = r.external_submission_config(self.state, 'gpt-6-luna', 'high')
        self.assertEqual(config['model'], 'gpt-6-luna')
        self.assertEqual(config['effort'], 'high')

    def test_external_astra_is_a_compatibility_alias(self):
        parser = r.build_parser()
        canonical = parser.parse_args(['run', str(self.run), '--external-coordinator'])
        legacy = parser.parse_args(['run', str(self.run), '--external-astra'])
        self.assertTrue(canonical.external_coordinator)
        self.assertTrue(legacy.external_coordinator)

    def test_step_dispatches_one_stage_with_frozen_profile(self):
        for mode, version, next_stage in (
            ('plan', None, 'respond'),
            ('plan', 2, 'adjudicate'),
            ('implementation', 1, 'respond'),
            ('implementation', 2, 'adjudicate'),
        ):
            with self.subTest(mode=mode, version=version):
                args = copy.deepcopy(self.args)
                args.mode = mode
                args.plan = str(ROOT/'tests/fixtures/sound-plan.md') if mode == 'plan' else None
                self.run, self.state = r.initialize(args)
                if mode == 'plan' and version is None:
                    self.state.pop('plan_protocol_version')
                elif mode == 'implementation' and version is not None:
                    self.state['implementation_evidence_version'] = version
                self.state['agent_profile']['reviewer'] = {'model': 'fixture-reviewer', 'effort': 'low'}
                if mode == 'implementation':
                    self.use_passing_check()
                r.save(self.run, self.state)
                response = self.response([finding()])
                if mode == 'plan' and version == 2:
                    response.pop('findings')
                    response.pop('plan_markdown')
                    response.update(plan_protocol_version=2, new_findings=[
                        {key: finding()[key] for key in r.FINDING_DEFINITION_FIELDS}])
                config = {'model': 'fixture-reviewer', 'effort': 'low', 'observed': {'source': 'fixture'}}
                with patch.object(sys, 'argv', ['review_cli.py', 'step', str(self.run)]), \
                        patch.object(sys, 'stdout', new_callable=io.StringIO) as output, \
                        patch.object(r, 'execute_process') as execute, \
                        patch.object(r, 'extract_response', return_value=(response, None, config)):
                    r.main()
                execute.assert_called_once()
                argv = execute.call_args.args[0]
                self.assertEqual(argv[argv.index('--model') + 1], 'fixture-reviewer')
                self.assertEqual(argv[argv.index('--effort') + 1], 'low')
                self.assertIn(r.dumps(r.packet(self.state)), execute.call_args.args[2])
                saved = r.read_json(self.run/'state.json')
                self.assertEqual(saved['stage'], next_stage)
                self.assertEqual(saved['status'], 'ready')
                self.assertEqual(saved['handoff_revision'], 1)
                self.assertEqual(len(saved['ledger']), 1)
                self.assertEqual(len(list((self.run/'calls').iterdir())), 1)
                self.assertIn(f'"stage": "{next_stage}"', output.getvalue())
                self.assertIn(str(self.run/'handoff.md'), output.getvalue())

    def test_step_does_not_dispatch_or_recover_nonready_runs(self):
        self.use_passing_check()
        self.accept(self.response([]))
        self.accept(self.response([]))
        self.assertEqual(self.state['status'], 'complete')
        for status in ('blocked', 'interrupted', 'running', 'complete', 'unresolved',
                       'needs_user', 'awaiting_coordinator', 'awaiting_astra'):
            with self.subTest(status=status):
                self.state['status'] = status
                r.save(self.run, self.state)
                original = (self.run/'state.json').read_bytes()
                with patch.object(sys, 'argv', ['review_cli.py', 'step', str(self.run)]), \
                        patch.object(sys, 'stdout', new_callable=io.StringIO) as output, \
                        patch.object(r, 'advance') as advance:
                    r.main()
                advance.assert_not_called()
                self.assertEqual((self.run/'state.json').read_bytes(), original)
                self.assertEqual(list((self.run/'calls').iterdir()), [])
                self.assertIn(f'"status": "{status}"', output.getvalue())

    def test_step_rejects_stale_target_before_dispatch(self):
        (self.project/'calculator.py').write_text('changed after run creation')
        original = (self.run/'state.json').read_bytes()
        with patch.object(sys, 'argv', ['review_cli.py', 'step', str(self.run)]), \
                patch.object(sys, 'stdout', new_callable=io.StringIO), \
                patch.object(sys, 'stderr', new_callable=io.StringIO), \
                patch.object(r, 'execute_process') as execute, \
                self.assertRaises(SystemExit) as stopped:
            r.main()
        self.assertEqual(stopped.exception.code, 2)
        execute.assert_not_called()
        self.assertEqual((self.run/'state.json').read_bytes(), original)

    def test_claude_fallback_model_rejected(self):
        call=self.root/'call'; call.mkdir()
        (call/'stdout.log').write_text(json.dumps({'structured_output':self.response([]),'session_id':str(__import__('uuid').uuid4()),'modelUsage':{'wrong-model':{}}}))
        with self.assertRaises(r.ReviewError): r.extract_response(self.state,call)

    def test_provider_schema_preserves_contract(self):
        self.assertNotIn('$schema', r.PROVIDER_SCHEMA)
        r.Draft202012Validator.check_schema(r.PROVIDER_SCHEMA)
        validator = r.Draft202012Validator(r.PROVIDER_SCHEMA)
        data = self.response([finding()])
        validator.validate(data)
        data.pop('handoff_revision')
        self.assertFalse(validator.is_valid(data))

    def test_advisory_schema_and_normalization_freeze_findings(self):
        self.state['implementation_evidence_version'] = 1
        first = finding()
        second = finding()
        second.update(id='FIND-002', location='test_calculator.py:4')
        for stage in ('respond', 'reply'):
            with self.subTest(stage=stage):
                self.state.update(stage=stage, findings=[first, second])
                schema = r.provider_schema(self.state)
                item = schema['properties']['findings']['items']
                self.assertEqual(set(item['properties']), {'id', 'disposition', 'rationale'})
                self.assertEqual(item['properties']['id']['enum'], ['FIND-001', 'FIND-002'])
                self.assertEqual(schema['properties']['findings']['minItems'], 2)
                self.assertEqual(schema['properties']['findings']['maxItems'], 2)
                self.assertIn('return only id, disposition, and rationale', r.prompt(self.state))

                data = self.response()
                data['findings'][0].update(disposition='ACCEPTED', rationale='The defect is reproduced.')
                data['findings'][1].update(disposition='REJECTED', rationale='The evidence disproves this finding.')
                normalized = r.normalize_response(self.state, data)
                self.assertEqual(normalized['findings'][0]['evidence'], first['evidence'])
                self.assertEqual(normalized['findings'][1]['location'], second['location'])
                self.assertEqual(normalized['findings'][0]['disposition'], 'ACCEPTED')
                self.assertEqual(normalized['findings'][1]['disposition'], 'REJECTED')

                mutations = [
                    lambda value: value['findings'].pop(),
                    lambda value: value['findings'].append(copy.deepcopy(value['findings'][0])),
                    lambda value: value['findings'].reverse(),
                    lambda value: value['findings'][0].update(id='FIND-999'),
                    lambda value: value['findings'][0].update(evidence='Changed definition.'),
                ]
                for mutate in mutations:
                    invalid = copy.deepcopy(data)
                    mutate(invalid)
                    with self.assertRaises(r.ReviewError):
                        r.normalize_response(self.state, invalid)

    def test_adjudication_can_add_a_scoped_finding_without_mutating_existing_findings(self):
        existing = finding()
        self.state.update(stage='adjudicate', findings=[existing])
        data = self.response()
        data['findings'][0].update(
            disposition='ACCEPTED', rationale='The original defect remains supported.',
        )
        discovered = finding()
        discovered.update(
            id='FIND-002', location='test_calculator.py:4',
            evidence='Adjudication found a second in-scope defect in the reviewed source.',
            correction_recommended='Correct the second defect within the authorized scope.',
            acceptance_check='The focused regression covers the second defect.',
            disposition='ACCEPTED', rationale='Current scoped evidence establishes the missed gap.',
        )
        data['findings'].append(discovered)
        r.validate_response(self.state, data)
        invalid_cases = []
        omitted = copy.deepcopy(data)
        omitted['findings'].pop(0)
        invalid_cases.append(omitted)
        reordered = copy.deepcopy(data)
        reordered['findings'].reverse()
        invalid_cases.append(reordered)
        mutated = copy.deepcopy(data)
        mutated['findings'][0]['evidence'] = 'Changed existing evidence.'
        invalid_cases.append(mutated)
        duplicate = copy.deepcopy(data)
        duplicate['findings'].append(copy.deepcopy(duplicate['findings'][-1]))
        invalid_cases.append(duplicate)
        out_of_scope = copy.deepcopy(data)
        out_of_scope['findings'][-1]['location'] = 'outside.py:1'
        invalid_cases.append(out_of_scope)
        verified = copy.deepcopy(data)
        verified['findings'][-1].update(
            verification_status='PASSED', verification_evidence=['SOURCE:test_calculator.py'],
        )
        invalid_cases.append(verified)
        nonsequential = copy.deepcopy(data)
        nonsequential['findings'][-1]['id'] = 'FIND-003'
        invalid_cases.append(nonsequential)
        for invalid in invalid_cases:
            with self.assertRaises(r.ReviewError):
                r.validate_response(self.state, invalid)

        self.accept(data)
        self.assertEqual(self.state['stage'], 'repair')
        self.assertEqual([item['id'] for item in self.state['findings']], ['FIND-001', 'FIND-002'])
        self.assertEqual(self.state['findings'][0]['evidence'], existing['evidence'])

    def test_advisory_artifact_retains_full_canonical_findings(self):
        self.state['implementation_evidence_version'] = 1
        self.accept(self.response([finding()]))
        data = self.response()
        data['findings'][0].update(disposition='ACCEPTED', rationale='Accept the reproduced defect.')
        self.accept(data)
        artifact = r.read_json(self.run/'artifacts/revision-002.json')
        self.assertEqual(artifact['response']['findings'][0]['evidence'], finding()['evidence'])
        self.assertEqual(artifact['response']['findings'][0]['disposition'], 'ACCEPTED')
        self.assertEqual(self.state['findings'][0]['disposition'], 'OPEN')

    def test_no_findings_cannot_bypass_configured_checks(self):
        r.perform_checks(self.run, self.state)
        self.assertNotEqual(self.state['checks'][0]['exit_code'], 0)
        self.accept(self.response([]))
        self.assertEqual(self.state['status'], 'unresolved')
        with self.assertRaises(r.ReviewError): self.accept(self.response([]))
        self.assertFalse((self.run/'final.md').exists())

    def test_check_rerun_preserves_receipts_and_invalidates_stale_handoffs(self):
        marker = self.root/'check-ready'
        self.state['check_commands'] = [[
            sys.executable, '-c',
            f'import pathlib,sys; sys.exit(0 if pathlib.Path({str(marker)!r}).exists() else 1)',
        ]]
        r.perform_checks(self.run, self.state)
        self.assertFalse(r.checks_pass(self.state))
        old_receipts = set((self.run/'checks').glob('*.json'))
        self.state.update(stage='adjudicate', findings=[finding()])
        stale = self.response()
        stale['findings'][0].update(disposition='ACCEPTED', rationale='Stale decision.')
        previous_revision = self.state['handoff_revision']
        marker.write_text('ready')

        r.rerun_checks(self.run, self.state)

        self.assertEqual(self.state['handoff_revision'], previous_revision + 1)
        self.assertTrue(r.checks_pass(self.state))
        self.assertEqual(self.state['checks'][0]['id'], 'CHECK-0-R1-1')
        self.assertTrue(old_receipts < set((self.run/'checks').glob('*.json')))
        artifact = r.read_json(self.run/'artifacts/revision-001.json')
        self.assertNotEqual(artifact['checks_before'][0]['exit_code'], 0)
        self.assertEqual(artifact['checks_after'][0]['exit_code'], 0)
        self.assertEqual(self.state['ledger'][-1]['stage'], 'rerun-checks')
        with self.assertRaises(r.ReviewError):
            r.validate_response(self.state, stale)

    def test_check_rerun_reopens_only_check_blocked_finalization(self):
        self.state['check_commands'] = [[sys.executable, '-c', 'pass']]
        self.state.update(stage='finalize', status='unresolved', findings=[],
                          error='Configured checks are missing or failing; no successful completion is claimed.')
        r.rerun_checks(self.run, self.state)
        self.assertEqual(self.state['status'], 'ready')
        self.assertIsNone(self.state['error'])
        self.assertEqual(self.state['stage'], 'finalize')

    def test_check_rerun_rejects_changed_targets_and_write_stages(self):
        self.state.update(stage='repair', status='ready')
        with self.assertRaisesRegex(r.ReviewError, 'read-only recoverable'):
            r.rerun_checks(self.run, self.state)
        self.state.update(stage='respond', status='blocked')
        (self.project/'calculator.py').write_text('changed')
        before = self.state['handoff_revision']
        with self.assertRaisesRegex(r.ReviewError, 'Project changed'):
            r.rerun_checks(self.run, self.state)
        self.assertEqual(self.state['handoff_revision'], before)

    def test_parser_exposes_check_rerun(self):
        args = r.build_parser().parse_args(['rerun-checks', str(self.run)])
        self.assertEqual(args.action, 'rerun-checks')

    def test_old_check_receipts_do_not_prove_new_target(self):
        self.state['checks'] = [{'argv': self.state['check_commands'][0], 'exit_code': 0,
                                'target_fingerprint': '0'*64}]
        self.assertFalse(r.checks_pass(self.state))

    def test_legacy_runs_keep_base_less_and_check_less_compatibility(self):
        legacy = copy.deepcopy(self.state)
        legacy.pop('implementation_evidence_version')
        legacy['base'] = None
        legacy['check_commands'] = []
        legacy['checks'] = []
        self.assertNotIn('diff', r.target(legacy))
        self.assertTrue(r.checks_pass(legacy))
        legacy['stage'] = 'respond'
        legacy['findings'] = [finding()]
        response = {
            'run_id': legacy['run_id'], 'target_fingerprint': legacy['target_fingerprint'],
            'handoff_revision': legacy['handoff_revision'], 'stage': legacy['stage'],
            'summary': 'Legacy-compatible response.', 'findings': copy.deepcopy(legacy['findings']),
            'plan_markdown': None,
        }
        response['findings'][0]['evidence'] = 'Legacy runs retain their prior mutable definition behavior.'
        r.validate_response(legacy, response)
        self.state['check_commands'] = []
        self.state['checks'] = []
        self.assertFalse(r.checks_pass(self.state))

    def test_context_revision_prevents_replay_after_user_decision(self):
        self.state['stage'] = 'adjudicate'
        stale = self.response([])
        self.state['requirements'] += '\nActual user decision.'
        self.state['handoff_revision'] += 1
        with self.assertRaises(r.ReviewError): r.validate_response(self.state, stale)

    def test_reordering_cannot_transfer_dispositions(self):
        first, second = finding(), finding()
        first.update(disposition='ACCEPTED', rationale='Accepted defect.')
        second.update(id='FIND-002', disposition='REJECTED', rationale='Rejected defect.')
        self.state.update(stage='repair', findings=[first, second])
        data = self.response([second, first])
        r.validate_response(self.state, data)
        data['findings'][0]['disposition'] = 'ACCEPTED'
        data['findings'][1]['disposition'] = 'REJECTED'
        with self.assertRaises(r.ReviewError): r.validate_response(self.state, data)

    def test_reconcile_preserves_orphan_and_resets_verification(self):
        self.to_repair()
        self.state['status'] = 'running'
        r.save(self.run, self.state)
        p = self.project/'calculator.py'
        p.write_text(p.read_text().replace('(len(values) + 1)', 'len(values)'))
        with patch.object(r, 'save', side_effect=OSError('Simulated interrupted state save')):
            with self.assertRaises(OSError): self.accept(self.response())
        self.state = r.read_json(self.run/'state.json')
        r.reconcile(self.run, self.state, 'Inspected scoped numerical fix after interrupted persistence.')
        self.assertEqual(self.state['ledger'][-1]['orphaned_artifacts'], ['revision-003'])
        self.assertEqual(self.state['findings'][0]['verification_status'], 'UNVERIFIED')
        self.assertTrue(r.checks_pass(self.state))
        data = self.response()
        data['findings'][0].update(verification_status='PASSED', verification_evidence=['CHECK-1-1'], rationale='Rechecked the recovered revision.')
        self.accept(data)
        self.assertEqual(self.state['stage'], 'finalize')
        self.assertTrue((self.run/'artifacts/revision-005.json').is_file())

    def test_timeout_records_process_exit_and_blocks_checks(self):
        self.state['check_commands'] = [[sys.executable, '-c', 'import time; time.sleep(20)']]
        self.state['timeout'] = 0.1
        with self.assertRaises(r.ReviewError): r.perform_checks(self.run, self.state)
        saved = r.read_json(self.run/'state.json')
        self.assertEqual(saved['status'], 'blocked')
        self.assertEqual(saved['checks'], [])
        receipts = list((self.run/'checks').glob('*/process.json'))
        self.assertEqual(len(receipts), 1)
        self.assertIsNotNone(r.read_json(receipts[0])['exit_code'])

    def test_installed_symlink_resources_and_idempotence(self):
        destination = self.root/'global-skills'
        argv = [sys.executable, str(ROOT/'scripts/install_skills.py'), '--skills-dir', str(destination)]
        for _ in range(2):
            result = subprocess.run(argv, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        for name in ('review-plan','review-implementation','review-handoff'):
            self.assertTrue((destination/name/'references/cli.md').is_file())
        (destination/'review-handoff').unlink()
        (destination/'review-handoff').mkdir()
        (destination/'review-plan').unlink()
        result = subprocess.run(argv, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((destination/'review-handoff').is_dir())
        self.assertFalse((destination/'review-handoff').is_symlink())
        self.assertFalse((destination/'review-plan').exists())

    def test_installer_preserves_saved_skill_profiles(self):
        source = self.root/'installer-source'
        (source/'scripts').mkdir(parents=True)
        (source/'scripts/install_skills.py').write_text((ROOT/'scripts/install_skills.py').read_text())
        for name in ('review-plan', 'review-implementation', 'review-handoff'):
            skill = source/'skills'/name
            skill.mkdir(parents=True)
            (skill/'SKILL.md').write_text(f'---\nname: {name}\ndescription: Fixture.\n---\n')
        profiles = {'review-plan': {
            'reviewer': {'model': 'claude-custom', 'effort': 'medium'},
        }}
        (source/'runtime.local.json').write_text(json.dumps({'skills': profiles}))
        result = subprocess.run([
            sys.executable, str(source/'scripts/install_skills.py'),
            '--skills-dir', str(self.root/'installed-skills'), '--codex-bin', sys.executable,
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        saved = json.loads((source/'runtime.local.json').read_text())
        self.assertEqual(saved['skills'], profiles)
        self.assertEqual(saved['codex_binary'], str(Path(sys.executable).resolve()))

    def test_child_keeps_lock_after_parent_context_closes(self):
        with r.project_lock(self.project):
            child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(20)'],
                                     pass_fds=(r.ACTIVE_LOCK.fileno(),))
        try:
            with self.assertRaises(r.ReviewError):
                with r.project_lock(self.project): pass
        finally:
            child.terminate()
            child.wait(timeout=5)
        with r.project_lock(self.project): pass

    def test_failed_checkpoint_does_not_double_count_repair(self):
        self.to_repair()
        before = copy.deepcopy(self.state)
        p = self.project/'calculator.py'
        p.write_text(p.read_text().replace('(len(values) + 1)', 'len(values)'))
        with patch.object(r, 'save', side_effect=OSError('Simulated interrupted state save')):
            with self.assertRaises(OSError): self.accept(self.response())
        self.assertEqual(self.state, before)

    def test_final_view_regenerates_from_accepted_artifact(self):
        self.use_passing_check()
        self.accept(self.response([]))
        self.accept(self.response([]))
        self.assertEqual([entry['stage'] for entry in self.state['ledger']], ['review', 'finalize'])
        expected = (self.run/'final.md').read_text()
        (self.run/'final.md').write_text('Interrupted derived output')
        r.render(self.run, self.state)
        self.assertEqual((self.run/'final.md').read_text(), expected)

    def test_background_child_blocks_next_stage(self):
        call = self.root/'background-call'; call.mkdir()
        next_call = self.root/'next-call'; next_call.mkdir()
        script = 'import subprocess,sys; subprocess.Popen([sys.executable,"-c","import time; time.sleep(20)"])'
        group = None
        try:
            with r.project_lock(self.project):
                with self.assertRaises(r.ReviewError):
                    r.execute_process([sys.executable,'-c',script], self.root, '', call, 10)
                group = r.read_json(call/'started.json')['process_group']
                with self.assertRaises(r.ReviewError):
                    r.execute_process([sys.executable,'-c','pass'], self.root, '', next_call, 10)
                self.assertFalse((next_call/'started.json').exists())
        finally:
            if group is not None: os.killpg(group, signal.SIGTERM)

    def test_provider_schema_limits_references_to_catalog(self):
        schema = r.provider_schema(self.state)
        validator = r.Draft202012Validator(schema)
        data = self.response([finding()])
        data['findings'][0]['verification_evidence'] = ['SOURCE:calculator.py']
        self.assertTrue(validator.is_valid(data))
        data['findings'][0]['verification_evidence'] = ['SOURCE:calculator.py:5: explanatory prose']
        self.assertFalse(validator.is_valid(data))


if __name__=='__main__': unittest.main()
