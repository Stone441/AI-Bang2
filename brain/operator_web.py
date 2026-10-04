"""Loopback operator UI for approved synthetic Confluence pages and fake model.

Token stays in this process, never goes to the browser. A short-lived one-use
bootstrap ticket attaches a browser to the verified operator, not employee SSO.
"""
import argparse
import os
import secrets
import time
from pathlib import Path

from .contracts import Actor
from .confluence_query import ConfluenceQueryPilot
from .server import App, create_server
from .store import Store


class OperatorApp:
    login_path = '/api/operator/login'
    auth_kind = 'operator'
    session = App.session

    def __init__(self, reader, store, actor_id, *, live=False):
        self.actor = Actor(actor_id, reader.tenant)
        # This verifies the token's current native identity, even if a page is denied.
        self.pilot = ConfluenceQueryPilot(reader, store, live=live)
        reader._credential(self.actor, sorted(reader.page_ids)[0])
        self.engine, self.world, self.audit = self.pilot.engine, self.pilot.authority, self.pilot.audit
        self.store, self.sessions = store, {}
        self._ticket = secrets.token_urlsafe(32)
        self._ticket_expires = time.monotonic() + 600

    def bootstrap_ticket(self):
        return self._ticket

    def authenticate(self, data):
        if (set(data) != {'ticket'} or not isinstance(data['ticket'], str)
                or not self._ticket or time.monotonic() >= self._ticket_expires
                or not secrets.compare_digest(data['ticket'], self._ticket)):
            raise PermissionError('Unavailable')
        self._ticket = None
        return self.actor

    def refresh(self):
        pass  # Engine performs per-query native refresh; no fixture source exists.


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--actor', default='eng_b')
    parser.add_argument('--port', type=int, default=8081)
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args(argv)
    if not args.live:
        print('not_run: --live required; no credentials or platform calls performed.')
        return 2
    store = server = None
    try:
        from scripts.confluence_probe import load_reader
        reader = load_reader(args.config, prompt_actor=args.actor)
        runtime = Path('.runtime'); runtime.mkdir(mode=0o700, exist_ok=True)
        db = runtime / 'confluence-web.sqlite'
        store = Store(str(db)); os.chmod(db, 0o600)
        app = OperatorApp(reader, store, args.actor, live=True)
        server = create_server(app, args.port)
        # Fragment never goes in HTTP request logs. The UI removes it before exchange.
        print('Confluence LIVE API / FAKE MODEL / LOCAL OPERATOR (not SSO)', flush=True)
        print(f'Open once within 10 minutes: http://127.0.0.1:{server.server_port}/#ticket={app.bootstrap_ticket()}', flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except Exception:
        print('Operator service could not start or continue safely. No credential details are logged.')
        return 2
    finally:
        if server is not None: server.server_close()
        if store is not None: store.db.close()


if __name__ == '__main__': raise SystemExit(main())
