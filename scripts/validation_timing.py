"""Operator-only wall timing. Never records call arguments, URLs or credentials."""
from contextlib import contextmanager
import threading
import time
from contextvars import ContextVar
from urllib.parse import urlsplit
from brain.confluence import JsonTransport


class Measurements:
    def __init__(self):
        self.phase_name = ContextVar('timing_phase', default='background_discovery')
        self.authorization_name = ContextVar('authorization_phase', default=None)
        self.lock = threading.Lock()
        self.samples = []

    @contextmanager
    def phase(self, name):
        token = self.phase_name.set(name)
        try:
            yield
        finally:
            self.phase_name.reset(token)

    @contextmanager
    def authorization_phase(self, name):
        token = self.authorization_name.set(name)
        try: yield
        finally: self.authorization_name.reset(token)

    def call(self, category, source, callback, *, endpoint=None):
        start = time.monotonic()
        try:
            return callback()
        finally:
            sample={'phase':self.phase_name.get(), 'authorization_phase':self.authorization_name.get(),
                'category':category,'source':source,'seconds':time.monotonic()-start}
            if endpoint is not None:sample['endpoint']=endpoint
            with self.lock:self.samples.append(sample)

    @contextmanager
    def acquire(self, lock):
        self.call('lock_wait', 'local', lock.acquire)
        try:
            yield
        finally:
            lock.release()

    def summary(self, phase):
        samples = [s for s in self.samples if s['phase'] == phase]
        return {'samples':samples,'seconds_by_category':{category:sum(s['seconds'] for s in samples
            if s['category']==category) for category in {s['category'] for s in samples}},
            'boundary':'Authorization wall time includes native HTTP; do not add these overlapping totals. Model timings are transport wall time.'}


class TimedNativeTransport(JsonTransport):
    def __init__(self, delegate, measurements, source):
        self.delegate, self.measurements, self.source = delegate, measurements, source

    def get(self, *args, **kwargs):
        # Fixed endpoint categories only; never persist IDs, hosts, query values or tokens.
        path=urlsplit(args[0]).path if args and isinstance(args[0],str) else ''
        endpoint='other'
        for suffix in ('auth.test','conversations.info','conversations.history','conversations.replies','myself','about','user/current','search/jql'):
            if path.endswith('/'+suffix):endpoint=suffix;break
        if endpoint=='other':
            if '/spaces/' in path:endpoint='space_pages'
            elif '/pages/' in path:endpoint='page_body' if 'body-format=storage' in args[0] else 'page_metadata'
            elif '/issue/' in path:endpoint='comment' if '/comment/' in path else 'issue'
            elif '/files/' in path:endpoint='file_metadata'
            elif path.endswith('/files'):endpoint='file_list'
        return self.measurements.call('native_http',self.source,
            lambda:self.delegate.get(*args,**kwargs),endpoint=endpoint)

    def media(self, *args, **kwargs):
        return self.measurements.call('native_http',self.source,
            lambda:self.delegate.media(*args,**kwargs),endpoint='file_body')
