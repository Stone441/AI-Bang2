"""AUTH-017 read-only CLI observer; creation is a separately approved owner UI step."""
import hashlib,json,time
from pathlib import Path
from brain.audit import verify_chain
from brain.contracts import Actor,now
from brain.delegated_query import DelegatedQueryPilot
from brain.discovery import ContainerDiscovery
from brain.keychain import MacKeychain
from brain.store import Store
from scripts.build_metadata import revision
from scripts.native_discovery_acceptance import prepare,saved_credentials
from scripts.validation_timing import Measurements,TimedNativeTransport

root=Path(__file__).parent/'native-freshness';root.mkdir(exist_ok=False)
def save(name,value):(root/name).write_text(json.dumps(value,indent=2)+'\n')
report={'code_commit':revision(),'started_at':now(),'mode':'native_api_fake_model','source_writes':'only one separately approved owner UI page; CLI read-only','cycle_min_interval_seconds':60,'poll_wakeup_seconds':1,'manual_cycles_after_start':False,'service_restarts':False,'model_cost_micro_usd':0,'browser_product':'blocked_saved_denial','G1':'not_run','G2':'not_run','source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('brain').glob('*.py'))}}
store=worker=None
try:
 readers,configs=prepare('.runtime/operator-bundle.json')
 saved_credentials(readers,configs,'.runtime/drive-oauth-client.json',MacKeychain())
 measured=Measurements()
 for source,reader in readers.items():reader.transport=TimedNativeTransport(reader.transport,measured,source)
 store=Store(root/'isolated-index.sqlite');pilot=DelegatedQueryPilot(readers,store,live=True)
 actor=Actor('eng_b',pilot.authority.tenant);worker=ContainerDiscovery(pilot,actor,bounded_queries=True)
 worker.start();deadline=time.monotonic()+180
 while time.monotonic()<deadline:
  with pilot.lock:complete=set(worker.last)==set(worker.scope) and all(x['status']=='complete' for x in worker.last.values())
  if complete:break
  if worker.stop_event.is_set():raise RuntimeError('Worker stopped')
  time.sleep(.2)
 if not complete:raise RuntimeError('Initial discovery unavailable')
 save('ready.json',{'ready_at':now(),'native_ids_before':sorted(r['native_id'] for r in store.resources() if r['source']=='confluence'),'cycles':worker.last})
 print('ready_for_one_owner_creation',flush=True)
 # Wait for the owner UI confirmation file. No database or API writes occur here.
 deadline=time.monotonic()+600;target=None
 while time.monotonic()<deadline:
  confirmation=root/'creation-observation.json'
  if confirmation.exists():
   observation=json.loads(confirmation.read_text());report['owner_observation']=observation
   matches=[r for r in store.resources() if r['source']=='confluence' and r['native_id']==observation['native_id']]
   if matches:target=matches[0];break
  if worker.stop_event.is_set():raise RuntimeError('Worker stopped')
  time.sleep(.2)
 if not target:raise RuntimeError('Automatic publication not observed')
 with pilot.lock:
  report['publication_report']=dict(worker.last['confluence'])
  report['publication_observed_at']=now();report['publication_observed_monotonic']=time.monotonic()
  answer=pilot.query(actor,'For PERF-20261008 automatic discovery probe, what is the approved probe value?')
 assert any(e['resource_id']==target['id'] and 'copper' in e['text'] for e in answer['evidence'])
 save('answer.json',answer);save('new-resource.json',target)
 report['first_answer_at']=now();report['first_answer_monotonic']=time.monotonic()
 report['status']='verified_native_automatic_subset'
except Exception as error:
 report['status']='failed';report['error_type']=type(error).__name__
 print('failure',type(error).__name__,flush=True)
finally:
 if worker:worker.close()
 if store:
  events=pilot.audit.export();save('audit.json',events);report['chain']=verify_chain(events)
  report['timing_samples']=measured.samples;store.db.close()
 report['finished_at']=now();save('verification.json',report)
print(report['status'],flush=True)
