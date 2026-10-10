"""Loopback-only synthetic demo server. Explicit --demo is mandatory."""
import argparse
import json
import secrets
import time
import threading
from .run_state import SessionRuns, runtime_status
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs
from .audit import Audit
from .contracts import Actor
from .confluence import JsonTransport
from .engine import Engine
from .sources import FixtureWorld
from .store import Store
from .runtime_version import runtime_version
from .deepseek import PriceReviewRequired

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
            name=self.server.session_cookie_name
            token=cookie[name].value if name in cookie else ''
            return app.session(token),token

        def dispatch(self, method):
            app=self.server.application
            try:
                self.gate()
                path=unquote(urlparse(self.path).path)
                if path not in ("/api/runtime", "/api/history/recent", "/api/session", "/api/logout", "/api/health", "/", "/app.js", "/style.css"):app.refresh()
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
                                          'auth_kind':app.auth_kind,'login_path':app.login_path,
                                          'runtime_version':runtime_version()})
                if method=='POST' and path==app.login_path:
                    actor=app.authenticate(data)
                    token=secrets.token_urlsafe(32); csrf=secrets.token_urlsafe(32)
                    app.sessions[token]={'actor':actor,'csrf':csrf,'expires':time.monotonic()+3600,'last_query':0}
                    return self.send(200,{'actor':actor.user_id,'csrf':csrf,'mode':app.engine.mode},cookie=f'{self.server.session_cookie_name}={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600')
                session,token=self.auth(); actor=session['actor']
                if method=='POST' and not secrets.compare_digest(self.headers.get('X-CSRF-Token',''),session['csrf']):
                    raise PermissionError('Unavailable')
                if method=='GET' and path=='/api/runtime':
                    return self.send(200,runtime_status(app,actor,app.session_runs.snapshot(token)))
                if method=='GET' and path=='/api/session':
                    return self.send(200,{'actor':actor.user_id,'csrf':session['csrf'],'mode':app.engine.mode})
                if method=='POST' and path=='/api/logout':
                    app.session_runs.discard(token)
                    del app.sessions[token]
                    return self.send(200,{'ok':True},cookie=f'{self.server.session_cookie_name}=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0')
                if method=='POST' and path=='/api/query':
                    if set(data)-{'question'}: raise ValueError('Unsupported query fields')
                    if time.monotonic()-session['last_query']<0.1: return self.send(429,{'error':'Please wait briefly before asking again.'})
                    session['last_query']=time.monotonic()
                    question=data.get('question')
                    if not isinstance(question,str) or not question.strip() or len(question)>4000:
                        raise ValueError('Invalid question')
                    rid=app.session_runs.begin(token,question)
                    try:
                        result=app.engine.query(actor,data.get('question'),request_id=rid,
                            progress=lambda phase:app.session_runs.phase(token,rid,phase))
                    except Exception as error:
                        from .deepseek import ModelUnavailable,ModelOutputRejected,ModelInputRejected
                        from .budget import BudgetExceeded,TrialAdmissionPaused
                        from .engine import VersionChanged
                        from .confluence import SourceUnavailable,SourceRefreshing
                        code=('model_price_review_required' if isinstance(error,PriceReviewRequired) else
                              'trial_admission_paused' if isinstance(error,TrialAdmissionPaused) else
                              'model_budget_unavailable' if isinstance(error,BudgetExceeded) else
                              'model_input_rejected' if isinstance(error,ModelInputRejected) else
                              'model_output_unavailable' if isinstance(error,ModelOutputRejected) else
                              'model_request_unavailable' if isinstance(error,ModelUnavailable) else
                              'source_refreshing' if isinstance(error,(VersionChanged,SourceRefreshing)) else 'source_unconfirmed')
                        messages={'trial_admission_paused':'This trial is paused at its authorized attempt, cost or unknown-usage limit. Contact the operator; no new model call was made.',
                                  'model_budget_unavailable':'The model budget is paused. Contact the operator before another attempt.',
                                  'model_input_rejected':'This question cannot be sent within the approved model boundary. Contact the operator.',
                                  'model_request_unavailable':'Model delivery or usage could not be confirmed. The budget reservation is retained. Contact the operator before another attempt.',
                                  'model_output_unavailable':'The model output did not pass validation. No draft is shown. You may explicitly try again; this can incur another model charge.',
                                  'source_refreshing':'Sources changed while this question was checked. Please wait briefly and explicitly try again.',
                                  'source_unconfirmed':'Current access or source integrity could not be confirmed. Try later or contact the operator.',
                                  'model_price_review_required':'The model needs a price review. Contact the operator; retrying will not resolve this.'}
                        app.session_runs.finish(token,rid,code=code)
                        return self.send(503,{'error':messages[code],'code':code,'request_id':rid,'run':app.session_runs.snapshot(token)})
                    app.session_runs.finish(token,rid,result=result)
                    app.audit.append('response_dispatch_attempted',actor.user_id,result['request_id'],{'transport':'http','meaning':'server attempted dispatch, not user read'})
                    return self.send(200,result)
                if method=='GET' and path.startswith('/api/evidence/'):
                    return self.send(200,app.engine.evidence(actor,path[len('/api/evidence/'):]))
                if method=='GET' and path=='/api/history/recent':
                    if urlparse(self.path).query:raise ValueError('Invalid history filter')
                    return self.send(200,{'history':app.engine.history_summaries(actor)})
                if method=='GET' and path=='/api/history':
                    params=parse_qs(urlparse(self.path).query,keep_blank_values=True)
                    if params:
                        if set(params)!={'request_id'} or len(params['request_id'])!=1:raise ValueError('Invalid history filter')
                        rid=params['request_id'][0]
                        if len(rid)!=32 or any(c not in '0123456789abcdef' for c in rid):raise ValueError('Invalid history filter')
                    else:rid=None
                    return self.send(200,{'history':app.engine.safe_history(actor,rid)})
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
            except PriceReviewRequired:
                self.send(503,{'error':'The model is paused pending an operator price review. Contact the operator; retrying will not resolve this.',
                               'code':'model_price_review_required'})
            except PermissionError:
                self.send(403,{'error':'Unavailable'})
            except (ValueError,TypeError,KeyError):
                self.send(400,{'error':'Invalid request'})
            except Exception:
                self.send(503,{'error':'Request could not be completed safely. Please try again.'})

        def do_GET(self):
            app=self.server.application
            if urlparse(self.path).path in ('/api/runtime','/api/history/recent','/api/session','/api/health','/','/app.js','/style.css'):
                return self.dispatch('GET')
            with getattr(app,'request_lock',app.store.lock):
                with app.store.lock:self.dispatch('GET')
        def do_POST(self):
            app=self.server.application
            if urlparse(self.path).path=='/api/logout':return self.dispatch('POST')
            # Admit one query per session before waiting on the query lock.
            if urlparse(self.path).path=='/api/query':
                try:
                    self.gate();session,token=self.auth()
                except PermissionError:return self.send(403,{'error':'Unavailable'})
                with app.admission_lock:
                    if token in app.active_queries:return self.send(409,{'error':'A question is already running.','code':'query_busy'})
                    app.active_queries.add(token)
                try:
                    with getattr(app,'request_lock',app.store.lock):
                        with app.store.lock:self.dispatch('POST')
                finally:
                    with app.admission_lock:app.active_queries.discard(token)
                return
            with getattr(app,'request_lock',app.store.lock):
                with app.store.lock:self.dispatch('POST')
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.application=app
    if app is not None:
        app.session_runs=SessionRuns();app.admission_lock=threading.Lock();app.active_queries=set()
    # Cookies have no browser port isolation. Select only this bound server's
    # cookie; tokens from other operators and legacy cookies never authenticate.
    server.session_cookie_name=f'aibang2_session_{server.server_port}'
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
