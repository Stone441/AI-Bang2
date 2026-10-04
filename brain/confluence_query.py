"""Operator pilot connecting delegated source reads to the shared query Engine.

No HTTP login route: Actor is supplied by a trusted local operator, not a browser.
Only allowlisted synthetic pages and the local extractive model are supported.
"""
import threading
from dataclasses import asdict

from .audit import Audit
from .confluence import JsonTransport
from .contracts import Decision, now
from .engine import Engine
from .store import canonical


class ConfluenceAuthority:
    def __init__(self, reader):
        self.reader=reader
        self.users={uid: {} for uid in reader.delegations}
        self.resources={}
        self.snapshots={}

    @staticmethod
    def resource(content, tenant):
        return dict(content, id='confluence:'+content['native_id'], tenant=tenant,
                    active=True, indexed_at=now(), links=[])

    def prepare(self, actor, store, audit, request_id):
        # Remove the previous positive snapshot before touching the source.
        self.snapshots[actor.user_id]={}
        for page_id in sorted(self.reader.page_ids):
            decision,content=self.reader.read(actor,page_id)
            resource_id='confluence:'+page_id
            audit.append('authorization_decided',actor.user_id,request_id,
                         {'resource_id':resource_id,'source':'confluence',
                          'version':content['version'] if content else None,
                          'phase':'source_refresh','resource_scope':'payment-service',
                          **asdict(decision)})
            if decision.result!='allow' or content is None:
                continue
            resource=self.resource(content,actor.tenant)
            with store.transaction() as db:
                db.execute('INSERT INTO resources VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
                           'version=excluded.version,active=excluded.active,body=excluded.body',
                           (resource_id,resource['version'],1,canonical(resource)))
                db.execute('INSERT OR IGNORE INTO versions VALUES(?,?,?)',
                           (resource_id,resource['version'],canonical(resource)))
            self.resources[resource_id]=resource
            self.snapshots[actor.user_id][resource_id]=resource['version']

    def prefilter(self, actor, resource):
        return (actor.tenant==self.reader.tenant
                and self.snapshots.get(actor.user_id,{}).get(resource['id'])==resource['version'])

    def adapter(self, source):
        if source!='confluence':
            raise ValueError('Confluence-only pilot')
        return self

    def check_read(self, actor, resource_id):
        resource=self.resources.get(resource_id)
        if (resource is None or actor.tenant!=self.reader.tenant
                or not resource_id.startswith('confluence:')):
            return Decision('unknown',now(),'confluence-pilot-unmapped',0)
        decision,content=self.reader.read(actor,resource['native_id'],resource['version'])
        # No cached allow: every call must read with this employee's credentials.
        if decision.result=='allow' and content is not None:
            self.resources[resource_id]=self.resource(content,actor.tenant)
        return decision


class ConfluenceQueryPilot:
    def __init__(self, reader, store, *, live=False):
        if not live and isinstance(reader.transport,JsonTransport):
            raise ValueError('Live transport requires explicit live mode')
        self.lock=threading.RLock()
        self.authority=ConfluenceAuthority(reader)
        self.authority.resources={r['id']:r for r in store.resources()
                                  if r.get('tenant')==reader.tenant
                                  and r.get('source')=='confluence'
                                  and r.get('native_id') in reader.page_ids}
        self.audit=Audit(store)
        self.engine=Engine(store,self.authority,self.audit,tenant=reader.tenant,
                           mode='confluence_live_api_fake_model' if live else 'confluence_mock_http_fake_model')

    def query(self, actor, question, history_id=None):
        with self.lock:
            return self.engine.query(actor,question,history_id)

    def evidence(self, actor, evidence_id):
        with self.lock:
            return self.engine.evidence(actor,evidence_id)

    def history(self, actor, request_id=None):
        with self.lock:
            return self.engine.safe_history(actor,request_id)
