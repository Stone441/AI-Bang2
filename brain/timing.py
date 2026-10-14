"""Opt-in private local diagnostics. No business data, networking or permission decisions."""
from contextlib import contextmanager, ExitStack
from contextvars import ContextVar
from functools import wraps
import json
import math
import os
from pathlib import Path
import re
import stat
import threading
import time
import uuid

from scripts.validation_timing import Measurements, TimedNativeTransport

_active = ContextVar('restricted_timing_request', default=None)
_parent = ContextVar('restricted_timing_parent', default=None)
_phase = ContextVar('restricted_timing_authorization', default=None)
CATEGORIES = frozenset(('request_wall', 'lock_wait', 'lock_held', 'retrieval',
    'authorization', 'source_lane', 'native_http', 'source_claims', 'model_input',
    'model_transport', 'model_output', 'ledger', 'commit'))
SOURCES = frozenset(('confluence', 'jira', 'slack', 'drive', 'deepseek', 'local'))
PHASES = frozenset(('link_seed', 'before_model', 'model_dispatch', 'review_dispatch',
    'before_dispatch', 'preview', 'history'))
ENDPOINTS = frozenset(('other', 'auth.test', 'conversations.info', 'conversations.history',
    'conversations.replies', 'myself', 'about', 'user/current', 'search/jql',
    'space_pages', 'page_body', 'page_metadata', 'comment', 'issue',
    'file_metadata', 'file_list', 'file_body'))
OUTCOMES = frozenset(('ok', 'deny', 'unknown', 'version_changed', 'cancelled', 'unavailable'))


class PrivateTiming:
    def __init__(self, directory, *, max_spans=512, clock=time.monotonic):
        if type(max_spans) is not int or not 1 <= max_spans <= 4096:
            raise ValueError('Invalid timing bound')
        path = Path(directory).absolute()
        # Reject symlink components; never chmod or replace existing directories.
        for component in reversed([path, *path.parents]):
            if component.is_symlink():
                raise ValueError('Private timing directory required')
        path.mkdir(mode=0o700, exist_ok=True)
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        info = os.fstat(fd)
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            os.close(fd)
            raise ValueError('Private timing directory required')
        self.fd, self.clock, self.max_spans = fd, clock, max_spans

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def save(self, state):
        # Fixed schema and generated filename; no user-supplied path/ID reaches open.
        body = json.dumps({'schema_version': 1, 'request_id': state.request_id,
            'operation': state.operation, 'incomplete': state.incomplete,
            'spans': state.spans,
            'boundary': 'Nested and parallel spans overlap; do not sum as request wall.'}).encode()
        name = uuid.uuid4().hex
        pending = name + '.pending'
        fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                     | os.O_NOFOLLOW, 0o600, dir_fd=self.fd)
        try:
            with os.fdopen(fd, 'wb') as stream:
                os.fchmod(stream.fileno(), 0o600)
                stream.write(body)
            # Publish a complete inode without replacing any existing file.
            os.link(pending, name + '.json', src_dir_fd=self.fd,
                    dst_dir_fd=self.fd, follow_symlinks=False)
        finally:
            os.unlink(pending, dir_fd=self.fd)


class _Request:
    def __init__(self, recorder, operation):
        self.recorder, self.operation = recorder, operation
        self.request_id = uuid.uuid4().hex
        self.started = recorder.clock()
        self.spans, self.incomplete, self.lock = [], False, threading.Lock()

    def now(self):
        value = self.recorder.clock() - self.started
        if not math.isfinite(value) or value < 0:
            raise ValueError('Invalid timing clock')
        return value


def bind_request(request_id):
    state = _active.get()
    if state is not None and isinstance(request_id, str) and re.fullmatch('[0-9a-f]{32}', request_id):
        state.request_id = request_id


def http_status(code):
    state = _active.get()
    if state is not None and state.spans and type(code) is int:
        state.spans[0]['outcome'] = ('deny' if code == 403 else
            'unavailable' if code >= 400 else 'ok')


@contextmanager
def authorization_scope(phase):
    token = _phase.set(phase if phase in PHASES else None)
    try:
        yield
    finally:
        _phase.reset(token)


