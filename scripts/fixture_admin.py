"""Local-only synthetic source management, deliberately absent from the HTTP API."""
import argparse
from pathlib import Path
from brain.sources import FixtureWorld
from brain.contracts import now


def main():
    parser=argparse.ArgumentParser(description='Change only the local synthetic source. Run one admin at a time.')
    parser.add_argument('action',choices=['runbook-v2','revoke','delete'])
    parser.add_argument('--resource',default='S-01');parser.add_argument('--user',default='eng_a')
    parser.add_argument('--source-file',default='.runtime/source.json')
    args=parser.parse_args();path=Path(args.source_file)
    if not path.is_file():parser.error('Start make demo first to create its synthetic authority file.')
    world=FixtureWorld();world.refresh(path)
    if args.action=='runbook-v2':
        update=dict(world.baseline['updates']['C-01']);update['source_updated_at']=now()
        if world.resources['C-01']['version']>=2:parser.error('Runbook v2 already published')
        event=world.mutate('C-01','content',**update)
    elif args.action=='revoke':
        if args.user not in world.users:parser.error('Unknown synthetic user')
        event=world.mutate(args.resource,'revoke',user_id=args.user)
    else:event=world.mutate(args.resource,'delete')
    world.save(path)
    print(f"Synthetic event {event['event_id']} persisted. The next application request will observe and process it.")

if __name__=='__main__':main()
