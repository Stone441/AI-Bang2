import json
import unittest
from unittest.mock import patch
import test_reviewer_access as helpers


class ApplicationRoles(unittest.TestCase):
    client = helpers.ReviewerAccess.client
    stop = helpers.ReviewerAccess.stop

    def setUp(self):
        self.policies = None
        helpers.ReviewerAccess.setUp(self)
        self.policies = {'engineer':{'resource_ids':None},
            'product':{'resource_ids':['C-02','J-02','J-03','S-02','D-02','D-03']},
            'partner':{'resource_ids':['C-02']}}
        for name, role in [('first','engineer'),('second','product'),('partner','partner')]:
            self.rows[name]['source_actor']='eng_b'
            self.rows[name]['demo_role']=role
        self.save()

    def save(self):
        helpers.ReviewerAccess.save(self)
        if self.policies is not None:
            body=json.loads(self.path.read_text());body['application_roles']=self.policies
            self.path.write_text(json.dumps(body));self.path.chmod(0o600)

    def test_three_roles_use_same_native_identity_but_different_model_evidence(self):
        evidence={}
        for name in ['first','second','partner']:
            c=self.client(name);status,body=c('/api/query',{'question':'payment-service payment-retry incident pilot'})
            self.assertEqual(status,200)
            evidence[name]={x['resource_id'] for x in self.base.engine.model.calls[-1]['evidence']}
        self.assertTrue(evidence['first']-evidence['second'])
        self.assertTrue(evidence['second']-evidence['partner'])
        self.assertEqual(evidence['partner'],{'C-02'})
        self.assertTrue(evidence['second']<=set(self.policies['product']['resource_ids']))
        checks=[e for e in self.base.audit.export() if e['event_type']=='authorization_decided' and e['payload'].get('application_role')=='partner']
        self.assertTrue(checks)
        self.assertTrue(all(e['actor']=='eng_b' and e['payload']['application_viewer'].startswith('reviewer:partner:') for e in checks))
        self.assertTrue(all(e['payload']['application_policy_digest'] for e in checks))

    def test_application_grant_cannot_override_native_denial(self):
        self.policies['partner']['resource_ids']=['C-03'];self.save()
        c=self.client('partner');status,body=c('/api/query',{'question':'security payroll incident'})
        self.assertEqual(status,200)
        self.assertEqual(body['evidence'],[])
        self.assertTrue(all(x['resource_id']!='C-03' for call in self.base.engine.model.calls for x in call['evidence']))

    def test_policy_revocation_covers_history_preview_and_new_query(self):
        c=self.client('partner');status,body=c('/api/query',{'question':'payment-retry pilot'})
        self.assertEqual(status,200);rid=body['request_id'];eid=body['evidence'][0]['evidence_id']
        self.policies['partner']['resource_ids']=[];self.save()
        self.assertEqual(c('/api/evidence/'+eid)[0],403)
        self.assertTrue(c('/api/history?request_id='+rid)[1]['history'][0]['unavailable'])
        import time
        time.sleep(.11)  # A new deliberate submission after the HTTP rate window.
        status,body=c('/api/query',{'question':'payment-retry pilot'})
        self.assertEqual(status,200);self.assertEqual(body['evidence'],[])

    def test_role_change_before_model_prevents_egress(self):
        original=self.base.engine.checks
        def checks(actor,resources,request_id,phase):
            if phase=='model_dispatch':
                self.policies['partner']['resource_ids']=[];self.save()
            return original(actor,resources,request_id,phase)
        c=self.client('partner')
        with patch.object(self.base.engine,'checks',side_effect=checks):
            self.assertEqual(c('/api/query',{'question':'payment-retry pilot'})[0],503)
        self.assertEqual(self.base.engine.model.calls,[])

    def test_role_change_before_response_stops_delivery_and_scope_does_not_leak(self):
        c=self.client('partner')
        def revoke():
            self.policies['partner']['resource_ids']=[];self.save()
        self.base.engine.before_dispatch=revoke
        self.assertEqual(c('/api/query',{'question':'payment-retry pilot'})[0],503)
        self.base.engine.before_dispatch=None
        from brain.application_access import current_access
        self.assertIsNone(current_access())
        status,body=self.client('first')('/api/query',{'question':'payment-service incident'})
        self.assertEqual(status,200);self.assertTrue(body['evidence'])

    def test_missing_application_policy_cannot_fall_back_to_full_native_access(self):
        c=self.client('partner')
        body=json.loads(self.path.read_text());del body['application_roles']
        self.path.write_text(json.dumps(body))
        self.assertEqual(c('/api/session')[0],403)
        self.assertEqual(self.base.engine.model.calls,[])
