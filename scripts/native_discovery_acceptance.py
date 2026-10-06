"""Explicit AUTH-017 read-only native discovery; saved AUTH-014 credentials only.

No prompts, OAuth consent, credential writes, platform writes, paid model or server.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path

from brain.audit import verify_chain
from brain.confluence import ConfluenceReader,Delegation
from brain.contracts import Actor,now
from brain.delegated_query import DelegatedQueryPilot
from brain.discovery import AUTH017,ContainerDiscovery
from brain.drive import DriveReader
from brain.drive_oauth import load_client,refresh_access,verify_account
from brain.jira import JiraReader
from brain.keychain import MacKeychain
from brain.slack import SlackReader
from brain.store import Store
from scripts.build_metadata import revision


def prepare(path):
    path=Path(path);bundle=json.loads(path.read_text())
    if (set(bundle)!={'approved_synthetic_only','identity_mapping_reviewed','sources'}
            or bundle['approved_synthetic_only'] is not True or bundle['identity_mapping_reviewed'] is not True
            or set(bundle['sources'])!=set(AUTH017)):
        raise ValueError('Reviewed four-source bundle required')
    configs={source:json.loads((path.parent/reference).read_text()) for source,reference in bundle['sources'].items()}
    readers={}
    for source,c in configs.items():
        if c.get('approved_synthetic_only') is not True:raise ValueError('Synthetic source required')
        if source=='drive':
            if c['oauth_operator']['actor']!='eng_b':raise ValueError('Existing eng_b OAuth mapping required')
            readers[source]=DriveReader(c['tenant'],c['files'],{'eng_b':Delegation('validation-only','Bearer validation-only')})
            continue
        mapping=c['delegations']['eng_b']
        if set(mapping)!={'account_id','authorization_env'}:raise ValueError('Existing credential reference required')
        delegations={'eng_b':Delegation(mapping['account_id'],'Bearer validation-only')}
        if source=='confluence':
            readers[source]=ConfluenceReader(c['site'],c['tenant'],c['page_ids'],c['space_ids'],delegations,cloud_id=c.get('cloud_id'))
        elif source=='jira':
            readers[source]=JiraReader(c['site'],c['tenant'],c['issues'],c['project_ids'],delegations,
                cloud_id=c.get('cloud_id'),comment_ids=c.get('comment_ids'))
        else:
            readers[source]=SlackReader(c['site'],c['tenant'],c['team_id'],c['channels'],c['messages'],delegations)
    return readers,configs


def saved_credentials(readers,configs,client_path,keychain):
    # Caller validates ContainerDiscovery scope before ANY Keychain/API operation.
    for source in sorted(readers):
        reader=readers[source];config=configs[source]
        if source=='drive':
            client=load_client(client_path,config['oauth_client_id'])
            email=config['oauth_operator']['email'];account=client.client_id+'|'+email.casefold()
            saved=keychain.get('drive',reader.tenant,'eng_b',account)
            if not saved:raise ValueError('Saved Drive grant unavailable')
            token=refresh_access(client,saved)  # Existing exact read-only grant, no consent fallback.
            reader.delegations['eng_b']=verify_account(token,email,reader.transport)
            del saved,token
        else:
            account=config['delegations']['eng_b']['account_id']
            saved=keychain.get(source,reader.tenant,'eng_b',account)
            if not saved:raise ValueError('Saved source credential unavailable')
            reader.delegations['eng_b']=Delegation(account,saved)
            del saved


def run(output,config,client):
    output=Path(output)
    if output.exists():raise FileExistsError('Preserve evidence; choose a new directory')
    output.mkdir(parents=True)
    report={'started_at':now(),'commit':revision(),'mode':'four_source_live_api_fake_model',
        'authorization':['AUTH-014','AUTH-017'],'actor':'eng_b','source_writes':False,
        'credential_writes':False,'model_network_calls':0,'browser':'not_run','live_model':'not_run',
        'human_G1':'not_run','lifecycle_latency':'not_run',
        'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('brain','scripts')
                       for p in sorted(Path(folder).glob('*.py'))}}
    store=discovery=pilot=None;phase='configuration';checks={}
    def write(name,value):
        with (output/(name+'.json')).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
    try:
        readers,configs=prepare(config);store=Store();pilot=DelegatedQueryPilot(readers,store,live=True)
        actor=Actor('eng_b',pilot.authority.tenant)
        discovery=ContainerDiscovery(pilot,actor)  # Scope validation before credentials/API.
        phase='saved_credentials';saved_credentials(readers,configs,client,MacKeychain())
        phase='native_identity'
        identities=[]
        for source,reader in sorted(readers.items()):
            if source=='confluence':reader._credential(actor,sorted(reader.page_ids)[0])
            else:reader._credential(actor)
            identities.append(source)
            print('native_identity_verified: '+source,flush=True)
        report['verified_identities']=identities
        baseline_ids={s:sorted(ids) for s,ids in pilot.authority.native_ids.items()}
        report['baseline_ids']=baseline_ids
        phase='discovery';print('native_discovery_started',flush=True)
        start=time.monotonic();cycles=discovery.run_once();report['cycle_elapsed_seconds']=time.monotonic()-start
        write('discovery-cycle',cycles)
        for source,row in cycles.items():
            print('native_discovery_result: '+source+' '+row['status']+' '+str(row['reason']),flush=True)
        report['new_ids']={s:sorted(pilot.authority.discovered_ids.get('eng_b',{}).get(s,())) for s in AUTH017}
        checks['four_native_identities_verified']=set(identities)==set(AUTH017)
        checks['four_source_cycles_complete']=set(cycles)==set(AUTH017) and all(r['status']=='complete' for r in cycles.values())
        checks['new_native_resource_discovered']=any(report['new_ids'].values())
        # Do not turn partial discovery into successful live query acceptance.
        if not checks['four_source_cycles_complete']:raise ValueError('Native discovery incomplete')
        phase='query';print('native_fake_model_query_started',flush=True)
        query_started=now();answer=pilot.query(actor,'What is the update-check queue revision?')
        write('answer',{'started_at':query_started,'returned_at':now(),'response':answer})
        new_resources={s+':'+i for s,ids in report['new_ids'].items() for i in ids}
        discovered_evidence=[e for e in answer['evidence'] if e['resource_id'] in new_resources]
        checks['discovered_resource_in_actual_answer']=bool(discovered_evidence)
        preview_checks=[]
        for e in discovered_evidence:
            preview=pilot.evidence(actor,e['evidence_id'])
            preview_checks.append({'evidence_id':e['evidence_id'],'matches_exact_text':preview['text']==e['text']})
        write('discovered-previews',preview_checks)
        checks['discovered_previews_match']=bool(preview_checks) and all(r['matches_exact_text'] for r in preview_checks)
        baseline_unchanged={source:(sorted(getattr(reader,'page_ids',getattr(reader,'native_ids',())))==baseline_ids[source]) for source,reader in readers.items()}
        checks['original_reader_allowlists_unchanged']=all(baseline_unchanged.values())
        checks['discovery_not_granted_to_product_ops']=not pilot.authority.discovered_ids.get('product_ops')
        write('published-resources',store.resources())
        checks['audit_chain_valid']=verify_chain(pilot.audit.export())['valid']
        report['status']='verified_native_subset' if all(checks.values()) else 'failed'
    except Exception as error:
        report['status']='failed';report['failure_phase']=phase;report['error_type']=type(error).__name__
        print('native_acceptance_stopped: '+phase+' '+type(error).__name__+' (upstream details suppressed)',flush=True)
    finally:
        if store is not None and pilot is not None:
            write('audit',pilot.audit.export());write('chain-check',verify_chain(pilot.audit.export()))
        if discovery is not None:discovery.close()
        if store is not None:store.db.close()
        report['checks']=checks;report['finished_at']=now();write('verification',report)
    return 0 if report['status']=='verified_native_subset' else 1


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true');parser.add_argument('--output',required=True)
    parser.add_argument('--config',default='.runtime/operator-bundle.json')
    parser.add_argument('--oauth-client',default='.runtime/drive-oauth-client.json')
    args=parser.parse_args(argv)
    if not args.live:
        print('not_run: explicit --live required; no credential or API access.');return 2
    return run(args.output,args.config,args.oauth_client)


if __name__=='__main__':raise SystemExit(main())
