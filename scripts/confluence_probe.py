"""Operator-only live diagnostic; this is not an employee login endpoint."""
import argparse
import base64
import getpass
import json
import os
import re
import sys
import warnings
from dataclasses import asdict
from pathlib import Path

from brain.confluence import ConfluenceReader, Delegation
from brain.contracts import Actor


def load_reader(path, prompt_actor=None, discovery_only=False):
    config = json.loads(Path(path).read_text())
    if config.get('approved_synthetic_only') is not True:
        raise ValueError('Synthetic approval required')
    delegations = {}
    for user_id, mapping in config['delegations'].items():
        # Secret values belong in environment, not the configuration template.
        if set(mapping) != {'account_id', 'authorization_env'}:
            raise ValueError('Invalid credential reference')
        key = mapping['authorization_env']
        if not isinstance(key, str) or not re.fullmatch(r'AIBANG2_CONFLUENCE_[A-Z0-9_]+', key):
            raise ValueError('Invalid environment reference')
        value = os.environ.get(key)
        if value:
            delegations[user_id] = Delegation(mapping['account_id'], value)
    reader=ConfluenceReader(config['site'], config['tenant'], config['page_ids'],
                            [] if discovery_only else config['space_ids'], delegations,
                            cloud_id=config.get('cloud_id'),discovery_only=discovery_only)
    if prompt_actor is not None:
        if not sys.stdin.isatty() or prompt_actor not in config['delegations']:
            raise ValueError('Interactive mapped operator required')
        reader.delegations[prompt_actor]=hidden_delegation(config['delegations'][prompt_actor]['account_id'])
    return reader


def hidden_delegation(account_id):
    if not sys.stdin.isatty():
        raise ValueError('Interactive mapped operator required')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error',getpass.GetPassWarning)
            email=getpass.getpass('Atlassian email (hidden): ').strip()
            token=getpass.getpass('Scoped API token (hidden; not saved): ').strip()
    except getpass.GetPassWarning:
        raise ValueError('Secure hidden input unavailable') from None
    if (not re.fullmatch(r'[^\s:@]+@[^\s:@]+',email) or not token or len(token)>4096
            or '\r' in token or '\n' in token):
        raise ValueError('Invalid credential input')
    authorization='Basic '+base64.b64encode((email+':'+token).encode()).decode()
    return Delegation(account_id,authorization)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--actor', required=True)
    parser.add_argument('--page', required=True)
    parser.add_argument('--version', type=int)
    parser.add_argument('--live', action='store_true', help='Explicitly enable GET requests')
    parser.add_argument('--prompt-credential',action='store_true',help='Hidden TTY input; no secret is saved')
    parser.add_argument('--discover-space',action='store_true',help='Metadata-only setup, never reads page body')
    args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({'mode': 'not_run', 'reason': 'live_flag_required'}))
        return 2
    try:
        if args.prompt_credential or args.discover_space:
            reader=load_reader(args.config,prompt_actor=args.actor if args.prompt_credential else None,
                               discovery_only=args.discover_space)
        else:
            reader=load_reader(args.config)
        actor=Actor(args.actor,reader.tenant)
        if args.discover_space:
            decision,space_id=reader.discover_space_id(actor,args.page)
            print(json.dumps({'mode':'live_api_configuration_probe','decision':asdict(decision),
                              'space_id':space_id,'content_returned_to_probe':False}))
            return 0 if decision.result=='allow' else 1
        decision, content = reader.read(actor, args.page, args.version)
    except (OSError, ValueError, KeyError, TypeError,EOFError):
        print(json.dumps({'mode': 'not_run', 'reason': 'configuration_unavailable'}))
        return 2
    # Neither credentials, titles nor page text leave this diagnostic's stdout.
    result = {'mode': 'live_api_probe', 'decision': asdict(decision),
              'content_returned_to_probe': content is not None,
              'version': content['version'] if content else None}
    print(json.dumps(result))
    return 0 if decision.result == 'allow' else 1


if __name__ == '__main__':
    raise SystemExit(main())
