"""Opt-in bounded HTTPS reuse for native readers; no cache or retry.

Only socket lifecycle changes. Readers still perform every identity, permission,
body and version read. Proxy routes use the original opener, never a direct
fallback. Each pool is confined to one configured origin and credential hash.
"""
import hashlib
import http.client
import ssl
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import getproxies, proxy_bypass


def origin(url):
    parsed = urlsplit(url)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
            or parsed.password or parsed.fragment):
        raise ValueError('Explicit HTTPS origin required')
    return parsed.hostname, parsed.port or 443


class PooledOpener:
    def __init__(self, base_url, fallback, *, maximum=2, idle_seconds=15,
                 context=None):
        if type(maximum) is not int or not 1 <= maximum <= 4 or not 0 < idle_seconds <= 60:
            raise ValueError('Bounded pool required')
        self.origin = origin(base_url)
        self.fallback = fallback
        self.maximum, self.idle_seconds = maximum, idle_seconds
        self.context = context or ssl.create_default_context()
        if not self.context.check_hostname or self.context.verify_mode != ssl.CERT_REQUIRED:
            raise ValueError('Verified TLS required')
        self.context.set_alpn_protocols(['http/1.1'])
        self.condition = threading.Condition()
        self.idle = []
        self.count = 0
        self.closed = False

    def _take(self, key, deadline):
        with self.condition:
            while True:
                if self.closed:
                    raise URLError('Source pool closed')
                now = time.monotonic()
                # Credential rotation cannot reuse the previous credential's socket.
                kept = []
                for old_key, connection, touched in self.idle:
                    if old_key != key or now-touched >= self.idle_seconds:
                        connection.close()
                        self.count -= 1
                    else:
                        kept.append((old_key, connection, touched))
                self.idle = kept
                if deadline <= now:
                    raise URLError('Source pool wait expired')
                if self.idle:
                    return self.idle.pop()[1]
                if self.count < self.maximum:
                    self.count += 1
                    return http.client.HTTPSConnection(*self.origin,
                        timeout=deadline-now, context=self.context)
                self.condition.wait(deadline-now)

    def _release(self, key, connection, reusable):
        with self.condition:
            if reusable and not self.closed and connection.sock is not None:
                self.idle.append((key, connection, time.monotonic()))
            else:
                connection.close()
                self.count -= 1
            self.condition.notify()

    def open(self, request, timeout=10):
        if not 0 < timeout <= 30 or origin(request.full_url) != self.origin:
            raise URLError('Source destination rejected')
        parsed = urlsplit(request.full_url)
        method = request.get_method()
        if method != 'GET' and not (method == 'POST' and
                request.full_url == 'https://slack.com/api/auth.test' and request.data == b''):
            raise URLError('Read-only source request required')
        headers = dict(request.header_items())
        lowered = {key.lower(): value for key, value in headers.items()}
        if any(name in lowered for name in ('host', 'proxy-authorization', 'connection',
                                             'transfer-encoding', 'content-length')):
            raise URLError('Source header rejected')
        credential = lowered.get('authorization', '')
        if not credential.startswith(('Bearer ', 'Basic ')):
            raise URLError('Source credential required')
        with self.condition:
            if self.closed:
                raise URLError('Source pool closed')
        # Honor OS/environment proxy policy using the original urllib stack.
        # No credentials, URL, proxy value or response are logged by this layer.
        if getproxies().get('https') and not proxy_bypass(parsed.netloc):
            return self.fallback.open(request, timeout=timeout)
        key = hashlib.sha256(credential.encode()).digest()
        deadline = time.monotonic()+timeout
        connection = self._take(key, deadline)
        try:
            connection.timeout = max(0.001, deadline-time.monotonic())
            if connection.sock is not None:
                connection.sock.settimeout(connection.timeout)
            target = (parsed.path or '/') + ('?'+parsed.query if parsed.query else '')
            connection.request(method, target, body=request.data, headers=headers)
            response = connection.getresponse()
        except (OSError, http.client.HTTPException, ValueError):
            self._release(key, connection, False)
            raise URLError('Source transport unavailable') from None
        if response.status >= 300:
            # Never consume an error body, and never follow redirects.
            status, response_headers = response.status, response.headers
            response.close()
            self._release(key, connection, False)
            raise HTTPError(request.full_url, status, 'Source request rejected', response_headers, None)
        return PooledResponse(self, key, connection, response)

    def close(self):
        with self.condition:
            self.closed = True
            for _, connection, _ in self.idle:
                connection.close()
                self.count -= 1
            self.idle.clear()
            self.condition.notify_all()


class PooledResponse:
    def __init__(self, pool, key, connection, response):
        self.pool, self.key, self.connection, self.response = pool, key, connection, response
        self.status, self.headers = response.status, response.headers
        self.complete = False
        self.closed = False

    def read(self, amount=None):
        try:
            remaining = self.response.length
            value = self.response.read(amount)
            expected = remaining if amount is None else min(amount, remaining) if remaining is not None else None
            if expected is not None and len(value) < expected:
                raise http.client.IncompleteRead(value)
            if self.response.isclosed():
                if self.response.length not in (None, 0):
                    raise http.client.IncompleteRead(value)
                self.complete = True
            return value
        except (OSError, http.client.HTTPException, ValueError):
            self.close()
            raise URLError('Source body unavailable') from None

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        self.close(reusable=kind is None)

    def close(self, reusable=False):
        if not self.closed:
            self.closed = True
            keep = reusable and self.complete and not self.response.will_close
            self.response.close()
            self.pool._release(self.key, self.connection, keep)


def install(readers, *, maximum=2):
    """Install after reader construction, before background/query threads start.

    Returns a rollback callback. Existing cooldown/timing wrappers stay intact.
    """
    from .confluence import JsonTransport
    changes = []
    try:
        for source, reader in sorted(readers.items()):
            base = reader.api_base if source in ('confluence', 'jira') else {
                'drive': 'https://www.googleapis.com', 'slack': 'https://slack.com'}[source]
            transport = reader.transport
            while hasattr(transport, 'delegate'):
                transport = transport.delegate
            if not isinstance(transport, JsonTransport) or isinstance(transport.opener, PooledOpener):
                raise ValueError('Unmodified native transport required')
            old = transport.opener
            pool = PooledOpener(base, old, maximum=maximum)
            changes.append((transport, old, pool))
            transport.opener = pool
    except Exception:
        for transport, old, pool in changes:
            transport.opener = old
            pool.close()
        raise
    def rollback():
        for transport, old, pool in changes:
            if transport.opener is pool:
                transport.opener = old
            pool.close()
    return rollback
