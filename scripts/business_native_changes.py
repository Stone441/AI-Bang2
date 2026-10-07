"""AUTH-021 owner-written probes; program credentials remain read-only.

Explicit one-shot operator capture, not a worker SLA or a live-model evaluation.
The persistent isolated index retains prior versions; phase evidence is create-only.
"""
import argparse
import hashlib
import json
import re
import time
from pathlib import Path

from brain.audit import verify_chain
from brain.contracts import Actor, now
from brain.discovery import ContainerDiscovery
from brain.keychain import MacKeychain
from brain.store import Store
from scripts.build_metadata import revision
from scripts.native_discovery_acceptance import prepare, saved_credentials
from brain.confluence import JsonTransport


class CountedTransport(JsonTransport):
    """Preserve actual live transport classification; retain counts only."""
    def __init__(self, transport):self.transport=transport;self.requests=0
    def get(self,*args):
        self.requests+=1;return self.transport.get(*args)
    def media(self,*args):
        self.requests+=1;return self.transport.media(*args)


def run(root, phase, capture_name=None, sources=('confluence','jira','slack','drive'), background=False):
    capture_name=capture_name or phase
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,63}',capture_name):raise ValueError('Bounded capture label required')
    if not set(sources)<=set(('confluence','jira','slack','drive')) or not sources:
        raise ValueError('Approved source subset required')
    root=Path(root);output=root/('capture-'+capture_name)
    output.mkdir(exist_ok=False)
    def write(name, value):
        with (output/(name+'.json')).open('x') as f:
            json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    report={'started_at':now(),'revision':revision(),'mode':'native_api_fake_model',
            'authorization':['AUTH-014','AUTH-017','AUTH-021'],
            'source_writes_by_runner':False,'model_network_calls':0,
            'measurement':'manual one-shot after owner UI; not automatic polling latency',
            'browser_product':'blocked','G1':'not_run','G2':'not_run',
            'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()
                for folder in ('brain','scripts') for p in sorted(Path(folder).glob('*.py'))}}
    store=discovery=pilot=None
    try:
        readers,configs=prepare('.runtime/operator-bundle.json')
        counters={s:CountedTransport(r.transport) for s,r in readers.items()}
        for s,r in readers.items():r.transport=counters[s]
        store=Store(root/'isolated-index.sqlite')
        from brain.delegated_query import DelegatedQueryPilot
        pilot=DelegatedQueryPilot(readers,store,live=True)
        actor=Actor('eng_b',pilot.authority.tenant)
        discovery=ContainerDiscovery(pilot,actor,bounded_queries=background)
        saved_credentials(readers,configs,'.runtime/drive-oauth-client.json',MacKeychain())
        cycle_start=now()
        if background:discovery.start()
        cycles=discovery.run_once();write('cycles',cycles)
        report['background_worker_enabled']=background
        report['cycle_started_at']=cycle_start
        value='green' if phase=='green' else 'amber'
        checks={}
        for source in ('confluence','jira','slack','drive'):
            if source not in sources:
                report[source]={'status':'not_run','reason':'not selected in this capture'};continue
            ui=root/(source+'-'+phase+'-ui.json')
            if not ui.exists():
                report[source]={'status':'not_run','reason':'no owner-confirmed probe for this phase'}
                continue
            confirmation=json.loads(ui.read_text())
            probes=[r for r in store.resources() if r['source']==source
                    and 'BV-20261007' in r['text']]
            # Slack correction replies form distinct native resources, not root edits.
            expected_id=confirmation.get('native_id')
            if expected_id:probes=[r for r in probes if r['native_id']==expected_id]
            if source!='slack':
                probes=[r for r in probes if r['title'].startswith('[SYNTHETIC] BV-20261007 change probe '+source)]
            checks[source+'_published']=len(probes)==1 and cycles[source]['status']=='complete'
            print('probe_published: '+source+' '+str(checks[source+'_published']),flush=True)
            if not checks[source+'_published']:
                report[source]={'status':'failed','owner_confirmation':confirmation};continue
            resource=probes[0];write(source+'-resource',resource)
            started=now();t=time.monotonic()
            question='What is the approved probe value for BV-20261007 '+source+'?'
            with pilot.lock:
                execution_start=time.monotonic()
                counts_before={s:c.requests for s,c in counters.items()}
                answer=pilot.query(actor,question);returned=now()
                execution_duration=time.monotonic()-execution_start
                query_calls={s:c.requests-counts_before[s] for s,c in counters.items()}
            query_duration=time.monotonic()-t
            write(source+'-answer',answer)
            matching=[e for e in answer['evidence'] if e['resource_id']==resource['id']
                      and e['version']==resource['version']]
            checks[source+'_current_evidence']=bool(matching)
            checks[source+'_exact_preview']=bool(matching) and all(
                pilot.evidence(actor,e['evidence_id'])['text']==e['text'] for e in matching)
            checks[source+'_expected_value_in_claim']=any(
                'probe value '+value in c['text'].lower() and
                any(e['evidence_id'] in c['evidence_ids'] for e in matching)
                for c in answer['claims'])
            write(source+'-history',pilot.history(actor,answer['request_id']))
            report[source]={'status':'verified_excerpt_subset' if all(checks[k] for k in checks if k.startswith(source+'_')) else 'failed',
                'owner_confirmation':confirmation,'resource_id':resource['id'],'version':resource['version'],
                'source_updated_at':resource['source_updated_at'],'observed_at':resource.get('observed_at'),
                'indexed_at':resource['indexed_at'],'query_started_at':started,'answer_returned_at':returned,
                'query_elapsed_seconds':query_duration,
                'query_execution_seconds':execution_duration,
                'query_queue_seconds':execution_start-t,
                'query_native_transport_attempts':query_calls,
                'query_plus_preview_history_seconds':time.monotonic()-t,
                'observed_at_semantics':'discovery source cycle began; not exact target read completion',
                'semantic_latest_value_resolution':'not_proved_by_excerpt_fake' if source=='slack' else 'exact current excerpt only'}
        discovery.close()  # Quiesce worker before pairing the final audit snapshot/head.
        events=pilot.audit.export()
        write('resources',store.resources());write('audit',events)
        report['chain']=verify_chain(events);report['checks']=checks
        report['status']='verified_subset' if checks and all(checks.values()) and report['chain']['valid'] else 'failed'
    except Exception as error:
        report['status']='failed';report['error_type']=type(error).__name__
        print('capture_failed: '+type(error).__name__+' (upstream details suppressed)',flush=True)
    finally:
        if discovery:discovery.close()
        if store:store.db.close()
        report['finished_at']=now();write('verification',report)
    return 0 if report['status']=='verified_subset' else 1


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true');parser.add_argument('--root',required=True)
    parser.add_argument('--phase',choices=['amber','green','amber-return'],required=True)
    parser.add_argument('--capture-name')
    parser.add_argument('--sources',nargs='+',choices=['confluence','jira','slack','drive'],default=['confluence','jira','slack','drive'])
    parser.add_argument('--background',action='store_true')
    args=parser.parse_args()
    if not args.live:raise SystemExit('not_run: explicit --live required')
    raise SystemExit(run(args.root,args.phase,args.capture_name,args.sources,args.background))
