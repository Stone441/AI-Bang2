import copy
import unittest
from unittest.mock import Mock

from brain.confluence import Delegation, SourceUnavailable
from brain.contracts import Actor
from brain.jira import JiraReader, adf_text


def document(text):
    return {'type': 'doc', 'version': 1, 'content': [
        {'type': 'paragraph', 'content': [{'type': 'text', 'text': text}]}]}


ISSUE = {'id': '10003', 'key': 'KAN-3', 'fields': {
    'project': {'id': '10000'}, 'summary': 'Payment-service safeguards',
    'description': document('Synthetic task, GA not approved.'),
    'status': {'name': 'In Progress'}, 'assignee': {'displayName': 'Maya'},
    'updated': '2026-10-05T00:00:00.000+0000'}}
COMMENT = {'id': '20001', 'body': document('SECURITY_ONLY_SYNTHETIC'),
           'updated': '2026-10-05T00:00:00.000+0000',
           'visibility': {'type': 'group', 'value': 'security'}}
USER = {'accountId': 'employee', 'active': True, 'accountType': 'atlassian'}


class JiraTransport:
    def __init__(self):
        self.issue = copy.deepcopy(ISSUE)
        self.comment = copy.deepcopy(COMMENT)
        self.issue_allowed = {'employee', 'security'}
        self.comment_allowed = {'security'}
        self.status = 200
        self.calls = []

    def get(self, url, authorization):
        self.calls.append(url)
        account = authorization.removeprefix('Bearer ')
        if url.endswith('/myself'):
            return 200, dict(USER, accountId=account)
        if self.status != 200:
            return self.status, None
        if account not in self.issue_allowed:
            return 404, None
        if '/comment/' in url:
            return (200, copy.deepcopy(self.comment)) if account in self.comment_allowed else (403, None)
        return 200, copy.deepcopy(self.issue)


def reader(transport):
    return JiraReader('https://test.atlassian.net', 'pilot', {'10003': 'KAN-3'}, ['10000'],
        {uid: Delegation(account, 'Bearer ' + account) for uid, account in
         [('eng_b', 'employee'), ('security', 'security'), ('product_ops', 'ops')]},
        transport, comment_ids={'20001': '10003'})


