import copy
import unittest
from email.message import Message
from unittest.mock import Mock, MagicMock
from urllib.error import HTTPError

from brain.confluence import ConfluenceReader, Delegation, JsonTransport, SourceUnavailable
from brain.contracts import Actor


PAGE = {'id': '98564', 'spaceId': '123', 'status': 'current',
        'title': 'Synthetic runbook', 'version': {'number': 1, 'createdAt': '2026-10-05T00:00:00Z'},
        'body': {'storage': {'representation': 'storage', 'value': '<p>Runbook &amp; evidence</p>'}}}


class DelegatedReads(unittest.TestCase):
    def setUp(self):
        self.transport = Mock()
        self.reader = ConfluenceReader('https://test.atlassian.net', 'pilot', ['98564'], ['123'],
                                      {'eng_b': Delegation('employee', 'Bearer test-only')}, self.transport)
        self.actor = Actor('eng_b', 'pilot')

    def responses(self, *pages, account='employee'):
        self.transport.get.side_effect = [(200, {'type': 'known', 'accountId': account}), *pages]

    def test_authorized_read_and_backend_link(self):
        page = copy.deepcopy(PAGE); page['_links'] = {'webui': 'https://evil.example/steal'}
        self.responses((200, page), (200, page))
        decision, content = self.reader.read(self.actor, '98564', expected_version=1)
        self.assertEqual(decision.result, 'allow')
        self.assertEqual(content['text'], 'Runbook & evidence')
        self.assertEqual(content['source_url'], 'https://test.atlassian.net/wiki/pages/viewpage.action?pageId=98564')
        self.assertEqual(self.transport.get.call_count, 3)

    def test_admin_credential_substitution_never_fetches_page(self):
        self.responses(account='admin')
        decision, content = self.reader.read(self.actor, '98564')
        self.assertEqual(decision.result, 'unknown'); self.assertIsNone(content)
        self.assertEqual(self.transport.get.call_count, 1)

    def test_unmapped_tenant_or_unapproved_page_never_calls_source(self):
        for actor, page in [(Actor('missing', 'pilot'), '98564'),
                            (Actor('eng_b', 'other'), '98564'), (self.actor, '../private')]:
            self.assertEqual(self.reader.read(actor, page)[0].result, 'unknown')
        self.transport.get.assert_not_called()

    def test_denied_metadata_never_requests_body(self):
        for status in (403, 404):
            self.transport.reset_mock(); self.responses((status, None))
            decision, content = self.reader.read(self.actor, '98564')
            self.assertEqual(decision.result, 'deny'); self.assertIsNone(content)
            self.assertEqual(self.transport.get.call_count, 2)

    def test_revoke_between_metadata_and_body_returns_no_content(self):
        self.responses((200, PAGE), (403, None))
        d, c = self.reader.read(self.actor, '98564')
        self.assertEqual(d.result, 'deny'); self.assertIsNone(c)

    def test_second_read_rechecks_access_no_positive_cache(self):
        self.responses((200, PAGE), (200, PAGE))
        self.assertEqual(self.reader.read(self.actor, '98564')[0].result, 'allow')
        self.responses((404, None))
        self.assertEqual(self.reader.read(self.actor, '98564')[0].result, 'deny')
        self.assertEqual(self.transport.get.call_count, 5)

    def test_version_mismatch_blocks_old_history_without_body(self):
        self.responses((200, PAGE))
        d, c = self.reader.read(self.actor, '98564', expected_version=2)
        self.assertEqual(d.result, 'deny'); self.assertIsNone(c)
        self.assertEqual(self.transport.get.call_count, 2)

    def test_update_during_fetch_and_wrong_space_fail_closed(self):
        changed = copy.deepcopy(PAGE); changed['version']['number'] = 2
        self.responses((200, PAGE), (200, changed))
        self.assertEqual(self.reader.read(self.actor, '98564')[0].result, 'unknown')
        changed['spaceId'] = '999'
        self.transport.reset_mock(); self.responses((200, changed))
        self.assertEqual(self.reader.read(self.actor, '98564')[0].result, 'unknown')
        self.assertEqual(self.transport.get.call_count, 2)

    def test_rate_limit_expired_token_and_network_fail_closed(self):
        for status in (401, 429, 500, 302):
            self.responses((status, None))
            d, c = self.reader.read(self.actor, '98564')
            self.assertEqual(d.result, 'unknown'); self.assertIsNone(c)
        self.transport.get.side_effect = SourceUnavailable()
        self.assertEqual(self.reader.read(self.actor, '98564')[0].result, 'unknown')

    def test_unsupported_macro_and_deleted_page_not_used(self):
        for field, value in [('status', 'trashed'), ('body', {'storage': {
                'representation': 'storage', 'value': '<ac:structured-macro>secret</ac:structured-macro>'}})]:
            page = copy.deepcopy(PAGE); page[field] = value
            self.responses((200, page), (200, page))
            d, c = self.reader.read(self.actor, '98564')
            self.assertEqual(d.result, 'unknown'); self.assertIsNone(c)

    def test_origin_and_credential_validation(self):
        for site in ('http://test.atlassian.net', 'https://test.atlassian.net.evil.com',
                     'https://user@test.atlassian.net', 'https://test.atlassian.net:443',
                     'https://test.atlassian.net/wiki'):
            with self.assertRaises(ValueError):
                ConfluenceReader(site, 'pilot', ['98564'], ['123'], {})
        credential = Delegation('employee', 'Bearer secret-test')
        self.assertNotIn('secret-test', repr(credential))
        with self.assertRaises(ValueError): Delegation('employee', 'Bearer test\nX: y')

    def test_scoped_token_gateway_is_pinned_and_site_links_stay_local(self):
        cloud_id = 'f8382509-310f-447e-be39-f8a59d03da27'
        reader = ConfluenceReader('https://test.atlassian.net', 'pilot', ['98564'], ['123'],
                                 {'eng_b': Delegation('employee', 'Basic test-only')},
                                 self.transport, cloud_id=cloud_id)
        self.responses((200, PAGE), (200, PAGE))
        d, c = reader.read(self.actor, '98564')
        self.assertEqual(d.result, 'allow')
        for call in self.transport.get.call_args_list:
            self.assertTrue(call.args[0].startswith('https://api.atlassian.com/ex/confluence/' + cloud_id + '/wiki/'))
        self.assertTrue(c['source_url'].startswith('https://test.atlassian.net/'))
        with self.assertRaises(ValueError):
            ConfluenceReader('https://test.atlassian.net', 'pilot', ['98564'], ['123'], {},
                             cloud_id='other-site/../../private')

    def test_space_discovery_is_metadata_only_and_cannot_query_content(self):
        reader=ConfluenceReader('https://test.atlassian.net','pilot',['98564'],[],
                                {'eng_b':Delegation('employee','Bearer test-only')},
                                self.transport,discovery_only=True)
        self.responses((200,PAGE))
        decision,space_id=reader.discover_space_id(self.actor,'98564')
        self.assertEqual(decision.result,'allow');self.assertEqual(space_id,'123')
        self.assertEqual(self.transport.get.call_count,2)
        self.assertFalse(any('body-format' in c.args[0] for c in self.transport.get.call_args_list))
        self.transport.reset_mock()
        self.assertEqual(reader.read(self.actor,'98564')[0].result,'unknown')
        self.transport.get.assert_not_called()
        self.assertEqual(self.reader.discover_space_id(self.actor,'98564')[0].result,'unknown')

    def test_space_discovery_rejects_wrong_account_or_unapproved_page(self):
        reader=ConfluenceReader('https://test.atlassian.net','pilot',['98564'],[],
                                {'eng_b':Delegation('employee','Bearer test-only')},
                                self.transport,discovery_only=True)
        self.responses(account='admin')
        self.assertEqual(reader.discover_space_id(self.actor,'98564')[0].result,'unknown')
        self.assertEqual(self.transport.get.call_count,1)
        self.transport.reset_mock()
        self.assertEqual(reader.discover_space_id(self.actor,'999')[0].result,'unknown')
        self.transport.get.assert_not_called()


