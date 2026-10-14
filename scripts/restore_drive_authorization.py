"""Human-operated renewal of the existing reviewed Drive read-only grant.

No model, document read, new account, new scope or application service. The old
Keychain item is replaced only after Google returns the exact existing scope
and the configured account passes native identity verification.
"""
import json
import webbrowser

from brain.drive_oauth import authorize, load_client, verify_account
from brain.keychain import MacKeychain
from scripts.drive_query import prepare_oauth_reader
from scripts.performance_trial import ROOT


def restore(reader, config, client, store, notify):
    email = config['oauth_operator']['email']
    account = client.client_id+'|'+email.casefold()
    # Only renewal of an existing item; never provision another account here.
    if store.get('drive', reader.tenant, 'eng_b', account) is None:
        raise ValueError('Existing reviewed Drive authorization required')
    grant = authorize(client, email, notify, offline=True)
    verify_account(grant['access_token'], email, reader.transport)
    store.put('drive', reader.tenant, 'eng_b', account, grant['refresh_token'])


def main():
    try:
        bundle_path = ROOT/'.runtime/operator-bundle.json'
        bundle = json.loads(bundle_path.read_text())
        if bundle.get('approved_synthetic_only') is not True or bundle.get('identity_mapping_reviewed') is not True:
            raise ValueError('Existing reviewed mapping required')
        reader, config = prepare_oauth_reader(bundle_path.parent/bundle['sources']['drive'], 'eng_b')
        client = load_client(ROOT/'.runtime/drive-oauth-client.json', config['oauth_client_id'])
        def notify(url):
            print('Review the existing Google account and Drive read-only scope in your browser.', flush=True)
            if not webbrowser.open(url):
                raise RuntimeError('Browser unavailable')
        restore(reader, config, client, MacKeychain(), notify)
        print('Existing Drive read-only authorization renewed and account verified. No model call was made.')
        return 0
    except Exception:
        print('Drive renewal stopped. The existing credential is retained unless verification and storage completed.')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
