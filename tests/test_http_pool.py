import concurrent.futures
import json
from pathlib import Path
import socket
import ssl
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.error import URLError
from urllib.request import Request

from brain.confluence import JsonTransport, SourceUnavailable, SourceRateLimited
from brain.http_pool import PooledOpener, install
from brain.source_cooldown import SourceCooldownTransport


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, *args):
        pass

    def do_GET(self):
        with self.server.guard:
            self.server.paths.append(self.path)
        if self.path == '/drop':
            self.close_connection = True
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
            return
        status = {'/deny': 403, '/redirect': 302, '/rate': 429}.get(self.path, 200)
        body = json.dumps({'authorization': self.headers.get('Authorization')}).encode()
        if self.path == '/large':
            body = b'x'*1000
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body) + (5 if self.path == '/truncated' else 0)))
        if status == 302:
            self.send_header('Location', self.server.base+'/ok')
        if status == 429:
            self.send_header('Retry-After', '17')
        self.end_headers()
        try:
            self.wfile.write(body)
            self.wfile.flush()
        except OSError:
            pass
        if self.path == '/truncated':
            self.close_connection = True


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def get_request(self):
        result = super().get_request()
        with self.guard:
            self.accepted += 1
        return result

    def handle_error(self, request, client_address):
        pass


class PoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        root = Path(cls.directory.name)
        cls.cert = root/'cert.pem'
        key = root/'key.pem'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
            '-keyout', str(key), '-out', str(cls.cert), '-days', '1', '-subj', '/CN=localhost',
            '-addext', 'subjectAltName=DNS:localhost'], check=True, capture_output=True)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cls.cert, key)
        cls.server = Server(('127.0.0.1', 0), Handler)
        cls.server.guard = threading.Lock()
        cls.server.accepted = 0
        cls.server.paths = []
        cls.server.socket = context.wrap_socket(cls.server.socket, server_side=True)
        cls.base = cls.server.base = f'https://localhost:{cls.server.server_port}'
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.directory.cleanup()

    def setUp(self):
        self.proxy_patch = patch('brain.http_pool.getproxies', return_value={})
        self.proxy_patch.start()
        self.addCleanup(self.proxy_patch.stop)
        self.transport = JsonTransport(timeout=2, max_bytes=100)
        self.original = self.transport.opener
        context = ssl.create_default_context(cafile=str(self.cert))
        self.pool = PooledOpener(self.base, self.original, context=context)
        self.transport.opener = self.pool
        self.addCleanup(self.pool.close)
        self.start = self.server.accepted
        self.path_start = len(self.server.paths)

    def get(self, path='/ok', credential='Bearer test-one'):
        return self.transport.get(self.base+path, credential)

    def request(self):
        return Request(self.base+'/ok', headers={'Authorization': 'Bearer test-one'})

    def test_three_reads_share_one_verified_tls_connection(self):
        for _ in range(3):
            self.assertEqual(self.get(), (200, {'authorization': 'Bearer test-one'}))
        self.assertEqual(self.server.accepted-self.start, 1)
        self.assertEqual(self.server.paths[self.path_start:], ['/ok']*3)

    def test_credential_rotation_isolated(self):
        self.get()
        self.assertEqual(self.get(credential='Bearer test-two')[1]['authorization'], 'Bearer test-two')
        self.assertEqual(self.server.accepted-self.start, 2)

    def test_redirect_denial_and_rate_limit_no_follow_or_retry(self):
        self.assertEqual(self.get('/deny'), (403, None))
        self.assertEqual(self.get('/redirect'), (302, None))
        with self.assertRaises(SourceRateLimited) as caught:
            self.get('/rate')
        self.assertEqual(caught.exception.retry_after, 17)
        self.assertEqual(self.server.paths[self.path_start:], ['/deny', '/redirect', '/rate'])
        self.assertEqual(self.pool.count, 0)

    def test_partial_oversize_and_truncated_reads_discard_connection(self):
        for path in ('/large', '/truncated'):
            with self.assertRaises(SourceUnavailable):
                self.get(path)
            self.assertEqual(self.pool.count, 0)
        with self.pool.open(self.request(), timeout=1) as response:
            response.read(1)
        self.assertEqual(self.pool.count, 0)
        self.assertEqual(self.get()[0], 200)

    def test_disconnect_has_one_attempt_and_recovery_on_new_request(self):
        with self.assertRaises(SourceUnavailable):
            self.get('/drop')
        self.assertEqual(self.server.paths[self.path_start:], ['/drop'])
        self.assertEqual(self.pool.count, 0)
        self.assertEqual(self.get()[0], 200)

    def test_bounded_pool_waits_and_timeout_does_not_send(self):
        first = self.pool.open(self.request(), timeout=1)
        second = self.pool.open(self.request(), timeout=1)
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                pending = executor.submit(self.pool.open, self.request(), 0.05)
                with self.assertRaises(URLError):
                    pending.result(timeout=2)
            self.assertEqual(self.server.accepted-self.start, 2)
            self.assertEqual(self.server.paths[self.path_start:], ['/ok', '/ok'])
        finally:
            first.close()
            second.close()
        self.assertEqual(self.get()[0], 200)

    def test_four_connection_limit_blocks_fifth_without_sending(self):
        pool = PooledOpener(self.base, self.original, maximum=4, context=self.pool.context)
        self.addCleanup(pool.close)
        held = []
        try:
            held = [pool.open(self.request(), timeout=1) for _ in range(4)]
            with self.assertRaises(URLError):
                pool.open(self.request(), timeout=0.05)
            self.assertEqual(self.server.accepted-self.start, 4)
            self.assertEqual(self.server.paths[self.path_start:], ['/ok']*4)
        finally:
            for response in held: response.close()
        self.assertEqual(pool.count, 0)

    def test_proxy_uses_original_opener_and_never_direct_connects(self):
        fallback = Mock()
        self.pool.fallback = fallback
        with patch('brain.http_pool.getproxies', return_value={'https': 'http://proxy.invalid:8080'}), \
             patch('brain.http_pool.proxy_bypass', return_value=False):
            request = self.request()
            self.assertIs(self.pool.open(request, timeout=1), fallback.open.return_value)
            fallback.open.assert_called_once_with(request, timeout=1)
        self.assertEqual(self.server.accepted, self.start)

    def test_untrusted_certificate_destination_and_write_rejected(self):
        untrusted = PooledOpener(self.base, self.original)
        self.addCleanup(untrusted.close)
        with self.assertRaises(URLError):
            untrusted.open(self.request(), timeout=1)
        for request in (Request('http://localhost/'), Request('https://other.invalid/'),
                        Request(self.base+'/ok', method='POST', data=b'')):
            with self.assertRaises((URLError, ValueError)):
                self.pool.open(request, timeout=1)
        self.assertEqual(self.server.paths[self.path_start:], [])

    def test_closed_pool_rejects_and_does_not_reopen(self):
        self.get()
        self.pool.close()
        with self.assertRaises(SourceUnavailable):
            self.get()
        self.assertEqual(self.pool.count, 0)
        self.assertEqual(self.server.accepted-self.start, 1)

    def test_error_body_is_never_read_and_socket_is_discarded(self):
        response = Mock(status=403, headers={})
        connection = Mock()
        connection.getresponse.return_value = response
        with patch('brain.http_pool.http.client.HTTPSConnection', return_value=connection):
            self.assertEqual(self.get('/deny'), (403, None))
        response.read.assert_not_called()
        connection.request.assert_called_once()
        self.assertEqual(self.pool.count, 0)

    def test_429_preserves_shared_cooldown_without_sleep_or_retry(self):
        wrapper = SourceCooldownTransport(self.transport)
        with self.assertRaises(SourceRateLimited):
            wrapper.get(self.base+'/rate', 'Bearer test-one')
        with self.assertRaises(SourceRateLimited):
            wrapper.get(self.base+'/ok', 'Bearer test-one')
        self.assertEqual(self.server.paths[self.path_start:], ['/rate'])

    def test_stale_connection_is_not_retried(self):
        response = Mock()
        response.isclosed.return_value = True
        response.length, response.will_close = 0, False
        response.status, response.headers = 200, {}
        response.read.return_value = b''
        connection = Mock()
        connection.getresponse.return_value = response
        with patch('brain.http_pool.http.client.HTTPSConnection', return_value=connection) as factory:
            with self.pool.open(self.request(), timeout=1) as result:
                result.read()
            connection.request.side_effect = ConnectionResetError('private upstream detail')
            with self.assertRaises(URLError) as caught:
                self.pool.open(self.request(), timeout=1)
            self.assertNotIn('private upstream detail', str(caught.exception))
            self.assertEqual(factory.call_count, 1)
            self.assertEqual(connection.request.call_count, 2)
        self.assertEqual(self.pool.count, 0)

    def test_tls_verification_cannot_be_disabled(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        with self.assertRaises(ValueError):
            PooledOpener(self.base, self.original, context=context)

    def test_install_preserves_wrappers_and_rolls_back(self):
        transport = JsonTransport()
        old = transport.opener
        wrapper = SourceCooldownTransport(transport)
        reader = SimpleNamespace(api_base=self.base, transport=wrapper)
        rollback = install({'confluence': reader})
        self.assertIs(reader.transport, wrapper)
        self.assertIsInstance(transport.opener, PooledOpener)
        pool = transport.opener
        rollback()
        self.assertIs(transport.opener, old)
        self.assertTrue(pool.closed)


if __name__ == '__main__':
    unittest.main()
