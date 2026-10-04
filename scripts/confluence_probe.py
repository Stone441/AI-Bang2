"""Operator-only live diagnostic; this is not an employee login endpoint."""
import argparse
import json
import os
import re
from dataclasses import asdict
from pathlib import Path

from brain.confluence import ConfluenceReader, Delegation
from brain.contracts import Actor


def load_reader(path):
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
    return ConfluenceReader(config['site'], config['tenant'], config['page_ids'],
                            config['space_ids'], delegations, cloud_id=config.get('cloud_id'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--actor', required=True)
    parser.add_argument('--page', required=True)
    parser.add_argument('--version', type=int)
    parser.add_argument('--live', action='store_true', help='Explicitly enable GET requests')
    args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({'mode': 'not_run', 'reason': 'live_flag_required'}))
        return 2
    try:
        reader = load_reader(args.config)
        decision, content = reader.read(Actor(args.actor, reader.tenant), args.page, args.version)
    except (OSError, ValueError, KeyError, TypeError):
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
