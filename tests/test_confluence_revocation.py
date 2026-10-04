import contextlib
import io
import unittest
from unittest.mock import patch

from brain.confluence import ConfluenceReader,Delegation
from brain.confluence_query import ConfluenceQueryPilot
from brain.contracts import Actor
from brain.store import Store
from scripts.confluence_revocation import exercise,main
from test_confluence_query import SourceTransport


class RevocationRunner(unittest.TestCase):
    def setUp(self):
        self.transport=SourceTransport()
        reader=ConfluenceReader('https://test.atlassian.net','pilot',['98564'],['123'],
                                {'eng_b':Delegation('employee','Bearer employee')},self.transport)
        self.store=Store();self.addCleanup(self.store.db.close)
        self.pilot=ConfluenceQueryPilot(reader,self.store)
        self.actor=Actor('eng_b','pilot')

    def test_revoke_checks_all_paths_without_rebuilding(self):
        report=exercise(self.pilot,self.actor,'98564',lambda *args:self.transport.allowed.clear())
        self.assertEqual(report['status'],'passed_operator_subset')
        self.assertEqual(report['mode'],'confluence_mock_http_fake_model')
        self.assertTrue(all(report['checks'].values()))
        self.assertIsNotNone(self.store.get('confluence:98564'))

    def test_no_revoke_does_not_report_pass(self):
        report=exercise(self.pilot,self.actor,'98564',lambda *args:None)
        self.assertEqual(report['status'],'failed')
        self.assertFalse(report['checks']['source_returns_deny_not_unknown'])
        self.assertFalse(report['checks']['old_citation_unavailable'])

    def test_expired_token_not_mistaken_for_source_revocation(self):
        def expire(*args):self.transport.status=401
        report=exercise(self.pilot,self.actor,'98564',expire)
        self.assertEqual(report['status'],'failed')
        self.assertFalse(report['checks']['source_returns_deny_not_unknown'])
        self.assertTrue(report['checks']['model_input_excludes_revoked_resource'])

    def test_baseline_unavailable_never_enters_revoke_stage(self):
        self.transport.allowed.clear()
        with patch('builtins.input') as wait:
            report=exercise(self.pilot,self.actor,'98564',wait)
        self.assertEqual(report['reason'],'baseline_evidence_unavailable');wait.assert_not_called()

    def test_cli_requires_live_flag_before_credentials(self):
        with contextlib.redirect_stdout(io.StringIO()),patch('scripts.confluence_revocation.load_reader') as load:
            self.assertEqual(main(['--config','missing']),2)
            load.assert_not_called()


if __name__=='__main__':unittest.main()
