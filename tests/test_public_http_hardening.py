"""Local synthetic abuse-boundary tests; no public traffic or model billing."""
import http.client
import json
import socket
import threading
import time
import unittest
from unittest.mock import patch
from brain.server import App, create_server


class PublicHardening(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.server = create_server(self.app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.app.store.db.close()

    def call(self, path, data=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        conn.request('POST' if data is not None else 'GET', path,
                     json.dumps(data) if data is not None else None,
                     {'Content-Type': 'application/json', **(headers or {})})
        response = conn.getresponse()
        result = response.status, response.read(), dict(response.getheaders())
        conn.close()
        return result

    def test_anonymous_and_unknown_routes_never_refresh(self):
        with patch.object(self.app, 'refresh') as refresh:
            for path in ('/api/evidence/C-01@1', '/api/history', '/.env', '/../../etc/passwd', '/api/admin/sync'):
                self.assertEqual(self.call(path)[0], 403)
            code, _, headers = self.call('/api/demo/login', {'user': 'eng_a'})
            self.assertEqual(code, 200)
            cookie = headers['Set-Cookie'].split(';')[0]
            self.assertEqual(self.call('/not-a-route', headers={'Cookie': cookie})[0], 404)
            refresh.assert_not_called()
            self.assertEqual(self.call('/api/history', headers={'Cookie': cookie})[0], 200)
            refresh.assert_called_once()

    def test_login_limit_precedes_expensive_authentication_and_expires(self):
        with patch.object(self.app, 'authenticate', side_effect=PermissionError) as authenticate:
            for _ in range(30):
                self.assertEqual(self.call('/api/demo/login', {'user': 'bad'})[0], 403)
            self.assertEqual(self.call('/api/demo/login', {'user': 'bad'})[0], 429)
            self.assertEqual(authenticate.call_count, 30)
            self.server.login_attempts = type(self.server.login_attempts)([time.monotonic()-61]*30)
            self.assertEqual(self.call('/api/demo/login', {'user': 'bad'})[0], 403)
            self.assertEqual(self.call('/')[0], 200)

    def test_session_capacity_and_expiry_cleanup(self):
        self.app.sessions = {str(i): {'expires': time.monotonic()+60} for i in range(128)}
        self.assertEqual(self.call('/api/demo/login', {'user': 'eng_a'})[0], 429)
        self.app.sessions['0']['expires'] = 0
        self.app.session_runs.runs['0'] = {'private': 'old'}
        self.assertEqual(self.call('/api/demo/login', {'user': 'eng_a'})[0], 200)
        self.assertEqual(len(self.app.sessions), 128)
        self.assertNotIn('0', self.app.session_runs.runs)

    def test_connection_saturation_does_not_create_more_threads(self):
        # Reserve every slot to deterministically simulate 32 slow connections.
        for _ in range(32):
            self.assertTrue(self.server.connection_slots.acquire(blocking=False))
        try:
            with socket.create_connection(('127.0.0.1', self.server.server_port), timeout=2) as conn:
                conn.sendall(b'GET / HTTP/1.0\r\n\r\n')
                try:
                    self.assertEqual(conn.recv(1), b'')
                except ConnectionResetError:
                    pass
        finally:
            for _ in range(32): self.server.connection_slots.release()
        self.assertEqual(self.call('/')[0], 200)

    def test_response_headers_and_query_queue_capacity(self):
        _, _, headers = self.call('/')
        self.assertNotIn('Python', headers['Server'])
        self.assertIn('microphone=()', headers['Permissions-Policy'])
        code, raw, headers = self.call('/api/demo/login', {'user': 'eng_a'})
        self.assertEqual(code, 200)
        self.app.active_queries.update({'a', 'b', 'c', 'd'})
        with patch.object(self.app.engine, 'query') as query:
            self.assertEqual(self.call('/api/query', {'question': 'payment-service'},
                {'Cookie': headers['Set-Cookie'].split(';')[0], 'X-CSRF-Token': json.loads(raw)['csrf']})[0], 429)
            query.assert_not_called()
