"""Jira trusted-operator pilot. No employee login or source writes."""
import argparse
import json
import os
import re
import sqlite3
from dataclasses import asdict
from pathlib import Path

from brain.confluence import Delegation, JsonTransport
from brain.contracts import Actor
from brain.delegated_query import DelegatedQueryPilot
from brain.jira import JiraReader
from brain.store import Store
from scripts.confluence_probe import hidden_delegation


def load_reader(path, prompt_actor=None):
    config = json.loads(Path(path).read_text())
    if config.get('approved_synthetic_only') is not True:
        raise ValueError('Synthetic approval required')
    delegations = {}
    for uid, mapping in config['delegations'].items():
        if set(mapping) != {'account_id', 'authorization_env'}:
            raise ValueError('Invalid credential reference')
        key = mapping['authorization_env']
        if not isinstance(key, str) or not re.fullmatch(r'AIBANG2_JIRA_[A-Z0-9_]+', key):
            raise ValueError('Jira-specific credential reference required')
        value = os.environ.get(key)
        if value:
            delegations[uid] = Delegation(mapping['account_id'], value)
    reader = JiraReader(config['site'], config['tenant'], config['issues'],
                        config['project_ids'], delegations, comment_ids=config.get('comment_ids'),
                        cloud_id=config.get('cloud_id'))
    if prompt_actor is not None:
        if prompt_actor not in config['delegations']:
            raise ValueError('Mapped operator required')
        reader.delegations[prompt_actor] = hidden_delegation(config['delegations'][prompt_actor]['account_id'])
    return reader


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--actor', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--resource', help='Allowlisted native issue ID or issue/comment/ID; metadata-only stdout')
    group.add_argument('--question', help='Print authorized synthetic answer and references')
    parser.add_argument('--history-id')
    parser.add_argument('--db', default='.runtime/jira-query.sqlite')
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--prompt-credential', action='store_true')
    args = parser.parse_args(argv)
    if not args.live:
        print(json.dumps({'mode': 'not_run', 'reason': 'live_flag_required'})); return 2
    store = None; started = False
    try:
        reader = load_reader(args.config, args.actor if args.prompt_credential else None)
        actor = Actor(args.actor, reader.tenant)
        if args.resource:
            started = True
            decision, content = reader.read(actor, args.resource)
            print(json.dumps({'mode': 'jira_live_api_probe' if isinstance(reader.transport, JsonTransport) else 'jira_mock_http_probe', 'decision': asdict(decision),
                              'content_returned_to_probe': content is not None,
                              'version': content['version'] if content else None}))
            return 0 if decision.result == 'allow' else 1
        path = Path(args.db).resolve()
        if not path.is_relative_to(Path('.runtime').resolve()):
            raise ValueError('Local runtime path required')
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        store = Store(str(path)); os.chmod(path, 0o600)
        pilot = DelegatedQueryPilot({'jira': reader}, store, live=True)
        started = True
        print(json.dumps(pilot.query(actor, args.question, args.history_id), ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, PermissionError, RuntimeError, sqlite3.Error, EOFError):
        print(json.dumps({'mode': 'jira_live_api_fake_model' if started else 'not_run',
                          'status': 'failed', 'reason': 'operation_stopped'})); return 2
    finally:
        if store is not None: store.db.close()


if __name__ == '__main__': raise SystemExit(main())
