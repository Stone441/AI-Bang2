"""Local operator query pilot, not a frontend login or production server."""
import argparse
import json
import sqlite3
from pathlib import Path

from brain.confluence_query import ConfluenceQueryPilot
from brain.contracts import Actor
from brain.store import Store
from scripts.confluence_probe import load_reader


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--actor',required=True)
    parser.add_argument('--question',required=True)
    parser.add_argument('--db',default='.runtime/confluence-query.sqlite')
    parser.add_argument('--history-id')
    parser.add_argument('--live',action='store_true')
    args=parser.parse_args(argv)
    if not args.live:
        print(json.dumps({'mode':'not_run','reason':'live_flag_required'}))
        return 2
    store=None
    query_started=False
    try:
        reader=load_reader(args.config)
        # Persist only inside the ignored local runtime directory.
        path=Path(args.db).resolve()
        runtime=Path('.runtime').resolve()
        if not path.is_relative_to(runtime):
            raise ValueError('Local runtime path required')
        path.parent.mkdir(parents=True,exist_ok=True)
        store=Store(str(path))
        pilot=ConfluenceQueryPilot(reader,store,live=True)
        query_started=True
        result=pilot.query(Actor(args.actor,reader.tenant),args.question,args.history_id)
        print(json.dumps(result,ensure_ascii=False))
        return 0
    except (OSError,ValueError,KeyError,TypeError,PermissionError,RuntimeError,sqlite3.Error):
        print(json.dumps({'mode':'confluence_live_api_fake_model' if query_started else 'not_run',
                          'status':'failed','reason':'query_stopped'}))
        return 2
    finally:
        if store is not None:
            store.db.close()


if __name__=='__main__':
    raise SystemExit(main())
