"""Approved synthetic Drive operator configuration; secret stays in process memory."""
import getpass
import json
import os
import re
import sys
import warnings
from pathlib import Path

from brain.confluence import Delegation
from brain.drive import DriveReader


def hidden_token(account_id):
    if not sys.stdin.isatty(): raise ValueError('Secure TTY required')
    with warnings.catch_warnings():
        warnings.simplefilter('error', getpass.GetPassWarning)
        token = getpass.getpass('Drive OAuth access token (hidden; not saved): ')
    if not token or any(ch.isspace() for ch in token): raise ValueError('Invalid credential')
    return Delegation(account_id, 'Bearer ' + token)


def load_reader(path, prompt_actor=None):
    config = json.loads(Path(path).read_text())
    if config.get('approved_synthetic_only') is not True: raise ValueError('Synthetic approval required')
    delegations = {}
    for uid, mapping in config['delegations'].items():
        if set(mapping) != {'account_id','authorization_env'}: raise ValueError('Credential reference required')
        if not isinstance(mapping['account_id'],str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,200}',mapping['account_id']):
            raise ValueError('Verified native Drive user required')
        key = mapping['authorization_env']
        if not isinstance(key,str) or not re.fullmatch(r'AIBANG2_DRIVE_[A-Z0-9_]+',key):
            raise ValueError('Drive-specific credential reference required')
        value = os.environ.get(key)
        if value: delegations[uid] = Delegation(mapping['account_id'],value)
    reader = DriveReader(config['tenant'], config['files'], delegations)
    if prompt_actor is not None:
        if prompt_actor not in config['delegations']: raise ValueError('Mapped operator required')
        reader.delegations[prompt_actor] = hidden_token(config['delegations'][prompt_actor]['account_id'])
    return reader


def load_oauth_reader(path, client_path, actor):
    from brain.drive import DriveTransport
    from brain.drive_oauth import load_client, authorize, verify_account
    config = json.loads(Path(path).read_text())
    if (set(config) != {'approved_synthetic_only','tenant','files','oauth_operator','oauth_client_id'}
            or config['approved_synthetic_only'] is not True
            or not isinstance(config['oauth_operator'], dict)
            or set(config['oauth_operator']) != {'actor','email'}
            or config['oauth_operator']['actor'] != actor
            or not isinstance(config['oauth_operator']['email'], str)
            or not re.fullmatch(r'[^\s:@]+@[^\s:@]+',config['oauth_operator']['email'])):
        raise ValueError('Reviewed OAuth operator configuration required')
    reader = DriveReader(config['tenant'],config['files'],{},DriveTransport())
    client = load_client(client_path,config['oauth_client_id'])
    email = config['oauth_operator']['email']
    def notify(url):
        print('Open this Google authorization link. Review the account and Drive read-only scope yourself:',flush=True)
        print(url,flush=True)
    token = authorize(client,email,notify)
    reader.delegations[actor] = verify_account(token,email,reader.transport)
    return reader
