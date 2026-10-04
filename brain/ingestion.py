"""Object-scoped incremental publication. No embeddings or external writes."""
import copy
from .contracts import now
from .store import canonical


class Ingestion:
    def __init__(self,store,world):
        self.store,self.world=store,world
        self.processed_objects=0
        self.fail_after_prepare=False

    def process(self,event):
        r=copy.deepcopy(event['snapshot']); source=r['source']; eid=event['event_id']
        with self.store.transaction() as db:
            job=db.execute('SELECT state,attempts FROM jobs WHERE event_id=?',(eid,)).fetchone()
            if job and job['state']=='done': return {'state':'duplicate','processed_objects':0}
            attempts=job['attempts']+1 if job else 1
            db.execute('INSERT OR REPLACE INTO jobs VALUES(?,?,?,?)',(eid,'processing',attempts,canonical(event)))
        try:
            with self.store.transaction() as db:
                old=db.execute('SELECT version,body FROM resources WHERE id=?',(r['id'],)).fetchone()
                published=False
                if event['kind']=='delete':
                    # Tombstone first; historical versions remain restricted from user paths.
                    db.execute('UPDATE resources SET active=0 WHERE id=?',(r['id'],))
                elif event['kind']=='revoke':
                    # Current authoritative policy is checked for every request. Never rebuild content.
                    pass
                elif not old or r['version']>old['version']:
                    r['indexed_at']=now()
                    if self.fail_after_prepare: raise RuntimeError('injected indexing failure')
                    db.execute('INSERT INTO versions VALUES(?,?,?)',(r['id'],r['version'],canonical(r)))
                    db.execute('INSERT OR REPLACE INTO resources VALUES(?,?,?,?)',(r['id'],r['version'],int(r['active']),canonical(r)))
                    published=True
                elif r['version']==old['version']:
                    import json
                    if r['text']!=json.loads(old['body'])['text']:
                        raise ValueError('Content changed without new revision')
                db.execute('UPDATE jobs SET state=? WHERE event_id=?',('done',eid))
                # Advance only through a contiguous prefix of successfully handled source events.
                cursor_row=db.execute('SELECT cursor FROM sync WHERE source=?',(source,)).fetchone()
                cursor=cursor_row[0] if cursor_row else 0
                for pending in self.world.events:
                    if pending['snapshot']['source']!=source or pending['event_id']<=cursor: continue
                    state=db.execute('SELECT state FROM jobs WHERE event_id=?',(pending['event_id'],)).fetchone()
                    if not state or state[0]!='done': break
                    cursor=pending['event_id']
                db.execute('INSERT INTO sync VALUES(?,?,?,?) ON CONFLICT(source) DO UPDATE SET cursor=excluded.cursor,checked_at=excluded.checked_at,health=excluded.health',
                           (source,cursor,now(),'ready'))
            if published:self.processed_objects+=1
            return {'state':'published' if published else 'applied','processed_objects':int(published),
                    'resource_id':r['id'],'source_updated_at':r['source_updated_at'],'observed_at':event['observed_at'],
                    'indexed_at':r.get('indexed_at'),'version':r['version']}
        except Exception:
            with self.store.transaction() as db:
                db.execute('UPDATE jobs SET state=? WHERE event_id=?',('failed',eid))
                db.execute('UPDATE sync SET health=? WHERE source=?',('stalled',source))
            raise

    def poll(self,source):
        with self.store.lock:
            row=self.store.db.execute('SELECT cursor FROM sync WHERE source=?',(source,)).fetchone()
        cursor=row[0] if row else 0
        page=self.world.adapter(source).list_changes(cursor)
        results=[]
        for event in page['items']:
            results.append(self.process(event))
        return results
