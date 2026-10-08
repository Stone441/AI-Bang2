import json,hashlib,subprocess
from pathlib import Path
from datetime import datetime
from brain.audit import verify_chain
root=Path(__file__).parent;rows=[]
audits={f:json.loads((root/f/'audit.json').read_text()) for f in ('automatic','automatic-recovery')}
for folder,audit in audits.items():
 v=json.loads((root/folder/'verification.json').read_text());assert verify_chain(audit)['valid'];assert v['model_cost']==0
 for fn,h in v['source_hashes'].items():assert hashlib.sha256(Path(fn).read_bytes()).hexdigest()==h
 for p in sorted((root/folder).glob('*-result.json')):
  d=json.loads(p.read_text());o=d['observation'];r=d['resource'];rid=o['resource_id'];value=o['value'];assert any(e['resource_id']==rid and value in e['text'] for e in d['answer']['evidence'])
  checks=[x for x in audit if x['request_id']==d['answer']['request_id'] and x['event_type']=='authorization_decided' and x['payload'].get('resource_id')==rid]
  phases={x['payload']['phase'] for x in checks if x['payload']['result']=='allow'};assert {'before_model','model_dispatch','before_dispatch'}<=phases
  if p.name.startswith('04-'):
   read_at=datetime.fromisoformat(r['indexed_at']);publish=next(x['payload']['indexed_at'] for x in audits['automatic'] if x['event_type']=='source_changed' and x['payload'].get('source')=='confluence' and x['payload'].get('status')=='complete' and datetime.fromisoformat(x['payload']['indexed_at'])>=read_at)
  else:publish=d['publication_cycle']['indexed_at']
  stamp=datetime.fromisoformat(r['source_updated_at'].replace('Z','+00:00'))
  rows.append(dict(operation=p.stem.replace('-result',''),resource_id=rid,value=value,version=r['version'],native_reported_updated_at=r['source_updated_at'],publication_at=publish,first_successful_fake_answer_at=d['first_fake_answer_at'],native_timestamp_to_publication_seconds=round((datetime.fromisoformat(publish)-stamp).total_seconds(),3),native_timestamp_to_observed_fake_answer_seconds=round((datetime.fromisoformat(d['first_fake_answer_at'])-stamp).total_seconds(),3),publication_mode='restart_recovery' if p.name.startswith(('05-','06-')) else 'continuous_automatic',answer_mode='fake_recovery_after_failure' if p.name.startswith(('04-','05-','06-')) else 'native_api_fake_model',allowed_phases=sorted(phases),evidence=str(p.relative_to(root))))
assert len(rows)==7
assert subprocess.check_output(['git','diff','2eabeb8','--','brain','scripts','tests','web'])==b''
failures=[dict(run=f,request_id=x['request_id'],seq=x['seq'],method=x['payload'].get('method'),resource_id=x['payload'].get('resource_id')) for f,a in audits.items() for x in a if x['payload'].get('result') in ('unknown','deny')]
summary=dict(main_baseline='2eabeb824e9d3ab8a5b17da391fc9246a4dfe426',application='cdbd62b',runtime_unchanged=True,authorization='AUTH026 consumed exactly3 creates+4updates',source_writes={'create':3,'update':4,'delete':0,'acl_change':0},operations=sorted(rows,key=lambda x:x['operation']),failed_closed_checks=failures,chains={f:verify_chain(a) for f,a in audits.items()},measurement_boundary='Source reported updated/version/message timestamps to completed publication are not exact source commit. UI observation records were delayed and must not be used as actual source latency. CF first publication identified from original completed cycle after version2 read. Successful fake update answers04/05/06 occurred after restart. Three creates and Drive update occurred with continuous worker; Jira/Slack updates recovered at restart. Fake has before_model/model_dispatch/before_dispatch checks; review_dispatch belongs to live synthesis and was not run. No p95/SLA or live model semantic latest-value assertion.',remaining='Multiple independent automatic repetitions per source, uninterrupted first-success answer monitoring, full native ACL/revoke/delete/failure matrix and human page trial remain unverified.',model_cost_micro_usd=0)
(root/'freshness-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print('verified7 operations; unchanged runtime; valid local chains; native API + fake only')
for r in summary['operations']:print(r['operation'],r['publication_mode'],r['native_timestamp_to_publication_seconds'],r['native_timestamp_to_observed_fake_answer_seconds'])
