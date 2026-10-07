import unittest
from brain.audit import Audit
from brain.contracts import Actor
from brain.store import Store
from brain.audit_query import parse_inquiry


class ResourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.audit=Audit(Store())
        for actor,rid,resource,scope in [('eng_a','a','C-01','payment-service'),
                                         ('eng_b','b','C-01','payment-service'),
                                         ('product_ops','c','C-02','payment-service'),
                                         ('security','d','C-01','payment-service'),
                                         ('eng_a','e','C-01','other')]:
            self.audit.append('request_started',actor,rid,{'query':'synthetic question'})
            self.audit.append('authorization_decided',actor,rid,{'resource_id':resource,'resource_scope':scope,'result':'deny' if actor=='eng_b' else 'allow'})
        self.audit.append('authorization_decided','eng_a','a',{'resource_id':'C-99','resource_scope':'payment-service','result':'allow'})

    def test_resource_scope_identity_and_exact_event_filter(self):
        response=self.audit.inquire(Actor('auditor'),{'resource_id':'C-01'})
        self.assertEqual({e['request_id'] for e in response['events']},{'a','b'})
        self.assertEqual({e['actor'] for e in response['events']},{'eng_a','eng_b'})
        self.assertEqual([e['payload']['result'] for e in response['events'] if e['event_type']=='authorization_decided'],['allow','deny'])
        self.assertNotIn('C-99',str(response))

    def test_snapshot_pagination_and_auditor_gate(self):
        first=self.audit.inquire(Actor('auditor'),{'resource_id':'C-01','page_size':1})
        self.audit.append('authorization_decided','eng_a','late',{'resource_id':'C-01','resource_scope':'payment-service','result':'allow'})
        rest=self.audit.inquire(Actor('auditor'),{'resource_id':'C-01','as_of':first['as_of'],'after':first['next_after']})
        self.assertNotIn('late',{e['request_id'] for e in rest['events']})
        with self.assertRaises(PermissionError):self.audit.inquire(Actor('eng_a'),{'resource_id':'C-01'})
        with self.assertRaises(ValueError):self.audit.inquire(Actor('auditor'),{'resource_id':"C-01' OR 1=1"})
        with self.assertRaises(PermissionError):self.audit.inquire(Actor('auditor'),{'actor':None})

    def test_resource_inquiry_template_retains_identifier_and_bounds(self):
        self.assertEqual(parse_inquiry('Who accessed confluence:164283 in the last 7 days?')['resource_id'],'confluence:164283')
        with self.assertRaises(ValueError):parse_inquiry('Who accessed C-01 in the last 0 days?')

    def test_reused_preview_identifier_does_not_cross_actor_or_scope(self):
        self.audit.append('authorization_decided','eng_a','evidence',{'resource_id':'C-01','resource_scope':'payment-service','result':'allow'})
        self.audit.append('authorization_decided','eng_a','evidence',{'resource_id':'C-01','resource_scope':'other','result':'allow'})
        self.audit.append('request_started','eng_b','evidence',{'query':'unrelated'})
        response=self.audit.inquire(Actor('auditor'),{'resource_id':'C-01'})
        self.assertFalse(any(e['actor']=='eng_b' and e['request_id']=='evidence' for e in response['events']))
        self.assertFalse(any(e['payload'].get('resource_scope')=='other' for e in response['events']))


if __name__=='__main__':unittest.main()
