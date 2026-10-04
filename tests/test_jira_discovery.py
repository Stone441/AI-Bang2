import contextlib
import io
import json
import unittest
from unittest.mock import Mock, patch

from brain.confluence import Delegation
from brain.contracts import Actor
from brain.jira import JiraReader
from scripts.jira_query import main


class JiraDiscovery(unittest.TestCase):
    def setUp(self):
        self.transport = Mock()
        self.user = {'accountId': 'employee', 'active': True, 'accountType': 'atlassian'}
        self.metadata = {'id': '10004', 'key': 'KAN-4', 'fields': {
            'project': {'id': '10000', 'key': 'KAN'}, 'summary': 'MUST_NOT_RETURN'}}
        self.reader = JiraReader('https://test.atlassian.net', 'pilot', {}, [],
            {'eng_b': Delegation('employee', 'Bearer synthetic')}, self.transport,
            discovery_only=True, discovery_keys={'KAN-4': 'KAN'})
        self.actor = Actor('eng_b', 'pilot')

    def test_only_selected_metadata_and_isolated_from_content_reads(self):
        self.transport.get.side_effect = [(200, self.user), (200, self.metadata)]
        decision, ids = self.reader.discover_ids(self.actor, 'KAN-4')
        self.assertEqual(decision.result, 'allow')
        self.assertEqual(ids, {'issue_id': '10004', 'issue_key': 'KAN-4',
                              'project_id': '10000', 'project_key': 'KAN'})
        self.assertTrue(self.transport.get.call_args.args[0].endswith('/issue/KAN-4?fields=project'))
        self.transport.reset_mock()
        self.assertEqual(self.reader.read(self.actor, '10004')[0].result, 'unknown')
        self.transport.get.assert_not_called()

    def test_unapproved_key_tenant_or_unmapped_actor_never_calls_source(self):
        for actor, key in [(self.actor, 'KAN-1'), (Actor('eng_b', 'other'), 'KAN-4'),
                           (Actor('admin', 'pilot'), 'KAN-4'), (self.actor, '../KAN-4')]:
            d, ids = self.reader.discover_ids(actor, key)
            self.assertEqual(d.result, 'unknown'); self.assertIsNone(ids)
        self.transport.get.assert_not_called()

    def test_substituted_native_identity_never_fetches_issue(self):
        self.transport.get.return_value = (200, dict(self.user, accountId='admin'))
        d, ids = self.reader.discover_ids(self.actor, 'KAN-4')
        self.assertEqual(d.result, 'unknown'); self.assertIsNone(ids)
        self.assertEqual(self.transport.get.call_count, 1)

    def test_moved_wrong_key_or_malformed_metadata_never_returns_ids(self):
        for metadata in [dict(self.metadata, key='OTHER-4'),
                         dict(self.metadata, id=10004),
                         {'id': '10004', 'key': 'KAN-4', 'fields': {'project': {'id': '10000', 'key': 'OTHER'}}},
                         {'id': '10004', 'key': 'KAN-4', 'fields': {'project': None}}]:
            self.transport.get.side_effect = [(200, self.user), (200, metadata)]
            d, ids = self.reader.discover_ids(self.actor, 'KAN-4')
            self.assertEqual(d.result, 'unknown'); self.assertIsNone(ids)

    def test_denied_and_unavailable_results_are_distinct(self):
        for status in (403, 404, 401, 429, 500):
            self.transport.get.side_effect = [(200, self.user), (status, None)]
            d, ids = self.reader.discover_ids(self.actor, 'KAN-4')
            self.assertEqual(d.result, 'deny' if status in (403, 404) else 'unknown')
            self.assertIsNone(ids)

    def test_cli_discovery_has_no_database_or_content(self):
        self.transport.get.side_effect = [(200, self.user), (200, self.metadata)]
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch('scripts.jira_query.load_reader', return_value=self.reader), \
             patch('scripts.jira_query.Store') as store:
            self.assertEqual(main(['--config', 'mock', '--actor', 'eng_b', '--discover-ids', 'KAN-4', '--live']), 0)
            store.assert_not_called()
        result = json.loads(output.getvalue())
        self.assertEqual(result['mode'], 'jira_mock_http_configuration_probe')
        self.assertFalse(result['content_returned_to_probe'])
        self.assertNotIn('MUST_NOT_RETURN', output.getvalue())
        self.assertNotIn('Bearer', output.getvalue())

    def test_live_flag_and_constructor_boundaries(self):
        with contextlib.redirect_stdout(io.StringIO()), patch('scripts.jira_query.load_reader') as load:
            self.assertEqual(main(['--config', 'missing', '--actor', 'eng_b', '--discover-ids', 'KAN-4']), 2)
            load.assert_not_called()
        for kwargs in [{'discovery_only': True, 'discovery_keys': {}},
                       {'discovery_only': True, 'discovery_keys': {'KAN-4': '../KAN'}},
                       {'discovery_only': 1, 'discovery_keys': {'KAN-4': 'KAN'}}]:
            with self.assertRaises(ValueError):
                JiraReader('https://test.atlassian.net', 'pilot', {}, [], {}, **kwargs)
