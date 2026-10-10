"""Fixture product HTTP and actual page script together; no browser/native/model fee."""
import subprocess
import threading
import time
import unittest
from brain.budget import TrialAdmissionPaused
from brain.server import App,create_server


class FrontendHTTP(unittest.TestCase):
    def test_page_lifecycle_matches_actual_http_contract(self):
        app=App();original=app.engine.query
        class Gate:
            calls=0
            def public_status(self):
                return {'allowed':self.calls<1,'reason':None if self.calls<1 else 'attempt_limit',
                        'attempts_used':self.calls,'attempts_limit':1,'attempts_remaining':max(0,1-self.calls)}
            def __call__(self,*args,**kwargs):
                if self.calls:raise TrialAdmissionPaused('Offline fixture limit')
                self.calls+=1;time.sleep(.4)
                return original(*args,**kwargs)
        gate=Gate();app.engine.query=gate;server=create_server(app)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            result=subprocess.run(['node','tests/frontend_http_lifecycle.js',f'http://127.0.0.1:{server.server_port}'],capture_output=True,text=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('PASS: real fixture product HTTP',result.stdout)
            self.assertEqual(gate.calls,1)
        finally:server.shutdown();server.server_close();thread.join(2);app.store.db.close()