class JiraBoundary(unittest.TestCase):
    def setUp(self):
        self.transport = JiraTransport()
        self.reader = reader(self.transport)
        self.actor = Actor('eng_b', 'pilot')

    def test_current_fields_and_backend_link_without_embedded_subresources(self):
        self.transport.issue['fields']['comment'] = {'comments': [COMMENT]}
        self.transport.issue['self'] = 'https://evil.invalid/'
        d, c = self.reader.read(self.actor, '10003')
        self.assertEqual(d.result, 'allow')
        self.assertIn('Status: In Progress\nAssignee: Maya', c['text'])
        self.assertNotIn('SECURITY_ONLY', str(c))
        self.assertEqual(c['source_url'], 'https://test.atlassian.net/browse/KAN-3')
        self.assertEqual(len(c['locator']['content_sha256']), 64)
        self.assertEqual(d.policy_version, 0)
        self.assertFalse(any('/comment/' in url for url in self.transport.calls))

    def test_parent_visibility_never_grants_comment_access(self):
        self.assertEqual(self.reader.read(self.actor, '10003')[0].result, 'allow')
        d, c = self.reader.read(self.actor, '10003/comment/20001')
        self.assertEqual(d.result, 'deny'); self.assertIsNone(c)
        d, c = self.reader.read(Actor('security', 'pilot'), '10003/comment/20001')
        self.assertEqual(d.result, 'allow')
        self.assertEqual(c['text'], 'SECURITY_ONLY_SYNTHETIC')
        self.assertEqual(c['locator']['comment_id'], '20001')
        self.assertIn('focusedCommentId=20001', c['source_url'])

    def test_revoked_parent_blocks_comment_endpoint(self):
        self.transport.issue_allowed.clear()
        d, c = self.reader.read(Actor('security', 'pilot'), '10003/comment/20001')
        self.assertEqual(d.result, 'deny'); self.assertIsNone(c)
        self.assertFalse(any('/comment/' in url for url in self.transport.calls))

    def test_credential_substitution_or_disabled_identity_never_fetches_issue(self):
        transport = Mock()
        r = reader(transport)
        for user in [dict(USER, accountId='admin'), dict(USER, active=False),
                     dict(USER, accountType='app')]:
            transport.reset_mock(); transport.get.return_value = (200, user)
            self.assertEqual(r.read(self.actor, '10003')[0].result, 'unknown')
            self.assertEqual(transport.get.call_count, 1)

    def test_missing_mapping_wrong_tenant_unapproved_id_never_calls(self):
        for actor, native in [(Actor('missing', 'pilot'), '10003'),
                              (Actor('eng_b', 'other'), '10003'),
                              (self.actor, '10003/comment/20002'), (self.actor, '../private')]:
            self.assertEqual(self.reader.read(actor, native)[0].result, 'unknown')
        self.assertEqual(self.transport.calls, [])

    def test_moved_reused_or_wrong_project_issue_fails_closed(self):
        for change in [{'id': '99999'}, {'key': 'KAN-4'},
                       {'fields': dict(ISSUE['fields'], project={'id': '99999'})}]:
            self.transport.issue = dict(copy.deepcopy(ISSUE), **change)
            d, c = self.reader.read(self.actor, '10003')
            self.assertEqual(d.result, 'unknown'); self.assertIsNone(c)

    def test_content_fingerprint_changes_even_if_timestamp_does_not(self):
        baseline = self.reader.read(self.actor, '10003')[1]
        self.transport.issue['fields']['status']['name'] = 'Done'
        d, c = self.reader.read(self.actor, '10003', baseline['version'])
        self.assertEqual(d.result, 'deny'); self.assertIsNone(c)
        new = self.reader.read(self.actor, '10003')[1]
        self.assertNotEqual(new['locator']['content_sha256'], baseline['locator']['content_sha256'])

    def test_comment_edit_changes_fingerprint_and_old_version_is_unavailable(self):
        actor = Actor('security', 'pilot')
        baseline = self.reader.read(actor, '10003/comment/20001')[1]
        self.transport.comment['body'] = document('Edited synthetic comment')
        self.assertEqual(self.reader.read(actor, '10003/comment/20001', baseline['version'])[0].result, 'deny')

    def test_rate_limit_token_expired_transport_error_and_redirect_are_unknown(self):
        for status in [401, 429, 500, 302]:
            self.transport.status = status
            d, c = self.reader.read(self.actor, '10003')
            self.assertEqual(d.result, 'unknown'); self.assertIsNone(c)
        r = reader(Mock()); r.transport.get.side_effect = SourceUnavailable()
        self.assertEqual(r.read(self.actor, '10003')[0].result, 'unknown')

    def test_second_read_rechecks_native_access(self):
        self.assertEqual(self.reader.read(self.actor, '10003')[0].result, 'allow')
        self.transport.issue_allowed.clear()
        self.assertEqual(self.reader.read(self.actor, '10003')[0].result, 'deny')

    def test_missing_required_field_and_embedded_media_do_not_return_partial_answer(self):
        del self.transport.issue['fields']['assignee']
        self.assertEqual(self.reader.read(self.actor, '10003')[0].result, 'unknown')
        self.transport.issue = copy.deepcopy(ISSUE)
        self.transport.issue['fields']['description']['content'] = [{'type': 'media', 'attrs': {'id': 'secret'}}]
        self.assertEqual(self.reader.read(self.actor, '10003')[0].result, 'unknown')

    def test_null_description_unassigned_and_empty_document(self):
        self.transport.issue['fields'].update(description=None, assignee=None)
        c = self.reader.read(self.actor, '10003')[1]
        self.assertIn('Assignee: Unassigned', c['text'])
        self.assertEqual(adf_text({'type': 'doc', 'version': 1, 'content': []}), '')

    def test_adf_depth_and_node_bounds(self):
        deep = {'type': 'paragraph', 'content': []}
        for _ in range(34):
            deep = {'type': 'blockquote', 'content': [deep]}
        for content in [[deep], [{'type': 'hardBreak'}] * 10001]:
            with self.assertRaises(SourceUnavailable):
                adf_text({'type': 'doc', 'version': 1, 'content': content})

    def test_origin_gateway_and_whitelist_validation(self):
        for site in ['http://test.atlassian.net', 'https://test.atlassian.net:443',
                     'https://test.atlassian.net.evil.invalid', 'https://test.atlassian.net/path']:
            with self.assertRaises(ValueError):
                JiraReader(site, 'pilot', {'10003': 'KAN-3'}, ['10000'], {})
        for issues, comments in [({'../secret': 'KAN-3'}, {}),
                                ({'10003': '../bad'}, {}), ({'10003': 'KAN-3'}, {'20001': '99999'})]:
            with self.assertRaises(ValueError):
                JiraReader('https://test.atlassian.net', 'pilot', issues, ['10000'], {}, comment_ids=comments)
        cloud = 'f8382509-310f-447e-be39-f8a59d03da27'
        r = JiraReader('https://test.atlassian.net', 'pilot', {'10003': 'KAN-3'}, ['10000'],
                       self.reader.delegations, self.transport, cloud_id=cloud)
        self.assertEqual(r.read(self.actor, '10003')[0].result, 'allow')
        self.assertTrue(all(url.startswith('https://api.atlassian.com/ex/jira/' + cloud)
                            for url in self.transport.calls))
        with self.assertRaises(ValueError):
            JiraReader('https://test.atlassian.net', 'pilot', {'10003': 'KAN-3'}, ['10000'], {}, cloud_id='../bad')


if __name__ == '__main__': unittest.main()
