"""Allowlisted, delegated Jira reads; issue and comment are separate resources.

Only selected fields and plain ADF are supported. No attachment, search or write.
Native user identity is checked before every read; upstream errors carry no body.
"""
import hashlib
import re
import uuid
from datetime import datetime
from urllib.parse import urlsplit

from .confluence import Delegation, JsonTransport, SourceUnavailable
from .contracts import Decision, now
from .store import canonical


def adf_text(document):
    if document is None:
        return ''
    if (not isinstance(document, dict) or document.get('type') != 'doc'
            or type(document.get('version')) is not int or document['version'] != 1):
        raise SourceUnavailable()
    blocks = {'doc', 'paragraph', 'heading', 'bulletList', 'orderedList', 'listItem',
              'blockquote', 'codeBlock', 'table', 'tableRow', 'tableCell', 'tableHeader'}
    count = 0
    def walk(node, depth=0):
        nonlocal count
        count += 1
        if depth > 32 or count > 10000 or not isinstance(node, dict):
            raise SourceUnavailable()
        kind = node.get('type')
        if kind == 'text':
            if not isinstance(node.get('text'), str):
                raise SourceUnavailable()
            return node['text']
        if kind == 'hardBreak':
            return '\n'
        if kind not in blocks or not isinstance(node.get('content'), list):
            # In particular, do not follow embedded media/cards/mentions.
            raise SourceUnavailable()
        text = ''.join(walk(child, depth + 1) for child in node['content'])
        return text + ('\n' if kind in blocks - {'doc'} else '')
    text = walk(document).strip()
    if len(text) > 40000:
        raise SourceUnavailable()
    return text


