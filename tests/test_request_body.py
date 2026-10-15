"""Real loopback clients: incomplete bodies must not monopolize application locks."""
import http.client
import json
import socket
import threading
import time
import unittest
from brain.server import App, create_server


class RequestBody(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.server = create_server(self.app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
        self.app.store.db.close()

    def test_stalled_unauthenticated_body_does_not_block_valid_login(self):
        slow = socket.create_connection(self.server.server_address)
        try:
            port = self.server.server_port
            slow.sendall((f'POST /api/demo/login HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n'
                          'Content-Type: application/json\r\nContent-Length: 120\r\n\r\n{').encode())
            time.sleep(.1)
            client = http.client.HTTPConnection('127.0.0.1', port, timeout=.5)
            try:
                client.request('POST', '/api/demo/login', json.dumps({'user':'eng_a'}),
                               {'Content-Type':'application/json'})
                try:
                    response = client.getresponse(); response.read()
                except TimeoutError:
                    self.fail('An unauthenticated partial body blocked another login')
                self.assertEqual(response.status, 200)
            finally:
                client.close()
        finally:
            slow.close()

    def test_incomplete_body_has_finite_deadline(self):
        self.server.body_timeout = .15
        slow = socket.create_connection(self.server.server_address, timeout=1)
        try:
            slow.sendall((f'POST /api/demo/login HTTP/1.1\r\nHost: 127.0.0.1:{self.server.server_port}\r\n'
                          'Content-Type: application/json\r\nContent-Length: 120\r\n\r\n{').encode())
            try:
                reply = slow.recv(4096)
            except TimeoutError:
                self.fail('Incomplete body has no finite deadline')
            self.assertIn(b'408', reply.split(b'\r\n')[0])
        finally:
            slow.close()
