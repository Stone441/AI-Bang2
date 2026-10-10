"""Append-only interface and deterministic chain. Signed checkpoints reserved for CodeBuddy."""
import hashlib
import json
import re
from .store import canonical
from .contracts import now

DOMAIN=b'ContextLedger.audit.v1\0'
ZERO='0'*64
AUDIT_ACTORS=('eng_a','eng_b','product_ops')
EVENT_TYPES={'model_request_unavailable','version_recovery','request_started','candidate_evaluated','authorization_decided','evidence_used','generation_completed','response_committed','response_dispatch_attempted','request_failed','audit_inquiry','source_changed',
             'model_dispatch_intent','model_dispatch_attempted','model_usage_received','model_output_accepted','model_output_rejected'}


def event_hash(event):
    return hashlib.sha256(DOMAIN+canonical({k:v for k,v in event.items() if k!='hash'}).encode()).hexdigest()


def verify_chain(events, trusted_head=None):
    """trusted_head must come from separately retained caller evidence, not this export.

    Not a signature verifier. Whole-chain replacement without a trusted head is undetectable.
    """
    previous=ZERO
    for seq,event in enumerate(events,1):
        if event.get('seq')!=seq or event.get('previous_hash')!=previous or event.get('hash')!=event_hash(event):
            return {'valid':False,'reason':'chain_mismatch','sequence':seq}
        previous=event['hash']
    if trusted_head:
        seq=trusted_head['through_seq']
        if seq>len(events) or (seq>0 and events[seq-1]['hash']!=trusted_head['head_hash']):
            return {'valid':False,'reason':'trusted_head_mismatch'}
    return {'valid':True,'events':len(events),'anchored_through':trusted_head['through_seq'] if trusted_head else 0,
            'signature_verified':False,'boundary':'local chain only; independent signed checkpoint pending'}


