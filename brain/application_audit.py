"""Explicit registry-bound application audit; raw events and hashes are preserved."""
from datetime import datetime
import json
import re
from .audit import EVENT_TYPES


def inquire(app, actor, filters):
    scope = app.registry.auditor_row(actor)
    if not isinstance(filters, dict) or set(filters)-{'application_identity','start_time','end_time','event_type',
            'after','as_of','page_size','source','resource_scope','resource_id'}:
        raise ValueError('Unsupported application audit fields')
    viewers = frozenset(scope['viewer_ids'])
    viewer = filters.get('application_identity')
    if viewer is not None:
        if viewer not in viewers: raise PermissionError('Unavailable')
        viewers = frozenset([viewer])
    if filters.get('resource_scope','payment-service') != 'payment-service':
        raise PermissionError('Unavailable')
    size, after = filters.get('page_size',50), filters.get('after',0)
    if type(size) is not int or not 1 <= size <= 100 or type(after) is not int or after < 0:
        raise ValueError('Invalid pagination')
    event_type = filters.get('event_type')
    if event_type is not None and event_type not in EVENT_TYPES: raise ValueError('Invalid event type')
    source = filters.get('source')
    if source not in (None,'confluence','jira','slack','drive'): raise ValueError('Invalid source')
    resource = filters.get('resource_id')
    if resource is not None and (not isinstance(resource,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_:./-]{0,199}',resource)):
        raise ValueError('Invalid resource identifier')
    times = {}
    for key in ('start_time','end_time'):
        if filters.get(key) is not None:
            dt=datetime.fromisoformat(filters[key])
            if dt.tzinfo is None: raise ValueError('Timezone required')
            times[key]=dt
    with app.store.lock:
        head=app.store.db.execute('SELECT coalesce(max(seq),0) FROM audit').fetchone()[0]
        as_of=filters.get('as_of',head)
        if type(as_of) is not int or not 0 <= as_of <= head: raise ValueError('Invalid snapshot')
        marks=','.join('?' for _ in viewers)
        owned={row[0]:row[1] for row in app.store.db.execute(
            'SELECT request_id,viewer FROM reviewer_requests WHERE viewer IN ('+marks+')',tuple(sorted(viewers)))}
        rows=app.store.db.execute('SELECT body FROM audit WHERE seq<=? ORDER BY seq',(as_of,)).fetchall()
    decoded=[json.loads(row[0]) for row in rows]
    # A stable request map alone is insufficient: require its immutable identity event.
    payment_requests={e['request_id'] for e in decoded if e['payload'].get('resource_scope')=='payment-service'
                      and e['payload'].get('resource_id') is not None}
    anchors={e['request_id']:e for e in decoded if e['event_type']=='reviewer_query'
             and owned.get(e['request_id'])==e['actor']
             and (e['payload'].get('resource_scope')=='payment-service'
                  or (e['payload'].get('resource_scope') is None and e['request_id'] in payment_requests))}
    grouped={rid:[] for rid in anchors}
    for e in decoded:
        rid=e['request_id']
        if rid in anchors and e['actor'] in (anchors[rid]['actor'], anchors[rid]['payload']['effective_source_actor']):
            grouped[rid].append(e)
    events=[]
    for rid, lifecycle in grouped.items():
        # Fail closed if any scoped resource event belongs to another domain.
        if any(e['payload'].get('resource_scope') not in (None,'payment-service')
               or (e['payload'].get('resource_id') is not None and e['payload'].get('resource_scope')!='payment-service')
               for e in lifecycle): continue
        if (source or resource) and not any((not source or e['payload'].get('source')==source)
                and (not resource or e['payload'].get('resource_id')==resource) for e in lifecycle): continue
        for e in lifecycle:
            if event_type and e['event_type'] != event_type: continue
            stamp=datetime.fromisoformat(e['timestamp'])
            if 'start_time' in times and stamp < times['start_time']: continue
            if 'end_time' in times and stamp >= times['end_time']: continue
            # Resource-filtered queries cannot expose other resources in the same request.
            if resource and e['payload'].get('resource_id') not in (None,resource): continue
            events.append(e)
    events.sort(key=lambda e:e['seq'])
    page=[e for e in events if e['seq']>after][:size]
    # Revocation/policy changes during the read invalidate this entire response.
    if app.registry.auditor_row(actor) != scope: raise PermissionError('Unavailable')
    normalized=dict(filters,as_of=as_of,page_size=size,resource_scope='payment-service')
    app.audit.append('audit_inquiry',actor.user_id,'audit',{'filters':normalized,'returned':len(page)})
    return {'filters':normalized,'events':page,'total':len(events),'as_of':as_of,
            'next_after':page[-1]['seq'] if page and any(e['seq']>page[-1]['seq'] for e in events) else None,
            'semantics':'Events through this application; not proof of human reading. Local hash chain; no independent custody.'}
