"""Loopback-only synthetic demo server. Explicit --demo is mandatory."""
import argparse
import json
import secrets
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote
from .audit import Audit
from .contracts import Actor
from .confluence import JsonTransport
from .engine import Engine
from .sources import FixtureWorld
from .store import Store

WEB=Path(__file__).resolve().parents[1]/'web'


class App:
    login_path='/api/demo/login'
    auth_kind='demo'
    def __init__(self, store=None, source_path=None):
        self.world=FixtureWorld(); self.store=store or Store()
        self.source_path=source_path
        self.world.authority_path=source_path
        if source_path:
            if Path(source_path).exists(): self.world.refresh(source_path)
            else: self.world.save(source_path)
        self.store.initialize(self.world)
        self.audit=Audit(self.store); self.engine=Engine(self.store,self.world,self.audit)
        self.sessions={}
        from .ingestion import Ingestion
        self.ingestion=Ingestion(self.store,self.world)

    def authenticate(self, data):
        if set(data)!={'user'} or data['user'] not in self.world.users:
            raise ValueError('Unknown demo user')
        return Actor(data['user'])

    def refresh(self):
        if self.source_path:
            self.world.refresh(self.source_path)
            for source in ('confluence','jira','slack','drive'):
                self.ingestion.poll(source)

    def session(self, token):
        value=self.sessions.get(token)
        if not value or value['expires']<time.monotonic():
            raise PermissionError('Sign in required')
        return value


def create_server(app, port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Avoid questions, cookies and raw payloads in generic logs.

        def send(self, code, body, content_type='application/json', cookie=None):
            raw=json.dumps(body).encode() if content_type=='application/json' else body
            self.send_response(code)
            self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Content-Security-Policy',"default-src 'self'; connect-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            if cookie: self.send_header('Set-Cookie',cookie)
            self.end_headers(); self.wfile.write(raw)

        def gate(self):
            expected={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
            if self.headers.get('Host') not in expected:
                raise PermissionError('Unavailable')
            origin=self.headers.get('Origin')
            if origin and origin not in {'http://'+host for host in expected}:
                raise PermissionError('Unavailable')
            if self.headers.get('Sec-Fetch-Site')=='cross-site':
                raise PermissionError('Unavailable')

        def auth(self):
            app=self.server.application
            cookie=SimpleCookie(); cookie.load(self.headers.get('Cookie',''))
            token=cookie['session'].value if 'session' in cookie else ''
            return app.session(token),token

        def dispatch(self, method):
            app=self.server.application
            try:
                self.gate()
                app.refresh()
                path=unquote(urlparse(self.path).path)
                data={}
                if method=='POST':
                    length=int(self.headers.get('Content-Length','0'))
                    if not 0<length<=12000: raise ValueError('Invalid request size')
                    if self.headers.get('Content-Type','').split(';')[0]!='application/json': raise ValueError('JSON required')
                    data=json.loads(self.rfile.read(length))
                    if not isinstance(data,dict): raise ValueError('Object required')
                if method=='GET' and path in ('/','/app.js','/style.css'):
                    filename={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[path]
                    mime={'/':'text/html; charset=utf-8','/app.js':'text/javascript; charset=utf-8','/style.css':'text/css; charset=utf-8'}[path]
                    return self.send(200,(WEB/filename).read_bytes(),mime)
                if method=='GET' and path=='/api/health':
                    return self.send(200,{'mode':app.engine.mode,'live_enabled':any(isinstance(r.transport, JsonTransport) for r in getattr(app.world,'readers',{}).values()),
                                          'auth_kind':app.auth_kind,'login_path':app.login_path})
                if method=='POST' and path==app.login_path:
                    actor=app.authenticate(data)
                    token=secrets.token_urlsafe(32); csrf=secrets.token_urlsafe(32)
                    app.sessions[token]={'actor':actor,'csrf':csrf,'expires':time.monotonic()+3600,'last_query':0}
                    return self.send(200,{'actor':actor.user_id,'csrf':csrf,'mode':app.engine.mode},cookie=f'session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600')
                session,token=self.auth(); actor=session['actor']
                if method=='POST' and not secrets.compare_digest(self.headers.get('X-CSRF-Token',''),session['csrf']):
                    raise PermissionError('Unavailable')
                if method=='GET' and path=='/api/session':
                    return self.send(200,{'actor':actor.user_id,'csrf':session['csrf'],'mode':app.engine.mode})
                if method=='POST' and path=='/api/logout':
                    del app.sessions[token]
                    return self.send(200,{'ok':True},cookie='session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
                if method=='POST' and path=='/api/query':
                    if set(data)-{'question','history_id'}: raise ValueError('Unsupported query fields')
                    if time.monotonic()-session['last_query']<0.1: return self.send(429,{'error':'Please wait briefly before asking again.'})
                    session['last_query']=time.monotonic()
                    result=app.engine.query(actor,data.get('question'),data.get('history_id'))
                    app.audit.append('response_dispatch_attempted',actor.user_id,result['request_id'],{'transport':'http','meaning':'server attempted dispatch, not user read'})
                    return self.send(200,result)
                if method=='GET' and path.startswith('/api/evidence/'):
                    return self.send(200,app.engine.evidence(actor,path[len('/api/evidence/'):]))
                if method=='GET' and path=='/api/history':
                    return self.send(200,{'history':app.engine.safe_history(actor)})
                if method=='GET' and path.startswith('/api/export/'):
                    return self.send(200,{'history':app.engine.safe_history(actor,path[len('/api/export/'):])})
                if method=='GET' and path=='/api/sources/status':
                    if actor.user_id!='auditor': raise PermissionError('Unavailable')
                    return self.send(200,{'sources':[app.world.adapter(s).capabilities() for s in ('confluence','jira','slack','drive')]})
                if method=='POST' and path=='/api/audit/events':
                    return self.send(200,app.audit.inquire(actor,data))
                if method=='POST' and path=='/api/audit/inquire':
                    if actor.user_id!='auditor': raise PermissionError('Unavailable')
                    if set(data)!={'question'}: raise ValueError('Unsupported inquiry fields')
                    from .audit_query import parse_inquiry
                    return self.send(200,app.audit.inquire(actor,parse_inquiry(data['question'])))
                return self.send(404,{'error':'Unavailable'})
            except PermissionError:
                self.send(403,{'error':'Unavailable'})
            except (ValueError,TypeError,KeyError):
                self.send(400,{'error':'Invalid request'})
            except Exception:
                self.send(503,{'error':'Request could not be completed safely. Please try again.'})

        def do_GET(self):
            with self.server.application.store.lock: self.dispatch('GET')
        def do_POST(self):
            with self.server.application.store.lock: self.dispatch('POST')
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.application=app
    return server


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--demo',action='store_true'); parser.add_argument('--port',type=int,default=8080)
    args=parser.parse_args()
    if not args.demo: parser.error('Only --demo synthetic loopback mode is implemented. Live mode is disabled.')
    runtime=Path('.runtime'); runtime.mkdir(mode=0o700,exist_ok=True)
    app=App(Store(str(runtime/'demo.sqlite')),runtime/'source.json')
    server=create_server(app,args.port)
    print(f'ContextLedger — SYNTHETIC / FAKE MODEL — http://127.0.0.1:{server.server_port}',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__': main()
