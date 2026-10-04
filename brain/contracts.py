"""Version 1 contracts. Source policy authority is distinct from the local index."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Literal, Protocol

SOURCES = ('confluence', 'jira', 'slack', 'drive')
MODE = 'fixture_fake_model'
TENANT = 'synthetic-demo'


def now():
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Actor:
    user_id: str
    tenant: str = TENANT


@dataclass(frozen=True)
class Decision:
    result: Literal['allow', 'deny', 'unknown']
    checked_at: str
    method: str
    policy_version: int


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    resource_id: str
    version: int
    source: str
    title: str
    locator: dict
    text: str
    source_updated_at: str
    indexed_at: str
    source_url: str

    def to_dict(self):
        return asdict(self)


class SourceAdapter(Protocol):
    """Live implementations must verify a mapped user's access, including subresources.

    Errors, absent mappings and incomplete ACLs return unknown, never allow.
    Content retrieval is ingestion-only until check_read succeeds for the query actor.
    """
    def capabilities(self) -> dict: ...
    def list_initial(self, cursor: int = 0, limit: int = 100) -> dict: ...
    def list_changes(self, cursor: int = 0, limit: int = 100) -> dict: ...
    def fetch_resource(self, resource_id: str) -> dict: ...
    def check_read(self, actor: Actor, resource_id: str) -> Decision: ...
    def source_link(self, resource_id: str) -> str: ...


class Model(Protocol):
    def generate(self, question: str, evidence: list[Evidence]) -> dict: ...
