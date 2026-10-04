"""Read-only, allowlisted Confluence pilot. No credential or response logging.

This boundary is not yet the demo Engine's SourceAdapter. Each read verifies the
credential identity and current page access; it never falls back to an admin.
"""
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

from .contracts import Actor, Decision, now


class SourceUnavailable(Exception):
    """Intentionally carries no upstream response or credential details."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class JsonTransport:
    def __init__(self, timeout=10, max_bytes=1_000_000):
        if not 0 < timeout <= 30 or not 0 < max_bytes <= 2_000_000:
            raise ValueError('Invalid transport limits')
        self.timeout, self.max_bytes = timeout, max_bytes
        self.opener = build_opener(NoRedirect())

    def get(self, url, authorization):
        request = Request(url, headers={'Accept': 'application/json',
                                       'Authorization': authorization}, method='GET')
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                if response.status != 200:
                    return response.status, None
                if response.headers.get_content_type() != 'application/json':
                    raise SourceUnavailable()
                payload = response.read(self.max_bytes + 1)
                if len(payload) > self.max_bytes:
                    raise SourceUnavailable()
                data = json.loads(payload)
                if not isinstance(data, dict):
                    raise SourceUnavailable()
                return 200, data
        except HTTPError as error:
            # Do not read an error body: it may contain restricted titles or text.
            status = error.code
            error.close()
            return status, None
        except (URLError, OSError, ValueError):
            raise SourceUnavailable() from None


@dataclass(frozen=True)
class Delegation:
    account_id: str
    authorization: str = field(repr=False)

    def __post_init__(self):
        if (not self.account_id or not self.authorization
                or '\r' in self.authorization or '\n' in self.authorization
                or not self.authorization.startswith(('Basic ', 'Bearer '))):
            raise ValueError('Invalid delegation')


class StorageText(HTMLParser):
    """Pilot supports plain synthetic pages, not macros or embedded resources."""
    SAFE = {'p', 'br', 'strong', 'em', 'b', 'i', 'u', 's', 'ul', 'ol', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div', 'code', 'pre',
            'table', 'tbody', 'thead', 'tr', 'td', 'th', 'blockquote', 'hr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.SAFE:
            raise SourceUnavailable()
        if tag in {'p', 'br', 'li', 'tr', 'div', 'hr'} or tag.startswith('h'):
            self.parts.append('\n')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag not in self.SAFE:
            raise SourceUnavailable()
        self.parts.append('\n' if tag in {'p', 'li', 'tr', 'div', 'pre'} else '')

    def handle_data(self, data):
        self.parts.append(data)


class ConfluenceReader:
    def __init__(self, site, tenant, page_ids, space_ids, delegations, transport=None):
        parsed = urlsplit(site)
        if (parsed.scheme != 'https' or not parsed.hostname
                or not re.fullmatch(r'[a-z0-9-]+\.atlassian\.net', parsed.hostname)
                or parsed.netloc != parsed.hostname or parsed.path not in ('', '/')
                or parsed.query or parsed.fragment):
            raise ValueError('An explicit HTTPS Atlassian site is required')
        self.site, self.tenant = site.rstrip('/'), tenant
        self.page_ids, self.space_ids = frozenset(page_ids), frozenset(space_ids)
        if (not tenant or not self.page_ids or not self.space_ids
                or any(not isinstance(i, str) or not i.isdecimal()
                       for i in self.page_ids | self.space_ids)):
            raise ValueError('Explicit page and space ID allowlists required')
        self.delegations = dict(delegations)
        self.transport = transport or JsonTransport()

    def _credential(self, actor, page_id):
        if actor.tenant != self.tenant or page_id not in self.page_ids:
            raise SourceUnavailable()
        credential = self.delegations.get(actor.user_id)
        if not isinstance(credential, Delegation):
            raise SourceUnavailable()
        status, user = self.transport.get(self.site + '/wiki/rest/api/user/current',
                                          credential.authorization)
        if (status != 200 or not isinstance(user, dict)
                or user.get('accountId') != credential.account_id
                or user.get('type') != 'known'):
            raise SourceUnavailable()
        return credential

    def _metadata(self, page_id, data):
        if (not isinstance(data, dict) or data.get('id') != page_id
                or data.get('spaceId') not in self.space_ids
                or data.get('status') != 'current'):
            raise SourceUnavailable()
        version = data.get('version', {}).get('number')
        if type(version) is not int or version < 1:
            raise SourceUnavailable()
        return version

    def read(self, actor: Actor, page_id, expected_version=None):
        """Return decision and authorized content together; no positive ACL cache."""
        method = 'confluence-delegated-current-read'
        try:
            credential = self._credential(actor, page_id)
            endpoint = self.site + '/wiki/api/v2/pages/' + page_id
            status, metadata = self.transport.get(endpoint, credential.authorization)
            if status in (403, 404):
                return Decision('deny', now(), method, 0), None
            if status != 200:
                raise SourceUnavailable()
            version = self._metadata(page_id, metadata)
            if expected_version is not None and (type(expected_version) is not int
                                                 or expected_version != version):
                return Decision('deny', now(), 'confluence-version-changed', 0), None
            status, data = self.transport.get(endpoint + '?body-format=storage',
                                            credential.authorization)
            if status in (403, 404):
                return Decision('deny', now(), method, 0), None
            if status != 200 or self._metadata(page_id, data) != version:
                raise SourceUnavailable()
            body = data.get('body', {}).get('storage', {})
            if body.get('representation') != 'storage' or not isinstance(body.get('value'), str):
                raise SourceUnavailable()
            parser = StorageText()
            parser.feed(body['value']); parser.close()
            text = '\n'.join(line.strip() for line in ''.join(parser.parts).splitlines() if line.strip())
            if not text or not isinstance(data.get('title'), str):
                raise SourceUnavailable()
            # Canonical backend URL, never an untrusted upstream link.
            result = {'native_id': page_id, 'source': 'confluence', 'version': version,
                      'title': data['title'], 'text': text,
                      'locator': {'page_id': page_id, 'version': version},
                      'source_updated_at': data['version'].get('createdAt'),
                      'source_url': self.site + '/wiki/pages/viewpage.action?pageId=' + page_id}
            return Decision('allow', now(), method, 0), result
        except (SourceUnavailable, KeyError, TypeError, AttributeError, ValueError):
            return Decision('unknown', now(), method, 0), None
