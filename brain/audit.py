"""Append-only interface and deterministic chain. Signed checkpoints reserved for CodeBuddy."""
import hashlib
import json
from .store import canonical
from .contracts import now

DOMAIN=b'ContextLedger.audit.v1\0'
ZERO='0'*64
AUDIT_ACTORS=('eng_a','eng_b','product_ops')
EVENT_TYPES={'request_started','candidate_evaluated','authorization_decided','evidence_used','generation_completed','response_committed','response_dispatch_attempted','request_failed','audit_inquiry','source_changed',
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

    def inquire(self, actor, filters):
        if actor.user_id!='auditor':
            raise PermissionError('Unavailable')
        allowed={'actor','start_time','end_time','event_type','after','as_of','page_size','source','resource_scope'}
        if set(filters)-allowed:
            raise ValueError('Unsupported audit fields')
        uid=filters.get('actor','eng_a')
        if uid=='jdoe': uid='eng_a'
        if uid not in AUDIT_ACTORS:
            raise PermissionError('Unavailable')
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
            rows=self.store.db.execute("SELECT body FROM audit WHERE seq<=? AND json_extract(body,'$.actor')=? ORDER BY seq",(as_of,uid)).fetchall()
        # Scoped exact filtering. SQL never comes from the model or request.
        # Scope matches exact resource events and includes the surrounding request lifecycle,
        # so the inquiry can reconstruct the question and final answer as well as checks.
        decoded=[json.loads(row[0]) for row in rows]
        scoped_requests={e['request_id'] for e in decoded if e['actor']==uid
                         and (not filters.get('source') or e['payload'].get('source')==filters['source'])
                         and (not filters.get('resource_scope') or e['payload'].get('resource_scope')==filters['resource_scope'])}
        events=[]
        for row in rows:
            e=json.loads(row[0])
            if e['actor']!=uid or (event_type and e['event_type']!=event_type): continue
            stamp=datetime.fromisoformat(e['timestamp'])
            if filters.get('start_time') and stamp<datetime.fromisoformat(filters['start_time']): continue
            if filters.get('end_time') and stamp>=datetime.fromisoformat(filters['end_time']): continue
            if (filters.get('source') or filters.get('resource_scope')) and e['request_id'] not in scoped_requests: continue
            events.append(e)
        page=[e for e in events if e['seq']>after][:size]
        normalized=dict(filters,actor=uid,as_of=as_of,page_size=size)
        self.append('audit_inquiry',actor.user_id,'audit',{'filters':normalized,'returned':len(page)})
        return {'filters':normalized,'events':page,'total':len(events),'as_of':as_of,
                'next_after':page[-1]['seq'] if page and any(e['seq']>page[-1]['seq'] for e in events) else None,
                'semantics':'Events through this application; not proof of human reading.'}
