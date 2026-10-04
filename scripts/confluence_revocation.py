"""Operator-only live revocation acceptance; source mutation is done separately.

One hidden credential entry, one pilot instance and one logical conversation.
The local model is fake; this is not a browser session or four-source acceptance.
"""
import argparse
import json
import os
import sqlite3
import tempfile
import uuid
from pathlib import Path

from brain.audit import verify_chain
from brain.confluence_query import ConfluenceQueryPilot
from brain.contracts import Actor, now
from brain.store import Store
from scripts.confluence_probe import load_reader


def exercise(pilot,actor,page_id,wait_for_revoke):
    resource_id='confluence:'+page_id
    baseline=pilot.query(actor,'Show the payment-service runbook')
    evidence=next((e for e in baseline['evidence'] if e['resource_id']==resource_id),None)
    if evidence is None:
        return {'status':'failed','reason':'baseline_evidence_unavailable',
                'baseline_request_id':baseline['request_id']}
    wait_for_revoke(baseline['request_id'],evidence['evidence_id'])
    call_offset=len(pilot.engine.model.calls)
    followup=pilot.query(actor,'Show that runbook again with details',baseline['request_id'])
    history=pilot.history(actor,baseline['request_id'])
    citation_denied=False
    try:
        pilot.evidence(actor,evidence['evidence_id'])
    except PermissionError:
        citation_denied=True
    events=pilot.audit.export()
    native_denial=any(e['request_id']==followup['request_id']
                      and e['event_type']=='authorization_decided'
                      and e['payload'].get('resource_id')==resource_id
                      and e['payload'].get('phase')=='source_refresh'
                      and e['payload'].get('method')=='confluence-delegated-current-read'
                      and e['payload'].get('result')=='deny' for e in events)
    checks={
        'source_returns_deny_not_unknown':native_denial,
        'followup_excludes_revoked_resource':not any(e['resource_id']==resource_id for e in followup['evidence']),
        'model_input_excludes_revoked_resource':not any(e['resource_id']==resource_id
                      for call in pilot.engine.model.calls[call_offset:] for e in call['evidence']),
        'old_answer_unavailable':bool(history and history[0].get('unavailable') is True),
        'old_citation_unavailable':citation_denied,
        'indexed_copy_retained_without_rebuild':pilot.engine.store.get(resource_id) is not None,
        'audit_chain_valid':verify_chain(events)['valid'],
    }
    return {'mode':pilot.engine.mode,'status':'passed_operator_subset' if all(checks.values()) else 'failed',
            'checks':checks,'baseline_request_id':baseline['request_id'],
            'followup_request_id':followup['request_id'],'evidence_id':evidence['evidence_id'],
            'audit_events':len(events),'signature_verified':False,
            'boundary':'Confluence API + fake model; trusted local operator, not frontend SSO; no independent signature checkpoint'}


def write_report(path,report):
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.revocation-',text=True)
    try:
        with os.fdopen(fd,'w') as stream:
            json.dump(report,stream,indent=2);stream.write('\n')
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--actor',default='eng_b')
    parser.add_argument('--page',default='98564')
    parser.add_argument('--live',action='store_true')
    args=parser.parse_args(argv)
    if not args.live:
        print(json.dumps({'mode':'not_run','reason':'live_flag_required'}));return 2
    store=None;report_path=None;report={};started_query=False
    try:
        reader=load_reader(args.config,prompt_actor=args.actor)
        if args.page not in reader.page_ids:
            raise ValueError('Unapproved page')
        runtime=Path('.runtime').resolve();runtime.mkdir(exist_ok=True)
        run_dir=runtime/('confluence-revocation-'+uuid.uuid4().hex)
        run_dir.mkdir(mode=0o700)
        report_path=run_dir/'report.json'
        store=Store(str(run_dir/'query.sqlite'))
        os.chmod(run_dir/'query.sqlite',0o600)
        pilot=ConfluenceQueryPilot(reader,store,live=True)
        report={'mode':'confluence_live_api_fake_model','started_at':now(),
                'actor':args.actor,'page_id':args.page,'status':'in_progress'}
        def wait_for_revoke(request_id,evidence_id):
            report.update(status='awaiting_source_revocation',baseline_request_id=request_id,
                          evidence_id=evidence_id)
            write_report(report_path,report)
            print(json.dumps({'status':'awaiting_source_revocation','report':str(report_path)}),flush=True)
            input('Wait for the test page restriction change. Press Enter only after it is saved: ')
        started_query=True
        result=exercise(pilot,Actor(args.actor,reader.tenant),args.page,wait_for_revoke)
        report.update(result,finished_at=now())
        write_report(report_path,report)
        print(json.dumps({'status':report['status'],'report':str(report_path)}))
        return 0 if report['status']=='passed_operator_subset' else 1
    except (OSError,ValueError,KeyError,TypeError,PermissionError,RuntimeError,sqlite3.Error,EOFError):
        report.update(status='failed',reason='acceptance_stopped',finished_at=now())
        if report_path is not None:write_report(report_path,report)
        print(json.dumps({'mode':'confluence_live_api_fake_model' if started_query else 'not_run',
                          'status':'failed','reason':'acceptance_stopped'}));return 2
    finally:
        if store is not None:store.db.close()


if __name__=='__main__':raise SystemExit(main())