@contextmanager
def span(category, source='local', *, endpoint=None):
    state = _active.get()
    item = token = None
    if state is not None:
        try:
            if category not in CATEGORIES or source not in SOURCES:
                raise ValueError('Unknown diagnostic category')
            started = state.now()
            with state.lock:
                if len(state.spans) >= state.recorder.max_spans:
                    state.incomplete = True
                else:
                    item = {'span_id': len(state.spans), 'parent_span_id': _parent.get(),
                        'category': category, 'source': source,
                        'authorization_phase': _phase.get() if _phase.get() in PHASES else None,
                        'start_offset_seconds': started, 'duration_seconds': None, 'outcome': 'ok'}
                    if endpoint is not None:
                        item['endpoint'] = endpoint if endpoint in ENDPOINTS else 'other'
                    state.spans.append(item)
            if item is not None:
                token = _parent.set(item['span_id'])
        except Exception:
            state.incomplete = True
    try:
        yield item
    except BaseException as error:
        if item is not None:
            # Type-based fixed labels only; never inspect exception message/args.
            item['outcome'] = ('deny' if isinstance(error, PermissionError) else
                'cancelled' if isinstance(error, (KeyboardInterrupt, SystemExit)) else 'unavailable')
        raise
    finally:
        if item is not None:
            try:
                duration = state.now() - item['start_offset_seconds']
                if duration < 0:
                    raise ValueError('Invalid timing clock')
                item['duration_seconds'] = duration
            except Exception:
                state.incomplete = True
            if token is not None:
                _parent.reset(token)


@contextmanager
def request_scope(app, operation):
    recorder = getattr(app, 'private_timing', None)
    if recorder is None or _active.get() is not None:
        yield
        return
    state = None
    try:
        if operation not in ('query', 'preview', 'history', 'background_discovery'):
            raise ValueError('Unknown diagnostic operation')
        state = _Request(recorder, operation)
    except Exception:
        pass  # Diagnostic failure never prevents the business operation.
    if state is None:
        yield
        return
    token, parent, phase = _active.set(state), _parent.set(None), _phase.set(None)
    try:
        with span('request_wall'):
            yield
    finally:
        try:
            recorder.save(state)
        except Exception:
            pass  # No retries, error logging, or replacement of business errors.
        _phase.reset(phase)
        _parent.reset(parent)
        _active.reset(token)


@contextmanager
def acquire(lock):
    # Preserve the original context-manager protocol, including test/operator
    # wrappers and exceptional __exit__ semantics; never replace the lock.
    with ExitStack() as stack:
        with span('lock_wait'):
            entered = stack.enter_context(lock)
        with span('lock_held'):
            yield entered


class _Measurements(Measurements):
    def call(self, category, source, callback, *, endpoint=None):
        with span(category, source, endpoint=endpoint) as item:
            value = callback()
            if (item is not None and category == 'native_http' and isinstance(value, tuple)
                    and value and type(value[0]) is int):
                status = value[0]
                if status in (403, 404): item['outcome'] = 'deny'
                elif status != 200: item['outcome'] = 'unavailable'
            return value


def install(app, directory, *, max_spans=512, clock=time.monotonic):
    """Trusted operator setup, once, before polling or serving. Not an HTTP API."""
    if getattr(app, 'private_timing', None) is not None:
        raise ValueError('Timing already installed')
    recorder = PrivateTiming(directory, max_spans=max_spans, clock=clock)
    measurements = _Measurements()

    def wrap(owner, name, category, source='local', authorization=False):
        original = getattr(owner, name)
        @wraps(original)
        def call(*args, **kwargs):
            token = None
            if authorization:
                phase = kwargs.get('phase', args[-1] if args else None)
                token = _phase.set(phase if phase in PHASES else None)
            try:
                with span(category, source) as item:
                    value = original(*args, **kwargs)
                    if item is not None and authorization and isinstance(value,list) and any(v is False for v in value):
                        item['outcome'] = 'unavailable'
                    return value
            finally:
                if token is not None: _phase.reset(token)
        setattr(owner, name, call)

    wrap(app.engine, 'checks', 'authorization', authorization=True)
    wrap(app.engine, 'check', 'authorization', authorization=True)
    wrap(app.store, 'save_run', 'commit')
    if hasattr(app.world, 'prepare'): wrap(app.world, 'prepare', 'retrieval')
    readers = getattr(app.world, 'readers', {})
    for source, reader in readers.items():
        reader.transport = TimedNativeTransport(reader.transport, measurements, source)
    model = app.engine.model
    if hasattr(model, 'source_claims'): wrap(model, 'source_claims', 'source_claims')
    if hasattr(model, 'ledger'):
        for name in ('reserve', 'dispatch', 'settle', 'model_outcome'):
            wrap(model.ledger, name, 'ledger')
    app.private_timing = recorder
    return recorder


def attach_discovery(app, discovery):
    if getattr(app, 'private_timing', None) is None:
        return
    original = discovery._cycle
    @wraps(original)
    def cycle(*args, **kwargs):
        with request_scope(app, 'background_discovery'):
            return original(*args, **kwargs)
    discovery._cycle = cycle
