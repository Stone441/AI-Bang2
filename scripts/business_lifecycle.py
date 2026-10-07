"""Five worked fixture scenes in the same 48-object business world, no live APIs/models."""
import argparse
import hashlib
import json
from pathlib import Path
from brain.audit import Audit,verify_chain
from brain.contracts import Actor,now
from brain.engine import Engine
from brain.ingestion import Ingestion
from brain.store import Store
from scripts.business_validation import build_world
from scripts.build_metadata import revision


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    def save(name,value):(output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    world,_=build_world();store=Store();store.initialize(world);audit=Audit(store);engine=Engine(store,world,audit)
    report={'started_at':now(),'commit':revision(),'mode':'fixture_fake_model','world_objects':len(world.resources),
            'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),*sorted(Path('brain').glob('*.py'))]},
            'native':'not_run','live_model':'not_run','browser':'blocked_saved_site_denial','G1':'not_run','G2':'not_run'}
    try:
        save('world-initial.json',{'users':world.users,'resources':list(world.resources.values())})
        product=engine.query(Actor('product_ops'),'Can payment-retry be offered to all customers? Does PAY-102 Done mean release approval?')
        assert any('not approved' in c['text'].lower() for c in product['claims'])
        engineering=engine.query(Actor('eng_a'),'payment-service incident cause withdrawn hypothesis safeguard status owner runbook')
        assert {'C-01','D-01','S-01','J-03'}<={e['resource_id'] for e in engineering['evidence']}
        save('S01-product-engineering.json',{'product':product,'engineering':engineering})
        old=next(e['evidence_id'] for e in engineering['evidence'] if e['resource_id']=='C-01')
        update=world.mutate('C-01','content',**world.baseline['updates']['C-01'])
        sync=Ingestion(store,world).process(update)
        latest=engine.query(Actor('eng_a'),'latest payment-service runbook standby processing queue')
        assert sync['processed_objects']==1
        assert any(e['resource_id']=='C-01' and e['version']==2 and 'standby processing queue' in e['text'] for e in latest['evidence'])
        try:engine.evidence(Actor('eng_a'),old)
        except PermissionError:old_denied=True
        else:raise AssertionError('Old version preview allowed')
        save('S02-update.json',{'object_scoped_sync':sync,'answer':latest,'old_preview_denied':old_denied,'management':'fixture event, not native source action'})
        restricted=engine.query(Actor('contractor'),'Q3 security incident CANARY_BV_RESTRICTED')
        assert restricted['evidence']==[]
        assert 'CANARY_SEC' not in json.dumps(restricted) and 'CANARY_BV_RESTRICTED' not in json.dumps(restricted['claims'])
        channel_yes=engine.query(Actor('eng_a'),'private partner-escalation channel membership')
        channel_no=engine.query(Actor('eng_b'),'private partner-escalation channel membership')
        assert 'BV-26' in {e['resource_id'] for e in channel_yes['evidence']}
        assert 'BV-26' not in {e['resource_id'] for e in channel_no['evidence']}
        save('S03-permissions.json',{'restricted':restricted,'same_engineering_role_allowed':channel_yes,'same_engineering_role_denied':channel_no})
        before=engine.query(Actor('eng_a'),'payment-service incident thread')
        prior=next(e['evidence_id'] for e in before['evidence'] if e['resource_id']=='S-01')
        world.mutate('S-01','revoke',user_id='eng_a')
        after=engine.query(Actor('eng_a'),'payment-service incident thread')
        assert 'S-01' not in {e['resource_id'] for e in after['evidence']}
        try:engine.evidence(Actor('eng_a'),prior)
        except PermissionError:preview_denied=True
        else:raise AssertionError('Revoked preview allowed')
        history=engine.safe_history(Actor('eng_a'),before['request_id']);assert history[0]['unavailable']
        save('S04-revocation.json',{'before':before,'after':after,'old_preview_denied':preview_denied,'history':history,'management':'fixture-only revocation; no native ACL write'})
        actor_inquiry=audit.inquire(Actor('auditor'),{'actor':'eng_a','resource_scope':'payment-service'})
        resource_inquiry=audit.inquire(Actor('auditor'),{'resource_id':'J-03'})
        assert actor_inquiry['events'] and resource_inquiry['events']
        save('S05-inquiries.json',{'actor':actor_inquiry,'resource':resource_inquiry,'caller':'explicit local fixture auditor'})
        save('audit.json',audit.export());report['chain']=verify_chain(audit.export());assert report['chain']['valid']
        report['status']='verified_local_subset';report['scenes']={sid:'passed_local_subset' for sid in ('S-01','S-02','S-03','S-04','S-05')}
    except Exception as exc:report['status']='failed';report['error_type']=type(exc).__name__;raise
    finally:
        store.db.close();report['finished_at']=now();save('verification.json',report)
    print('Five scenes / same-role channel boundary verified in one 48-object fixture world')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.output)
