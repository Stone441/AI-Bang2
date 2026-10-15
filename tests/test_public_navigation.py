"""Public static navigation is distinct from authenticated cross-site API access."""
import http.client
import threading
import unittest
from brain.server import App,create_server


class PublicNavigation(unittest.TestCase):
    def test_external_link_can_open_static_page_but_cannot_access_private_api(self):
        app=App();server=create_server(app,public_origin='https://demo.example.test')
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        def request(path,host='demo.example.test',method='GET'):
            client=http.client.HTTPConnection(*server.server_address,timeout=2)
            client.request(method,path,body='{}' if method=='POST' else None,headers={
                'Host':host,'Origin':'https://external.example','Sec-Fetch-Site':'cross-site',
                'Content-Type':'application/json'})
            response=client.getresponse();response.read();client.close();return response.status
        try:
            for path in ('/','/app.js','/style.css'):
                self.assertEqual(request(path),200,path)
            for path in ('/api/session','/api/runtime','/api/history','/api/health'):
                self.assertEqual(request(path),403,path)
            self.assertEqual(request('/api/demo/login',method='POST'),403)
            self.assertEqual(request('/',host='attacker.example'),403)
        finally:
            server.shutdown();server.server_close();worker.join();app.store.db.close()
