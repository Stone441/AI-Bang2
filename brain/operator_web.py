"""Loopback operator UI for approved synthetic delegated resources and fake model.

Credentials never go to the browser; explicit opt-in permits app-owned Keychain reuse. A short-lived one-use
bootstrap ticket attaches a browser to the verified operator, not employee SSO.
"""
import argparse
import errno
import getpass
import os
import secrets
import time
import warnings
from pathlib import Path

from .contracts import Actor
from .confluence_query import ConfluenceQueryPilot
from .confluence import ConfluenceReader
from .delegated_query import DelegatedQueryPilot
from .jira import JiraReader
from .slack import SlackReader
from .drive import DriveReader
from .server import App, create_server
from .store import Store
from .credential_input import HiddenInputUnavailable
from .runtime_version import runtime_version


class OperatorApp:
    login_path = '/api/operator/login'
    auth_kind = 'operator'
    session = App.session

    def __init__(self, reader, store, actor_id, *, live=False):
        if isinstance(reader, dict):
            self.pilot = DelegatedQueryPilot(reader, store, live=live)
            self.actor = Actor(actor_id, self.pilot.authority.tenant)
            # All mappings must exist before any native identity call. A missing
            # source cannot silently become another user's delegation.
            if any(actor_id not in r.delegations for r in reader.values()):
                raise ValueError('Mapped operator required on every source')
            if any(getattr(r, 'discovery_only', False) for r in reader.values()):
                raise ValueError('Content readers required')
            for source, configured in sorted(reader.items()):
                if source == 'confluence':
                    configured._credential(self.actor, sorted(configured.page_ids)[0])
                else:
                    configured._credential(self.actor)
        else:
            self._single_source(reader, store, actor_id, live)
        self.engine, self.world, self.audit = self.pilot.engine, self.pilot.authority, self.pilot.audit
        self.store, self.sessions = store, {}
        self._ticket = secrets.token_urlsafe(32)
        self._ticket_expires = time.monotonic() + 600

    def _single_source(self, reader, store, actor_id, live):
        self.actor = Actor(actor_id, reader.tenant)
        # This verifies the token's current native identity, even if a page is denied.
        if isinstance(reader, ConfluenceReader):
            self.pilot = ConfluenceQueryPilot(reader, store, live=live)
            reader._credential(self.actor, sorted(reader.page_ids)[0])
        elif ((isinstance(reader, JiraReader) and not reader.discovery_only)
              or isinstance(reader, (SlackReader, DriveReader))):
            source = 'drive' if isinstance(reader, DriveReader) else 'slack' if isinstance(reader, SlackReader) else 'jira'
            self.pilot = DelegatedQueryPilot({source: reader}, store, live=live)
            reader._credential(self.actor)
        else:
            raise ValueError('Configured content reader required')

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
    parser.add_argument('--source', choices=['confluence', 'jira', 'slack', 'drive', 'multi'], default='confluence')
    parser.add_argument('--port', type=int, default=8081)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--discovery-auth017',action='store_true',help='Opt-in eng_b discovery in AUTH-017 fixed four containers; default off')
    parser.add_argument('--oauth-client', help='Private Google desktop JSON, Drive or multi; browser consent instead of hidden Drive token')
    parser.add_argument('--model', choices=['fake', 'deepseek'], default='fake', help='Explicit approved synthetic-only DeepSeek evidence selection')
    parser.add_argument('--answer-style', choices=['excerpts','synthesis'], default='excerpts',
                        help='Synthesis uses two budgeted calls and exact grounding plus model review')
    parser.add_argument('--credential-store',choices=['memory','macos-keychain'],default='memory',
                        help='Explicit opt-in: save/reuse app-owned credentials in this Mac Keychain')
    parser.add_argument('--replace-credential',choices=['confluence','jira','slack','drive','deepseek'],
                        help='Re-enter only one credential for this launch; keep all others')
    args = parser.parse_args(argv)
    if args.discovery_auth017 and (args.source!='multi' or args.actor!='eng_b'):
        print('not_run: AUTH-017 discovery requires multi-source eng_b; no credentials or platform calls performed.')
        return 2
    if args.answer_style=='synthesis' and args.model!='deepseek':
        print('not_run: synthesis requires DeepSeek; no credentials or platform calls performed.')
        return 2
    if not args.live:
        print('not_run: --live required; no credentials or platform calls performed.')
        return 2
    if ((args.credential_store=='macos-keychain' and args.source not in ('multi','confluence'))
            or (args.replace_credential and args.credential_store!='macos-keychain')
            or (args.source=='confluence' and args.replace_credential not in (None,'confluence'))):
        print('not_run: Keychain reuse requires a reviewed multi-source or Confluence operator; replacement requires Keychain mode.')
        return 2
    if args.oauth_client and args.source not in ('drive','multi'):
        print('not_run: --oauth-client requires Drive or multi; no credential or platform calls performed.')
        return 2
    if args.model == 'deepseek':
        from .deepseek import check_price_review
        try:
            check_price_review()
        except ValueError:
            from .deepseek import PRICE_SOURCE
            print('not_run [model_price_review_required]: Review ' + PRICE_SOURCE
                  + ', record the Singapore review date and verified rates, then restart the reviewed build. '
                  'Preserve the existing USD20 ledger. No credentials or platform calls performed.')
            return 2
    store = server = ledger = discovery = None
    stage = 'bind'
    try:
        # Reserve the listener before asking for a credential. Do not serve until
        # the verified application is attached; no race-prone bind/release probe.
        server = create_server(None, args.port)
        stage = 'configuration_or_hidden_input'
        credential_store=None
        if args.credential_store=='macos-keychain':
            from .keychain import MacKeychain, ReplaceOne
            credential_store=MacKeychain()
            if args.replace_credential:credential_store=ReplaceOne(credential_store,args.replace_credential)
        if args.source == 'multi':
            from scripts.operator_bundle import load_reader
        elif args.source == 'drive':
            from scripts.drive_query import load_reader
        elif args.source == 'slack':
            from scripts.slack_query import load_reader
        elif args.source == 'jira':
            from scripts.jira_query import load_reader
        else:
            from scripts.confluence_probe import load_reader
        if credential_store is not None:
            if args.source == 'confluence':
                reader=load_reader(args.config,prompt_actor=args.actor,credential_store=credential_store)
            else:
                reader=load_reader(args.config,prompt_actor=args.actor,oauth_client=args.oauth_client,
                                   credential_store=credential_store)
        elif args.oauth_client and args.source == 'multi':
            reader = load_reader(args.config, prompt_actor=args.actor, oauth_client=args.oauth_client)
        elif args.oauth_client:
            from scripts.drive_query import load_oauth_reader
            reader = load_oauth_reader(args.config,args.oauth_client,args.actor)
        else:
            reader = load_reader(args.config, prompt_actor=args.actor)
        stage = 'local_store'
        runtime = Path('.runtime'); runtime.mkdir(mode=0o700, exist_ok=True)
        if args.source == 'confluence' and credential_store is not None:
            import hashlib
            import json
            # The reviewed native-account identity is distinct from other operators;
            # a digest keeps arbitrary CLI actor strings out of filesystem paths.
            identity = [args.actor, reader.tenant, reader.delegations[args.actor].account_id]
            db = runtime / ('confluence-' + hashlib.sha256(json.dumps(identity).encode()).hexdigest()[:16] + '-web.sqlite')
        else:
            db = runtime / (args.source + ('-auth017' if args.discovery_auth017 else '') + '-web.sqlite')
        store = Store(str(db)); os.chmod(db, 0o600)
        stage = 'native_identity'
        app = OperatorApp(reader, store, args.actor, live=True)
        if args.model == 'deepseek':
            from .budget import BudgetLedger
            from .deepseek import DeepSeekEvidenceModel
            import sys
            stage = 'model_configuration'
            ledger_path = runtime / 'deepseek-budget.sqlite'
            # One durable budget across all source operators. Never delete/reset
            # this file to repeat the pilot or bypass prior unknown charges.
            ledger = BudgetLedger(str(ledger_path)); os.chmod(ledger_path, 0o600)
            key=credential_store.get('deepseek',app.actor.tenant,args.actor,'deepseek-flash') if credential_store else None
            new_key=key is None
            if new_key:
                if not sys.stdin.isatty():raise ValueError('Hidden model input requires a local TTY')
                with warnings.catch_warnings():
                    warnings.simplefilter('error', getpass.GetPassWarning)
                    key = getpass.getpass('DeepSeek API key (hidden): ').strip()
            model = DeepSeekEvidenceModel(key, ledger, synthetic_only=True)
            if args.answer_style=='synthesis':
                from .synthesis import DeepSeekSynthesisModel
                model=DeepSeekSynthesisModel(key,ledger,synthetic_only=True)
            if credential_store and new_key:
                credential_store.put('deepseek',app.actor.tenant,args.actor,'deepseek-flash',key)
            del key
            app.engine.model = model
            app.engine.mode = app.engine.mode.removesuffix('_fake_model') + '_live_model_selection'
            if args.answer_style=='synthesis':
                app.engine.mode=app.engine.mode.removesuffix('_live_model_selection')+'_live_model_synthesis'
        if args.discovery_auth017:
            from .discovery import ContainerDiscovery
            stage='discovery_configuration'
            discovery=ContainerDiscovery(app.pilot,app.actor)
            discovery.start()
        server.application = app
        # Fragment never goes in HTTP request logs. The UI removes it before exchange.
        label = 'LIVE MODEL EVIDENCE SELECTION' if args.model == 'deepseek' else 'FAKE MODEL'
        if args.answer_style=='synthesis': label='LIVE MODEL GROUNDED SYNTHESIS / SEPARATE MODEL REVIEW'
        print(f'{args.source.title()} LIVE API / {label} / LOCAL OPERATOR (not SSO)', flush=True)
        version = runtime_version()
        print(f"Startup source: {version['startup_source_sha256']} / loaded {version['process_loaded_at']}", flush=True)
        print(f'Open once within 10 minutes: http://127.0.0.1:{server.server_port}/#ticket={app.bootstrap_ticket()}', flush=True)
        stage = 'runtime'
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except Exception as error:
        from .keychain import KeychainUnavailable
        if isinstance(error,KeychainUnavailable):
            print('Operator service stopped [macos_keychain_unavailable]: Unlock or approve access to the app-owned Keychain item. No plaintext fallback is used.')
        elif isinstance(error, HiddenInputUnavailable):
            print(f'Operator service stopped [credential_{error.code}]: Hidden credential input was not accepted. '
                  'No platform or model request was sent for this input; no credential details are logged.')
        elif stage == 'bind' and isinstance(error, OSError) and error.errno == errno.EADDRINUSE:
            print(f'Startup stopped [port_in_use]: port {args.port} is already in use. '
                  'Keep the existing service, or retry with --port 8082. No credentials were requested.')
        else:
            messages = {
                'bind': 'Could not bind the loopback listener. Check local port permissions.',
                'configuration_or_hidden_input': 'Check the approved configuration, mapped actor and secure TTY input.',
                'local_store': 'Could not open the local database. Check .runtime access and database locks.',
                'discovery_configuration': 'Check AUTH-017 exact eng_b container mappings; discovery stays within approved scope.',
                'native_identity': 'Could not verify the mapped native account. Check token, account mapping and network access.',
                'model_configuration': 'Check the reviewed model price date, secure TTY and durable budget. No model request was sent.',
                'runtime': 'The running service stopped unexpectedly.',
            }
            print(f'Operator service stopped [{stage}_unavailable]: {messages[stage]} '
                  'No credential or upstream error details are logged.')
        return 2
    finally:
        if discovery is not None: discovery.close()
        if ledger is not None: ledger.close()
        if server is not None: server.server_close()
        if store is not None: store.db.close()


if __name__ == '__main__': raise SystemExit(main())