class TransportLimits(unittest.TestCase):
    def test_error_body_not_read_and_redirect_not_followed(self):
        transport = JsonTransport(); transport.opener = Mock()
        body = Mock()
        transport.opener.open.side_effect = HTTPError('https://test.atlassian.net', 302,
                                                      'Redirect', {}, body)
        self.assertEqual(transport.get('https://test.atlassian.net', 'Bearer test'), (302, None))
        body.read.assert_not_called()
        # Real opener includes our redirect blocker, rather than default follow behavior.
        real = JsonTransport()
        from brain.confluence import NoRedirect
        self.assertTrue(any(isinstance(h, NoRedirect) for h in real.opener.handlers))

    def test_payload_limits_and_non_json(self):
        for mime, payload in [('text/html', b'<p>Login</p>'), ('application/json', b'x' * 11),
                              ('application/json', b'[]'), ('application/json', b'{oops')]:
            transport = JsonTransport(max_bytes=10); transport.opener = MagicMock()
            response = Mock(); response.status = 200
            response.headers = Message(); response.headers['Content-Type'] = mime
            response.read = Mock(return_value=payload)
            transport.opener.open.return_value.__enter__.return_value = response
            with self.assertRaises(SourceUnavailable):
                transport.get('https://test.atlassian.net', 'Bearer test')


if __name__ == '__main__':
    unittest.main()
