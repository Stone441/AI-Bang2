"""Ephemeral session state. Only own submitted question; no source bodies, titles, counts or upstream IDs."""
import threading
import time
import uuid
from .contracts import now

STAGES=('queued','retrieval','authorization','generation','review','final_checks')

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
                 'sources_used':[],'error_code':None,'question':question,'phases':['queued'],
                 'stage_states':{stage:'running' if stage=='queued' else 'pending' for stage in STAGES}}
            self.runs[token]=run
            return run['request_id']

    def phase(self, token, request_id, phase):
        with self.lock:
            run=self.runs.get(token)
            if run and run['request_id']==request_id and run['status']=='running':
                states=run['stage_states']
                if phase=='synthesis_failed':
                    if run['phase'] in ('generation','review'):states[run['phase']]='failed'
                    return
                previous=run['phase']
                if previous!=phase and states.get(previous)=='running':
                    states[previous]='pending' if phase=='refreshing' else 'completed'
                if phase in states:states[phase]='running'
                run['phase']=phase
                if phase not in run['phases']:run['phases'].append(phase)

    def finish(self, token, request_id, *, result=None, code=None):
        with self.lock:
            run=self.runs.get(token)
            if run and run['request_id']==request_id:
                states=run['stage_states']
                if states.get(run['phase'])=='running':states[run['phase']]='failed' if code else 'completed'
                for stage,state in states.items():
                    if state=='pending':states[stage]='not_run'
                run.update(status='failed' if code else 'evidence_only' if (result or {}).get('answer_status')=='evidence_only' else 'completed',error_code=code or (result or {}).get('synthesis_failure'),
                           elapsed_seconds=time.monotonic()-run['started'],
                           sources_used=sorted({e['source'] for e in (result or {}).get('evidence',[])
                               if e['evidence_id'] in {eid for c in (result or {}).get('claims',[]) for eid in c['evidence_ids']}}))

    def snapshot(self, token):
        with self.lock:
            run=self.runs.get(token)
            if not run:return None
            return {k:(list(v) if isinstance(v,list) else dict(v) if isinstance(v,dict) else v) for k,v in run.items() if k!='started'} | {
                'elapsed_seconds':run.get('elapsed_seconds',time.monotonic()-run['started'])}

    def discard(self, token):
        with self.lock:self.runs.pop(token,None)


def runtime_status(app, actor, run):
    from .discovery import SNAPSHOT_MAX_AGE_SECONDS
    readers=getattr(app.world,'readers',{})
    discovery=getattr(app.world,'discovery',None)
    sources=[]
    for source in ('confluence','jira','slack','drive'):
        configured=app.auth_kind=='demo' or actor.user_id in getattr(readers.get(source),'delegations',{})
        report=(discovery.last.get(source,{}) if discovery and actor==discovery.actor else {})
        owns_discovery=discovery is not None and actor==discovery.actor
        published=discovery.published_at.get(source) if owns_discovery else None
        age=max(0,discovery.clock()-published) if published is not None else None
        due=getattr(discovery,'due',{}).get(source) if owns_discovery else None
        worker_running=(owns_discovery and not discovery.stop_event.is_set()
                        and discovery.thread is not None and discovery.thread.is_alive())
        sources.append({'source':source,'configured':configured,
            'mode':'fixture' if app.auth_kind=='demo' else 'delegated',
            'last_check_at':report.get('observed_at'),
            'last_check_result':report.get('status','unconfirmed'),
            'last_successful_check_at':report.get('last_successful_checkpoint_at'),
            'snapshot_age_seconds':round(age,3) if age is not None else None,
            'snapshot_max_age_seconds':SNAPSHOT_MAX_AGE_SECONDS,
            'next_check_in_seconds':round(max(0,due-discovery.clock()),3) if due is not None and worker_running else None,
            'snapshot_status':('current' if worker_running and age is not None
                               and age<=SNAPSHOT_MAX_AGE_SECONDS and report.get('status')=='complete' else 'unconfirmed'),
            'checking':source in getattr(discovery,'checking',frozenset()) if discovery and actor==discovery.actor else False,
            'used_in_answer':bool(run and run['status']=='completed' and source in run['sources_used'])})
    admission=getattr(app.engine.query,'public_status',None)
    return {'mode':app.engine.mode,'model':app.engine.model.name,'sources':sources,'run':run,
            'query_admission':admission() if callable(admission) else None}
