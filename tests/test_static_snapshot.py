import http.client
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from brain.server import App, create_server


class StaticSnapshot(unittest.TestCase):
    def test_disk_update_cannot_mix_new_frontend_with_loaded_backend(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for name in ('index.html','app.js','style.css','ntu-logo.png','aspire-logo.svg','tencent-cloud-logo.svg'):(root/name).write_bytes(b'original paired build')
            app=App()
            with patch('brain.server.WEB',root):server=create_server(app)
            worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
            try:
                (root/'app.js').write_bytes(b'new incompatible frontend')
                with patch('brain.server.WEB',root):
                    client=http.client.HTTPConnection(*server.server_address,timeout=2)
                    client.request('GET','/app.js');response=client.getresponse()
                    self.assertEqual(response.status,200)
                    self.assertEqual(response.read(),b'original paired build')
                    client.close()
            finally:
                server.shutdown();server.server_close();worker.join();app.store.db.close()
