"""AUTH026 ongoing native read-only observer. Owner writes are separate UI actions."""
import json,time,hashlib,threading
from pathlib import Path
from brain.audit import verify_chain
from brain.contracts import Actor,now
from brain.delegated_query import DelegatedQueryPilot
from brain.discovery import ContainerDiscovery
from brain.keychain import MacKeychain
from brain.store import Store
from scripts.native_discovery_acceptance import prepare,saved_credentials
from scripts.validation_timing import Measurements,TimedNativeTransport
root=Path(__file__).parent/'automatic-recovery';root.mkdir(exist_ok=False);(root/'observations').mkdir()
import shutil
shutil.copy2(root.parent/'automatic'/'isolated-index.sqlite',root/'isolated-index.sqlite')
for old in (root.parent/'automatic'/'observations').glob('0[456]-*.json'):shutil.copy2(old,root/'observations'/old.name)
def save(name,v):(root/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
class ClockedMeasurements(Measurements):
 def call(self,category,source,callback,*,endpoint=None):
  start=now();clock=time.monotonic()
  try:return super().call(category,source,callback,endpoint=endpoint)
  finally:
   with self.lock: self.timestamps.append({'source':source,'endpoint':endpoint,'started_at':start,'finished_at':now(),'start_monotonic':clock,'end_monotonic':time.monotonic()})
 def __init__(self):super().__init__();self.timestamps=[]
worker=store=None;report={'mode':'native_api_fake_model','application_baseline':'cdbd62b','started_at':now(),'automatic':True,'interrupted_run':'automatic/verification.json','measurement_boundary':'Restart recovery for CF/Jira/Slack update; Drive update after new ready is continuous. No repeated writes.','manual_cycles':0,'model_cost':0,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('brain').glob('*.py')}};done=[];retry_at={}
try:
 readers,configs=prepare('.runtime/operator-bundle.json');saved_credentials(readers,configs,'.runtime/drive-oauth-client.json',MacKeychain());measured=ClockedMeasurements()
 for source,reader in readers.items():reader.transport=TimedNativeTransport(reader.transport,measured,source)
 store=Store(root/'isolated-index.sqlite');pilot=DelegatedQueryPilot(readers,store,live=True);pilot.engine.mode='native_api_fake_model';actor=Actor('eng_b',pilot.authority.tenant);worker=ContainerDiscovery(pilot,actor,bounded_queries=True);worker.start()
 deadline=time.monotonic()+180
 while time.monotonic()<deadline:
  with pilot.lock:ready=set(worker.last)==set(worker.scope) and all(x['status']=='complete' for x in worker.last.values())
  if ready:break
  time.sleep(.2)
 if not ready:raise RuntimeError('Initial cycle not complete')
 save('ready.json',{'at':now(),'cycles':worker.last,'minimum_cycle_seconds':60,'existing_ids':{s:sorted(r['native_id'] for r in store.resources() if r['source']==s) for s in readers}});print('ready',flush=True)
 deadline=time.monotonic()+3600
 while time.monotonic()<deadline:
  for path in sorted((root/'observations').glob('*.json')):
   if path.stem in done or time.monotonic()<retry_at.get(path.stem,0):continue
   obs=json.loads(path.read_text());source=obs['source'];rid=obs['resource_id'];value=obs['value']
   with pilot.lock:
    matches=[r for r in store.resources() if r['id']==rid and r['active'] and value in r['text']]
    if not matches:continue
    target=matches[0];cycle=dict(worker.last[source]);publication_observed_at=now();publication_clock=time.monotonic()
    start=time.monotonic()
    try:answer=pilot.query(actor,obs['question'])
    except Exception as exc:
     save(path.stem+'-query-failure-'+str(time.time_ns())+'.json',{'at':now(),'observation':obs,'resource':target,'publication_cycle':cycle,'publication_observed_at':publication_observed_at,'error_type':type(exc).__name__,'boundary':'Failed closed; retry only read-only query, no new source mutation.'});retry_at[path.stem]=time.monotonic()+60;continue
   if not any(e['resource_id']==rid and value in e['text'] for e in answer['evidence']):
    save(path.stem+'-query-failure.json',{'at':now(),'observation':obs,'returned_ids':[e['resource_id'] for e in answer['evidence']]});raise RuntimeError('New evidence not used')
   result={'observation':obs,'resource':target,'publication_cycle':cycle,'publication_observed_at':publication_observed_at,'publication_monotonic':publication_clock,'first_fake_answer_at':now(),'answer_monotonic':time.monotonic(),'query_seconds':time.monotonic()-start,'answer':answer,'ui_confirmation_to_publication_seconds':publication_clock-obs['observed_monotonic'],'ui_confirmation_to_answer_seconds':time.monotonic()-obs['observed_monotonic'],'boundary':'Owner UI confirmation is not exact source commit. Native timestamped list/body reads retained; fake is new evidence usage only.'}
   save(path.stem+'-result.json',result);done.append(path.stem);save('progress.json',done);print('captured',path.stem,flush=True)
  if len(done)==4:report['status']='four_update_observations_captured_after_observer_recovery';break
  if (root/'stop').exists():report['status']='stopped_preserving_partial';break
  time.sleep(.3)
 else:report['status']='observation_deadline_partial'
except Exception as exc:
 report['status']='failed';report['error_type']=type(exc).__name__;print(type(exc).__name__,flush=True)
finally:
 if worker:worker.close()
 if store:events=pilot.audit.export();save('audit.json',events);report['chain']=verify_chain(events);store.db.close()
 if 'measured' in globals():save('native-call-times.json',measured.timestamps);save('timing-samples.json',measured.samples)
 report['completed_operations']=done;report['finished_at']=now();save('verification.json',report)
