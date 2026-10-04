"""Compatibility entry point for the Confluence-only trusted operator pilot."""
from .delegated_query import DelegatedAuthority, DelegatedQueryPilot


class ConfluenceAuthority(DelegatedAuthority):
    def __init__(self, reader):
        super().__init__({'confluence': reader})
        self.reader = reader


class ConfluenceQueryPilot(DelegatedQueryPilot):
    def __init__(self, reader, store, *, live=False):
        super().__init__({'confluence': reader}, store, live=live)
        self.engine.mode = 'confluence_live_api_fake_model' if live else 'confluence_mock_http_fake_model'