class Audit:
    def __init__(self, store):
        self.store=store
        self.fail=False

    def append(self, event_type, actor, request_id, payload):
        if self.fail:
            raise RuntimeError('audit unavailable')
        if event_type not in EVENT_TYPES:
            raise ValueError('event type')
        with self.store.transaction() as db:
            row=db.execute('SELECT seq,body FROM audit ORDER BY seq DESC LIMIT 1').fetchone()
            event={'schema_version':1,'seq':row[0]+1 if row else 1,
                   'previous_hash':json.loads(row[1])['hash'] if row else ZERO,
                   'event_type':event_type,'actor':actor,'request_id':request_id,'timestamp':now(),'payload':payload}
            event['hash']=event_hash(event)
            db.execute('INSERT INTO audit VALUES(?,?)',(event['seq'],canonical(event)))
            return event

    def export(self):
        with self.store.lock:
            return [json.loads(r[0]) for r in self.store.db.execute('SELECT body FROM audit ORDER BY seq')]

    def request_has_unknown(self, actor, request_id):
        """Internal completeness check; never exposes source/object diagnostics."""
        with self.store.lock:
            return self.store.db.execute("SELECT 1 FROM audit WHERE "
                "json_extract(body,'$.actor')=? AND json_extract(body,'$.request_id')=? "
                "AND json_extract(body,'$.event_type')='authorization_decided' "
                "AND json_extract(body,'$.payload.result')='unknown' LIMIT 1",
                (actor,request_id)).fetchone() is not None

    def inquire(self, actor, filters):
        if actor.user_id!='auditor':
            raise PermissionError('Unavailable')
        allowed={'actor','start_time','end_time','event_type','after','as_of','page_size','source','resource_scope','resource_id'}
        if set(filters)-allowed:
            raise ValueError('Unsupported audit fields')
        resource_id=filters.get('resource_id')
        if resource_id is not None and (not isinstance(resource_id,str)
                or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_:./-]{0,199}',resource_id)):
            raise ValueError('Invalid resource identifier')
        if resource_id is not None and filters.get('resource_scope','payment-service')!='payment-service':
            raise PermissionError('Unavailable')
        uid=filters.get('actor',None if resource_id is not None else 'eng_a')
        if uid=='jdoe': uid='eng_a'
        if uid is None and resource_id is None:
            raise PermissionError('Unavailable')
        if uid is not None and uid not in AUDIT_ACTORS:
            raise PermissionError('Unavailable')
        actors=(uid,) if uid is not None else AUDIT_ACTORS
        size=filters.get('page_size',50); after=filters.get('after',0)
        if type(size)!=int or not 1<=size<=100 or type(after)!=int or after<0:
            raise ValueError('Invalid pagination')
        event_type=filters.get('event_type')
        if event_type is not None and event_type not in EVENT_TYPES:
            raise ValueError('Invalid event type')
        from datetime import datetime
        for field in ('start_time','end_time'):
            if filters.get(field):
                dt=datetime.fromisoformat(filters[field])
                if dt.tzinfo is None: raise ValueError('Timezone required')
        if filters.get('source') not in (None,'confluence','jira','slack','drive'):
            raise ValueError('Invalid source')
        if filters.get('resource_scope') not in (None,'payment-service'):
            raise ValueError('Unknown scope; confirm payment-service')
        with self.store.lock:
            head=self.store.db.execute('SELECT coalesce(max(seq),0) FROM audit').fetchone()[0]
            as_of=filters.get('as_of',head)
            if type(as_of)!=int or as_of<0 or as_of>head: raise ValueError('Invalid snapshot')
            placeholders=','.join('?' for _ in actors)
            rows=self.store.db.execute("SELECT body FROM audit WHERE seq<=? AND json_extract(body,'$.actor') IN ("+placeholders+") ORDER BY seq",(as_of,*actors)).fetchall()
        # Scoped exact filtering. SQL never comes from the model or request.
        # Scope matches exact resource events and includes the surrounding request lifecycle,
        # so the inquiry can reconstruct the question and final answer as well as checks.
        decoded=[json.loads(row[0]) for row in rows]
        scoped_requests={(e['actor'],e['request_id']) for e in decoded if e['actor'] in actors
                         and (resource_id is None or e['payload'].get('resource_id')==resource_id)
                         and (resource_id is None or e['payload'].get('resource_scope')=='payment-service')
                         and (not filters.get('source') or e['payload'].get('source')==filters['source'])
                         and (not filters.get('resource_scope') or e['payload'].get('resource_scope')==filters['resource_scope'])}
        events=[]
        for row in rows:
            e=json.loads(row[0])
            if e['actor'] not in actors or (event_type and e['event_type']!=event_type): continue
            stamp=datetime.fromisoformat(e['timestamp'])
            if filters.get('start_time') and stamp<datetime.fromisoformat(filters['start_time']): continue
            if filters.get('end_time') and stamp>=datetime.fromisoformat(filters['end_time']): continue
            if (resource_id is not None or filters.get('source') or filters.get('resource_scope')) and (e['actor'],e['request_id']) not in scoped_requests: continue
            if resource_id is not None and e['payload'].get('resource_id') not in (None,resource_id): continue
            if resource_id is not None and e['payload'].get('resource_id') is not None and e['payload'].get('resource_scope')!='payment-service': continue
            if resource_id is not None and filters.get('source') and e['payload'].get('resource_id') is not None and e['payload'].get('source')!=filters['source']: continue
            events.append(e)
        page=[e for e in events if e['seq']>after][:size]
        normalized=dict(filters,actor=uid,as_of=as_of,page_size=size)
        self.append('audit_inquiry',actor.user_id,'audit',{'filters':normalized,'returned':len(page)})
        return {'filters':normalized,'events':page,'total':len(events),'as_of':as_of,
                'next_after':page[-1]['seq'] if page and any(e['seq']>page[-1]['seq'] for e in events) else None,
                'semantics':'Events through this application; not proof of human reading.'}
