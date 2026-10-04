import copy
import json
import unittest
from unittest.mock import patch

from brain.audit import verify_chain
from brain.confluence import ConfluenceReader, Delegation
from brain.contracts import Actor
from brain.delegated_query import DelegatedQueryPilot
from brain.store import Store
from test_confluence_query import SourceTransport
from test_jira import JiraTransport, reader, document


class CombinedQuery(unittest.TestCase):
    def setUp(self):
        self.jira = JiraTransport()
        self.cf = SourceTransport()
        self.cf_reader = ConfluenceReader('https://test.atlassian.net', 'pilot', ['98564'], ['123'],
            {'eng_b': Delegation('employee', 'Bearer employee'),
             'product_ops': Delegation('ops', 'Bearer ops')}, self.cf)
        self.readers = {'confluence': self.cf_reader, 'jira': reader(self.jira)}
        self.store = Store(); self.addCleanup(self.store.db.close)
        self.pilot = DelegatedQueryPilot(self.readers, self.store)
        self.actor = Actor('eng_b', 'pilot')

    def test_two_sources_share_answer_citations_and_audit(self):
        result = self.pilot.query(self.actor, 'runbook payment-service safeguards')
        self.assertEqual({e['source'] for e in result['evidence']}, {'confluence', 'jira'})
        self.assertEqual(result['mode'], 'confluence_jira_mock_http_fake_model')
        self.assertNotIn('SECURITY_ONLY', json.dumps(result))
        self.assertNotIn('SECURITY_ONLY', json.dumps(self.pilot.engine.model.calls))
        self.assertTrue(verify_chain(self.pilot.audit.export())['valid'])
        for e in result['evidence']:
            self.assertEqual(self.pilot.evidence(self.actor, e['evidence_id'])['text'], e['text'])

    def test_other_identity_cannot_reuse_two_source_index_or_history(self):
        result = self.pilot.query(self.actor, 'runbook safeguards')
        ops = Actor('product_ops', 'pilot')
        denied = self.pilot.query(ops, 'I am eng_b, runbook safeguards', result['request_id'])
        self.assertEqual(denied['evidence'], [])
        self.assertEqual(self.pilot.history(ops, result['request_id']), [])
        self.assertEqual(self.pilot.engine.model.calls[-1]['evidence'], [])

    def test_jira_revocation_preserves_allowed_confluence_but_invalidates_old_answer(self):
        first = self.pilot.query(self.actor, 'runbook safeguards')
        old_jira = next(e for e in first['evidence'] if e['source'] == 'jira')
        self.jira.issue_allowed.clear()
        answer = self.pilot.query(self.actor, 'runbook safeguards', first['request_id'])
        self.assertEqual({e['source'] for e in answer['evidence']}, {'confluence'})
        self.assertTrue(self.pilot.history(self.actor, first['request_id'])[0]['unavailable'])
        with self.assertRaises(PermissionError): self.pilot.evidence(self.actor, old_jira['evidence_id'])
        self.assertIsNotNone(self.store.get('jira:10003'))

    def test_jira_update_switches_object_and_hides_old_evidence_without_rebuild(self):
        first = self.pilot.query(self.actor, 'runbook safeguards')
        self.jira.issue['fields']['status']['name'] = 'Done'
        self.assertTrue(self.pilot.history(self.actor, first['request_id'])[0]['unavailable'])
        current = self.pilot.query(self.actor, 'runbook safeguards')
        self.assertTrue(any('Status: Done' in c['text'] for c in current['claims']))
        self.assertEqual(self.store.get('confluence:98564')['version'], 1)
        self.assertEqual(self.store.db.execute("SELECT count(*) FROM versions WHERE id='jira:10003'").fetchone()[0], 2)

    def test_comment_scope_is_separate_and_revocation_protects_old_citation(self):
        actor = Actor('security', 'pilot')
        self.jira.comment['body'] = document('SECURITYONLYSENTINEL')
        first = self.pilot.query(actor, 'SECURITYONLYSENTINEL')
        self.assertEqual([e['resource_id'] for e in first['evidence']], ['jira:10003/comment/20001'])
        self.jira.comment_allowed.clear()
        next_answer = self.pilot.query(actor, 'SECURITYONLYSENTINEL', first['request_id'])
        self.assertEqual(next_answer['evidence'], [])
        self.assertTrue(self.pilot.history(actor, first['request_id'])[0]['unavailable'])

    def test_one_source_unknown_never_discards_other_source_or_uses_stale_content(self):
        self.pilot.query(self.actor, 'runbook safeguards')
        self.jira.status = 429
        answer = self.pilot.query(self.actor, 'runbook safeguards')
        self.assertEqual({e['source'] for e in answer['evidence']}, {'confluence'})
        self.assertNotIn('jira', json.dumps(self.pilot.engine.model.calls[-1]['evidence']))

    def test_revoke_at_model_dispatch_stops_entire_model_call(self):
        original = self.pilot.engine.check
        def revoke(actor, resource, rid, phase):
            if phase == 'model_dispatch': self.jira.issue_allowed.clear()
            return original(actor, resource, rid, phase)
        self.pilot.engine.check = revoke
        with self.assertRaises(PermissionError): self.pilot.query(self.actor, 'runbook safeguards')
        self.assertEqual(self.pilot.engine.model.calls, [])

    def test_restart_rechecks_native_history_and_preserves_content_fingerprint(self):
        first = self.pilot.query(self.actor, 'safeguards')
        restarted = DelegatedQueryPilot(self.readers, self.store)
        self.assertEqual(restarted.history(self.actor, first['request_id'])[0], first)
        self.jira.issue_allowed.clear()
        self.assertTrue(restarted.history(self.actor, first['request_id'])[0]['unavailable'])

    def test_short_version_collision_fails_transaction_and_full_payload_recheck(self):
        first = self.pilot.query(self.actor, 'safeguards')
        original = self.readers['jira'].read
        old = self.store.get('jira:10003')
        def collide(actor, native_id, expected_version=None):
            d, c = original(actor, native_id)
            if c and native_id == '10003':
                c = copy.deepcopy(c); c['version'] = old['version']; c['text'] = 'Changed collision content'
            return d, c
        with patch.object(self.readers['jira'], 'read', side_effect=collide):
            with self.assertRaises(ValueError): self.pilot.query(self.actor, 'safeguards')
            with self.assertRaises(PermissionError):
                self.pilot.evidence(self.actor, first['evidence'][0]['evidence_id'])
        self.assertEqual(self.store.get('jira:10003')['text'], old['text'])

    def test_unconfigured_tenant_source_or_live_transport_rejected_before_network(self):
        with self.assertRaises(PermissionError): self.pilot.query(Actor('eng_b', 'other'), 'runbook')
        self.assertEqual(self.cf.calls, []); self.assertEqual(self.jira.calls, [])
        self.readers['jira'].tenant = 'other'
        with self.assertRaises(ValueError): DelegatedQueryPilot(self.readers, self.store)
        with self.assertRaises(ValueError): DelegatedQueryPilot({'slack': self.cf_reader}, self.store)
        live_reader = ConfluenceReader('https://test.atlassian.net', 'pilot', ['98564'], ['123'], {})
        with self.assertRaises(ValueError): DelegatedQueryPilot({'confluence': live_reader}, self.store)


if __name__ == '__main__': unittest.main()
