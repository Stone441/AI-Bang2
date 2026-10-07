"""AUTH-017 fixed-container discovery. Trusted operator only; source APIs read-only."""
import copy
import json
import re
import threading
import time
import uuid
from urllib.parse import urlencode, urlsplit, parse_qs

from .confluence import JsonTransport, SourceUnavailable, SourceRateLimited
from .contracts import Actor, now
from .deepseek import marked_synthetic_text
from .drive import BASE, ID
from .slack import TS
from .store import canonical

AUTH017 = {'confluence':'131227', 'jira':'10001', 'slack':'C0C6R70SGG4',
           'drive':'1EMYjaNhzBFQ3TXHC6ukEwN6otVIIeOEv'}
SLACK_TEAM = 'T0C6FQ246TF'
SLACK_OLDEST = '1791142152.858189'


class DiscoveryFailure(SourceUnavailable):
    def __init__(self, code='discovery_unavailable', retry_after=0):
        self.code, self.retry_after = code, retry_after


def token(value):
    if not isinstance(value,str) or len(value)>2048 or any(ord(c)<32 for c in value):
        raise DiscoveryFailure('invalid_cursor')
    return value


def candidate_label(source, name):
    if not isinstance(name,str):return False
    return (name.startswith('[SYNTHETIC]') or (source=='jira'
            and re.search(r'(?:^|\s)\[SYNTHETIC ONLY\]$',name) is not None))


class NativeCounter:
    """Count actual adapter transport attempts without retaining URL/auth/body."""
    def __init__(self, transport, stop_event):
        self.transport=transport;self.requests=0;self.stop_event=stop_event

    def get(self, *args):
        if self.stop_event.is_set():raise DiscoveryFailure('stopped')
        self.requests+=1
        return self.transport.get(*args)

    def media(self, *args):
        if self.stop_event.is_set():raise DiscoveryFailure('stopped')
        self.requests+=1
        return self.transport.media(*args)


