"""Operator-only wall timing. Never records call arguments, URLs or credentials."""
from contextlib import contextmanager
import threading
import time
from brain.confluence import JsonTransport


class Measurements:
    def __init__(self):
        self.local = threading.local()
        self.samples = []

    @contextmanager
    def phase(self, name):
        previous = getattr(self.local, 'phase', 'background_discovery')
        self.local.phase = name
        try:
            yield
        finally:
            self.local.phase = previous

    def call(self, category, source, callback):
        start = time.monotonic()
        try:
            return callback()
        finally:
            self.samples.append({'phase':getattr(self.local,'phase','background_discovery'),
                'category':category,'source':source,'seconds':time.monotonic()-start})

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
        return self.measurements.call('native_http',self.source,
            lambda:self.delegate.get(*args,**kwargs))

    def media(self, *args, **kwargs):
        return self.measurements.call('native_http',self.source,
            lambda:self.delegate.media(*args,**kwargs))
