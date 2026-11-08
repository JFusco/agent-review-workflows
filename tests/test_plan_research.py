"""Research contract fixtures: no model calls or production access."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib
import unittest
from unittest.mock import patch

import test_review_cli as fixtures
import test_plan_protocol as plan_fixtures

r = fixtures.r


class PlanResearchTests(unittest.TestCase):
    def setUp(self):
        fixtures.ReviewTests.setUp(self)
        self.draft = self.root / 'draft.md'
        self.draft.write_text('Specify average for nonempty lists and verify empty-list behavior.')
        self.args.mode = 'plan'
        self.args.plan = str(self.draft)
        self.args.base = None
        self.args.check = []
        self.run, self.state = r.initialize(self.args)

    response = plan_fixtures.PlanProtocolTests.response
    gap = plan_fixtures.PlanProtocolTests.gap
    to_recheck = plan_fixtures.PlanProtocolTests.to_recheck
    assert_rejected = plan_fixtures.PlanProtocolTests.assert_rejected
    cli = plan_fixtures.PlanProtocolTests.cli

    def accept(self, data):
        who = r.role(self.state)
        r.accept(self.run, self.state, data, {**r.agent_candidate(self.state, who),
                                             'observed': {'source': 'fixture'}})

    def brief(self):
        data = r.read_json(fixtures.ROOT / 'tests/fixtures/research.json')
        data.update({key: self.state[key] for key in
                     ('run_id', 'stage', 'handoff_revision', 'target_fingerprint')})
        for source in data['sources']:
            source['retrieved_on'] = datetime.now(timezone.utc).date().isoformat()
        return data

    def test_start_snapshots_and_freezes_research_without_provider(self):
        with patch.object(r, 'execute_process', side_effect=AssertionError('No provider at start')):
            run, state = r.initialize(self.args)
        self.assertEqual((state['schema_version'], state['plan_protocol_version'],
                          state['research_contract_version'], state['stage']), (3, 2, 1, 'research'))
        self.assertEqual(state['agent_profile']['researcher'], {'model': 'gpt-6-astra', 'effort': 'high'})
        self.assertEqual(state['agent_fallbacks']['researcher'], [])
        self.assertFalse(list((run / 'calls').iterdir()))
        self.assertIn('required; awaiting research', (run / 'handoff.md').read_text())
        self.assertEqual(r.read_json(run / 'original.json')['research_contract_version'], 1)
        with patch.object(r, 'load_runtime_config', side_effect=AssertionError('Frozen settings only')):
            self.assertEqual(r.agent_settings(state, 'researcher'), ('gpt-6-astra', 'high'))

    def test_precedence_and_mode_specific_configuration(self):
        r.RUNTIME_CONFIG.write_text(r.dumps({'skills': {'review-plan': {
            'researcher': {'model': 'gpt-fixture', 'effort': 'xhigh'}}}}))
        _, state = r.initialize(self.args)
        self.assertEqual(state['agent_profile']['researcher'], {'model': 'gpt-fixture', 'effort': 'xhigh'})
        self.args.researcher_model = 'gpt-override'
        run, state = r.initialize(self.args)
        self.assertEqual(state['agent_profile']['researcher'], {'model': 'gpt-override', 'effort': 'xhigh'})
        self.assertIn('gpt-override', (run / 'handoff.md').read_text())
        self.args.researcher_effort = 'high'
        _, state = r.initialize(self.args)
        self.assertEqual(state['agent_profile']['researcher']['effort'], 'high')
        parsed = r.build_parser().parse_args(['start', 'plan', '--requirements', 'req.md',
                                             '--researcher-model', 'gpt-test', '--researcher-effort', 'xhigh'])
        self.assertEqual((parsed.researcher_model, parsed.researcher_effort), ('gpt-test', 'xhigh'))
        for mode in ('implementation', 'diff'):
            args = copy.deepcopy(self.args)
            args.mode = mode
            with self.assertRaisesRegex(r.ReviewError, 'Only plan'):
                r.initialize(args)
            with self.assertRaises(r.ReviewError):
                r.validate_runtime_config({'skills': {r.MODE_TO_SKILL[mode]: {'researcher': {}}}})
            self.assertNotIn('researcher', r.DEFAULT_PROFILES[r.MODE_TO_SKILL[mode]])
        with self.assertRaisesRegex(r.ReviewError, 'fallback is disabled'):
            r.validate_fallbacks('researcher', [{'provider': 'codex', 'model': 'gpt-other', 'effort': 'high'}])

    def test_accepted_research_is_immutable_bound_and_given_to_both_roles(self):
        brief = self.brief()
        before = self.state['target_fingerprint']
        self.accept(brief)
        self.assertEqual((self.state['stage'], self.state['round'], self.state['handoff_revision']), ('review', 0, 1))
        self.assertNotEqual(self.state['target_fingerprint'], before)
        self.assertEqual(r.target(self.state)['research_digest'], r.digest(brief))
        artifact = r.read_json(self.run / 'artifacts/revision-001.json')
        self.assertEqual(artifact['submitted_response'], brief)
        self.assertEqual(artifact['research_digest'], r.digest(brief))
        for stage in ('review', 'adjudicate', 'recheck'):
            self.state['stage'] = stage
            self.assertEqual(r.packet(self.state)['research'], brief)
            self.assertIn('source applicability', r.prompt(self.state))
            self.assertIn('RES-001', r.evidence_catalog(self.state))
        self.assertEqual(r.status_payload(self.run, self.state)['research'], self.state['research'])

    def test_research_does_not_consume_refinements_and_is_reused(self):
        brief = self.brief()
        self.accept(brief)
        self.to_recheck()
        first = self.response([self.gap()])
        self.accept(first)
        self.accept(self.response())
        self.assertEqual(self.state['round'], 2)
        self.accept(self.response())
        self.assertEqual((self.state['status'], self.state['round']), ('complete', 2))
        self.assertEqual([e['stage'] for e in self.state['ledger']],
                         ['research', 'review', 'adjudicate', 'recheck', 'adjudicate', 'recheck'])
        self.assertEqual(r.accepted_research(self.state), brief)
        self.assert_rejected(brief)
        self.assertEqual(self.draft.read_text(), 'Specify average for nonempty lists and verify empty-list behavior.')

    def test_missing_research_cannot_enter_review_or_replay(self):
        self.assert_rejected(self.response())
        self.state['stage'] = 'review'
        with patch.object(r, 'execute_process') as execute:
            with self.assertRaisesRegex(r.ReviewError, 'research is missing'):
                r.advance(self.run, self.state)
            execute.assert_not_called()
        self.state['stage'] = 'research'
        brief = self.brief()
        self.accept(brief)
        self.assert_rejected(brief)

    def test_malformed_stale_and_unsupported_evidence_is_rejected(self):
        good = self.brief()
        variants = []
        for key in good:
            bad = copy.deepcopy(good)
            del bad[key]
            variants.append(bad)
        for key, value in (('run_id', 'other'), ('handoff_revision', 10), ('target_fingerprint', 'f' * 64),
                           ('stage', 'review'), ('research_contract_version', 2), ('unknown', True)):
            variants.append({**good, key: value})
        for mutate in (lambda b: b['searches'].pop(),
                       lambda b: b['sources'].append(copy.deepcopy(b['sources'][0])),
                       lambda b: b['searches'][0].update(source_ids=[]),
                       lambda b: b['searches'][0].update(source_ids=['RES-002']),
                       lambda b: b['searches'][0].update(source_ids=['RES-001', 'RES-001']),
                       lambda b: b['recommendation'].update(source_ids=['RES-999']),
                       lambda b: b['recommendation'].update(source_ids=['RES-001', 'RES-001']),
                       lambda b: b['sources'][1].update(primary=False),
                       lambda b: b['sources'][0].update(retrieved_on='2999-01-01'),
                       lambda b: b['sources'][0].update(retrieved_on='2026-02-30'),
                       lambda b: b.update(unavailable_sources=[]),
                       lambda b: b['sources'][0].update(evidence=' ')):
            bad = copy.deepcopy(good)
            mutate(bad)
            variants.append(bad)
        for bad in variants:
            with self.subTest(bad=bad):
                self.assert_rejected(bad)
        r.Draft202012Validator.check_schema(r.provider_schema(self.state))
        self.assertNotIn('uniqueItems', r.dumps(r.provider_schema(self.state)))

    def test_brain_snapshot_and_missing_activity_are_visible(self):
        brief = self.brief()
        brain = brief['searches'][4]
        brain.update(status='read', source_ids=['RES-003'])
        brief['sources'].append({**brief['sources'][0], 'id': 'RES-003', 'channel': 'brain',
                                 'locator': 'a' * 40 + ':knowledge/example.md'})
        self.assert_rejected(brief)
        brief['brain'].update(snapshot='a' * 40, limitations=[])
        self.assert_rejected(brief)
        brief['brain']['limitations'] = ['Usage recording denied by managed permissions.']
        self.accept(brief)
        self.assertEqual(r.accepted_research(self.state)['brain']['snapshot'], 'a' * 40)
        self.assertIn('Usage recording denied', r.prompt(self.state))

    def test_source_link_errors_report_all_offending_ids_without_repairing_evidence(self):
        brief = self.brief()
        brief['sources'].append({**brief['sources'][0], 'id': 'RES-010'})
        brief['sources'].append({**brief['sources'][0], 'id': 'RES-017'})
        brief['searches'][4].update(status='read', source_ids=['RES-002'])
        original = copy.deepcopy(brief)
        with self.assertRaises(r.ReviewError) as raised:
            r.validate_research(self.state, brief)
        message = str(raised.exception)
        self.assertIn('searches[4] (brain/brain): RES-002 has channel web, not brain.', message)
        self.assertIn('Sources missing from searches[].source_ids: RES-010, RES-017.', message)
        self.assertEqual(brief, original)
        # A correction must come from the researcher; the helper never infers reads.
        brief['searches'][4].update(status='unavailable', source_ids=[])
        brief['searches'][0]['source_ids'].extend(['RES-010', 'RES-017'])
        r.validate_research(self.state, brief)

    def test_source_reference_diagnostics_preserve_rejection_boundaries(self):
        cases = [
            ({'source_ids': ['RES-001', 'RES-001']}, 'duplicate source IDs: RES-001'),
            ({'source_ids': ['RES-999']}, 'unknown source ID RES-999'),
            ({'source_ids': []}, 'status read requires at least one source ID'),
            ({'status': 'no_matches'}, 'status no_matches cannot cite source IDs: RES-001'),
            ({'status': 'unavailable'}, 'status unavailable cannot cite source IDs: RES-001'),
        ]
        for change, expected in cases:
            with self.subTest(change=change):
                brief = self.brief()
                brief['searches'][0].update(change)
                with self.assertRaises(r.ReviewError) as raised:
                    r.validate_research(self.state, brief)
                self.assertIn('searches[0] (local/repository): ' + expected, str(raised.exception))

    def test_explicit_retry_uses_latest_rejection_without_resetting_correction_budget(self):
        good = self.brief()
        first, second = copy.deepcopy(good), copy.deepcopy(good)
        first['searches'][4].update(status='read', source_ids=['RES-002'])
        second['sources'].append({**second['sources'][0], 'id': 'RES-010'})
        second['sources'].append({**second['sources'][0], 'id': 'RES-017'})
        pending = iter([first, second, second, good])
        prompts = []

        def execute(argv, cwd, content, call_dir, timeout):
            prompts.append(content)
            r.write_new(call_dir / 'last-message.json', next(pending))

        def extract(state, call_dir):
            return (r.read_json(call_dir / 'last-message.json'), None,
                    {**r.agent_candidate(state, 'researcher'), 'observed': {'source': 'fixture'}})

        with patch.object(r, 'execute_process', side_effect=execute), \
                patch.object(r, 'extract_response', side_effect=extract):
            with self.assertRaisesRegex(r.ContractResponseError, 'RES-010, RES-017'):
                r.advance(self.run, self.state)
            self.assertEqual(len(prompts), 2)
            self.assertEqual(len(self.state['response_corrections']), 1)
            self.assertEqual(len(self.state['response_rejections']), 2)
            history = copy.deepcopy(self.state['response_rejections'])
            self.cli('retry')
            self.cli('status')
            self.assertEqual(self.state['response_rejections'], history)
            with self.assertRaisesRegex(r.ContractResponseError, 'RES-010, RES-017'):
                r.advance(self.run, self.state)
            self.assertEqual(len(prompts), 3)  # Explicit retry grants no new automatic correction.
            latest_feedback = prompts[2].split('PREVIOUS RESPONSE REJECTED\n')[1]
            self.assertIn('RES-010, RES-017', latest_feedback)
            self.assertNotIn('has channel web, not brain', latest_feedback)
            self.assertEqual(self.state['response_rejections'][:2], history)
            self.cli('retry')
            r.advance(self.run, self.state)
        self.assertEqual(self.state['stage'], 'review')
        self.assertEqual(len(self.state['response_corrections']), 1)
        self.assertEqual(len(self.state['response_rejections']), 3)
        self.assertEqual(self.state['fallback_history'], [])
        self.assertIsNone(r.current_rejection(self.state))
        for index, expected in enumerate([first, second, second, good], 1):
            self.assertEqual(r.read_json(self.run / f'calls/{index:03d}-research/last-message.json'), expected)

    def test_rejection_feedback_respects_revision_and_legacy_history(self):
        event = {'stage': 'research', 'handoff_revision': 0, 'reason': 'Legacy correction.'}
        self.state['response_corrections'] = [event]
        self.assertEqual(r.current_rejection(self.state), event)
        self.state['response_rejections'] = [{**event, 'reason': 'Latest rejection.'}]
        self.assertEqual(r.current_rejection(self.state)['reason'], 'Latest rejection.')
        self.state['handoff_revision'] += 1
        self.assertIsNone(r.current_rejection(self.state))

    def test_provider_schema_delivers_source_link_contract(self):
        schema = r.provider_schema(self.state)
        self.assertIn('searches[].source_ids', schema['properties']['sources']['description'])
        refs = schema['properties']['searches']['items']['properties']['source_ids']
        self.assertIn('same channel', refs['description'])
        self.assertIn('Never invent a read', r.research_prompt(self.state))

    def test_corrupted_and_symlinked_accepted_artifact_blocks(self):
        self.accept(self.brief())
        path = self.run / 'artifacts/revision-001.json'
        original = path.read_text()
        artifact = r.read_json(path)
        artifact['submitted_response']['summary'] = 'Corrupted'
        path.write_text(r.dumps(artifact))
        for operation in (lambda: r.assert_fresh(self.state), lambda: r.packet(self.state),
                          lambda: r.status_payload(self.run, self.state)):
            with self.assertRaisesRegex(r.ReviewError, 'corrupted'):
                operation()
        other = self.root / 'other.json'
        other.write_text(original)
        path.unlink()
        path.symlink_to(other)
        with self.assertRaisesRegex(r.ReviewError, 'symlink'):
            r.assert_fresh(self.state)

    def test_interrupted_acceptance_preserves_orphan_and_rejects_replay(self):
        brief = self.brief()
        before = copy.deepcopy(self.state)
        with patch.object(r, 'save', side_effect=OSError('Interrupted checkpoint')):
            with self.assertRaises(OSError):
                self.accept(brief)
        self.assertEqual(self.state, before)
        self.accept(brief)
        self.assertEqual(self.state['research']['digest'], r.digest(brief))
        self.assertEqual(self.state['ledger'][0]['orphaned_artifacts'], ['revision-001'])
        self.assertEqual(len(list((self.run / 'artifacts').iterdir())), 2)
        self.assert_rejected(brief)

    def test_dispatch_uses_isolated_codex_and_fails_without_fallback(self):
        brief = self.brief()
        config = {**r.agent_candidate(self.state, 'researcher'), 'observed': {'source': 'fixture'}}
        with patch.object(r, 'execute_process') as execute, \
                patch.object(r, 'extract_response', return_value=(brief, 'fixture-session', config)):
            r.advance(self.run, self.state)
        argv, cwd, content, *_ = execute.call_args.args
        self.assertEqual(str(cwd), self.state['research_access']['scratch'])
        self.assertIn('web_search="live"', argv)
        self.assertIn('permissions.plan-research.network.enabled=false', argv)
        self.assertIn('permissions.plan-research.extends=":read-only"', argv)
        self.assertIn('default_permissions="plan-research"', argv)
        self.assertIn('never authority', content)
        self.assertEqual(self.state['sessions']['researcher'], 'fixture-session')
        reviewer_argv = r.cli_argv(self.state, self.run / 'calls/reviewer')
        self.assertNotIn('--resume', reviewer_argv)
        self.assertEqual(r.role(self.state), 'opus')
        self.state = r.read_json(self.run / 'state.json')
        self.state.update(stage='research', research=None, sessions={})
        self.state['target_fingerprint'] = r.digest(r.target(self.state))
        with patch.object(r, 'execute_process', side_effect=r.ProviderCallError('Fixture capacity failure')) as execute:
            with self.assertRaises(r.ProviderCallError):
                r.advance(self.run, self.state)
        execute.assert_called_once()
        self.assertEqual(self.state['status'], 'blocked')
        self.assertEqual(self.state['fallback_history'], [])
        self.cli('retry')
        self.assertEqual(self.state['status'], 'ready')

    def test_project_changes_and_permission_root_substitution_are_denied(self):
        brief = self.brief()
        (self.project / 'calculator.py').write_text('Unexpected project write.')
        self.assert_rejected(brief)
        self.assertEqual((self.project / 'calculator.py').read_text(), 'Unexpected project write.')
        roots = r.research_writable_roots(self.state)
        self.assertNotIn(str(self.project), roots)
        self.assertNotIn(str(self.run), roots)
        self.state['research_access']['brain_metadata'] = str(self.project)
        with self.assertRaises(r.ReviewError):
            r.research_writable_roots(self.state)

    @unittest.skipUnless(sys.platform == 'darwin' and shutil.which('codex'), 'Local macOS Codex sandbox check')
    def test_local_sandbox_denies_project_knowledge_and_artifact_writes(self):
        brain = self.root / 'brain'
        metadata = brain / '.state/visual-brain'
        metadata.mkdir(parents=True)
        knowledge = brain / 'knowledge'
        knowledge.mkdir()
        (self.run / 'artifacts').mkdir(exist_ok=True)
        self.state['research_access'].update(brain_root=str(brain), brain_metadata=str(metadata))
        paths = {'scratch': self.run / 'research-scratch/probe', 'metadata': metadata / 'probe',
                 'project': self.project / 'probe', 'knowledge': knowledge / 'probe',
                 'artifact': self.run / 'artifacts/probe', 'executor': self.run / 'executor/probe',
                 'temp': self.root / 'probe'}
        script = ('import json,pathlib\nresults={}\n'
                  'for key,path in ' + repr({key: str(path) for key, path in paths.items()}) + '.items():\n'
                  ' try:\n  pathlib.Path(path).write_text("fixture")\n  results[key]="allowed"\n'
                  ' except PermissionError:\n  results[key]="denied"\n'
                  'print(json.dumps(results))\n')
        args = r.research_permission_args(self.state)
        # Parse the exact generated TOML, including paths containing dots/spaces.
        config = tomllib.loads('\n'.join(args[1::2]))
        self.assertEqual(set(config['permissions']['plan-research']['filesystem']),
                         set(r.research_writable_roots(self.state)))
        result = subprocess.run([shutil.which('codex'), 'sandbox', '-P', 'plan-research', *args,
                                 '-C', str(self.run / 'research-scratch'), '--', sys.executable, '-c', script],
                                cwd=Path(self.state['research_access']['scratch']), capture_output=True,
                                text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {key: 'allowed' if key in ('scratch', 'metadata') else 'denied'
                                                    for key in paths})

    def test_comparison_separates_research_provenance_from_observed_execution(self):
        brief = self.brief()
        self.accept(brief)
        report = r.compare_runs(self.run, self.run)
        evidence = report['candidate']
        self.assertEqual(evidence['research']['status'], 'recorded')
        self.assertEqual(evidence['research']['brief'], brief)
        self.assertEqual(evidence['protocol']['research_contract_version'], 1)
        self.assertEqual(evidence['accepted_counts']['synthetic'], 1)
        self.assertEqual(evidence['launch_attempt_count'], 0)
        self.assertEqual(evidence['accepted_events'][0]['observed'], {'source': 'fixture'})
        path = self.run / 'artifacts/revision-001.json'
        path.write_text('{}')
        report = r.compare_runs(self.run, self.run)
        self.assertEqual(report['candidate']['research']['status'], 'unavailable')

    def test_saved_schema_two_keeps_two_roles_and_unrecorded_research(self):
        state = self.state
        state.update(schema_version=2, stage='review')
        state['agent_profile'].pop('researcher')
        state['agent_fallbacks'].pop('researcher')
        for key in ('research', 'research_access', 'research_contract_version', 'agent_providers'):
            state.pop(key)
        state['target_fingerprint'] = r.digest(r.target(state))
        r.render(self.run, state)
        self.assertEqual(r.packet(state)['research'], 'unrecorded')
        self.assertEqual(set(r.effective_profile(state)), {'reviewer', 'coordinator'})
        self.accept(self.response())
        self.accept(self.response())
        self.assertEqual(state['status'], 'complete')
        self.assertIn('Research: unrecorded', (self.run / 'handoff.md').read_text())


if __name__ == '__main__':
    unittest.main()
