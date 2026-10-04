import contextlib
import io
import threading
import unittest
from unittest.mock import Mock, patch

from brain.confluence import Delegation, SourceUnavailable
from brain.jira import JiraReader
from brain.operator_web import OperatorApp, main
from brain.server import create_server
from brain.store import Store
import test_http
from test_jira import JiraTransport, reader


class JiraOperatorHTTP(unittest.TestCase):
    request = test_http.HTTP.request

    def setUp(self):
        self.transport = JiraTransport()
        self.reader = reader(self.transport)
        self.app = OperatorApp(self.reader, Store(), 'eng_b')
        self.server = create_server(self.app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start(); self.cookie = ''; self.csrf = ''

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.app.store.db.close()

    def login(self):
        status, body = self.request('/api/operator/login', {'ticket': self.app.bootstrap_ticket()})
        self.assertEqual(status, 200); self.csrf = body['csrf']

    def test_one_input_session_reuses_delegation_but_rechecks_source_identity(self):
        self.login()
        with patch('scripts.confluence_probe.hidden_delegation') as prompt:
            for _ in range(2):
                self.app.sessions[next(iter(self.app.sessions))]['last_query'] = 0
                before = len(self.transport.calls)
                status, answer = self.request('/api/query', {'question': 'safeguards'})
                self.assertEqual(status, 200)
                self.assertEqual(answer['mode'], 'jira_mock_http_fake_model')
                self.assertEqual(answer['evidence'][0]['resource_id'], 'jira:10003')
                self.assertTrue(any(u.endswith('/myself') for u in self.transport.calls[before:]))
                self.assertNotIn('Bearer', str(answer))
            prompt.assert_not_called()
        self.assertEqual(self.request('/api/health')[1]['auth_kind'], 'operator')
        # Authenticated operator sees no demo login route; cannot switch actor.
        self.assertEqual(self.request('/api/demo/login', {'user': 'security'})[0], 404)
        self.assertEqual(self.request('/api/session')[1]['actor'], 'eng_b')

    def test_same_jira_session_revocation_blocks_query_history_export_and_citation(self):
        self.login()
        first = self.request('/api/query', {'question': 'safeguards'})[1]
        self.transport.issue_allowed.clear()
        self.app.sessions[next(iter(self.app.sessions))]['last_query'] = 0
        second = self.request('/api/query', {'question': 'safeguards', 'history_id': first['request_id']})[1]
        self.assertEqual(second['evidence'], [])
        self.assertEqual(self.app.engine.model.calls[-1]['evidence'], [])
        for endpoint in ['/api/history', '/api/export/' + first['request_id']]:
            result = self.request(endpoint)[1]
            self.assertTrue(any(h.get('unavailable') for h in result['history']))
            self.assertNotIn('GA not approved', str(result))
        self.assertEqual(self.request('/api/evidence/' + first['evidence'][0]['evidence_id']),
                         self.request('/api/evidence/missing@1'))

    def test_native_identity_substitution_stops_startup_and_discovery_reader_cannot_serve(self):
        self.reader.delegations['eng_b'] = Delegation('admin', 'Bearer employee')
        store = Store(); self.addCleanup(store.db.close)
        with self.assertRaises(SourceUnavailable): OperatorApp(self.reader, store, 'eng_b')
        discovery = JiraReader('https://test.atlassian.net', 'pilot', {}, [], {},
                               discovery_only=True, discovery_keys={'KAN-4': 'KAN'})
        with self.assertRaises(ValueError): OperatorApp(discovery, store, 'eng_b')

    def test_cli_selects_jira_loader_and_prompts_once_per_service_start(self):
        server = Mock(); server.serve_forever.side_effect = KeyboardInterrupt
        output = io.StringIO()
        with contextlib.redirect_stdout(output), \
             patch('brain.operator_web.create_server', return_value=server), \
             patch('scripts.jira_query.load_reader', return_value=self.reader) as load, \
             patch('scripts.confluence_probe.load_reader') as cf_load, \
             patch('brain.operator_web.Store', return_value=self.app.store), \
             patch('brain.operator_web.os.chmod'):
            self.assertEqual(main(['--source', 'jira', '--config', 'mock', '--actor', 'eng_b', '--live']), 0)
            load.assert_called_once_with('mock', prompt_actor='eng_b'); cf_load.assert_not_called()
        self.assertIn('Jira LIVE API / FAKE MODEL', output.getvalue())
        self.assertNotIn('Bearer', output.getvalue())
        server.server_close.assert_called_once()
