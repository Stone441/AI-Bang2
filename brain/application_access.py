"""Request-local additional application ACL; never replaces source authorization."""
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

_CURRENT = ContextVar('application_demo_access', default=None)


@dataclass(frozen=True)
class ApplicationAccess:
    viewer: str
    role: str
    source_actor: str
    policy_digest: str
    resource_ids: frozenset | None
    validate_current: object

    def allows(self, resource):
        self.validate_current()
        return self.resource_ids is None or resource['id'] in self.resource_ids


@contextmanager
def bind_access(scope):
    token = _CURRENT.set(scope)
    try:
        yield scope
    finally:
        _CURRENT.reset(token)


def current_access():
    return _CURRENT.get()


def allows(resource):
    scope = current_access()
    return scope is None or scope.allows(resource)
