"""Shared trusted-operator query boundary; this is not a browser login endpoint."""
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from contextvars import copy_context
from dataclasses import asdict

from .audit import Audit
from .confluence import ConfluenceReader, JsonTransport
from .jira import JiraReader
from .slack import SlackReader
from .drive import DriveReader
from .contracts import Decision, now
from .engine import Engine
from .store import canonical
from .deepseek import marked_synthetic_text


class DelegatedAuthority:
    def __init__(self, readers):
        self.readers = dict(readers)
        if not self.readers or set(self.readers) - {'confluence', 'jira', 'slack', 'drive'}:
            raise ValueError('Supported readers required')
        types = {'confluence': ConfluenceReader, 'jira': JiraReader, 'slack': SlackReader, 'drive': DriveReader}
        if any(not isinstance(reader, types[source]) for source, reader in self.readers.items()):
            raise ValueError('Reader source mapping mismatch')
        tenants = {r.tenant for r in self.readers.values()}
        if len(tenants) != 1:
            raise ValueError('Readers must belong to one tenant')
        self.tenant = tenants.pop()
        self.native_ids = {s: frozenset(r.page_ids if s == 'confluence' else r.native_ids)
                           for s, r in self.readers.items()}
        self.approved_synthetic_resource_ids = frozenset(
            source + ':' + native_id for source, ids in self.native_ids.items() for native_id in ids)
        self.users = {uid: {} for r in self.readers.values() for uid in r.delegations}
        self.resources, self.snapshots = {}, {}
        self.discovered_ids = {}

    @staticmethod
    def resource(content, tenant, previous=None):
        resource=dict(content, id=content['source'] + ':' + content['native_id'], tenant=tenant,
                      active=True, indexed_at=now(), links=[])
        if previous and DelegatedAuthority.same_content(previous,content):
            for key in ('indexed_at','observed_at','source_confirmed_at'):
                if key in previous:resource[key]=previous[key]
        return resource

    @staticmethod
    def same_content(resource, content):
        return all(resource.get(key) == content.get(key) for key in
                   ('source', 'native_id', 'version', 'title', 'text', 'locator',
                    'source_updated_at', 'source_url'))

    def read_current(self, actor, source, native_id, expected_version=None):
        reader=self.readers[source]
        dynamic=self.discovered_ids.get(actor.user_id,{}).get(source,frozenset())
        if source=='slack' and native_id in dynamic:
            parent=reader.messages.get(native_id)
            if parent is not None:
                root=native_id.split('/')[0]+'/'+parent
                decision,content=reader.read(actor,root)
                if decision.result!='allow' or content is None or not marked_synthetic_text(content['text'],source):
                    return Decision('unknown',now(),'discovered-thread-parent-unavailable',0),None
        return reader.read(actor,native_id,expected_version)

    def prepare(self, actor, store, audit, request_id):
        discovery=getattr(self,'discovery',None)
        published=discovery.query_snapshot(actor) if discovery else None
        if published is not None:
            self.snapshots[actor.user_id]={rid:version for rid,version in published.items()
                if (current:=store.get(rid)) and current['tenant']==actor.tenant
                and current['version']==version and current['active']}
            audit.append('source_changed',actor.user_id,request_id,
                         {'phase':'retrieval_snapshot_prefilter','resource_scope':'payment-service',
                          'native_reads':0,'is_current_authorization':False})
            return
        self.snapshots[actor.user_id] = {}
        for source, reader in sorted(self.readers.items()):
            dynamic = self.discovered_ids.get(actor.user_id, {}).get(source, frozenset())
            for native_id in sorted(self.native_ids[source] | dynamic):
                decision, content = self.read_current(actor,source,native_id)
                resource_id = source + ':' + native_id
                audit.append('authorization_decided', actor.user_id, request_id,
                             {'resource_id': resource_id, 'source': source,
                              'version': content['version'] if content else None,
                              'phase': 'source_refresh', 'resource_scope': 'payment-service',
                              'source_mode': 'live_api' if isinstance(reader.transport, JsonTransport)
                                             else 'mock_http', **asdict(decision)})
                if decision.result != 'allow' or content is None:
                    continue
                if native_id in dynamic:
                    if not marked_synthetic_text(content['text'],source):
                        continue
                if content['source'] != source or content['native_id'] != native_id:
                    raise ValueError('Reader content mapping mismatch')
                current=store.get(resource_id)
                if (current and source in ('confluence','drive') and content['version']<current['version']):
                    raise ValueError('Source version regressed')
                resource = self.resource(content, actor.tenant, current)
                with store.transaction() as db:
                    existing = db.execute('SELECT body FROM versions WHERE id=? AND version=?',
                                          (resource_id, resource['version'])).fetchone()
                    if existing and not self.same_content(json.loads(existing[0]), content):
                        raise ValueError('Content version collision')
                    db.execute('INSERT INTO resources VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
                               'version=excluded.version,active=excluded.active,body=excluded.body',
                               (resource_id, resource['version'], 1, canonical(resource)))
                    db.execute('INSERT OR IGNORE INTO versions VALUES(?,?,?)',
                               (resource_id, resource['version'], canonical(resource)))
                self.resources[resource_id] = resource
                self.snapshots[actor.user_id][resource_id] = resource['version']

    def prefilter(self, actor, resource):
        return (actor.tenant == self.tenant
                and self.snapshots.get(actor.user_id, {}).get(resource['id']) == resource['version'])

    def adapter(self, source):
        if source not in self.readers:
            raise ValueError('Unconfigured source')
        return self

    def _checked_read(self, actor, resource, reader, dynamic):
        source,native_id=resource['source'],resource['native_id']
        if reader is None or native_id not in self.native_ids[source] | dynamic:
            return Decision('unknown',now(),'delegated-pilot-unmapped',0),None
        if source=='slack' and native_id in dynamic:
            parent=reader.messages.get(native_id)
            if parent is not None:
                root=native_id.split('/')[0]+'/'+parent
                decision,content=reader.read(actor,root)
                if decision.result!='allow' or content is None or not marked_synthetic_text(content['text'],source):
                    return Decision('unknown',now(),'discovered-thread-parent-unavailable',0),None
        decision,content=reader.read(actor,native_id,resource['version'])
        if decision.result=='allow' and (content is None or not self.same_content(resource,content)
                or (native_id in dynamic and not marked_synthetic_text(content['text'],source))):
            return Decision('deny',now(),source+'-content-changed',0),None
        return decision,content

    def check_read(self, actor, resource_id):
        resource=self.resources.get(resource_id)
        if not resource or actor.tenant!=self.tenant:
            return Decision('unknown',now(),'delegated-pilot-unmapped',0)
        source=resource['source']
        decision,content=self._checked_read(actor,resource,self.readers.get(source),
            self.discovered_ids.get(actor.user_id,{}).get(source,frozenset()))
        if decision.result=='allow':self.resources[resource_id]=self.resource(content,actor.tenant,resource)
        return decision

    def check_many(self, actor, resources, *, phase):
        """One serial lane per source, at most four; caller holds pilot.lock.

        Workers only read request-local mappings/content. All mutable authority
        updates and ordered audit writes remain on the requesting thread.
        No cached allow, retry, smaller evidence set or within-source fanout.
        """
        discovery=getattr(self,'discovery',None)
        if not (discovery and discovery.bounded_queries and discovery.background_started
                and actor==discovery.actor):
            return [self.check_read(actor,r['id']) for r in resources]
        groups={}
        for index,r in enumerate(resources):
            resource=dict(self.resources[r['id']])
            source=resource['source']
            groups.setdefault(source,[]).append((index,resource))
        readers=dict(self.readers)
        dynamic=dict(self.discovered_ids.get(actor.user_id,{}))
        def lane(source,items):
            results=[];unavailable=False
            for i,r in items:
                if unavailable:
                    decision,content=Decision('unknown',now(),'source-lane-not-attempted',0),None
                else:
                    try:decision,content=self._checked_read(actor,r,readers[source],dynamic.get(source,frozenset()))
                    except Exception:
                        decision,content=Decision('unknown',now(),'source-lane-unavailable',0),None
                # Unknown (including rate limiting) ends this lane, never retries
                # or proceeds to more objects after the source becomes unavailable.
                unavailable=decision.result=='unknown'
                results.append((i,r,decision,content))
            return results
        results=[]
        with ThreadPoolExecutor(max_workers=min(4,len(groups)) or 1) as pool:
            futures=[pool.submit(copy_context().run,lane,source,items) for source,items in groups.items()]
            for future in futures:results.extend(future.result())
        ordered=sorted(results,key=lambda item:item[0]);decisions=[]
        for _,resource,decision,content in ordered:
            if decision.result=='allow':
                self.resources[resource['id']]=self.resource(content,actor.tenant,resource)
            decisions.append(decision)
        return decisions


