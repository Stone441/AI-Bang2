"""Desktop Drive OAuth: PKCE, loopback, fixed scope, secrets only in memory."""
import base64
import hashlib
import json
import os
import re
import secrets
import stat
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request

from .confluence import JsonTransport, SourceUnavailable, Delegation
from .drive import BASE

SCOPE = 'https://www.googleapis.com/auth/drive.readonly'
AUTH = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN = 'https://oauth2.googleapis.com/token'
ISSUER = 'https://accounts.google.com'


@dataclass(frozen=True)
class DesktopClient:
    client_id: str
    client_secret: str = field(repr=False)


def load_client(path, expected_id):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or info.st_mode & 0o077 or info.st_size > 16384):
            raise ValueError('Private client configuration required')
        with os.fdopen(fd, 'r') as stream:
            fd = None
            data = json.load(stream)
    finally:
        if fd is not None: os.close(fd)
    client = data.get('installed', {})
    if (not isinstance(client, dict) or 'web' in data
            or not isinstance(expected_id, str)
            or not re.fullmatch(r'[A-Za-z0-9_-]+\.apps\.googleusercontent\.com', expected_id)
            or client.get('client_id') != expected_id
            or client.get('auth_uri') not in (AUTH, 'https://accounts.google.com/o/oauth2/auth')
            or client.get('token_uri') != TOKEN
            or not isinstance(client.get('client_secret'), str)
            or not re.fullmatch(r'[A-Za-z0-9_-]{1,4096}', client['client_secret'])):
        raise ValueError('Reviewed Google desktop client required')
    return DesktopClient(expected_id, client['client_secret'])


class TokenTransport(JsonTransport):
    def exchange(self, fields):
        return self._send(Request(TOKEN, data=urlencode(fields).encode(), method='POST',
            headers={'Content-Type':'application/x-www-form-urlencoded', 'Accept':'application/json'}))


class Consent:
    def __init__(self, client, port, timeout=600, *, offline=False):
        if not 1 <= port <= 65535 or not 1 <= timeout <= 600:
            raise ValueError('Bounded loopback required')
        self.client, self.port = client, port
        self.offline = offline
        self.redirect = f'http://127.0.0.1:{port}/oauth/callback'
        self.state, self.verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(48)
        self.expires = time.monotonic() + timeout
        self.code = None
        self.finished = False
        self.reason = 'awaiting_callback'

    def url(self, email):
        if not isinstance(email, str) or not re.fullmatch(r'[^\s:@]+@[^\s:@]+', email):
            raise ValueError('Reviewed Google email required')
        challenge = base64.urlsafe_b64encode(hashlib.sha256(self.verifier.encode()).digest()).decode().rstrip('=')
        parameters={'client_id':self.client.client_id, 'redirect_uri':self.redirect,
            'response_type':'code','scope':SCOPE,'state':self.state,'code_challenge':challenge,
            'code_challenge_method':'S256','login_hint':email,'access_type':'offline' if self.offline else 'online',
            'include_granted_scopes':'false'}
        if self.offline:parameters['prompt']='consent'
        return AUTH + '?' + urlencode(parameters)

    def callback(self, target, host, origin=None):
        def reject(reason, status=400):
            self.reason = reason
            return status
        if self.finished: return reject('callback_already_consumed')
        if time.monotonic() >= self.expires: return reject('callback_expired')
        if host != f'127.0.0.1:{self.port}': return reject('callback_host_mismatch')
        if origin: return reject('callback_origin_rejected')
        if len(target) > 8192: return reject('callback_malformed')
        parsed = urlsplit(target)
        if parsed.path != '/oauth/callback' or parsed.scheme or parsed.netloc or parsed.fragment:
            return reject('callback_path_rejected')
        try:
            query = parse_qs(parsed.query, keep_blank_values=True, max_num_fields=12)
        except ValueError:
            return reject('callback_malformed')
        returned_state = query.get('state', [''])[0]
        if any(len(v) != 1 for v in query.values()): return reject('callback_duplicate_parameter')
        if not secrets.compare_digest(returned_state.encode(), self.state.encode()):
            return reject('callback_state_mismatch')
        if set(query) - {'state','code','scope','error','authuser','prompt','iss'}:
            return reject('callback_unsupported_parameter')
        # Google discovery advertises RFC 9207 support. Issuer is required and
        # compared exactly; accepting an arbitrary issuer would enable mix-up.
        if query.get('iss') != [ISSUER]: return reject('callback_issuer_mismatch')
        if 'error' in query:
            if 'code' in query: return reject('callback_malformed')
            self.finished = True
            return reject('consent_denied', 403)
        code = query.get('code', [''])[0]
        if not code or len(code) > 4096 or any(c.isspace() for c in code):
            return reject('callback_code_unavailable')
        self.code, self.finished = code, True
        self.reason = 'callback_received'
        return 200

    def exchange(self, transport):
        if not self.finished or not self.code or time.monotonic() >= self.expires:
            raise SourceUnavailable()
        code, self.code = self.code, None  # No callback/code reuse, including exchange failure.
        status, data = transport.exchange({'client_id':self.client.client_id,
            'client_secret':self.client.client_secret,'code':code,'code_verifier':self.verifier,
            'grant_type':'authorization_code','redirect_uri':self.redirect})
        if (status != 200 or not isinstance(data, dict) or data.get('token_type') != 'Bearer'
                or not isinstance(data.get('scope'), str) or data['scope'].split() != [SCOPE]
                or type(data.get('expires_in')) != int or not 0 < data['expires_in'] <= 86400
                or not isinstance(data.get('access_token'), str)
                or not 1 <= len(data['access_token']) <= 8192
                or any(c.isspace() for c in data['access_token'])):
            raise SourceUnavailable()
        if self.offline:
            refresh=data.get('refresh_token')
            if not valid_token(refresh):raise SourceUnavailable()
            return {'access_token':data['access_token'],'refresh_token':refresh}
        # Memory-only remains the default; refresh tokens are discarded.
        return data['access_token']


