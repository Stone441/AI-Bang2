"""Exact-message Slack user delegation; no search, source writes or bot fallback."""
import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urlencode, urlsplit
from urllib.request import Request

from .confluence import Delegation, JsonTransport, SourceUnavailable
from .contracts import Decision, now
from .store import canonical

TS = r'[1-9][0-9]{9}\.[0-9]{6}'


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(TS, value):
        raise SourceUnavailable()
    seconds, micros = value.split('.')
    return datetime.fromtimestamp(int(seconds), timezone.utc).replace(microsecond=int(micros)).isoformat()


class SlackTransport(JsonTransport):
    def get(self, url, authorization):
        if url == 'https://slack.com/api/auth.test':
            return self._send(Request(url, data=b'', method='POST', headers={
                'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': authorization}))
        return super().get(url, authorization)


def plain_blocks(blocks):
    """Accept plain rich-text fallback only; no embedded links/media/hidden cards."""
    parts = []
    def walk(node, depth=0):
        if depth > 16 or not isinstance(node, dict):
            raise SourceUnavailable()
        if node.get('type') == 'text':
            if not isinstance(node.get('text'), str): raise SourceUnavailable()
            parts.append(node['text']); return
        if node.get('type') not in ('rich_text', 'rich_text_section'):
            raise SourceUnavailable()
        children = node.get('elements')
        if not isinstance(children, list) or len(children) > 1000: raise SourceUnavailable()
        for child in children: walk(child, depth + 1)
        if node['type'] == 'rich_text_section': parts.append('\n')
    if not isinstance(blocks, list) or len(blocks) > 100: raise SourceUnavailable()
    for block in blocks: walk(block)
    return ''.join(parts).strip()


