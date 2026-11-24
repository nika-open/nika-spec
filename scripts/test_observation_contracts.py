#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Fixture admission and discovery only; subprocess is forbidden in every test."""
import contextlib
import functools
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


def source(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), Path(__file__).with_name(name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = source('runtime-differential')
contracts = source('observation_contracts')
CORPUS = Path(__file__).resolve().parent.parent / 'conformance/tests'


@functools.lru_cache(maxsize=None)
def fixtures():
    return tuple(sorted(p for name in contracts.DOORS for p in CORPUS.rglob(name)))


class ObservationAdmission(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.process = patch.object(runner.subprocess, 'run', side_effect=AssertionError('no engine is allowed'))
        self.mock_process = self.process.start()
        self.addCleanup(self.process.stop)

    def copy_fixture(self, claim, fragment=None):
        candidates = [p for p in fixtures() if p.name == claim and (fragment is None or fragment in p.parent.name)]
        self.assertTrue(candidates)
        src = candidates[0]
        dst = self.root / 'case'
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src.parent, dst)
        return dst, json.loads((dst / claim).read_text())

    def rejected(self, directory, claim, document):
        (directory / claim).write_text(json.dumps(document))
        with self.assertRaises(runner.InvalidFixture):
            runner.fixture_door(directory)
        self.mock_process.assert_not_called()

    def test_every_published_contract_is_valid_but_unsupported(self):
        paths = fixtures()
        self.assertEqual({p.name for p in paths}, set(contracts.DOORS))
        for path in paths:
            with self.subTest(case=path.parent.name):
                self.assertEqual(contracts.validate(path.parent, path.name), contracts.DOORS[path.name])
                with self.assertRaises(runner.UnsupportedFixture):
                    runner.fixture_door(path.parent)
        self.mock_process.assert_not_called()

    def test_unknown_members_at_every_contract_layer_refuse(self):
        for claim in contracts.DOORS:
            for location in ((), ('given',), ('observations',)):
                directory, document = self.copy_fixture(claim)
                target = document
                for key in location:
                    target = target[key]
                target['misspelled_assertion'] = True
                with self.subTest(claim=claim, location=location):
                    self.rejected(directory, claim, document)
        for path in [('given','responses',0), ('observations','output')]:
            directory, document = self.copy_fixture('expected-http.json', 'accepted-status-retains')
            target = document
            for key in path:
                target = target[key]
            target['headers_leaked'] = 'forbidden'
            self.rejected(directory, 'expected-http.json', document)

    def test_malformed_json_is_never_unsupported(self):
        directory, document = self.copy_fixture('expected-approval.json')
        for raw in ['[]', '{', '{"x":1,"x":2}', '{"x":NaN}', '{"x":1e999}',
                    json.dumps(document).replace('"contract_version": 1', '"contract_version": true')]:
            (directory/'expected-approval.json').write_text(raw)
            with self.subTest(raw=raw[:35]), self.assertRaises(runner.InvalidFixture):
                runner.fixture_door(directory)
        (directory/'expected-approval.json').write_bytes(b'\xff')
        with self.assertRaises(runner.InvalidFixture):
            runner.fixture_door(directory)
        self.mock_process.assert_not_called()

    def test_expectation_symlink_is_refused_before_its_json_is_read(self):
        directory, document = self.copy_fixture('expected-approval.json')
        external = self.root / 'outside-contract.json'
        external.write_text(json.dumps(document))
        expectation = directory / 'expected-approval.json'
        expectation.unlink()
        expectation.symlink_to(external)
        with self.assertRaises(runner.InvalidFixture):
            runner.fixture_door(directory)
        self.mock_process.assert_not_called()

    def test_fixture_root_is_explicit_and_deployment_ancestors_are_canonicalized(self):
        directory, _ = self.copy_fixture('expected-approval.json')
        alias = self.root / 'deployment-alias'
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(runner.UnsupportedFixture):
            runner.fixture_door(alias / directory.name)
        direct = self.root / 'fixture-alias'
        direct.symlink_to(directory, target_is_directory=True)
        with self.assertRaises(runner.InvalidFixture):
            runner.fixture_door(direct)
        self.mock_process.assert_not_called()

    def test_received_status_transient_assertions_follow_the_table(self):
        for fragment in ['absent-policy-keeps-error', 'intermediate-status-does-not-admit-final',
                         'keyless-transport-failure']:
            directory, document = self.copy_fixture('expected-http.json', fragment)
            with self.subTest(case=fragment):
                with self.assertRaises(runner.UnsupportedFixture):
                    runner.fixture_door(directory)
                observed = document['observations']['error']
                observed['transient'] = not observed['transient']
                self.rejected(directory, 'expected-http.json', document)
                observed['transient'] = None
                (directory / 'expected-http.json').write_text(json.dumps(document))
                with self.assertRaises(runner.UnsupportedFixture):
                    runner.fixture_door(directory)
        self.mock_process.assert_not_called()

    def test_pre_transport_refusal_asserts_requests_but_no_attempt_count(self):
        directory, document = self.copy_fixture('expected-http.json', 'resolved-null')
        self.assertEqual(document['observations']['requests'], 0)
        self.assertIsNone(document['observations']['attempts'])
        with self.assertRaises(runner.UnsupportedFixture):
            runner.fixture_door(directory)
        for claimed_attempts in [0, 1, True]:
            document['observations']['attempts'] = claimed_attempts
            self.rejected(directory, 'expected-http.json', document)
        self.mock_process.assert_not_called()

    def test_replay_cannot_authorize_an_effect(self):
        directory, document = self.copy_fixture('expected-approval.json', 'other-operator')
        document['observations']['gated_effects'] = 1
        self.rejected(directory, 'expected-approval.json', document)
        directory, document = self.copy_fixture('expected-approval.json', 'fresh-denial')
        document['observations']['gated_effects'] = 1
        self.rejected(directory, 'expected-approval.json', document)

    def test_a_record_never_reaches_a_changed_world(self):
        for fragment in ['workflow-change', 'permits-change', 'model-change', 'input-change',
                         'read-file-change', 'expired-record', 'without-twin']:
            for field, value in [('gated_effects', 1), ('reuse', 'applied'), ('re_prompted', False),
                                 ('reuse_attested', 1), ('new_decisions', 1)]:
                directory, document = self.copy_fixture('expected-consent.json', fragment)
                document['observations'][field] = value
                with self.subTest(case=fragment, field=field):
                    self.rejected(directory, 'expected-consent.json', document)

    def test_a_reuse_is_attested_and_decides_nothing_new(self):
        for field, value in [('reuse_attested', 0), ('new_decisions', 1), ('gated_effects', 2),
                             ('gated_effects', True), ('re_prompted', True), ('reuse', 'not-applied')]:
            directory, document = self.copy_fixture('expected-consent.json', 'unchanged-world')
            document['observations'][field] = value
            with self.subTest(field=field):
                self.rejected(directory, 'expected-consent.json', document)
        directory, document = self.copy_fixture('expected-consent.json', 'unchanged-world')
        document['given']['answer'] = 'affirmative'
        self.rejected(directory, 'expected-consent.json', document)

    def test_one_standing_case_varies_one_premise(self):
        for path, value in [(('operator_store',), 'other'), (('now_ms',), 3000), (('now_ms',), 2000),
                            (('tested', 'model'), 'mock/text'), (('tested', 'notes'), 'alpha\n'),
                            (('tested', 'secret'), 'unlisted'), (('changed',), 'none')]:
            directory, document = self.copy_fixture('expected-consent.json', 'read-file-change')
            target = document['given']
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            with self.subTest(path=path, value=value):
                self.rejected(directory, 'expected-consent.json', document)

    def test_a_changed_workflow_is_a_file_premise(self):
        for fragment in ['workflow-change', 'permits-change']:
            directory, document = self.copy_fixture('expected-consent.json', fragment)
            with self.assertRaises(runner.UnsupportedFixture):
                runner.fixture_door(directory)
            (directory/'changed.nika').write_bytes((directory/'input.nika').read_bytes())
            self.rejected(directory, 'expected-consent.json', document)
            (directory/'changed.nika').unlink()
            self.rejected(directory, 'expected-consent.json', document)
        directory, document = self.copy_fixture('expected-consent.json', 'unchanged-world')
        (directory/'changed.nika').write_text('nika: orphan\n')
        self.rejected(directory, 'expected-consent.json', document)

    def test_published_standing_cases_share_one_granted_world(self):
        def body(path):
            return json.loads(path.read_text().split('\n', 1)[1])
        cases = [p.parent for p in fixtures() if p.name == 'expected-consent.json']
        given = [json.loads((case/'expected-consent.json').read_text())['given'] for case in cases]
        self.assertEqual(len({(case/'input.nika').read_bytes() for case in cases}), 1)
        self.assertEqual(sorted(g['changed'] for g in given if g['changed'] != 'none'),
                         sorted(contracts.WORLD_CHANGES))
        self.assertEqual(sum(g['operator_store'] == 'other' for g in given), 1)
        self.assertEqual(sum(g['now_ms'] > g['expires_ms'] for g in given), 1)
        self.assertEqual(sum(g == dict(given[0], changed='none', tested=contracts.GRANTED_WORLD,
                                       operator_store='same', now_ms=1000) for g in given), 1)
        for case, change in zip(cases, given):
            if change['changed'] in {'workflow', 'permits'}:
                granted, tested = body(case/'input.nika'), body(case/'changed.nika')
                same_permits = granted['permits'] == tested['permits']
                same_rest = ({k: v for k, v in granted.items() if k != 'permits'}
                             == {k: v for k, v in tested.items() if k != 'permits'})
                with self.subTest(case=case.name):
                    self.assertEqual((same_permits, same_rest),
                                     (change['changed'] == 'workflow', change['changed'] == 'permits'))

    def test_refusal_cannot_send_and_success_cannot_retry(self):
        for fragment, field, value in [('resolved-null', 'requests', 1),
                                       ('agent-resolved', 'attempts', 1),
                                       ('accepted-status-retains', 'attempts', 2),
                                       ('accepted-status-retains', 'sibling', 'quarantined')]:
            directory, document = self.copy_fixture('expected-http.json', fragment)
            document['observations'][field] = value
            self.rejected(directory, 'expected-http.json', document)

    def test_transport_does_not_fabricate_status_or_route(self):
        directory, document = self.copy_fixture('expected-http.json', 'unknown-final-route')
        document['observations']['output']['url'] = 'https://example.test/probe'
        self.rejected(directory, 'expected-http.json', document)
        directory, document = self.copy_fixture('expected-http.json', 'keyless-transport')
        document['observations']['error']['status_code'] = 503
        self.rejected(directory, 'expected-http.json', document)
        directory, document = self.copy_fixture('expected-http.json', 'keyless-transport')
        document['observations']['error']['transient'] = True
        self.rejected(directory, 'expected-http.json', document)

    def test_compose_admission_is_separate_from_execution_and_findings(self):
        for fragment, field, value in [('effectful', 'draft_effects', 1),
                                       ('missing-child', 'child_reads', 1),
                                       ('secret-flow', 'valid', False),
                                       ('secret-flow', 'secret_findings', 'zero')]:
            directory, document = self.copy_fixture('expected-compose.json', fragment)
            document['observations'][field] = value
            self.rejected(directory, 'expected-compose.json', document)
        directory, document = self.copy_fixture('expected-compose.json', 'missing-child')
        (directory/'absent-child.nika').write_text('nika: present\ntasks: {}\n')
        self.rejected(directory, 'expected-compose.json', document)

    def test_export_cannot_skip_a_surface_or_claim_a_task_value(self):
        for field, value in [('secret_occurrences', 1), ('derived_value', 'true'),
                             ('surfaces', ['stdout']), ('public_sentinel', 'redacted')]:
            directory, document = self.copy_fixture('expected-export.json', 'derived')
            document['observations'][field] = value
            self.rejected(directory, 'expected-export.json', document)
        directory, document = self.copy_fixture('expected-export.json', 'identity')
        document['observations']['allowed_outcomes'] = ['delivered']
        self.rejected(directory, 'expected-export.json', document)

    def test_layout_does_not_hide_or_escape_an_assertion(self):
        directory, document = self.copy_fixture('expected-compose.json')
        document['input'] = '../draft.nika'
        self.rejected(directory, 'expected-compose.json', document)
        directory, document = self.copy_fixture('expected-approval.json')
        (directory/'input.nika').unlink()
        self.rejected(directory, 'expected-approval.json', document)
        directory, document = self.copy_fixture('expected-approval.json')
        (directory/'run.json').write_text('{}')
        self.rejected(directory, 'expected-approval.json', document)
        directory, document = self.copy_fixture('expected-approval.json')
        (directory/'expected-run.json').write_text('{}')
        with self.assertRaises(runner.InvalidFixture):
            runner.fixture_door(directory)

    def test_sweep_collects_every_door_and_keeps_nonzero(self):
        for index, path in enumerate(fixtures()):
            shutil.copytree(path.parent, self.root / str(index))
        output = io.StringIO()
        with patch.object(runner, 'RUNTIME', self.root), contextlib.redirect_stdout(output):
            code = runner.main(['runtime-differential.py'])
        self.assertEqual(code, 1)
        self.assertEqual(output.getvalue().count('UNSUPPORTED  '), len(fixtures()))
        self.assertIn('0 agree', output.getvalue())
        self.mock_process.assert_not_called()

    def test_sweep_reports_an_orphan_draft_and_an_invalid_contract(self):
        orphan = self.root/'orphan'; orphan.mkdir(); (orphan/'draft.nika').write_text('nika: orphan\n')
        directory, document = self.copy_fixture('expected-export.json')
        document['unknown'] = 1; (directory/'expected-export.json').write_text(json.dumps(document))
        output = io.StringIO()
        with patch.object(runner, 'RUNTIME', self.root), contextlib.redirect_stdout(output):
            code = runner.main(['runtime-differential.py'])
        self.assertEqual(code, 1)
        self.assertEqual(output.getvalue().count('FIXTURE-ERROR  '), 2)
        self.assertNotIn('UNSUPPORTED  ', output.getvalue())
        self.mock_process.assert_not_called()


if __name__ == '__main__':
    unittest.main()
