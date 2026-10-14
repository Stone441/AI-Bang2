"""Request-local delegated query state. Explicit context required through send.

Enabled only by the explicit isolated3 trial launcher option. No native authorization result
is cached. Candidate snapshots are eligibility only. Shared publications are
fenced at model dispatch and through final response delivery.
"""
import copy
from contextlib import contextmanager, ExitStack
from contextvars import ContextVar
import threading

from .confluence import SourceUnavailable
from .delegated_query import DelegatedAuthority
from .engine import Engine, VersionChanged
from .timing import span, authorization_scope, acquire


class RequestStore:
    def __init__(self, store, authority):
        self.original=store;self.authority=authority

    def resources(self):
        return copy.deepcopy(self.authority.catalog)

    def __getattr__(self,name):
        return getattr(self.original,name)


class RequestAuthority(DelegatedAuthority):
    def __init__(self, root, store, actor):
        self.root=root;self.store=store;self.actor=actor
        self.state_lock=threading.RLock()
        self._fence=None
        self._fence_phase=None
        self.capture()

    def capture(self):
        with self.root.state_lock,self.store.lock:
            discovery=getattr(self.root,'discovery',None)
            if not discovery or discovery.actor!=self.actor:
                raise SourceUnavailable('Request isolation requires current delegated coverage')
            published=discovery.query_snapshot(self.actor)
            if published is None:
                raise SourceUnavailable('Request isolation requires current delegated coverage')
            self.discovery=discovery
            self.tenant=self.root.tenant;self.users=copy.deepcopy(self.root.users)
            self.native_ids=dict(self.root.native_ids)
            self.readers=dict(self.root.readers)
            self.discovered_ids=copy.deepcopy(self.root.discovered_ids)
            self.read_concurrency=self.root.read_concurrency
            self.approved_synthetic_resource_ids=self.root.approved_synthetic_resource_ids
            self.resources=copy.deepcopy(self.root.resources)
            self.publication_epochs=dict(self.root.publication_epochs)
            self.catalog=self.store.resources()
            self.eligible=dict(published)
            self.snapshots={}

    def _actor(self,actor):
        if actor!=self.actor:raise PermissionError('Unavailable')

    def prepare(self,actor,store,audit,request_id):
        self._actor(actor)
        with self.root.state_lock,self.store.lock:
            self.discovery.query_snapshot(actor)  # Never inherit unhealthy coverage.
            self.snapshots[actor.user_id]={r['id']:r['version'] for r in self.catalog
                if r['tenant']==actor.tenant and r['active'] and self.eligible.get(r['id'])==r['version']}
        audit.append('source_changed',actor.user_id,request_id,
            {'phase':'retrieval_snapshot_prefilter','resource_scope':'payment-service',
             'native_reads':0,'is_current_authorization':False,'request_local':True})

    def _validate(self,resources):
        published=self.discovery.query_snapshot(self.actor)
        changed=[]
        for old in resources:
            current=self.root.resources.get(old['id']);stored=self.store.get(old['id'])
            if (not current or not stored or current.get('active') is not True
                    or current.get('tenant')!=self.actor.tenant):
                raise SourceUnavailable('Current source cannot be confirmed')
            if current['version']!=old['version'] or stored['version']!=old['version']:
                changed.append(old);continue
            if (self.root.publication_epochs.get(old['id'],0)!=self.publication_epochs.get(old['id'],0)
                    or not self.same_content(current,old) or not self.same_content(stored,old)):
                raise SourceUnavailable('Current source cannot be confirmed')
        if changed:raise VersionChanged(changed)
        if published!=self.eligible:
            # Newly published or removed candidate material could be relevant
            # counterevidence even when already selected documents are unchanged.
            raise SourceUnavailable('Current source coverage changed')

    def _validate_locked(self,resources):
        with self.root.state_lock,self.store.lock:self._validate(resources)

    def check_read(self,actor,resource_id):
        self._actor(actor)
        old=copy.deepcopy(self.resources[resource_id])
        self._validate_locked([old])
        decision=super().check_read(actor,resource_id)
        self._validate_locked([old])
        return decision

    def check_many(self,actor,resources,*,phase):
        if self._fence is not None and self._fence_phase=='model_dispatch' and phase=='review_dispatch':
            self.release_fence()  # Legacy source-review constructs locally before its sole call.
        self._actor(actor);self._validate_locked(resources)
        decisions=super().check_many(actor,resources,phase=phase)
        # Native I/O has finished. Hold the publication/store fences while the
        # engine validates immutable mappings and builds the outgoing request.
        # The model dispatch audit event releases the fence at the send boundary.
        if resources and phase in ('model_dispatch','review_dispatch','before_dispatch'):
            if self._fence is not None:raise RuntimeError('Previous publication fence not released')
            stack=ExitStack()
            try:
                stack.enter_context(self.root.state_lock)
                stack.enter_context(self.store.lock)
                self._validate(resources)
            except BaseException:
                stack.close();raise
            self._fence=stack
            self._fence_phase=phase
        else:self._validate_locked(resources)
        return decisions

    def model_event(self,event):
        if event=='model_dispatch_attempted':self.release_fence()

    def release_fence(self):
        if self._fence is not None:
            fence,self._fence=self._fence,None
            self._fence_phase=None
            fence.close()

    def recover_versions(self,actor,resources,store,audit,request_id):
        self._actor(actor);self.release_fence()
        # Keep the existing single pre-model recovery, including all original
        # native reads and publication checks. It is rare and remains serialized.
        with self.root.state_lock,self.store.lock:
            self.root.recover_versions(actor,resources,self.store,audit,request_id)
            self.capture()


