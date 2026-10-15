import http.client
import json
import threading
import unittest
import time
from unittest.mock import patch
from brain.server import create_server
import test_application_audit as audit_cases


class ApplicationAuditHTTP(unittest.TestCase):
    save=audit_cases.ApplicationAudit.save
    seed=audit_cases.ApplicationAudit.seed
    def setUp(self):
        audit_cases.ApplicationAudit.setUp(self)
        self.server=create_server(self.app)
        self.worker=threading.Thread(target=self.server.serve_forever,daemon=True);self.worker.start()
        self.addCleanup(self.stop)
        self.cookie='';self.csrf=''
    def stop(self):
        self.server.shutdown();self.server.server_close();self.worker.join()
    def request(self,path,data=None):
        client=http.client.HTTPConnection(*self.server.server_address,timeout=3)
        headers={'Cookie':self.cookie,'X-CSRF-Token':self.csrf,'Content-Type':'application/json'}
        client.request('POST' if data is not None else 'GET',path,
                       json.dumps(data) if data is not None else None,headers)
        response=client.getresponse();body=json.loads(response.read())
        if response.getheader('Set-Cookie'):self.cookie=response.getheader('Set-Cookie').split(';')[0]
        client.close();return response.status,body
    def login(self,user):
        status,body=self.request('/api/reviewer/login',{'username':user,'password':'test-password-long'})
        self.assertEqual(status,200);self.csrf=body['csrf'];return body
    def test_scoped_auditor_login_runtime_and_query_denial(self):
        session=self.login('inspector')
        self.assertTrue(session['can_audit'])
        self.assertEqual(session['audit_viewer_ids'],[self.viewer])
        self.assertEqual(self.request('/api/runtime')[0],200)
        self.assertEqual(self.request('/api/query',{'question':'payment-service'})[0],403)
        self.seed('audited')
        status,result=self.request('/api/audit/events',{'application_identity':self.viewer})
        self.assertEqual(status,200);self.assertEqual({e['request_id'] for e in result['events']},{'audited'})
        self.assertEqual(self.request('/api/audit/events',{'actor':'eng_b'})[0],400)
    def test_early_request_failure_is_auditable_and_employee_still_denied(self):
        self.login('first')
        with patch.object(self.app,'refresh',side_effect=ValueError('private failure')):
            status,failed=self.request('/api/query',{'question':'payment-service'})
        self.assertEqual(status,503)
        self.assertEqual(self.request('/api/audit/events',{})[0],403)
        self.login('inspector')
        status,result=self.request('/api/audit/events',{'application_identity':self.viewer})
        self.assertEqual(status,200)
        self.assertIn(failed['request_id'],{e['request_id'] for e in result['events']})
        self.assertEqual(next(e['payload']['query'] for e in result['events']
            if e['event_type']=='reviewer_query'),'payment-service')

    def test_registration_failure_finishes_run_and_session_can_submit_again(self):
        self.login('first')
        with patch.object(self.app,'register_request',side_effect=OSError('private failure')):
            status,failed=self.request('/api/query',{'question':'payment-service'})
        self.assertEqual(status,503)
        self.assertEqual(self.request('/api/runtime')[1]['run']['status'],'failed')
        time.sleep(.11)
        self.assertEqual(self.request('/api/query',{'question':'payment-service'})[0],200)

    def test_registration_and_failure_audit_outage_still_finishes_run(self):
        self.login('first')
        with patch.object(self.app,'register_request',side_effect=OSError('store offline')),patch.object(self.app.audit,'append',side_effect=OSError('store offline')):
            self.assertEqual(self.request('/api/query',{'question':'payment-service'})[0],503)
        self.assertEqual(self.request('/api/runtime')[1]['run']['status'],'failed')
