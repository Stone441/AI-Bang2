"""Offline automatic poll timing; mock HTTP and fake model, no native claims."""
import copy,json,threading,time
from pathlib import Path
from brain.audit import verify_chain
from brain.contracts import Actor,now
from brain.discovery import ContainerDiscovery
from test_container_discovery import setup

root=Path(__file__).parent
store,pilot,http,_=setup();actor=Actor('eng_b','pilot')
worker=ContainerDiscovery(pilot,actor,bounded_queries=True)
ready=threading.Event();published=threading.Event();times={};original=worker._finish_cycle
original_get=http['confluence'].get

def get(url,authorization):
    if '/spaces/' in url and 'source_change_at' in times:
        times.setdefault('discovery_listing_at',now());times.setdefault('discovery_listing_monotonic',time.monotonic())
    return original_get(url,authorization)
http['confluence'].get=get

def finish(source,status,reason,retry_after,observed,budget,counter,staged,started,timing,rid):
    original(source,status,reason,retry_after,observed,budget,counter,staged,started,timing,rid)
    if source=='confluence' and '98566' in staged and status=='complete':
        times['publication_at']=now();times['publication_monotonic']=time.monotonic();published.set()
    if set(worker.last)==set(worker.scope):ready.set()
worker._finish_cycle=finish
report={'code_commit':'cdbd62b','mode':'mock_http_fixture_fake_model','cycle_min_interval_seconds':60,
        'poll_sleep_seconds':1,'source_writes':'local fixture only','native_freshness':'not_run_requires_new_specific_write_authorization'}
try:
    worker.start()
    if not ready.wait(5):raise RuntimeError('Initial worker publication missing')
    resource=copy.deepcopy(http['confluence'].content['98565'])
    resource.update(id='98566',title='[SYNTHETIC] freshnessrepair')
    resource['body']['storage']['value']='<p>[SYNTHETIC] freshnessrepair uses the new automatic poll.</p>'
    times['source_change_at']=now();times['source_change_monotonic']=time.monotonic()
    http['confluence'].content['98566']=resource
    if not published.wait(70):raise RuntimeError('Automatic discovery missing')
    start=time.monotonic();answer=pilot.query(actor,'freshnessrepair')
    times['answer_at']=now();times['answer_monotonic']=time.monotonic()
    assert any('new automatic poll' in c['text'] for c in answer['claims'])
    report.update(status='verified_mock_automatic_poll',times=times,
        change_to_listing_seconds=times['discovery_listing_monotonic']-times['source_change_monotonic'],
        change_to_publication_seconds=times['publication_monotonic']-times['source_change_monotonic'],
        change_to_answer_seconds=times['answer_monotonic']-times['source_change_monotonic'],
        query_seconds=times['answer_monotonic']-start,chain=verify_chain(pilot.audit.export()))
    (root/'freshness-answer.json').write_text(json.dumps(answer,indent=2)+'\n')
finally:
    worker.close();store.db.close()
    (root/'freshness-mock.json').write_text(json.dumps(report,indent=2)+'\n')
print(report.get('status','failed'),flush=True)
