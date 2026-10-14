"""Credential-free, loopback-only reviewer demo; synthetic data and fake model."""
import argparse
from pathlib import Path
import sys
import webbrowser


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accounts', action='store_true', help='Password-based engineer/product/partner demo roles')
    parser.add_argument('--open', action='store_true', help='Open the local demo in your default browser')
    args = parser.parse_args(argv)
    if sys.version_info < (3, 11):
        parser.error('Python 3.11 or newer is required')
    from brain.server import App, create_server
    from brain.store import Store
    root = Path(__file__).resolve().parents[1]/'.runtime/reviewer-demo'
    root.mkdir(parents=True, exist_ok=True)
    store = Store(str(root/'demo.sqlite'))
    app = App(store, root/'sources.json')
    if args.accounts:
        from brain.contracts import Actor
        from brain.reviewer_access import ReviewerApp
        from scripts.reviewer_accounts import create
        registry, cards = root/'accounts.json', root/'login-cards.txt'
        if not registry.exists():
            create(registry, cards, 'synthetic-demo', {'engineer':'eng_b', 'product':'product_ops', 'partner':'contractor'},
                   personas={'engineer':('engineer_blair','Blair'), 'product':('product_morgan','Morgan'),
                             'partner':('partner_jordan','Jordan')})
        app.actor = Actor('eng_b')
        app = ReviewerApp(app, registry)
        print('Private usernames/passwords: '+str(cards), flush=True)
    server = create_server(app, 0)
    url = f'http://127.0.0.1:{server.server_port}'
    print('ContextLedger reviewer demo — SYNTHETIC DATA / FAKE MODEL', flush=True)
    print('No API keys, external accounts or model charges. Local access only.', flush=True)
    print(url, flush=True)
    print('Sign in with a demo account (or select an identity in selector mode), then try a suggested question. Ctrl+C stops the server.', flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        store.db.close()


if __name__ == '__main__':
    main()
