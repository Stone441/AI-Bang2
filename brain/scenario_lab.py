"""Isolated, in-memory fixture laboratory; never used by the employee server."""
import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .audit import Audit, verify_chain
from .contracts import Actor, now
from .engine import Engine
from .ingestion import Ingestion
from .sources import FixtureWorld
from .store import Store

WEB=Path(__file__).resolve().parents[1]/'web'


class ScenarioLab:
    actions=('baseline','update','revoke','audit')
    def __init__(self):
        self.world=FixtureWorld();self.store=Store();self.store.initialize(self.world)
        self.audit=Audit(self.store);self.engine=Engine(self.store,self.world,self.audit)
        self.actor=Actor('eng_a');self.steps=[];self.answers=[];self.lock=threading.Lock()
        self.csrf=secrets.token_urlsafe(32);self.failure=None

    def close(self):self.store.db.close()

    def state(self):
        return {'mode':'Synthetic sources / fake extractive model / local memory only',
            'limitations':'No live APIs, no model fees, no native update SLA or independent audit custody.',
            'next_action':self.actions[len(self.steps)] if not self.failure and len(self.steps)<len(self.actions) else None,
            'steps':self.steps,'csrf':self.csrf,'failure':self.failure}

    def preview_blocked(self,eid):
        try:self.engine.evidence(self.actor,eid)
        except PermissionError:return True
        return False

    def step(self,action):
        if self.failure or action not in self.actions or len(self.steps)>=len(self.actions) or action!=self.actions[len(self.steps)]:
            raise ValueError('Run the next stage in order; restart the lab for a fresh rehearsal.')
        started=now();checks={};source_events=[]
        if action=='baseline':
            answer=self.engine.query(self.actor,'payment-service runbook')
            checks['runbook_v1_returned']=any(e['resource_id']=='C-01' and e['version']==1 for e in answer['evidence'])
        elif action=='update':
            event=self.world.mutate('C-01','content',**self.world.baseline['updates']['C-01'])
            source_events.append({'event':'synthetic source changed','at':event['observed_at']})
            result=Ingestion(self.store,self.world).process(event)
            source_events.append({'event':'local version published','at':now()})
            answer=self.engine.query(self.actor,'payment-service runbook standby processing queue')
            old=self.answers[0];eid=next(e['evidence_id'] for e in old['evidence'] if e['resource_id']=='C-01')
            checks={'one_object_processed':result['processed_objects']==1,
                'runbook_v2_returned':any(e['resource_id']=='C-01' and e['version']==2 and 'standby processing queue' in e['text'] for e in answer['evidence']),
                'old_version_preview_blocked':self.preview_blocked(eid),
                'old_version_history_hidden':self.engine.safe_history(self.actor,old['request_id'])[0].get('unavailable') is True}
        elif action=='revoke':
            prior=self.answers[-1];eid=next(e['evidence_id'] for e in prior['evidence'] if e['resource_id']=='C-01')
            event=self.world.mutate('C-01','revoke',user_id=self.actor.user_id)
            source_events.append({'event':'synthetic authority revoked access','at':event['observed_at']})
            answer=self.engine.query(self.actor,'payment-service runbook standby processing queue')
            checks={'new_query_excludes_runbook':all(e['resource_id']!='C-01' for e in answer['evidence']),
                'old_preview_blocked':self.preview_blocked(eid),
                'old_history_hidden':self.engine.safe_history(self.actor,prior['request_id'])[0].get('unavailable') is True,
                'other_authorized_evidence_remains':bool(answer['evidence'])}
        else:
            events=self.audit.export();answer=None
            scoped=self.audit.inquire(Actor('auditor'),{'actor':'eng_a','resource_scope':'payment-service'})
            checks={'local_chain_valid':verify_chain(events)['valid'],
                'scoped_audit_has_events':bool(scoped['events']),
                'three_answers_recorded':sum(e['event_type']=='response_committed' for e in events)==3}
        if answer is not None:self.answers.append(answer)
        # Operator-only lab transcript: deliberately retains earlier fixture observations
        # after revocation; it is never an employee History or preview endpoint.
        self.steps.append({'action':action,'started_at':started,'finished_at':now(),
            'checks':checks,'passed':all(checks.values()),'source_events':source_events,
            'answer':answer,'request_id':answer['request_id'] if answer else None})
        if not all(checks.values()):self.failure='A recorded check failed.'
        return self.state()

    def export(self):
        state={k:v for k,v in self.state().items() if k!='csrf'}
        return {**state,'transcript_boundary':'Operator fixture observations retained; not employee history.',
            'audit':self.audit.export(),'chain':verify_chain(self.audit.export())}


def create_lab_server(lab,port=0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def send(self,status,body,content_type='application/json'):
            raw=json.dumps(body).encode() if content_type=='application/json' else body
            self.send_response(status)
            for key,value in {'Content-Type':content_type,'Content-Length':str(len(raw)),
                'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',
                'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"}.items():self.send_header(key,value)
            self.end_headers();self.wfile.write(raw)
        def gate(self):
            hosts={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
            if (self.headers.get('Host') not in hosts or self.headers.get('Sec-Fetch-Site')=='cross-site'
                    or self.headers.get('Origin') not in (None,*('http://'+h for h in hosts))):
                raise PermissionError('Unavailable')
        def do_GET(self):
            try:
                self.gate()
                with lab.lock:
                    if self.path=='/api/lab/state':return self.send(200,lab.state())
                    if self.path=='/api/lab/export':return self.send(200,lab.export())
                assets={'/':('scenario_lab.html','text/html; charset=utf-8'),
                    '/scenario_lab.js':('scenario_lab.js','application/javascript'),
                    '/scenario_lab.css':('scenario_lab.css','text/css'),'/style.css':('style.css','text/css')}
                if self.path not in assets:return self.send(404,{'error':'Unavailable'})
                filename,kind=assets[self.path];return self.send(200,(WEB/filename).read_bytes(),kind)
            except PermissionError:return self.send(403,{'error':'Unavailable'})
        def do_POST(self):
            try:
                self.gate()
                if self.path!='/api/lab/step':return self.send(404,{'error':'Unavailable'})
                if self.headers.get('X-CSRF-Token')!=lab.csrf:raise PermissionError('Unavailable')
                if self.headers.get('Content-Type')!='application/json':raise ValueError('JSON required')
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=256:raise ValueError('Invalid request')
                data=json.loads(self.rfile.read(length))
                if not isinstance(data,dict) or set(data)!={'action'} or not isinstance(data['action'],str):raise ValueError('Invalid action')
                with lab.lock:state=lab.step(data['action'])
                return self.send(200,state)
            except PermissionError:return self.send(403,{'error':'Unavailable'})
            except (ValueError,KeyError):return self.send(400,{'error':'Run the next stage using the lab controls.'})
            except Exception as error:
                lab.failure=type(error).__name__+' during a fixture stage'
                return self.send(500,{'error':'Lab step stopped; save the transcript and restart a fresh lab to investigate.'})
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)
