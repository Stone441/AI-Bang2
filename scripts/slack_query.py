"""Approved synthetic Slack operator configuration; secret stays in process memory."""
import getpass
import json
import os
import re
import sys
import warnings
from pathlib import Path

from brain.confluence import Delegation
from brain.slack import SlackReader


def hidden_token(account_id):
    if not sys.stdin.isatty(): raise ValueError('Secure TTY required')
    with warnings.catch_warnings():
        warnings.simplefilter('error', getpass.GetPassWarning)
        token = getpass.getpass('Slack USER OAuth token (hidden; not saved): ')
    if not token or any(ch.isspace() for ch in token): raise ValueError('Invalid credential')
    return Delegation(account_id, 'Bearer ' + token)


def load_reader(path, prompt_actor=None):
    config = json.loads(Path(path).read_text())
    if config.get('approved_synthetic_only') is not True: raise ValueError('Synthetic approval required')
    delegations = {}
    for uid, mapping in config['delegations'].items():
        if set(mapping) != {'account_id','authorization_env'}: raise ValueError('Credential reference required')
        if not isinstance(mapping['account_id'],str) or not re.fullmatch(r'[UW][A-Z0-9]+',mapping['account_id']):
            raise ValueError('Verified native Slack user required')
        key = mapping['authorization_env']
        if not isinstance(key,str) or not re.fullmatch(r'AIBANG2_SLACK_[A-Z0-9_]+',key):
            raise ValueError('Slack-specific credential reference required')
        value = os.environ.get(key)
        if value: delegations[uid] = Delegation(mapping['account_id'],value)
    reader = SlackReader(config['site'], config['tenant'], config['team_id'],
        config['channels'], config['messages'], delegations)
    if prompt_actor is not None:
        if prompt_actor not in config['delegations']: raise ValueError('Mapped operator required')
        reader.delegations[prompt_actor] = hidden_token(config['delegations'][prompt_actor]['account_id'])
    return reader