class JiraReader:
    def __init__(self, site, tenant, issues, project_ids, delegations,
                 transport=None, *, comment_ids=None, cloud_id=None,
                 discovery_only=False, discovery_keys=None):
        parsed = urlsplit(site)
        if (parsed.scheme != 'https' or not parsed.hostname
                or not re.fullmatch(r'[a-z0-9-]+\.atlassian\.net', parsed.hostname)
                or parsed.netloc != parsed.hostname or parsed.path not in ('', '/')
                or parsed.query or parsed.fragment):
            raise ValueError('Explicit HTTPS Atlassian site required')
        self.site, self.tenant = site.rstrip('/'), tenant
        self.api_base = self.site
        if cloud_id is not None:
            try:
                if str(uuid.UUID(cloud_id)) != cloud_id:
                    raise ValueError()
            except (ValueError, TypeError, AttributeError):
                raise ValueError('Canonical cloud UUID required') from None
            self.api_base = 'https://api.atlassian.com/ex/jira/' + cloud_id
        self.issues = dict(issues)
        self.project_ids = frozenset(project_ids)
        self.comment_ids = dict(comment_ids or {})
        self.discovery_only = discovery_only
        self.discovery_keys = dict(discovery_keys or {})
        if (type(discovery_only) is not bool
                or (discovery_only and (self.issues or self.project_ids or self.comment_ids
                                       or not self.discovery_keys))
                or (not discovery_only and (not self.issues or not self.project_ids))
                or any(not isinstance(k, str) or not re.fullmatch(r'[A-Z][A-Z0-9_]*-[1-9][0-9]*', k)
                       or not isinstance(v, str) or not re.fullmatch(r'[A-Z][A-Z0-9_]*', v)
                       for k, v in self.discovery_keys.items())):
            raise ValueError('Explicit isolated discovery mapping required')
        if (not isinstance(tenant, str) or not tenant
                or any(not isinstance(i, str) or not re.fullmatch(r'[0-9]+', i)
                       for i in set(self.issues) | self.project_ids | set(self.comment_ids))
                or any(not isinstance(key, str) or not re.fullmatch(r'[A-Z][A-Z0-9_]*-[1-9][0-9]*', key)
                       for key in self.issues.values())
                or any(parent not in self.issues for parent in self.comment_ids.values())):
            raise ValueError('Explicit issue/project/comment mapping required')
        self.native_ids = frozenset(self.issues) | frozenset(
            parent + '/comment/' + cid for cid, parent in self.comment_ids.items())
        self.delegations = dict(delegations)
        self.transport = transport or JsonTransport()

    def _get(self, path, credential):
        status, data = self.transport.get(self.api_base + path, credential.authorization)
        if status in (403, 404):
            return None
        if status != 200 or not isinstance(data, dict):
            raise SourceUnavailable()
        return data

    def _credential(self, actor):
        if actor.tenant != self.tenant:
            raise SourceUnavailable()
        credential = self.delegations.get(actor.user_id)
        if not isinstance(credential, Delegation):
            raise SourceUnavailable()
        user = self._get('/rest/api/3/myself', credential)
        if (not user or user.get('accountId') != credential.account_id
                or user.get('active') is not True or user.get('accountType') != 'atlassian'):
            raise SourceUnavailable()
        return credential

    def discover_ids(self, actor, issue_key):
        method = 'jira-allowlisted-issue-project-discovery'
        try:
            if not self.discovery_only or issue_key not in self.discovery_keys:
                raise SourceUnavailable()
            credential = self._credential(actor)
            data = self._get('/rest/api/3/issue/' + issue_key + '?fields=project', credential)
            if data is None:
                return Decision('deny', now(), method, 0), None
            project = data['fields']['project']
            issue_id, project_id = data['id'], project['id']
            if (data['key'] != issue_key or project['key'] != self.discovery_keys[issue_key]
                    or any(not isinstance(i, str) or not re.fullmatch(r'[0-9]+', i)
                           for i in (issue_id, project_id))):
                raise SourceUnavailable()
            return Decision('allow', now(), method, 0), {
                'issue_id': issue_id, 'issue_key': issue_key,
                'project_id': project_id, 'project_key': project['key']}
        except (SourceUnavailable, KeyError, TypeError, ValueError, AttributeError):
            return Decision('unknown', now(), method, 0), None

    def _issue(self, issue_id, credential):
        data = self._get('/rest/api/3/issue/' + issue_id
                         + '?fields=summary,description,status,assignee,project,updated', credential)
        if data is None:
            return None
        fields = data.get('fields')
        if (data.get('id') != issue_id or data.get('key') != self.issues[issue_id]
                or not isinstance(fields, dict)
                or fields.get('project', {}).get('id') not in self.project_ids):
            raise SourceUnavailable()
        return fields

    @staticmethod
    def _updated(value):
        if not isinstance(value, str):
            raise SourceUnavailable()
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise SourceUnavailable()
        return value

    def read(self, actor, native_id, expected_version=None):
        method = 'jira-delegated-current-read'
        try:
            if self.discovery_only or actor.tenant != self.tenant or native_id not in self.native_ids:
                raise SourceUnavailable()
            credential = self._credential(actor)
            issue_id, *comment = native_id.split('/comment/')
            fields = self._issue(issue_id, credential)
            if fields is None:
                return Decision('deny', now(), method, 0), None
            key = self.issues[issue_id]
            locator = {'issue_id': issue_id, 'issue_key': key}
            url = self.site + '/browse/' + key
            if comment:
                cid = comment[0]
                data = self._get('/rest/api/3/issue/' + issue_id + '/comment/' + cid, credential)
                if data is None:
                    return Decision('deny', now(), method, 0), None
                if data.get('id') != cid:
                    raise SourceUnavailable()
                text = adf_text(data['body'])
                updated = self._updated(data['updated'])
                title = key + ' comment ' + cid
                locator['comment_id'] = cid
                url += '?focusedCommentId=' + cid
            else:
                title = fields['summary']
                status = fields['status']['name']
                assignee = fields['assignee']
                owner = 'Unassigned' if assignee is None else assignee['displayName']
                if not all(isinstance(s, str) and s.strip() for s in (title, status, owner)):
                    raise SourceUnavailable()
                description = adf_text(fields['description'])
                text = key + '\nStatus: ' + status + '\nAssignee: ' + owner
                if description:
                    text += '\n' + description
                updated = self._updated(fields['updated'])
            if not text:
                raise SourceUnavailable()
            digest = hashlib.sha256(canonical({'native_id': native_id, 'title': title,
                'text': text, 'updated': updated, 'locator': locator}).encode()).hexdigest()
            version = int(digest[:15], 16)
            if expected_version is not None and (type(expected_version) is not int
                                                 or version != expected_version):
                return Decision('deny', now(), 'jira-content-changed', 0), None
            locator['content_sha256'] = digest
            content = {'source': 'jira', 'native_id': native_id, 'version': version,
                       'title': title, 'text': text, 'locator': locator,
                       'source_updated_at': updated, 'source_url': url}
            return Decision('allow', now(), method, 0), content
        except (SourceUnavailable, KeyError, TypeError, ValueError, AttributeError, RecursionError):
            return Decision('unknown', now(), method, 0), None
