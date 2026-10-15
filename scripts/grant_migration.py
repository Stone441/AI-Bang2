"""Prepare a private checked grant migration, or apply its exact reviewed digest.

Planning reads a SQLite backup, preserving the original ledger and legacy JSON.
Applying requires unchanged legacy bytes and reservation snapshot. No model calls.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
from brain.budget import BudgetLedger
from scripts.attributed_allowance import migration_plan, apply_migration


def digest(raw):return hashlib.sha256(raw).hexdigest()


def prepare(ledger_path, state_path, grant_id, output, external=None):
    raw=state_path.read_bytes()
    with tempfile.TemporaryDirectory() as folder:
        snapshot=Path(folder)/'budget.sqlite'
        source=sqlite3.connect(ledger_path.resolve().as_uri()+'?mode=ro',uri=True)
        target=sqlite3.connect(snapshot)
        try:source.backup(target)
        finally:target.close();source.close()
        ledger=BudgetLedger(str(snapshot))
        try:plan=migration_plan(ledger,grant_id,json.loads(raw),external_reservations=external)
        finally:ledger.close()
    envelope={'schema':1,'legacy_state_sha256':digest(raw),'plan':plan}
    payload=(json.dumps(envelope,sort_keys=True,indent=2)+'\n').encode()
    fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(payload)
    return digest(payload)


def apply(ledger_path,state_path,plan_path,expected_sha256):
    payload=plan_path.read_bytes()
    if digest(payload)!=expected_sha256:raise ValueError('Reviewed envelope digest required')
    envelope=json.loads(payload)
    if envelope['schema']!=1 or digest(state_path.read_bytes())!=envelope['legacy_state_sha256']:
        raise ValueError('Legacy state changed; regenerate and review plan')
    if ledger_path.is_symlink() or not ledger_path.is_file():raise ValueError('Original ledger required')
    ledger=BudgetLedger(str(ledger_path))
    try:apply_migration(ledger,envelope['plan'],expected_plan_sha256=digest(envelope['plan'].encode()))
    finally:ledger.close()


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['plan','apply'])
    parser.add_argument('--ledger',type=Path,required=True)
    parser.add_argument('--legacy-state',type=Path,required=True)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--grant-id')
    parser.add_argument('--external-evidence',type=Path)
    parser.add_argument('--expected-sha256')
    args=parser.parse_args(argv)
    if args.action=='plan':
        if not args.grant_id:parser.error('Plan requires stable grant ID')
        external=json.loads(args.external_evidence.read_text()) if args.external_evidence else None
        print(prepare(args.ledger,args.legacy_state,args.grant_id,args.plan,external))
    else:
        if not args.expected_sha256:parser.error('Apply requires exact reviewed envelope digest')
        apply(args.ledger,args.legacy_state,args.plan,args.expected_sha256)
        print('Checked migration applied; original costs and reservations preserved.')


if __name__=='__main__':main()
