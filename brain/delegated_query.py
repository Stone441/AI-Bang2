"""Shared trusted-operator query boundary; this is not a browser login endpoint."""
import json
import threading
from dataclasses import asdict

from .audit import Audit
from .confluence import ConfluenceReader, JsonTransport
from .jira import JiraReader
from .slack import SlackReader
from .drive import DriveReader
from .contracts import Decision, now
from .engine import Engine
from .store import canonical


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
        self.users = {uid: {} for r in self.readers.values() for uid in r.delegations}
        self.resources, self.snapshots = {}, {}

    @staticmethod
    def resource(content, tenant):
        return dict(content, id=content['source'] + ':' + content['native_id'], tenant=tenant,
                    active=True, indexed_at=now(), links=[])

    @staticmethod
    def same_content(resource, content):
        return all(resource.get(key) == content.get(key) for key in
                   ('source', 'native_id', 'version', 'title', 'text', 'locator',
                    'source_updated_at', 'source_url'))

    def prepare(self, actor, store, audit, request_id):
        self.snapshots[actor.user_id] = {}
        for source, reader in sorted(self.readers.items()):
            for native_id in sorted(self.native_ids[source]):
                decision, content = reader.read(actor, native_id)
                resource_id = source + ':' + native_id
                audit.append('authorization_decided', actor.user_id, request_id,
                             {'resource_id': resource_id, 'source': source,
                              'version': content['version'] if content else None,
                              'phase': 'source_refresh', 'resource_scope': 'payment-service',
                              'source_mode': 'live_api' if isinstance(reader.transport, JsonTransport)
                                             else 'mock_http', **asdict(decision)})
                if decision.result != 'allow' or content is None:
                    continue
                if content['source'] != source or content['native_id'] != native_id:
                    raise ValueError('Reader content mapping mismatch')
                resource = self.resource(content, actor.tenant)
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

    def check_read(self, actor, resource_id):
        resource = self.resources.get(resource_id)
        if not resource or actor.tenant != self.tenant:
            return Decision('unknown', now(), 'delegated-pilot-unmapped', 0)
        source, native_id = resource['source'], resource['native_id']
        reader = self.readers.get(source)
        if reader is None or native_id not in self.native_ids[source]:
            return Decision('unknown', now(), 'delegated-pilot-unmapped', 0)
        decision, content = reader.read(actor, native_id, resource['version'])
        if decision.result == 'allow':
            if content is None or not self.same_content(resource, content):
                return Decision('deny', now(), source + '-content-changed', 0)
            self.resources[resource_id] = self.resource(content, actor.tenant)
        return decision


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