class ContainerDiscovery:
    def __init__(self, pilot, actor, *, scope=None, clock=time.monotonic, bounded_queries=False):
        if type(bounded_queries) is not bool:raise ValueError('Trusted boolean query policy required')
        self.bounded_queries=bounded_queries
        self.pilot, self.actor, self.clock = pilot, actor, clock
        self.scope = dict(AUTH017 if scope is None else scope)
        a = pilot.authority
        if self.scope != AUTH017 or actor != Actor('eng_b',a.tenant) or set(a.readers)!=set(AUTH017):
            raise ValueError('AUTH-017 exact eng_b four-source scope required')
        c,j,s,d=(a.readers[k] for k in ('confluence','jira','slack','drive'))
        if (c.space_ids != frozenset([self.scope['confluence']]) or c.discovery_only
                or j.project_ids != frozenset([self.scope['jira']]) or j.discovery_only
                or any(not key.startswith('KAN-') for key in j.issues.values())
                or s.team_id != SLACK_TEAM or s.channels != {self.scope['slack']:'private'}
                or any(native.split('/')[1]<SLACK_OLDEST for native in s.native_ids)
                or set(d.files.values()) != {self.scope['drive']}
                or any(actor.user_id not in r.delegations for r in a.readers.values())):
            raise ValueError('Existing mappings must fit exact approved containers')
        self.base_readers = dict(a.readers)
        self.stop_event=threading.Event(); self.thread=None
        self.failures={s:0 for s in self.scope}; self.due={s:0 for s in self.scope}
        self.offsets={s:0 for s in self.scope}
        self.last={}
        self.background_started=False
        self.published_at={};self.published_versions={}
        a.discovery=self
        with pilot.engine.store.transaction() as db:
            db.execute('CREATE TABLE IF NOT EXISTS discovery_catalog (actor TEXT, source TEXT, native_id TEXT, mapping TEXT NOT NULL, PRIMARY KEY(actor,source,native_id))')
            db.execute('CREATE TABLE IF NOT EXISTS discovery_state (actor TEXT, source TEXT, body TEXT NOT NULL, PRIMARY KEY(actor,source))')

    def _get(self, reader, url, credential):
        try:
            status,data=reader.transport.get(url,credential.authorization)
        except SourceRateLimited as e:
            raise DiscoveryFailure('rate_limited',e.retry_after) from None
        if status==429: raise DiscoveryFailure('rate_limited')
        if status!=200 or not isinstance(data,dict): raise DiscoveryFailure()
        if isinstance(reader, type(self.base_readers['slack'])):
            if data.get('ok') is not True:
                codes={'ratelimited':'rate_limited','missing_scope':'missing_scope',
                       'invalid_auth':'identity_unavailable','not_in_channel':'access_unavailable',
                       'channel_not_found':'access_unavailable'}
                raise DiscoveryFailure(codes.get(data.get('error'),'discovery_unavailable'))
        return data

    def _credential(self, source, reader):
        if source=='confluence': return reader._credential(self.actor,sorted(reader.page_ids)[0])
        return reader._credential(self.actor)

    def _known(self, source):
        r=self.base_readers[source]
        if source=='confluence': result={i:None for i in r.page_ids}
        elif source=='jira': result={i:k for i,k in r.issues.items()}
        elif source=='slack': result=dict(r.messages)
        else: result=dict(r.files)
        for row in self.pilot.engine.store.db.execute(
                'SELECT native_id,mapping FROM discovery_catalog WHERE actor=? AND source=?',
                (self.actor.user_id,source)):
            result[row[0]]=json.loads(row[1])
        return result

    def _reader(self, source, mappings, transport=None):
        r=copy.copy(self.base_readers[source])
        if transport is not None:r.transport=transport
        if source=='confluence':
            if any(not i.isdecimal() or m is not None for i,m in mappings.items()): raise DiscoveryFailure('invalid_mapping')
            r.page_ids=frozenset(mappings)
        elif source=='jira':
            if any(not i.isdecimal() or not re.fullmatch(r'KAN-[1-9][0-9]*',k) for i,k in mappings.items()): raise DiscoveryFailure('invalid_mapping')
            r.issues=dict(mappings)
            r.native_ids=frozenset(mappings)|frozenset(p+'/comment/'+c for c,p in r.comment_ids.items())
        elif source=='slack':
            for native,parent in mappings.items():
                parts=native.split('/')
                if (len(parts)!=2 or parts[0]!=self.scope[source] or not re.fullmatch(TS,parts[1])
                        or parts[1]<SLACK_OLDEST or (parent is not None and
                        (not isinstance(parent,str) or not re.fullmatch(TS,parent) or parent>=parts[1]
                         or mappings.get(parts[0]+'/'+parent,'missing') is not None))):
                    raise DiscoveryFailure('invalid_mapping')
            r.messages=dict(mappings);r.native_ids=frozenset(mappings)
        else:
            if any(not re.fullmatch(ID,i) or parent!=self.scope[source] for i,parent in mappings.items()): raise DiscoveryFailure('invalid_mapping')
            r.files=dict(mappings);r.native_ids=frozenset(mappings)
        return r

    def _pages(self, source, reader, credential, budget, *, parent=None):
        cursor='';seen=set()
        while budget[0]<10:
            size=15 if source=='slack' else 50
            if source=='confluence':
                endpoint='/wiki/api/v2/spaces/'+self.scope[source]+'/pages'
                params={'limit':size,'status':'current'}
                if cursor:params['cursor']=cursor
                url=reader.api_base+endpoint+'?'+urlencode(params)
            elif source=='jira':
                params={'jql':'project = 10001 ORDER BY id ASC','fields':'summary,updated,project','maxResults':size}
                if cursor:params['nextPageToken']=cursor
                url=reader.api_base+'/rest/api/3/search/jql?'+urlencode(params)
            elif source=='drive':
                params={'q':"'"+self.scope[source]+"' in parents and trashed = false",'pageSize':size,
                        'corpora':'user','spaces':'drive','fields':'nextPageToken,incompleteSearch,files(id,name,mimeType,parents,trashed,modifiedTime)'}
                if cursor:params['pageToken']=cursor
                url=BASE+'/files?'+urlencode(params)
            else:
                params={'channel':self.scope[source],'oldest':SLACK_OLDEST,'inclusive':'true','limit':size}
                if parent:params['ts']=parent
                if cursor:params['cursor']=cursor
                url='https://slack.com/api/conversations.'+('replies' if parent else 'history')+'?'+urlencode(params)
            budget[0]+=1
            data=self._get(reader,url,credential)
            key={'confluence':'results','jira':'issues','drive':'files','slack':'messages'}[source]
            rows=data.get(key)
            if not isinstance(rows,list) or len(rows)>size or any(not isinstance(row,dict) for row in rows): raise DiscoveryFailure('invalid_page')
            if source=='confluence':
                link=data.get('_links',{}).get('next','')
                cursor=''
                if link:
                    parsed=urlsplit(link);query=parse_qs(parsed.query,strict_parsing=True)
                    expected={endpoint,urlsplit(reader.api_base).path+endpoint}
                    if (parsed.scheme not in ('','https') or (parsed.netloc and parsed.netloc!=urlsplit(reader.api_base).netloc)
                            or parsed.path not in expected or parsed.fragment
                            or set(query)-{'cursor','limit','status'} or len(query.get('cursor',[]))!=1
                            or ('limit' in query and query['limit']!=[str(size)])
                            or ('status' in query and query['status']!=['current'])):raise DiscoveryFailure('invalid_cursor')
                    cursor=token(query['cursor'][0])
            elif source=='jira':
                if type(data.get('isLast')) is not bool:raise DiscoveryFailure('invalid_page')
                cursor=token(data.get('nextPageToken',''))
                if data['isLast']==bool(cursor):raise DiscoveryFailure('invalid_cursor')
            elif source=='drive':
                if data.get('incompleteSearch',False) is not False:raise DiscoveryFailure('incomplete_search')
                cursor=token(data.get('nextPageToken',''))
            else:
                cursor=token(data.get('response_metadata',{}).get('next_cursor',''))
                if type(data.get('has_more',False)) is not bool or (data.get('has_more') and not cursor):raise DiscoveryFailure('invalid_cursor')
            yield rows
            if not cursor:return
            if cursor in seen:raise DiscoveryFailure('cursor_loop')
            seen.add(cursor)
        raise DiscoveryFailure('page_backlog')

    def _list(self, source, reader, credential, mappings, budget):
        if source=='slack':
            data=self._get(reader,'https://slack.com/api/conversations.info?'+urlencode(
                {'channel':self.scope[source],'include_num_members':'false'}),credential)
            c=data['channel']
            if (c.get('id')!=self.scope[source] or c.get('context_team_id')!=SLACK_TEAM
                    or c.get('is_private') is not True or c.get('is_member') is not True
                    or any(c.get(k) is not False for k in ('is_im','is_mpim','is_shared','is_ext_shared','is_pending_ext_shared'))):raise DiscoveryFailure('channel_unavailable')
        roots=[];ids=set()
        for rows in self._pages(source,reader,credential,budget):
            for row in rows:
                if source=='confluence':
                    native=row['id'];name=row['title'];mapping=None
                    if not isinstance(native,str) or not native.isdecimal() or row.get('spaceId')!=self.scope[source] or row.get('status')!='current':raise DiscoveryFailure('container_mismatch')
                elif source=='jira':
                    native=row['id'];name=row['fields']['summary'];mapping=row['key']
                    if (not isinstance(native,str) or not native.isdecimal() or not isinstance(mapping,str)
                            or not re.fullmatch(r'KAN-[1-9][0-9]*',mapping)
                            or row['fields']['project'].get('id')!=self.scope[source]):raise DiscoveryFailure('container_mismatch')
                elif source=='drive':
                    native=row['id'];name=row['name'];mapping=self.scope[source]
                    if not isinstance(native,str) or not re.fullmatch(ID,native) or row.get('parents')!=[mapping] or row.get('trashed') is not False:raise DiscoveryFailure('container_mismatch')
                    if row.get('mimeType')!='text/plain':continue
                else:
                    ts=row['ts'];name=row.get('text');mapping=None
                    if not isinstance(ts,str) or not re.fullmatch(TS,ts) or ts<SLACK_OLDEST or row.get('team',SLACK_TEAM)!=SLACK_TEAM:raise DiscoveryFailure('container_mismatch')
                    if row.get('thread_ts') not in (None,ts):continue
                    native=self.scope[source]+'/'+ts
                    if row.get('subtype') or row.get('files') or row.get('attachments') or row.get('bot_id'):continue
                if native in ids:raise DiscoveryFailure('duplicate_object')
                ids.add(native)
                if not isinstance(name,str):raise DiscoveryFailure('invalid_metadata')
                if native in mappings or candidate_label(source,name):
                    mappings[native]=mapping
                    if source=='slack' and row.get('reply_count',0):roots.append(native)
        # Thread list reads follow exact current parent read and synthetic validation.
        for native in roots:
            rootreader=self._reader(source,mappings,reader.transport)
            if budget[1]>=100:raise DiscoveryFailure('object_backlog')
            budget[1]+=1
            decision,content=rootreader.read(self.actor,native)
            if decision.result!='allow' or content is None or not marked_synthetic_text(content['text'],source):raise DiscoveryFailure('parent_unavailable')
            parent=native.split('/')[1]
            for rows in self._pages(source,reader,credential,budget,parent=parent):
                for row in rows:
                    ts=row['ts']
                    if ts==parent:continue
                    if (not isinstance(ts,str) or not re.fullmatch(TS,ts) or ts<=parent or row.get('thread_ts')!=parent
                            or row.get('team',SLACK_TEAM)!=SLACK_TEAM):raise DiscoveryFailure('thread_mismatch')
                    if isinstance(row.get('text'),str) and row['text'].startswith('[SYNTHETIC]'):
                        mappings[self.scope[source]+'/'+ts]=parent
        return mappings

    def _disable(self, source, native):
        a=self.pilot.authority;rid=source+':'+native
        with self.pilot.engine.store.transaction() as db:
            db.execute('UPDATE resources SET active=0 WHERE id=?',(rid,))
        if rid in a.resources:a.resources[rid]=dict(a.resources[rid],active=False)
        for snapshot in a.snapshots.values():snapshot.pop(rid,None)

    def run_once(self):
        with self.pilot.lock:
            for source in sorted(self.scope):
                if self.stop_event.is_set():break
                if self.clock()<self.due[source]:continue
                self._cycle(source)
            return copy.deepcopy(self.last)

    def _cycle(self, source):
        started=self.clock();observed=now();budget=[0,0];staged={};resolved={};reads=0
        status='complete';reason=None;retry_after=0
        counter=NativeCounter(self.base_readers[source].transport,self.stop_event)
        a=self.pilot.authority;store=self.pilot.engine.store;rid=uuid.uuid4().hex
        try:
            reader=copy.copy(self.base_readers[source]);reader.transport=counter
            credential=self._credential(source,reader)
            mappings=self._known(source);previously_known=set(mappings)
            self._list(source,reader,credential,mappings,budget)
            listed=self.clock()
            expanded=self._reader(source,mappings,counter)
            keys=sorted(mappings)
            if keys:
                offset=self.offsets[source]%len(keys);keys=keys[offset:]+keys[:offset]
            limit=100-budget[1]
            if len(keys)>limit:status='backlog';reason='object_backlog'
            self.offsets[source]+=min(limit,len(keys))
            for native in keys[:limit]:
                parent=mappings[native] if source=='slack' else None
                if parent is not None:
                    if budget[1]>=99:status='backlog';reason='object_backlog';break
                    budget[1]+=1
                    root=native.split('/')[0]+'/'+parent
                    decision,original=expanded.read(self.actor,root)
                    if decision.result!='allow' or original is None or not marked_synthetic_text(original['text'],source):
                        self._disable(source,native)
                        if decision.result=='unknown':raise DiscoveryFailure('parent_unavailable')
                        if native in previously_known:resolved[native]=mappings[native]
                        continue
                if budget[1]>=100:status='backlog';reason='object_backlog';break
                reads+=1;budget[1]+=1;decision,content=expanded.read(self.actor,native)
                if decision.result!='allow' or content is None:
                    self._disable(source,native)
                    if decision.result=='unknown':raise DiscoveryFailure('native_read_unknown')
                    if native in previously_known:resolved[native]=mappings[native]
                    continue
                if (content['source']!=source or content['native_id']!=native
                        or not marked_synthetic_text(content['text'],source)
                        or (native not in previously_known and source in ('confluence','jira','drive')
                            and not candidate_label(source,content['title']))):
                    self._disable(source,native)
                    if native in previously_known:resolved[native]=mappings[native]
                    continue
                resource=a.resource(content,self.actor.tenant)
                resource['observed_at']=observed;resource['source_confirmed_at']=content['source_updated_at']
                current=store.get(resource['id'])
                if current and source in ('confluence','drive') and content['version']<current['version']:
                    raise DiscoveryFailure('version_regressed')
                if current and a.same_content(current,content):
                    resource['indexed_at']=current['indexed_at']
                    resource['observed_at']=current.get('observed_at',observed)
                staged[native]=resource;resolved[native]=mappings[native]
            fetched=self.clock()
            # Persist source publication intent before making objects queryable.
            self.pilot.audit.append('source_changed',self.actor.user_id,rid,
                {'source':source,'resource_scope':'payment-service','phase':'discovery_publication_prepared',
                 'observed_at':observed,'objects':[r['id'] for r in staged.values()]})
            # All changes/catalog become current together; errors roll back publication.
            with store.transaction() as db:
                for native,resource in staged.items():
                    old=db.execute('SELECT body FROM versions WHERE id=? AND version=?',(resource['id'],resource['version'])).fetchone()
                    if old and not a.same_content(json.loads(old[0]),resource):raise DiscoveryFailure('version_collision')
                    db.execute('INSERT INTO resources VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET version=excluded.version,active=excluded.active,body=excluded.body',
                               (resource['id'],resource['version'],1,canonical(resource)))
                    db.execute('INSERT OR IGNORE INTO versions VALUES(?,?,?)',(resource['id'],resource['version'],canonical(resource)))
                for native,mapping in resolved.items():
                    db.execute('INSERT INTO discovery_catalog VALUES(?,?,?,?) ON CONFLICT(actor,source,native_id) DO UPDATE SET mapping=excluded.mapping',
                               (self.actor.user_id,source,native,canonical(mapping)))
            # Rebuild expanded reader from committed IDs only; unvalidated candidates never grant read access.
            committed=self._known(source);a.readers[source]=self._reader(source,committed)
            dynamic=frozenset(committed)-a.native_ids[source]
            a.discovered_ids.setdefault(self.actor.user_id,{})[source]=dynamic
            a.approved_synthetic_resource_ids=frozenset(a.approved_synthetic_resource_ids)|frozenset(source+':'+i for i in staged)
            for native,resource in staged.items():a.resources[resource['id']]=resource
            if status=='complete':
                self.published_at[source]=self.clock()
                self.published_versions[source]={r['id']:r['version'] for r in staged.values()}
            self.failures[source]=0
            timing={'listing_seconds':listed-started,'read_seconds':fetched-listed,'publish_seconds':self.clock()-fetched}
        except Exception as error:
            status='failed';reason=error.code if isinstance(error,DiscoveryFailure) else 'discovery_unavailable'
            retry_after=error.retry_after if isinstance(error,(DiscoveryFailure,SourceRateLimited)) else 0
            self.failures[source]+=1;timing={}
        delay=max(60,min(3600,60*2**min(self.failures[source],6)),retry_after)
        self.due[source]=self.clock()+delay
        prior=store.db.execute('SELECT body FROM discovery_state WHERE actor=? AND source=?',(self.actor.user_id,source)).fetchone()
        checkpoint=json.loads(prior[0]).get('last_successful_checkpoint_at') if prior else None
        report={'source':source,'actor':self.actor.user_id,'scope':self.scope[source],'status':status,'reason':reason,
                'observed_at':observed,'indexed_at':now() if status!='failed' else None,'answerable_at':None,
                'last_successful_checkpoint_at':now() if status=='complete' else checkpoint,
                'list_pages':budget[0],'exact_read_attempts':budget[1],'native_request_attempts':counter.requests,'published_objects':len(staged) if status!='failed' else 0,
                'elapsed_seconds':self.clock()-started,'retry_after_seconds':delay,**timing}
        self.pilot.audit.append('source_changed',self.actor.user_id,rid,dict(report,resource_scope='payment-service',mode='live_api' if isinstance(self.base_readers[source].transport,JsonTransport) else 'mock_http'))
        with store.transaction() as db:
            db.execute('INSERT INTO discovery_state VALUES(?,?,?) ON CONFLICT(actor,source) DO UPDATE SET body=excluded.body',
                       (self.actor.user_id,source,canonical(report)))
        self.last[source]=report

    def start(self):
        if self.thread is not None:raise ValueError('Discovery already started')
        self.background_started=True
        def poll():
            while not self.stop_event.is_set():
                try:self.run_once()
                except Exception:self.stop_event.set()  # Audit/store failure stops unattended polling.
                self.stop_event.wait(1)
        self.thread=threading.Thread(target=poll,name='auth017-discovery',daemon=True);self.thread.start()

    def query_snapshot(self, actor):
        """Local candidate eligibility only. Final native checks remain mandatory.

        A stopped/failed/backlogged/expired worker cannot silently imply a complete
        answer. No DB checkpoint alone restores this process-local snapshot.
        """
        if not self.bounded_queries or actor!=self.actor or not self.background_started:return None
        if (self.stop_event.is_set() or self.thread is None or not self.thread.is_alive()
                or any(self.last.get(s,{}).get('status')!='complete'
                       or s not in self.published_at or self.clock()-self.published_at[s]>120
                       for s in self.scope)):
            raise SourceUnavailable('Current source coverage unavailable; retry later')
        return {rid:version for source in self.scope
                for rid,version in self.published_versions[source].items()}

    def close(self):
        self.stop_event.set()
        if self.thread is not None:self.thread.join()
