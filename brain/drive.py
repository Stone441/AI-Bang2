"""Allowlisted personal-Drive UTF-8 files, read with the current user's token."""
import hashlib
import re
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request

from .confluence import Delegation, JsonTransport, SourceUnavailable
from .contracts import Decision, now

BASE = 'https://www.googleapis.com/drive/v3'
ID = r'[A-Za-z0-9_-]{1,200}'
FIELDS = 'id,name,mimeType,version,modifiedTime,trashed,parents,driveId,spaces,size,md5Checksum,headRevisionId,capabilities(canDownload)'


class DriveTransport(JsonTransport):
    def media(self, file_id, authorization):
        if not isinstance(file_id, str) or not re.fullmatch(ID, file_id):
            raise SourceUnavailable()
        request = Request(BASE + '/files/' + file_id + '?alt=media',
                          headers={'Authorization': authorization, 'Accept': 'text/plain'})
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                if response.status != 200: return response.status, None
                if response.headers.get_content_type() != 'text/plain': raise SourceUnavailable()
                charset = response.headers.get_content_charset()
                if charset and charset.lower() not in ('utf-8', 'us-ascii'): raise SourceUnavailable()
                payload = response.read(self.max_bytes + 1)
                if len(payload) > self.max_bytes: raise SourceUnavailable()
                return 200, payload
        except HTTPError as error:
            status = error.code; error.close()
            return status, None
        except (URLError, OSError, ValueError):
            raise SourceUnavailable() from None


class DriveReader:
    def __init__(self, tenant, files, delegations, transport=None):
        if not isinstance(tenant, str) or not tenant or not isinstance(files, dict) or not files:
            raise ValueError('Explicit synthetic file mapping required')
        if any(not isinstance(i, str) or not re.fullmatch(ID, i)
               or not isinstance(parent, str) or not re.fullmatch(ID, parent)
               for i, parent in files.items()):
            raise ValueError('Exact file and parent IDs required')
        self.tenant, self.files, self.delegations = tenant, dict(files), dict(delegations)
        self.native_ids = frozenset(files)
        self.transport = transport or DriveTransport()

    def _credential(self, actor):
        credential = self.delegations.get(actor.user_id)
        if (actor.tenant != self.tenant or not isinstance(credential, Delegation)
                or not credential.authorization.startswith('Bearer ')):
            raise SourceUnavailable()
        status, result = self.transport.get(BASE + '/about?' + urlencode({'fields':'user(permissionId,me)'}),
                                            credential.authorization)
        if (status != 200 or not isinstance(result, dict)
                or result.get('user', {}).get('me') is not True
                or result['user'].get('permissionId') != credential.account_id):
            raise SourceUnavailable()
        return credential

    def _metadata(self, native_id, credential):
        status, data = self.transport.get(BASE + '/files/' + native_id + '?' + urlencode({'fields':FIELDS}),
                                          credential.authorization)
        if status in (403, 404): return None
        if status != 200 or not isinstance(data, dict): raise SourceUnavailable()
        if data.get('trashed') is True: return None
        if data.get('capabilities', {}).get('canDownload') is False: return None
        if (data.get('id') != native_id or data.get('mimeType') != 'text/plain'
                or data.get('trashed') is not False or data.get('driveId')
                or data.get('spaces') != ['drive'] or data.get('parents') != [self.files[native_id]]
                or data.get('capabilities', {}).get('canDownload') is not True
                or not isinstance(data.get('name'), str) or not data['name'].strip()
                or len(data['name']) > 1000):
            raise SourceUnavailable()
        for field in ('version', 'size'):
            if not isinstance(data.get(field), str) or not re.fullmatch(r'[0-9]{1,19}', data[field]):
                raise SourceUnavailable()
        if not 1 <= int(data['version']) <= 2**63-1 or not 1 <= int(data['size']) <= 1_000_000:
            raise SourceUnavailable()
        if (not isinstance(data.get('md5Checksum'), str)
                or not re.fullmatch(r'[0-9a-f]{32}', data['md5Checksum'])
                or not isinstance(data.get('headRevisionId'), str)
                or not re.fullmatch(ID, data['headRevisionId'])):
            raise SourceUnavailable()
        updated = datetime.fromisoformat(data['modifiedTime'].replace('Z', '+00:00'))
        if updated.tzinfo is None: raise SourceUnavailable()
        return data

    def read(self, actor, native_id, expected_version=None):
        method = 'drive-delegated-current-read'
        try:
            if native_id not in self.native_ids: raise SourceUnavailable()
            credential = self._credential(actor)
            metadata = self._metadata(native_id, credential)
            if metadata is None: return Decision('deny', now(), method, 0), None
            version = int(metadata['version'])
            if expected_version is not None and (type(expected_version) is not int or expected_version != version):
                return Decision('deny', now(), 'drive-version-changed', 0), None
            status, payload = self.transport.media(native_id, credential.authorization)
            if status in (403, 404): return Decision('deny', now(), method, 0), None
            if status != 200 or not isinstance(payload, bytes): raise SourceUnavailable()
            if (len(payload) != int(metadata['size'])
                    or hashlib.md5(payload, usedforsecurity=False).hexdigest() != metadata['md5Checksum']):
                raise SourceUnavailable()
            text = payload.decode('utf-8')
            if not text.strip() or any(ord(c) < 32 and c not in '\t\r\n' for c in text):
                raise SourceUnavailable()
            # Close the metadata/body race before releasing any evidence.
            current = self._metadata(native_id, credential)
            if current is None: return Decision('deny', now(), method, 0), None
            if current != metadata: return Decision('unknown', now(), 'drive-read-changed', 0), None
            return Decision('allow', now(), method, 0), {
                'source':'drive', 'native_id':native_id, 'version':version,
                'title':metadata['name'], 'text':text, 'source_updated_at':metadata['modifiedTime'],
                'source_url':'https://drive.google.com/file/d/' + native_id + '/view',
                'locator':{'file_id':native_id, 'revision_id':metadata['headRevisionId'],
                           'version':version, 'format':'text/plain',
                           'content_sha256':hashlib.sha256(payload).hexdigest()}}
        except (SourceUnavailable, KeyError, ValueError, TypeError, AttributeError, OverflowError, OSError):
            return Decision('unknown', now(), method, 0), None
