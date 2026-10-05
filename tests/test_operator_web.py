import contextlib
import errno
import io
import json
import threading
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from brain.confluence import ConfluenceReader, Delegation, SourceUnavailable
from brain.operator_web import OperatorApp, main
from brain.server import create_server
from brain.store import Store
from test_confluence_query import SourceTransport
import test_http


def setup_app():
    transport = SourceTransport()
    reader = ConfluenceReader('https://test.atlassian.net', 'pilot', ['98564'], ['123'],
        {'eng_b': Delegation('employee', 'Bearer employee')}, transport)
    store = Store()
    return OperatorApp(reader, store, 'eng_b'), transport


class OperatorIdentity(unittest.TestCase):
    def setUp(self):
        self.app, self.transport = setup_app()
        self.addCleanup(self.app.store.db.close)

    def test_ticket_is_one_use_and_server_actor_cannot_be_chosen(self):
        ticket = self.app.bootstrap_ticket()
        for payload in [{'ticket': ticket, 'user': 'security'}, {'user': 'eng_b'}, {'ticket': 'wrong'}]:
            with self.assertRaises(PermissionError): self.app.authenticate(payload)
        actor = self.app.authenticate({'ticket': ticket})
        self.assertEqual(actor.user_id, 'eng_b'); self.assertEqual(actor.tenant, 'pilot')
        with self.assertRaises(PermissionError): self.app.authenticate({'ticket': ticket})

    def test_expired_ticket_is_not_accepted(self):
        self.app._ticket_expires = 0
        with self.assertRaises(PermissionError):
            self.app.authenticate({'ticket': self.app.bootstrap_ticket()})

    def test_startup_substitution_fails_before_page_read_or_session(self):
        store = Store(); self.addCleanup(store.db.close)
        reader = self.app.pilot.authority.readers['confluence']
        reader.delegations['eng_b'] = Delegation('different-employee', 'Bearer employee')
        count = len(self.transport.calls)
        with self.assertRaises(SourceUnavailable): OperatorApp(reader, store, 'eng_b')
        self.assertEqual(len(self.transport.calls), count + 1)
        self.assertTrue(self.transport.calls[-1][0].endswith('/user/current'))

    def test_default_cli_and_real_transport_guard_do_not_contact_source(self):
        with contextlib.redirect_stdout(io.StringIO()), patch('scripts.confluence_probe.load_reader') as load:
            self.assertEqual(main(['--config', 'missing']), 2); load.assert_not_called()
        reader = ConfluenceReader('https://test.atlassian.net', 'pilot', ['98564'], ['123'], {})
        with patch.object(reader.transport, 'get') as get:
            with self.assertRaises(ValueError): OperatorApp(reader, self.app.store, 'eng_b')
            get.assert_not_called()

    def test_port_conflict_is_reported_before_any_credential_request(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), \
             patch('brain.operator_web.create_server', side_effect=OSError(errno.EADDRINUSE, 'private detail')), \
             patch('scripts.confluence_probe.load_reader') as load:
            self.assertEqual(main(['--config', 'missing', '--live']), 2)
            load.assert_not_called()
        self.assertIn('[port_in_use]', output.getvalue())
        self.assertIn('--port 8082', output.getvalue())
        self.assertNotIn('private detail', output.getvalue())

    def test_native_identity_failure_has_safe_stage_and_releases_reserved_listener(self):
        output = io.StringIO()
        from unittest.mock import Mock
        server = Mock()
        reader = self.app.pilot.authority.readers['confluence']
        # Use a real isolated disk store: mocking Store with :memory: while main
        # chmods its DB path accidentally depended on a leftover local pilot DB.
        with tempfile.TemporaryDirectory() as directory, \
             contextlib.redirect_stdout(output), \
             patch('brain.operator_web.create_server', return_value=server), \
             patch('scripts.confluence_probe.load_reader', return_value=reader), \
             patch('brain.operator_web.Path', return_value=Path(directory)), \
             patch('brain.operator_web.OperatorApp', side_effect=SourceUnavailable('secret upstream response')):
            self.assertEqual(main(['--config', 'mock', '--live']), 2)
            self.assertEqual((Path(directory) / 'confluence-web.sqlite').stat().st_mode & 0o777, 0o600)
        server.serve_forever.assert_not_called()
        server.server_close.assert_called_once()
        self.assertIn('[native_identity_unavailable]', output.getvalue())
        self.assertNotIn('secret upstream response', output.getvalue())

    def test_configuration_failure_releases_listener_without_serving(self):
        output = io.StringIO()
        from unittest.mock import Mock
        server = Mock()
        with contextlib.redirect_stdout(output), \
             patch('brain.operator_web.create_server', return_value=server), \
             patch('scripts.confluence_probe.load_reader', side_effect=ValueError('secret input')):
            self.assertEqual(main(['--config', 'mock', '--live']), 2)
        server.serve_forever.assert_not_called()
        server.server_close.assert_called_once()
        self.assertIn('[configuration_or_hidden_input_unavailable]', output.getvalue())
        self.assertNotIn('secret input', output.getvalue())

    def test_hidden_input_failure_reports_fixed_code_and_never_requests_native_identity(self):
        from brain.credential_input import HiddenInputUnavailable
        from unittest.mock import Mock
        for code in ('email_invalid','token_empty','token_multiline','token_too_long',
                     'hidden_input_unavailable','secure_tty_required','input_ended'):
            output=io.StringIO();server=Mock()
            with self.subTest(code=code),contextlib.redirect_stdout(output), \
                 patch('brain.operator_web.create_server',return_value=server), \
                 patch('scripts.confluence_probe.load_reader',side_effect=HiddenInputUnavailable(code)), \
                 patch('brain.operator_web.OperatorApp') as application:
                self.assertEqual(main(['--config','mock','--live']),2)
                application.assert_not_called();server.serve_forever.assert_not_called()
                server.server_close.assert_called_once()
            self.assertIn('[credential_'+code+']',output.getvalue())