class DelegatedQueryPilot:
    def __init__(self, readers, store, *, live=False):
        if not live and any(isinstance(r.transport, JsonTransport) for r in readers.values()):
            raise ValueError('Live transport requires explicit live mode')
        self.lock = threading.RLock()
        self.authority = DelegatedAuthority(readers)
        self.authority.resources = {r['id']: r for r in store.resources()
                                    if r.get('tenant') == self.authority.tenant
                                    and r.get('source') in self.authority.native_ids
                                    and r.get('native_id') in self.authority.native_ids[r['source']]}
        self.audit = Audit(store)
        transports = {isinstance(r.transport, JsonTransport) for r in readers.values()}
        kind = 'mixed_api' if len(transports) > 1 else 'live_api' if True in transports else 'mock_http'
        mode = '_'.join(sorted(readers)) + '_' + kind + '_fake_model'
        self.engine = Engine(store, self.authority, self.audit,
                             tenant=self.authority.tenant, mode=mode)

    def query(self, actor, question, history_id=None):
        with self.lock:
            return self.engine.query(actor, question, history_id)

    def evidence(self, actor, evidence_id):
        with self.lock:
            return self.engine.evidence(actor, evidence_id)

    def history(self, actor, request_id=None):
        with self.lock:
            return self.engine.safe_history(actor, request_id)
