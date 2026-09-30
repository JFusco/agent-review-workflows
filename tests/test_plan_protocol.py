"""Plan protocol fixtures. No provider invocations or production access."""
import copy
import io
import sys
import unittest
from unittest.mock import patch

import test_review_cli as fixtures

r = fixtures.r


class PlanProtocolTests(unittest.TestCase):
    def setUp(self):
        fixtures.ReviewTests.setUp(self)
        self.draft = self.root / 'draft.md'
        self.draft.write_text('Specify average for nonempty lists and verify empty-list behavior.')
        self.args.mode = 'plan'
        self.args.plan = str(self.draft)
        self.args.base = None
        self.args.check = []
        self.run, self.state = r.initialize(self.args)

    accept = fixtures.ReviewTests.accept

    def gap(self, adjudicated=False):
        result = dict(severity='WARN', location='Plan: empty-list behavior',
                      evidence='The draft does not choose an empty-list result.',
                      correction_recommended='Specify an empty-list ValueError.',
                      acceptance_check='The plan specifies a ValueError and a future regression test.')
        if adjudicated:
            result.update(disposition='ACCEPTED', rationale='Resolve the unspecified behavior.')
        return result

    def response(self, new_findings=None):
        result = {key: self.state[key] for key in
                  ('plan_protocol_version', 'run_id', 'stage', 'handoff_revision', 'target_fingerprint')}
        result.update(summary='Fixture assessment; no provider evidence.', new_findings=new_findings or [])
        if self.state['stage'] == 'adjudicate':
            result['assessments'] = [dict(id=f['id'], disposition='ACCEPTED', rationale='Supported plan gap.')
                                     for f in self.state['findings']]
            result['plan_markdown'] = ('Specify average and an empty-list ValueError with regression tests.'
                                       if self.state['findings'] or new_findings else None)
        elif self.state['stage'] == 'recheck':
            result['assessments'] = [dict(id=f['id'], verification_status='PASSED',
                                         verification_evidence=['PLAN:current'],
                                         rationale='The current plan specifies the requested behavior and test.')
                                     for f in self.state['findings'] if f['disposition'] == 'ACCEPTED']
        return result

    def to_recheck(self):
        self.accept(self.response([self.gap()]))
        self.accept(self.response())
        self.assertEqual(self.state['stage'], 'recheck')

    def assert_rejected(self, data):
        before = copy.deepcopy(self.state)
        artifacts = sorted((self.run / 'artifacts').glob('*'))
        with self.assertRaises(r.ReviewError):
            self.accept(data)
        self.assertEqual(self.state, before)
        self.assertEqual(sorted((self.run / 'artifacts').glob('*')), artifacts)

    def cli(self, *args):
        with patch.object(sys, 'argv', ['review_cli.py', *args, str(self.run)]), \
                patch.object(sys, 'stdout', new_callable=io.StringIO):
            r.main()
        self.state = r.read_json(self.run / 'state.json')

    def test_clean_two_call_completion_and_protocol_visibility(self):
        original = self.draft.read_text()
        profile = copy.deepcopy(self.state['agent_profile'])
        for payload in (r.read_json(self.run / 'original.json'), r.packet(self.state),
                        r.status_payload(self.run, self.state)):
            self.assertEqual(payload['plan_protocol_version'], 2)
        self.assertIn('Plan protocol: 2', (self.run / 'handoff.md').read_text())
        with patch.object(r, 'perform_checks', side_effect=AssertionError('Plan reviews cannot run checks')):
            self.accept(self.response())
            self.assertEqual((self.state['stage'], self.state['status']), ('adjudicate', 'ready'))
            self.assertIn('Assess the complete plan even if', r.prompt(self.state))
            self.accept(self.response())
        self.assertEqual([e['stage'] for e in self.state['ledger']], ['review', 'adjudicate'])
        self.assertEqual((self.state['stage'], self.state['status'], self.state['round']), ('finalize', 'complete', 0))
        self.assertEqual((self.run / 'final.md').read_text(), original)
        self.assertEqual(self.draft.read_text(), original)
        self.assertEqual(self.state['agent_profile'], profile)
        self.assertEqual(r.inventory(self.project), self.state['inventory'])

    def test_corrected_plan_three_calls_and_raw_canonical_artifacts(self):
        review = self.response([self.gap()])
        self.accept(review)
        definition = copy.deepcopy(self.state['findings'][0])
        self.assertEqual(definition['id'], 'FIND-001')
        self.assertEqual(definition['verification_status'], 'UNVERIFIED')
        artifact = r.read_json(self.run / 'artifacts/revision-001.json')
        self.assertEqual(artifact['submitted_response'], review)
        self.assertEqual(artifact['response']['findings'], self.state['findings'])
        self.assertEqual(artifact['plan_protocol_version'], 2)
        refinement = self.response()
        missing = copy.deepcopy(refinement)
        missing['plan_markdown'] = None
        self.assert_rejected(missing)
        self.accept(refinement)
        self.assertEqual(self.state['round'], 1)
        self.assertNotEqual(self.state['target_fingerprint'], review['target_fingerprint'])
        self.assertIn('whole revised plan', r.prompt(self.state))
        self.accept(self.response())
        self.assertEqual(self.state['status'], 'complete')
        self.assertEqual([e['stage'] for e in self.state['ledger']], ['review', 'adjudicate', 'recheck'])
        for key in r.FINDING_DEFINITION_FIELDS:
            self.assertEqual(self.state['findings'][0][key], definition[key])
        self.assertEqual((self.run / 'final.md').read_text(), refinement['plan_markdown'])

    def test_coordinator_can_find_gap_after_clean_review(self):
        self.accept(self.response())
        data = self.response([self.gap(adjudicated=True)])
        self.accept(data)
        self.assertEqual(self.state['stage'], 'recheck')
        self.assertEqual(self.state['findings'][0]['id'], 'FIND-001')
        self.assertEqual(self.state['findings'][0]['verification_evidence'], [])
        self.accept(self.response())
        self.assertEqual(self.state['status'], 'complete')

    def test_stage_schemas_forbid_unowned_fields(self):
        envelope = {'plan_protocol_version', 'run_id', 'stage', 'handoff_revision', 'target_fingerprint', 'summary'}
        for stage, extra in (('review', {'new_findings'}),
                             ('adjudicate', {'assessments', 'new_findings', 'plan_markdown'}),
                             ('recheck', {'assessments', 'new_findings'})):
            self.state['stage'] = stage
            schema = r.provider_schema(self.state)
            r.Draft202012Validator.check_schema(schema)
            self.assertEqual(set(schema['required']), envelope | extra)
            self.assertEqual(set(schema['properties']), envelope | extra)
            self.assertIn(r.dumps(schema), r.prompt(self.state))
            good = self.response([self.gap(adjudicated=stage == 'adjudicate')])
            self.assertTrue(r.Draft202012Validator(schema).is_valid(good))
            for field, value in (('id', 'FIND-004'), ('verification_status', 'PASSED'),
                                 ('verification_evidence', ['PLAN:current'])):
                bad = copy.deepcopy(good)
                bad['new_findings'][0][field] = value
                self.assert_rejected(bad)
            for field in good:
                bad = copy.deepcopy(good)
                del bad[field]
                self.assert_rejected(bad)
            for field, value in (('findings', []), ('next_stage', 'finalize'), ('summary', ' '),
                                 ('new_findings', {}), ('stage', 'repair'), ('plan_protocol_version', 3),
                                 ('target_fingerprint', '0' * 64), ('handoff_revision', 42), ('run_id', 'wrong')):
                bad = copy.deepcopy(good)
                bad[field] = value
                self.assert_rejected(bad)

    def test_assessment_coverage_order_and_field_ownership(self):
        self.accept(self.response([self.gap(), self.gap()]))
        for stage in ('adjudicate', 'recheck'):
            if stage == 'recheck':
                self.accept(self.response())
            good = self.response()
            variants = []
            for assessments in ([], good['assessments'][:1], list(reversed(good['assessments'])),
                                [good['assessments'][0], good['assessments'][0]]):
                variants.append({**good, 'assessments': assessments})
            for field, value in (('id', 'FIND-099'), ('acceptance_check', 'Weakened'),
                                 ('verification_status' if stage == 'adjudicate' else 'disposition',
                                  'PASSED' if stage == 'adjudicate' else 'REJECTED'), ('rationale', ' ')):
                bad = copy.deepcopy(good)
                bad['assessments'][0][field] = value
                variants.append(bad)
            for bad in variants:
                self.assert_rejected(bad)

    def test_recheck_requires_current_evidence_and_no_plan_output(self):
        self.to_recheck()
        good = self.response()
        for refs in ([], ['PLAN:old'], ['PLAN:current:line-1']):
            bad = copy.deepcopy(good)
            bad['assessments'][0]['verification_evidence'] = refs
            self.assert_rejected(bad)
        self.assert_rejected({**good, 'plan_markdown': 'Unreviewed replacement'})
        canonical = r.normalize_response(self.state, good)
        canonical['findings'][0]['acceptance_check'] = 'Weakened acceptance'
        with self.assertRaisesRegex(r.ReviewError, 'immutable'):
            r.validate_response(self.state, canonical)

    def test_all_rejected_finishes_without_rewrite(self):
        self.accept(self.response([self.gap()]))
        data = self.response()
        data['assessments'][0].update(disposition='REJECTED', rationale='The requirements already choose this behavior.')
        self.assert_rejected(data)
        data['plan_markdown'] = None
        self.accept(data)
        self.assertEqual(self.state['status'], 'complete')
        self.assertEqual(self.state['round'], 0)
        self.assertEqual((self.run / 'final.md').read_text(), self.draft.read_text())

    def test_recheck_carries_rejected_records_without_model_output(self):
        self.accept(self.response([self.gap(), self.gap()]))
        decision = self.response()
        decision['assessments'][1].update(disposition='REJECTED', rationale='Duplicate of the first finding.')
        self.accept(decision)
        rejected = copy.deepcopy(self.state['findings'][1])
        data = self.response()
        self.assertEqual([a['id'] for a in data['assessments']], ['FIND-001'])
        self.accept(data)
        self.assertEqual(self.state['status'], 'complete')
        self.assertEqual(self.state['findings'][1], rejected)

    def test_new_recheck_gap_and_passed_rejected_completion(self):
        self.to_recheck()
        self.accept(self.response([self.gap()]))
        self.assertEqual(self.state['stage'], 'adjudicate')
        self.assertEqual([f['id'] for f in self.state['findings']], ['FIND-001', 'FIND-002'])
        self.assertEqual(self.state['findings'][1]['disposition'], 'OPEN')
        data = self.response()
        data['assessments'][1].update(disposition='REJECTED', rationale='Duplicate of the already satisfied condition.')
        data['plan_markdown'] = None
        self.accept(data)
        self.assertEqual((self.state['status'], self.state['round']), ('complete', 1))
        self.assertEqual([f['disposition'] for f in self.state['findings']], ['ACCEPTED', 'REJECTED'])

    def test_second_refinement_invalidates_passes_and_can_complete(self):
        self.to_recheck()
        self.accept(self.response([self.gap()]))
        self.assertEqual(self.state['findings'][0]['verification_status'], 'PASSED')
        self.accept(self.response())  # Same plan bytes still consume an attempt.
        self.assertEqual(self.state['round'], 2)
        for finding in self.state['findings']:
            self.assertEqual((finding['verification_status'], finding['verification_evidence']), ('UNVERIFIED', []))
        self.accept(self.response())
        self.assertEqual(self.state['status'], 'complete')
        self.assertEqual(len(self.state['ledger']), 5)

    def test_two_failed_rechecks_end_unresolved_and_third_attempt_is_rejected(self):
        self.to_recheck()
        for attempt in (1, 2):
            data = self.response()
            data['assessments'][0].update(verification_status='FAILED', verification_evidence=[])
            self.accept(data)
            if attempt == 1:
                self.assertEqual(self.state['stage'], 'adjudicate')
                self.accept(self.response())
        self.assertEqual((self.state['status'], self.state['round']), ('unresolved', 2))
        self.assertFalse((self.run / 'final.md').exists())
        self.assert_rejected(self.response())
        self.state.update(stage='adjudicate', status='ready')
        self.assert_rejected(self.response())
        with patch.object(r, 'execute_process') as execute:
            with self.assertRaisesRegex(r.ReviewError, 'limit'):
                r.advance(self.run, self.state, external_coordinator=True)
            execute.assert_not_called()

    def test_user_decision_and_external_submission_share_contract(self):
        self.accept(self.response([self.gap()]))
        r.advance(self.run, self.state, external_coordinator=True)
        request = r.read_json(self.run / 'external-request.json')
        self.assertEqual(request['schema'], r.provider_schema(self.state))
        self.assertEqual(request['packet'], r.packet(self.state))
        pending = self.response()
        pending['assessments'][0].update(disposition='PENDING_USER', rationale='Choose empty-list behavior.')
        self.assert_rejected(pending)
        pending['plan_markdown'] = None
        response_file = self.root / 'response.json'
        response_file.write_text(r.dumps(pending))
        self.cli('submit', '--response', str(response_file), '--model', 'gpt-6-astra', '--effort', 'max')
        self.assertEqual((self.state['status'], self.state['round']), ('needs_user', 0))
        revision = self.state['handoff_revision']
        self.cli('decide', '--instruction', 'Use ValueError for an empty list.')
        self.assertEqual((self.state['stage'], self.state['status']), ('adjudicate', 'ready'))
        self.assertEqual(self.state['handoff_revision'], revision + 1)
        self.assert_rejected(pending)
        r.advance(self.run, self.state, external_coordinator=True)
        response_file.write_text(r.dumps(self.response()))
        self.cli('submit', '--response', str(response_file), '--model', 'gpt-6-astra', '--effort', 'max')
        self.assertEqual(self.state['stage'], 'recheck')
        self.accept(self.response())
        self.assertEqual(self.state['status'], 'complete')

    def test_interrupted_acceptance_and_replay_do_not_double_count(self):
        self.accept(self.response([self.gap()]))
        data = self.response()
        before = copy.deepcopy(self.state)
        with patch.object(r, 'save', side_effect=OSError('Interrupted checkpoint')):
            with self.assertRaises(OSError):
                self.accept(data)
        self.assertEqual(self.state, before)
        self.state = r.read_json(self.run / 'state.json')
        self.accept(data)
        self.assertEqual(self.state['round'], 1)
        self.assertEqual(self.state['ledger'][-1]['orphaned_artifacts'], ['revision-002'])
        self.assert_rejected(data)
        self.accept(self.response())
        self.assertEqual(self.state['status'], 'complete')
        self.assert_rejected(data)

    def test_final_render_recovers_from_artifact_after_original_changes(self):
        original = self.draft.read_text()
        self.accept(self.response())
        self.accept(self.response())
        self.draft.write_text('Later unrelated draft edit.')
        (self.run / 'final.md').write_text('Interrupted derived output')
        r.render(self.run, self.state)
        self.assertEqual((self.run / 'final.md').read_text(), original)

    def test_post_accept_view_failure_preserves_progress_without_provider_replay(self):
        config = {'model': 'fixture', 'effort': 'high', 'observed': {'source': 'fixture'}}
        for expected_status in ('ready', 'complete'):
            data = self.response()
            with patch.object(r, 'execute_process'), \
                    patch.object(r, 'extract_response', return_value=(data, None, config)), \
                    patch.object(r, 'render', side_effect=OSError('Interrupted derived view')):
                with self.assertRaises(OSError):
                    r.advance(self.run, self.state)
            saved = r.read_json(self.run / 'state.json')
            self.assertEqual(saved['status'], expected_status)
            self.assertEqual(self.state, saved)
        with patch.object(r, 'execute_process') as execute:
            self.cli('run')
            execute.assert_not_called()
        self.assertEqual(len(self.state['ledger']), 2)
        self.assertEqual((self.run / 'final.md').read_text(), self.draft.read_text())

    def test_readonly_and_freshness_guards_preserve_changes(self):
        data = self.response()
        self.draft.write_text('Unexpected draft change.')
        self.assert_rejected(data)
        self.assertEqual(self.draft.read_text(), 'Unexpected draft change.')
        self.draft.write_text('Specify average for nonempty lists and verify empty-list behavior.')
        (self.project / 'calculator.py').write_text('Unexpected project change.')
        self.assert_rejected(data)
        self.assertEqual((self.project / 'calculator.py').read_text(), 'Unexpected project change.')

    def test_unknown_versions_and_removed_dispatch_stages_fail_closed(self):
        for version in (None, 1, 3, '2', 2.0, True):
            self.state['plan_protocol_version'] = version
            for operation in (lambda: r.status_payload(self.run, self.state),
                              lambda: r.packet(self.state), lambda: r.provider_schema(self.state)):
                with self.assertRaisesRegex(r.ReviewError, 'Unsupported'):
                    operation()
        self.state['plan_protocol_version'] = 2
        for stage in ('respond', 'reply', 'refine', 'finalize', 'repair'):
            self.state['stage'] = stage
            with patch.object(r, 'execute_process') as execute:
                with self.assertRaises(r.ReviewError):
                    r.advance(self.run, self.state)
                execute.assert_not_called()
            self.assert_rejected(self.response())

    def test_legacy_paused_stages_keep_their_recorded_contract(self):
        self.state.pop('plan_protocol_version')
        baseline = copy.deepcopy(self.state)
        for stage, next_stage in (('respond', 'reply'), ('reply', 'adjudicate'),
                                  ('refine', 'recheck'), ('finalize', 'finalize')):
            self.state = copy.deepcopy(baseline)
            self.state['stage'] = stage
            data = fixtures.ReviewTests.response(self, [])
            if stage in ('refine', 'finalize'):
                data['plan_markdown'] = self.draft.read_text()
            r.Draft202012Validator(r.provider_schema(self.state)).validate(data)
            self.accept(data)
            self.assertEqual(self.state['stage'], next_stage)
            self.assertEqual(self.state['status'], 'complete' if stage == 'finalize' else 'ready')
            artifact = r.read_json(self.run / 'artifacts' / (self.state['ledger'][-1]['artifact_id'] + '.json'))
            self.assertNotIn('submitted_response', artifact)
            self.assertNotIn('plan_protocol_version', artifact)


if __name__ == '__main__':
    unittest.main()
