import json
from pathlib import Path
from brain.keychain import MacKeychain
from brain.confluence import Delegation
from brain.contracts import Actor
from brain.discovery import ContainerDiscovery
from brain.delegated_query import DelegatedQueryPilot
from brain.store import Store
from scripts.native_discovery_acceptance import prepare
readers,configs=prepare('.runtime/operator-bundle.json');store=Store();pilot=DelegatedQueryPilot(readers,store,live=True);actor=Actor('eng_b',pilot.authority.tenant)
d=ContainerDiscovery(pilot,actor);output={'mode':'live_metadata_only','source_writes':False,'body_reads':0,'candidates':{}}
try:
 for source in ('confluence','jira'):
  r=readers[source];c=configs[source];account=c['delegations']['eng_b']['account_id']
  auth=MacKeychain().get(source,r.tenant,'eng_b',account)
  if not auth:raise ValueError('saved missing')
  r.delegations['eng_b']=Delegation(account,auth)
  cred=d._credential(source,r);rows=[]
  for page in d._pages(source,r,cred,[0,0]):
   for item in page:
    name=item['title'] if source=='confluence' else item['fields']['summary']
    rows.append({'native_id':item['id'],'name':name,'existing_fixed_id':item['id'] in pilot.authority.native_ids[source],
                 'eligible_exact_prefix':name.startswith('[SYNTHETIC]')})
  output['candidates'][source]=rows
 path=Path('evidence/runs/review-r2-native-20261006/metadata-diagnostic.json')
 with path.open('x') as f:json.dump(output,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(output,ensure_ascii=False))
finally:store.db.close()
