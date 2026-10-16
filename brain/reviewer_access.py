"""Password-account review of an explicitly shared synthetic source identity.

Viewer identity and effective native source identity are distinct. This does not
implement employee SSO or grant platform permissions. Native checks remain in
the original engine; local records scope history and previews to each viewer.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import threading
import time

from .contracts import Actor
from .server import App

_QUESTION_UNSET = object()


class ReviewAccounts:
    def __init__(self, path, tenant, allowed_roles):
        self.path = Path(path)
        self.tenant = tenant
        self.allowed_roles = frozenset(allowed_roles)
        self.lock = threading.RLock()
        self.failures = {}
        self.read()

    def read(self):
        if self.path.is_symlink():
            raise ValueError('Private account registry required')
        st = self.path.stat()
        if st.st_uid != os.getuid() or st.st_mode & 0o777 != 0o600:
            raise ValueError('Owned 0600 account registry required')
        body = json.loads(self.path.read_text())
        if (body.get('schema') != 1 or body.get('source_tenant') != self.tenant
                or body.get('purpose') != 'shared-synthetic-review' or not isinstance(body.get('accounts'), dict)):
            raise ValueError('Explicit shared synthetic identity required')
        policies = body.get('application_roles')
        if policies is not None:
            if not isinstance(policies,dict) or set(policies)!={'engineer','product','partner'}:
                raise ValueError('Explicit three-role application policy required')
            for role, rule in policies.items():
                if (not isinstance(rule,dict) or set(rule)!={'resource_ids'}
                        or (rule['resource_ids'] is None and role!='engineer')
                        or (rule['resource_ids'] is not None and (not isinstance(rule['resource_ids'],list)
                            or any(not isinstance(r,str) or not r for r in rule['resource_ids'])))):
                    raise ValueError('Exact resource policy required')
        login_names = set()
        for key, row in body['accounts'].items():
            if not isinstance(row, dict):
                raise ValueError('Invalid account registry')
            login_name = row.get('login_name', key)
            display_name = row.get('display_name', login_name)
            if (not isinstance(login_name, str) or not re.fullmatch(r'[a-z0-9_-]{1,48}', login_name)
                    or login_name in login_names or not isinstance(display_name, str)
                    or not 1 <= len(display_name) <= 80 or not display_name.isprintable()):
                raise ValueError('Unique login names and printable display names required')
            login_names.add(login_name)
            if policies is None and 'demo_role' in row:
                raise ValueError('Application role accounts require an explicit policy')
            if policies is not None and row.get('demo_role') not in policies:
                raise ValueError('Account requires an application demo role')
            if (not re.fullmatch(r'[a-z0-9_-]{1,48}', key) or not isinstance(row, dict)
                    or type(row.get('active')) is not bool or type(row.get('expires')) not in (int, float)
                    or row.get('source_actor') not in self.allowed_roles
                    or not re.fullmatch(r'[0-9a-f]{32}', row.get('salt', ''))
                    or not re.fullmatch(r'[0-9a-f]{64}', row.get('password_hash', ''))
                    or not re.fullmatch(r'[0-9a-f]{16}', row.get('revision', ''))):
                raise ValueError('Invalid account registry or unmapped source identity')
        auditors = body.get('application_auditors', {})
        if not isinstance(auditors, dict):
            raise ValueError('Invalid application auditors')
        for key, row in auditors.items():
            if (not isinstance(key, str) or not re.fullmatch(r'[a-z0-9_-]{1,48}', key)
                    or not isinstance(row, dict)
                    or set(row)-{'active','expires','revision','salt','password_hash','viewer_ids','resource_scope','login_name','display_name'}
                    or type(row.get('active')) is not bool or type(row.get('expires')) not in (int,float)
                    or not re.fullmatch(r'[0-9a-f]{32}', row.get('salt',''))
                    or not re.fullmatch(r'[0-9a-f]{64}', row.get('password_hash',''))
                    or not re.fullmatch(r'[0-9a-f]{16}', row.get('revision',''))
                    or row.get('resource_scope') != 'payment-service'
                    or not isinstance(row.get('viewer_ids'), list) or not row['viewer_ids']
                    or any(not isinstance(v,str) or not re.fullmatch(r'reviewer:[a-z0-9_-]{1,48}:[0-9a-f]{16}',v)
                           for v in row['viewer_ids'])):
                raise ValueError('Exact application audit scope required')
            login = row.get('login_name', key)
            display = row.get('display_name', login)
            if (not isinstance(login,str) or not re.fullmatch(r'[a-z0-9_-]{1,48}',login)
                    or login in login_names or not isinstance(display,str)
                    or not 1 <= len(display) <= 80 or not display.isprintable()):
                raise ValueError('Unique auditor login required')
            login_names.add(login)
        return body

    def auditor_row(self, actor):
        if actor.tenant != 'reviewer-demo' or not actor.user_id.startswith('application-auditor:'):
            raise PermissionError('Unavailable')
        try:
            _, key, revision = actor.user_id.split(':')
            row = self.read().get('application_auditors', {}).get(key)
        except (OSError, ValueError, KeyError):
            raise PermissionError('Unavailable') from None
        if not row or not row['active'] or time.time() >= row['expires'] or row['revision'] != revision:
            raise PermissionError('Unavailable')
        return row

    def is_auditor(self, actor):
        try:
            self.auditor_row(actor)
            return True
        except PermissionError:
            return False

    def row(self, actor):
        if actor.tenant != 'reviewer-demo' or not actor.user_id.startswith('reviewer:'):
            raise PermissionError('Unavailable')
        try:
            _, username, revision = actor.user_id.split(':')
            row = self.read()['accounts'].get(username)
        except (OSError, ValueError, KeyError):
            raise PermissionError('Unavailable') from None
        if not row or not row['active'] or time.time() >= row['expires'] or row['revision'] != revision:
            raise PermissionError('Unavailable')
        return row

    def validate(self, actor):
        if actor.user_id.startswith('application-auditor:'):
            self.auditor_row(actor)
        else:
            self.row(actor)

    def source_actor(self, actor):
        return Actor(self.row(actor)['source_actor'], self.tenant)

    def demo_role(self, actor):
        if actor.user_id.startswith('application-auditor:'):
            self.auditor_row(actor)
            return 'auditor'
        row = self.row(actor)
        return row.get('demo_role', row['source_actor'])

    def display_name(self, actor):
        row = self.auditor_row(actor) if actor.user_id.startswith('application-auditor:') else self.row(actor)
        return row.get('display_name', row.get('login_name', actor.user_id.split(':')[1]))

    def access_scope(self, actor):
        from .application_access import ApplicationAccess
        body = self.read()
        row = self.row(actor)
        if 'application_roles' not in body:
            return None
        digest = hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()
        role = row['demo_role']
        ids = body['application_roles'][role]['resource_ids']
        def validate():
            self.validate(actor)
            current = hashlib.sha256(json.dumps(self.read(),sort_keys=True).encode()).hexdigest()
            if current != digest:
                raise PermissionError('Application access changed')
        validate()
        return ApplicationAccess(actor.user_id,role,row['source_actor'],digest,
                                 None if ids is None else frozenset(ids),validate)

    @staticmethod
    def derive(password, salt):
        return hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1, dklen=32).hex()

    def authenticate(self, data):
        if (set(data) != {'username', 'password'} or not isinstance(data['username'], str)
                or not re.fullmatch(r'[a-z0-9_-]{1,48}', data['username'])
                or not isinstance(data['password'], str) or not 12 <= len(data['password']) <= 256):
            raise PermissionError('Unavailable')
        with self.lock:
            now = time.monotonic()
            # Fixed global window also bounds random-username abuse and memory.
            recent = [t for t in self.failures.get('*', []) if now-t < 60]
            if len(recent) >= 30:
                raise PermissionError('Unavailable')
            self.failures['*'] = recent
            body = self.read()
            principals = [('reviewer',k,r) for k,r in body['accounts'].items()] + [('application-auditor',k,r) for k,r in body.get('application_auditors',{}).items()]
            kind, key, row = next(((kind, key, row) for kind, key, row in principals
                             if row.get('login_name', key) == data['username']), (None, None, None))
            digest = self.derive(data['password'], row['salt'] if row else '0'*32)
            valid = secrets.compare_digest(digest, row['password_hash'] if row else '0'*64)
            if not row or not valid or not row['active'] or time.time() >= row['expires']:
                self.failures['*'].append(now)
                raise PermissionError('Unavailable')
            actor = Actor(kind+':'+key+':'+row['revision'], 'reviewer-demo')
            self.validate(actor)
            return actor


class ReviewerQuery:
    def __init__(self, engine):
        self.engine = engine

    def public_status(self):
        get = getattr(self.engine.original.query, 'public_status', None)
        return get() if callable(get) else None

    def __call__(self, actor, question, *, request_id, progress=None):
        e = self.engine
        e.register_request(actor, request_id, question=question)
        source_actor = e.registry.source_actor(actor)
        scope = e.registry.access_scope(actor)
        if scope and scope.source_actor != source_actor.user_id:
            raise PermissionError('Application access changed')
        from .application_access import bind_access
        with bind_access(scope):
            result = e.original.query(source_actor, question, request_id=request_id, progress=progress)
            if scope:scope.validate_current()
        e.registry.validate(actor)
        with e.store.transaction() as db:
            for evidence in result.get('evidence', []):
                db.execute('INSERT OR IGNORE INTO reviewer_evidence VALUES(?,?)',
                           (actor.user_id, evidence['evidence_id']))
        return result


class ReviewerEngine:
    def __init__(self, original, registry):
        self.original, self.registry = original, registry
        self.store, self.audit = original.store, original.audit
        with self.store.transaction() as db:
            db.execute('CREATE TABLE IF NOT EXISTS reviewer_requests(request_id TEXT PRIMARY KEY, viewer TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS reviewer_evidence(viewer TEXT NOT NULL, evidence_id TEXT NOT NULL, PRIMARY KEY(viewer,evidence_id))')
        self.query = ReviewerQuery(self)

    def register_request(self, actor, request_id, *, question=_QUESTION_UNSET):
        # Establish ownership before readiness/model admission can fail. No client actor accepted.
        if question is not _QUESTION_UNSET and (not isinstance(question,str) or len(question)>4000):
            raise ValueError('Invalid question')
        source = self.registry.source_actor(actor)
        scope = self.registry.access_scope(actor)
        with self.store.transaction() as db:
            row = db.execute('SELECT viewer FROM reviewer_requests WHERE request_id=?',(request_id,)).fetchone()
            if row:
                if row[0] != actor.user_id:
                    raise PermissionError('Unavailable')
                return
            db.execute('INSERT INTO reviewer_requests VALUES(?,?)',(request_id,actor.user_id))
            self.audit.append_in_transaction(db,'reviewer_query',actor.user_id,request_id,
                {'effective_source_actor':source.user_id,'effective_source_tenant':source.tenant,
                 'purpose':'shared-synthetic-review','resource_scope':'payment-service',
                 'application_role':scope.role if scope else None,
                 'application_policy_digest':scope.policy_digest if scope else None,
                 **({'query':question} if question is not _QUESTION_UNSET else {})})

    @property
    def mode(self):
        return self.original.mode

    @property
    def model(self):
        return self.original.model

    def owned_ids(self, actor):
        self.registry.row(actor)
        with self.store.lock:
            return {r[0] for r in self.store.db.execute(
                'SELECT request_id FROM reviewer_requests WHERE viewer=?', (actor.user_id,))}

    def history_summaries(self, actor):
        owned = self.owned_ids(actor)
        return [r for r in self.original.history_summaries(self.registry.source_actor(actor)) if r['request_id'] in owned]

    def safe_history(self, actor, request_id=None):
        owned = self.owned_ids(actor)
        if request_id is not None and request_id not in owned:
            raise PermissionError('Unavailable')
        results = []
        from .application_access import bind_access
        scope = self.registry.access_scope(actor)
        with bind_access(scope):
            for rid in ([request_id] if request_id else sorted(owned)):
                results.extend(self.original.safe_history(self.registry.source_actor(actor), rid))
            if scope:scope.validate_current()
        self.registry.validate(actor)
        return results

    def evidence(self, actor, evidence_id):
        self.registry.row(actor)
        with self.store.lock:
            row = self.store.db.execute('SELECT 1 FROM reviewer_evidence WHERE viewer=? AND evidence_id=?',
                                        (actor.user_id, evidence_id)).fetchone()
        if not row:
            raise PermissionError('Unavailable')
        from .application_access import bind_access
        scope = self.registry.access_scope(actor)
        with bind_access(scope):
            result = self.original.evidence(self.registry.source_actor(actor), evidence_id)
            if scope:scope.validate_current()
        self.registry.validate(actor)
        return result


class ReviewerApp:
    auth_kind = 'reviewer'
    login_path = '/api/reviewer/login'

    def __init__(self, original, path):
        self.original = original
        self.actor = original.actor
        self.store, self.world, self.audit = original.store, original.world, original.audit
        readers = getattr(original.world, 'readers', {})
        roles = (set.intersection(*(set(r.delegations) for r in readers.values()))
                 if readers else set(original.world.users))
        self.registry = ReviewAccounts(path, self.actor.tenant, roles)
        self.engine = ReviewerEngine(original.engine, self.registry)
        self.request_lock = getattr(original, 'request_lock', self.store.lock)
        self.sessions = {}
        from .run_state import SessionRuns
        self.session_runs = SessionRuns()
        self.admission_lock = threading.Lock()
        self.active_queries = set()

    @property
    def private_timing(self):
        # The HTTP adapter shares only the explicitly enabled private recorder.
        # Dynamic lookup supports installation before or after this wrapper.
        return getattr(self.original, 'private_timing', None)

    def authenticate(self, data):
        actor = self.registry.authenticate(data)
        self.audit.append('reviewer_session', actor.user_id, 'login',
                          {'effective_source_actor': None if self.can_audit(actor) else self.registry.source_actor(actor).user_id, 'purpose': 'shared-synthetic-review'})
        return actor

    def session(self, token):
        session = App.session(self, token)
        self.registry.validate(session['actor'])
        return session

    def refresh(self):
        self.original.refresh()

    def can_audit(self, actor):
        return self.registry.is_auditor(actor)

    def session_details(self, actor):
        self.registry.validate(actor)
        result = {'demo_role':self.registry.demo_role(actor),
                  'display_name':self.registry.display_name(actor),'can_audit':self.can_audit(actor)}
        if result['can_audit']:
            row = self.registry.auditor_row(actor)
            result.update(audit_viewer_ids=sorted(set(row['viewer_ids'])),audit_resource_scope=row['resource_scope'])
        return result

    def register_request(self, actor, request_id, *, question=_QUESTION_UNSET):
        self.engine.register_request(actor, request_id, question=question)

    def audit_inquire(self, actor, filters):
        from .application_audit import inquire
        return inquire(self, actor, filters)
