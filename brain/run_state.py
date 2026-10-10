"""Ephemeral session state. Only own submitted question; no source bodies, titles, counts or upstream IDs."""
import threading
import time
import uuid
from .contracts import now


class SessionRuns:
    def __init__(self):
        self.lock=threading.RLock()
        self.runs={}

    def begin(self, token, question=""):
        if not isinstance(question,str) or len(question)>4000:raise ValueError("Invalid question")
        with self.lock:
            old=self.runs.get(token)
            if old and old['status']=='running':raise PermissionError('Question already running')
            run={'request_id':uuid.uuid4().hex,'status':'running','phase':'queued','started':time.monotonic(),
                 'sources_used':[],'error_code':None,'question':question,'phases':['queued']}
            self.runs[token]=run
            return run['request_id']

    def phase(self, token, request_id, phase):
        with self.lock:
            run=self.runs.get(token)
            if run and run['request_id']==request_id and run['status']=='running':
                run['phase']=phase
                if phase not in run['phases']:run['phases'].append(phase)

    def finish(self, token, request_id, *, result=None, code=None):
        with self.lock:
            run=self.runs.get(token)
            if run and run['request_id']==request_id:
                run.update(status='failed' if code else 'completed',error_code=code,
                           elapsed_seconds=time.monotonic()-run['started'],
                           sources_used=sorted({e['source'] for e in (result or {}).get('evidence',[])
                               if e['evidence_id'] in {eid for c in (result or {}).get('claims',[]) for eid in c['evidence_ids']}}))

    def snapshot(self, token):
        with self.lock:
            run=self.runs.get(token)
            if not run:return None
            return {k:(list(v) if isinstance(v,list) else v) for k,v in run.items() if k!='started'} | {
                'elapsed_seconds':run.get('elapsed_seconds',time.monotonic()-run['started'])}

    def discard(self, token):
        with self.lock:self.runs.pop(token,None)


def runtime_status(app, actor, run):
    readers=getattr(app.world,'readers',{})
    discovery=getattr(app.world,'discovery',None)
    sources=[]
    for source in ('confluence','jira','slack','drive'):
        configured=app.auth_kind=='demo' or actor.user_id in getattr(readers.get(source),'delegations',{})
        report=(discovery.last.get(source,{}) if discovery and actor==discovery.actor else {})
        sources.append({'source':source,'configured':configured,
            'mode':'fixture' if app.auth_kind=='demo' else 'delegated',
            'last_check_at':report.get('observed_at'),
            'last_check_result':report.get('status','unconfirmed'),
            'snapshot_status':('current' if discovery and actor==discovery.actor and source in discovery.published_at
                               and discovery.clock()-discovery.published_at[source]<=120 and report.get('status')=='complete'
                               and not discovery.stop_event.is_set() else 'unconfirmed'),
            'checking':source in getattr(discovery,'checking',frozenset()) if discovery and actor==discovery.actor else False,
            'used_in_answer':bool(run and run['status']=='completed' and source in run['sources_used'])})
    admission=getattr(app.engine.query,'public_status',None)
    return {'mode':app.engine.mode,'model':app.engine.model.name,'sources':sources,'run':run,
            'query_admission':admission() if callable(admission) else None}