class SlackReader:
    def __init__(self, site, tenant, team_id, channels, messages, delegations, transport=None):
        parsed = urlsplit(site)
        if (parsed.scheme != 'https' or not parsed.hostname
                or not re.fullmatch(r'[a-z0-9-]+\.slack\.com', parsed.hostname)
                or parsed.netloc != parsed.hostname or parsed.path not in ('', '/')
                or parsed.query or parsed.fragment):
            raise ValueError('Explicit Slack HTTPS workspace required')
        if not isinstance(tenant, str) or not tenant or not re.fullmatch(r'T[A-Z0-9]+', team_id):
            raise ValueError('Explicit workspace mapping required')
        self.site, self.tenant, self.team_id = site.rstrip('/'), tenant, team_id
        self.channels, self.messages, self.delegations = dict(channels), dict(messages), dict(delegations)
        if (not self.channels or not self.messages
                or any(not isinstance(k, str) or not re.fullmatch(r'[CG][A-Z0-9]+', k)
                       or v not in ('public', 'private') for k, v in self.channels.items())):
            raise ValueError('Explicit channel type mapping required')
        for native_id, parent in self.messages.items():
            if not isinstance(native_id, str) or native_id.count('/') != 1:
                raise ValueError('Explicit message mapping required')
            channel, ts = native_id.split('/')
            if channel not in self.channels or not re.fullmatch(TS, ts):
                raise ValueError('Explicit message mapping required')
            if parent is not None and (not isinstance(parent, str) or not re.fullmatch(TS, parent)
                                      or channel + '/' + parent not in self.messages
                                      or self.messages[channel + '/' + parent] is not None
                                      or tuple(map(int, parent.split('.'))) >= tuple(map(int, ts.split('.')))):
                raise ValueError('Allowlisted earlier thread root required')
        self.native_ids = frozenset(self.messages)
        self.transport = transport or SlackTransport()

    def _get(self, method, credential, **params):
        url = 'https://slack.com/api/' + method
        if params: url += '?' + urlencode(params)
        status, data = self.transport.get(url, credential.authorization)
        if status in (403, 404): return None
        if status != 200 or not isinstance(data, dict): raise SourceUnavailable()
        if data.get('ok') is not True:
            if data.get('ok') is False and data.get('error') in (
                    'channel_not_found', 'not_in_channel', 'access_denied', 'no_permission',
                    'message_not_found', 'thread_not_found'):
                return None
            raise SourceUnavailable()
        return data

    def _credential(self, actor):
        if actor.tenant != self.tenant: raise SourceUnavailable()
        credential = self.delegations.get(actor.user_id)
        if (not isinstance(credential, Delegation) or not credential.authorization.startswith('Bearer ')
                or not re.fullmatch(r'[UW][A-Z0-9]+', credential.account_id)):
            raise SourceUnavailable()
        user = self._get('auth.test', credential)
        if (not user or user.get('user_id') != credential.account_id
                or user.get('team_id') != self.team_id or 'bot_id' in user):
            raise SourceUnavailable()
        return credential

    def read(self, actor, native_id, expected_version=None):
        method = 'slack-delegated-current-read'
        try:
            if native_id not in self.native_ids: raise SourceUnavailable()
            credential = self._credential(actor)
            channel_id, ts = native_id.split('/')
            metadata = self._get('conversations.info', credential, channel=channel_id,
                                 include_num_members='false')
            if metadata is None: return Decision('deny', now(), method, 0), None
            channel = metadata['channel']
            if (channel['id'] != channel_id or channel['context_team_id'] != self.team_id
                    or channel.get('is_im') is not False or channel.get('is_mpim') is not False
                    or channel.get('is_shared') is not False
                    or channel.get('is_ext_shared') is not False
                    or channel.get('is_pending_ext_shared') is not False
                    or channel.get('is_private') is not (self.channels[channel_id] == 'private')):
                raise SourceUnavailable()
            if self.channels[channel_id] == 'private':
                if channel.get('is_member') is False: return Decision('deny', now(), method, 0), None
                if channel.get('is_member') is not True: raise SourceUnavailable()
            parent = self.messages[native_id]
            params = {'channel': channel_id, 'oldest': ts, 'latest': ts, 'inclusive': 'true', 'limit': '1'}
            if parent is not None: params['ts'] = parent
            data = self._get('conversations.replies' if parent else 'conversations.history', credential, **params)
            if data is None: return Decision('deny', now(), method, 0), None
            messages = data['messages']
            if messages == []: return Decision('deny', now(), 'slack-message-unavailable', 0), None
            if not isinstance(messages, list) or len(messages) != 1: raise SourceUnavailable()
            message = messages[0]
            if (message.get('ts') != ts or message.get('type') != 'message'
                    or message.get('subtype') is not None or message.get('files')
                    or message.get('attachments') or message.get('bot_id')
                    or message.get('team', self.team_id) != self.team_id
                    or message.get('thread_ts') not in ((parent,) if parent else (None, ts))):
                raise SourceUnavailable()
            text, name = message['text'], channel['name']
            if (not isinstance(text, str) or not text.strip() or len(text) > 40000
                    or not isinstance(name, str) or not re.fullmatch(r'[a-z0-9_-]+', name)):
                raise SourceUnavailable()
            if message.get('blocks') and plain_blocks(message['blocks']) != text.strip():
                raise SourceUnavailable()
            updated_ts = message['edited']['ts'] if 'edited' in message else ts
            updated = timestamp(updated_ts)
            title = '#' + name + ' · ' + ts
            locator = {'channel_id': channel_id, 'message_ts': ts, 'thread_ts': parent}
            digest = hashlib.sha256(canonical({'native_id': native_id, 'text': text,
                'title': title, 'updated': updated, 'locator': locator}).encode()).hexdigest()
            version = int(digest[:15], 16)
            if expected_version is not None and (type(expected_version) is not int or expected_version != version):
                return Decision('deny', now(), 'slack-content-changed', 0), None
            locator['content_sha256'] = digest
            return Decision('allow', now(), method, 0), {'source': 'slack', 'native_id': native_id,
                'version': version, 'title': title, 'text': text, 'locator': locator,
                'source_updated_at': updated, 'source_url': self.site + '/archives/' + channel_id + '/p' + ts.replace('.', '')}
        except (SourceUnavailable, KeyError, ValueError, TypeError, AttributeError, RecursionError, OverflowError, OSError):
            return Decision('unknown', now(), method, 0), None
