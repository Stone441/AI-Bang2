"""Offline structural checks; semantic review remains separate."""
import collections,hashlib,json
from pathlib import Path
from brain.audit import verify_chain
from brain.budget import BudgetLedger
from scripts.run_cost import usage_cost
root=Path(__file__).parent
names=['core24-cooldown-final','known12-cooldown-final','native-cooldown-final']
oldroot=Path('evidence/runs/candidate-closure-20261008/native-timing-80b9ffc')
out={};costs={};counts=[];rows=[]
old=json.loads(Path('evidence/runs/candidate-closure-20261008/native-timing-summary.json').read_text())
for name in names:
 folder=root/name;v=json.loads((folder/'verification.json').read_text());events=json.loads((folder/'audit.json').read_text())
 chain=verify_chain(events);assert chain['valid']
 commit=v.get('commit',v.get('implementation_commit',v.get('baseline_commit')))
 assert commit.startswith('cdbd62b') and v['reasoning_effort']=='low' and v['output_token_cap']==8192
 assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in v['source_hashes'].items() if p.startswith('brain/'))
 supports=0;answered=0
 for p in folder.glob('*-answer.json'):
  a=json.loads(p.read_text());by={e['evidence_id']:e for e in a.get('evidence',[])}
  auth={(e['payload'].get('resource_id'),e['payload'].get('phase')):e['payload']['result'] for e in events if e['request_id']==a['request_id'] and e['event_type']=='authorization_decided'}
  if a.get('claims'):
   answered+=1
   for e in a['evidence']:
    for phase in ['before_model','model_dispatch','review_dispatch','before_dispatch']:assert auth.get((e['resource_id'],phase))=='allow',(name,p,phase)
  for c in a.get('claims',[]):
   for s in c.get('supports',[]):
    assert s['quote'] in by[s['evidence_id']]['text'];supports+=1
 costs[name]=usage_cost(events)
 out[name]={'commit':commit,'mode':v.get('mode',v.get('started_mode')),'chain':chain,'returned_answers_with_claims':answered,'exact_supports':supports,'four_stage_current_allow_for_all_answered_evidence':True}
 if name=='native-cooldown-final':
  for x,prev in zip(v['results'],old['cases']):
   before=json.loads((oldroot/(x['case']+'-answer.json')).read_text());after=json.loads((folder/(x['case']+'-answer.json')).read_text())
   def fp(a):return {(e['evidence_id'],hashlib.sha256(e['text'].encode()).hexdigest()) for e in a['evidence']}
   assert fp(before)==fp(after) and before['question']==after['question']
   rows.append({'case':x['case'],'same_questions_evidence_ids_and_text':True,'evidence_windows':len(after['evidence']),
    'old_query_seconds':prev['query_to_return_seconds'],'new_query_seconds':x['query_to_return_seconds'],
    'old_authorization_wall_seconds':prev['query_categories']['authorization'],'new_authorization_wall_seconds':x['query_timing']['seconds_by_category']['authorization_batch_wall'],
    'old_preview_seconds':prev['single_preview_seconds'],'new_preview_seconds':x['single_preview_seconds'],
    'old_preview_lock_wait_seconds':prev['preview_categories']['lock_wait'],'new_preview_lock_wait_seconds':x['preview_timing']['seconds_by_category']['lock_wait'],
    'generation_seconds':x['query_timing']['seconds_by_category']['generation'],'review_seconds':x['query_timing']['seconds_by_category']['review'],
    'native_http_cumulative_seconds':x['query_timing']['seconds_by_category']['native_http'],'error_type':x['error_type']})
   for kind,key in [('query','query_timing'),('preview','preview_timing')]:
    grouped=collections.defaultdict(lambda:[0,0.0])
    for s in x[key]['samples']:
     if s['category']=='native_http':
      g=(s['source'],s.get('authorization_phase'),s.get('endpoint'));grouped[g][0]+=1;grouped[g][1]+=s['seconds']
    for (source,phase,endpoint),(n,t) in grouped.items():counts.append({'case':x['case'],'operation':kind,'source':source,'phase':phase,'endpoint':endpoint,'calls':n,'cumulative_seconds':t})
oldcases=Path('evidence/runs/business-validation-20261007/live-core-low4096-0bc90ae/development-cases.json')
assert json.loads(oldcases.read_text())==json.loads((root/names[0]/'development-cases.json').read_text())
assert json.loads((root/names[1]/'cases.json').read_text())==json.loads(Path('evidence/runs/candidate-closure-20261008/known12-80b9ffc/cases.json').read_text())
out['same_original_24_and_known12']=True
(root/'structural-cdbd62b.json').write_text(json.dumps(out,indent=2)+'\n')
(root/'performance-cdbd62b.json').write_text(json.dumps({'code_commit':'cdbd62b','baseline_commit':old['code_commit'],'mode':'native_api_live_model_synthesis','results':rows,'calls_by_source_phase_endpoint':counts,'limits':['Independent executions at different times; one sample each, no stable percentile/SLA.','Authorization batch wall overlaps concurrent native HTTP cumulative time; do not add them.','Background discovery remains running; CLI native and mock HTTP tests are distinct from browser blocked.','Source lanes serial within request; foreground and one worker may each have a previously admitted native read. Cooldown blocks new admissions after429.']},indent=2)+'\n')
ledger=BudgetLedger('.runtime/deepseek-budget.sqlite')
try:budget=ledger.summary()
finally:ledger.close()
allcosts={}
for name in ['native-final','core24-final','known12-final',*names]:allcosts[name]=usage_cost(json.loads((root/name/'audit.json').read_text()))
(root/'budget-final-cdbd62b.json').write_text(json.dumps({'final_flows':costs,'all_task_flows':allcosts,'task_total_settled_micro_usd':sum(c['accounted_upper_micro_usd'] for c in allcosts.values()),'final_shared_ledger':budget,'original_unknown_reservation_micro_usd':324404,'original_unknown_retained':budget['pending_requests']==1,'basis':'Unique captured receipts per flow; shared concurrent snapshot differences are not flow costs.'},indent=2)+'\n')
print('verified',rows,budget)