def authorize(client, email, notify_url, *, timeout=600, transport=None, offline=False):
    class Callback(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)
        def log_message(self, *_): pass
        def do_GET(self):
            status = consent.callback(self.path, self.headers.get('Host'), self.headers.get('Origin'))
            text = ('Google authorization received. This is a temporary callback page; do not reload it. '
                    'Return to the terminal for the application link after account verification.'
                    if status == 200 else f'Authorization unavailable [{consent.reason}]. Return to the terminal.')
            if status != 200 and consent.reason not in diagnostics:
                diagnostics.add(consent.reason)
                print(f'OAuth callback stopped [{consent.reason}]. No callback URL or code is logged.',flush=True)
            body = text.encode()
            self.send_response(status)
            self.send_header('Content-Type','text/plain; charset=utf-8')
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Content-Security-Policy',"default-src 'none'; frame-ancestors 'none'")
            self.end_headers(); self.wfile.write(body)
    with HTTPServer(('127.0.0.1',0),Callback) as server:
        diagnostics = set()
        consent = Consent(client,server.server_port,timeout,offline=offline)
        server.timeout = 1
        notify_url(consent.url(email))
        while not consent.finished and time.monotonic() < consent.expires:
            server.handle_request()
        return consent.exchange(transport or TokenTransport())


def valid_token(token):
    return isinstance(token,str) and 1<=len(token)<=8192 and not any(c.isspace() for c in token)


class ReauthorizationRequired(SourceUnavailable):
    pass


def refresh_access(client, refresh_token, *, transport=None):
    if not valid_token(refresh_token):raise SourceUnavailable()
    status,data=(transport or TokenTransport()).exchange({'client_id':client.client_id,
        'client_secret':client.client_secret,'refresh_token':refresh_token,'grant_type':'refresh_token'})
    if status==400 and isinstance(data,dict) and data.get('error')=='invalid_grant':
        raise ReauthorizationRequired()
    if (status!=200 or not isinstance(data,dict) or data.get('token_type')!='Bearer'
            or data.get('scope','').split()!=[SCOPE] or not valid_token(data.get('access_token'))
            or type(data.get('expires_in')) is not int or not 0<data['expires_in']<=86400):
        raise SourceUnavailable()
    return data['access_token']


def verify_account(token, email, transport):
    # Metadata only; no file listing/content/extra identity scope is requested.
    status, data = transport.get(BASE + '/about?' + urlencode({'fields':'user(permissionId,me,emailAddress)'}),
                                 'Bearer ' + token)
    user = data.get('user', {}) if isinstance(data, dict) else {}
    if (status != 200 or user.get('me') is not True
            or not isinstance(user.get('emailAddress'), str)
            or user['emailAddress'].casefold() != email.casefold()
            or not isinstance(user.get('permissionId'), str)
            or not re.fullmatch(r'[A-Za-z0-9_-]{1,200}',user['permissionId'])):
        raise SourceUnavailable()
    return Delegation(user['permissionId'], 'Bearer ' + token)