class IsolatedQueries:
    def __init__(self,engine,*,maximum=3):
        if maximum!=3:raise ValueError('Only bounded three-query isolation supported')
        from .synthesis import (DeepSeekReviewAllSourcesModel,DeepSeekCompactSourceReviewModel,
            DeepSeekCoveredSourceReviewModel,DeepSeekWholeSourceReviewModel,DeepSeekStructuredSourceReviewModel)
        if type(engine.model) not in (DeepSeekReviewAllSourcesModel,DeepSeekCompactSourceReviewModel,
                DeepSeekCoveredSourceReviewModel,DeepSeekWholeSourceReviewModel,DeepSeekStructuredSourceReviewModel):
            raise ValueError('Request isolation requires an audited request-local reviewer')
        if not isinstance(engine.world,DelegatedAuthority):raise ValueError('Delegated authority required')
        self.engine=engine
        self.capacity=threading.BoundedSemaphore(maximum)
        self.context=ContextVar('isolated_query_scope',default=None)

    @contextmanager
    def request(self):
        if self.context.get() is not None:raise RuntimeError('Nested isolated request')
        with acquire(self.capacity):
            state={};token=self.context.set(state)
            try:yield
            finally:
                if 'authority' in state:state['authority'].release_fence()
                self.context.reset(token)

    def query(self,actor,*args,**kwargs):
        state=self.context.get()
        if state is None or state:
            raise RuntimeError('One query requires one explicit HTTP request scope')
        authority=RequestAuthority(self.engine.world,self.engine.store,actor)
        state['authority']=authority
        options={key:getattr(self.engine,key) for key in ('tenant','mode','retrieval_strategy',
            'query_expansion','evidence_on_model_rejection','source_review_dispatch','history_read_mode','window_strategy')}
        engine=IsolatedEngine(RequestStore(self.engine.store,authority),authority,
            self.engine.audit,self.engine.model,**options)
        engine.before_dispatch=self.engine.before_dispatch
        return engine.query(actor,*args,**kwargs)


class IsolatedEngine(Engine):
    # New bound methods must use the request authority, never copy a timing
    # closure bound to the shared prototype Engine.
    def checks(self,actor,resources,request_id,phase):
        with authorization_scope(phase),span('authorization'):
            return super().checks(actor,resources,request_id,phase)

    def check(self,actor,resource,request_id,phase):
        with authorization_scope(phase),span('authorization'):
            return super().check(actor,resource,request_id,phase)