class OperatorHTTP(unittest.TestCase):
    request = test_http.HTTP.request

    def setUp(self):
        self.app, self.transport = setup_app()
        self.server = create_server(self.app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start(); self.cookie = ''; self.csrf = ''

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.app.store.db.close()

    def login(self):
        status, body = self.request('/api/operator/login', {'ticket': self.app.bootstrap_ticket()})
        self.assertEqual(status, 200); self.csrf = body['csrf']
        return body

    def test_browser_session_binds_verified_identity_and_never_returns_api_credential(self):
        status, health = self.request('/api/health')
        self.assertEqual(status, 200); self.assertEqual(health['auth_kind'], 'operator')
        self.assertEqual(health['mode'], 'confluence_mock_http_fake_model')
        self.assertFalse(health['live_enabled'])
        self.assertNotIn(self.app.bootstrap_ticket(), json.dumps(health))
        self.assertEqual(self.request('/api/demo/login', {'user': 'security'})[0], 403)
        login = self.login()
        self.assertEqual(login['actor'], 'eng_b')
        self.assertNotIn('Bearer', json.dumps(login))
        self.assertEqual(self.request('/api/session')[1]['actor'], 'eng_b')
        status, answer = self.request('/api/query', {'question': 'runbook'})
        self.assertEqual(status, 200); self.assertEqual(answer['actor'], 'eng_b')
        self.assertEqual(answer['evidence'][0]['resource_id'], 'confluence:98564')
        self.assertNotIn('Bearer', json.dumps(answer))
        self.assertTrue(any(e['event_type'] == 'response_dispatch_attempted' for e in self.app.audit.export()))

    def test_same_http_session_revocation_protects_history_export_and_citation(self):
        self.login()
        first = self.request('/api/query', {'question': 'runbook'})[1]
        self.transport.allowed.clear(); self.app.sessions[next(iter(self.app.sessions))]['last_query'] = 0
        status, next_answer = self.request('/api/query', {'question': 'details'})
        self.assertEqual(status, 200); self.assertEqual(next_answer['evidence'], [])
        self.assertEqual(self.app.engine.model.calls[-1]['evidence'], [])
        for endpoint in ['/api/history', '/api/export/' + first['request_id']]:
            if endpoint.startswith('/api/export/'):
                self.assertEqual(self.request(endpoint)[0],404)
                continue
            history = self.request(endpoint)[1]['history']
            self.assertTrue(any(h.get('unavailable') for h in history))
            self.assertNotIn('budget version 1', json.dumps(history))
        citation = '/api/evidence/' + first['evidence'][0]['evidence_id']
        self.assertEqual(self.request(citation), self.request('/api/evidence/missing@1'))

    def test_host_csrf_origin_and_identity_field_forgery_are_blocked(self):
        ticket = self.app.bootstrap_ticket()
        self.assertEqual(self.request('/api/operator/login', {'ticket': ticket}, {'Origin': 'https://evil.example'})[0], 403)
        self.assertEqual(self.app.bootstrap_ticket(), ticket)
        self.assertEqual(self.request('/api/health', extra={'Host': 'evil.example'})[0], 403)
        self.login()
        self.assertEqual(self.request('/api/query', {'question': 'runbook'}, {'X-CSRF-Token': 'bad'})[0], 403)
        for field in ['role', 'user_id', 'tenant']:
            self.assertEqual(self.request('/api/query', {'question': 'runbook', field: 'admin'})[0], 400)
        self.assertEqual(self.app.engine.model.calls, [])

    def test_logout_invalidates_session_and_consumed_link_does_not_log_in_again(self):
        ticket = self.app.bootstrap_ticket(); self.login()
        self.assertEqual(self.request('/api/logout', {})[0], 200)
        self.assertEqual(self.request('/api/session')[0], 403)
        self.assertEqual(self.request('/api/operator/login', {'ticket': ticket})[0], 403)
        self.assertEqual(self.request('/api/audit/events', {})[0], 403)


if __name__ == '__main__': unittest.main()
