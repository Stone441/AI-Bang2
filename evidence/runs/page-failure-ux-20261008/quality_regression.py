"""Original24 + known12, fixture sources/live model, original ledger and limits.

No raw vendor response or reasoning. This does not replace native HTTP trials.
"""
import hashlib,importlib.util,json,time
from pathlib import Path
from brain.audit import Audit,verify_chain
from brain.budget import BudgetLedger
from brain.contracts import Actor,now
from brain.deepseek import check_price_review
from brain.engine import Engine
from brain.keychain import MacKeychain
from brain.store import Store
from brain.synthesis import DeepSeekSynthesisModel
from scripts.business_validation import build_world

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'evidence/runs/page-failure-ux-20261008/quality36'

def main():
 check_price_review();OUT.mkdir(exist_ok=False)
 baseline=ROOT/'evidence/runs/lock-contention-20261008'
 groups=[('core24',baseline/'core24-cooldown-final/development-cases.json'),('known12',baseline/'known12-cooldown-final/cases.json')]
 cases=[]
 for group,path in groups:
  raw=path.read_bytes();(OUT/(group+'-cases.json')).write_bytes(raw)
  cases.extend((group,c) for c in json.loads(raw))
 world,_=build_world()
 for r in world.resources.values():
  if not r['text'].startswith('[SYNTHETIC]'):r['text']='[SYNTHETIC]\n'+r['text']
 store=Store();store.initialize(world);audit=Audit(store)
 ledger=BudgetLedger(str(ROOT/'.runtime/deepseek-budget.sqlite'))
 bundle=json.loads((ROOT/'.runtime/operator-bundle.json').read_text());assert bundle['approved_synthetic_only'] is True and bundle['identity_mapping_reviewed'] is True
 config=json.loads((ROOT/'.runtime'/bundle['sources']['jira']).read_text())
 key=MacKeychain().get('deepseek',config['tenant'],'eng_b','deepseek-flash');assert key
 model=DeepSeekSynthesisModel(key,ledger,synthetic_only=True,reasoning_effort='low',output_tokens=8192);del key
 engine=Engine(store,world,audit,model,mode='fixture_source_live_model_synthesis',retrieval_strategy='bm25')
 spec=importlib.util.spec_from_file_location('bounded_trial',Path(__file__).with_name('launch.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 query=module.Admission(engine.query,ledger,ROOT/'.runtime/page-failure-ux-20261008/.runtime/trial-admission.json')
 report={'started_at':now(),'mode':engine.mode,'questions':36,'browser':'not_run_saved_denial','native_source':'not_run_fixture_sources','model':'low8192_unchanged','source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'brain').glob('*.py'))},'results':[]}
 try:
  for group,case in cases:
   # Respect the persisted shared trial admission before executing a case.
   state=json.loads(query.path.read_text());maximum=state['max_attempts']
   if query.attempts>=maximum:
    report['not_run']=[{'group':g,'id':c['id'],'reason':'AUTH029 attempt ceiling; pending explicit extension'} for g,c in cases[len(report['results']):]]
    break
   world.faults=set(case.get('fixture_setup',{}).get('fault_sources',[]));start=time.monotonic();error=None
   try:answer=query(Actor(case['actor']),case['question'])
   except Exception as exc:
    error=type(exc).__name__;events=audit.export();answer={'request_id':events[-1]['request_id'] if events else None,'claims':[],'evidence':[]}
   result={'group':group,'id':case['id'],'question':case['question'],'expected_behavior':case['expected_behavior'],'error':error,'elapsed_seconds':time.monotonic()-start,'answer':answer}
   report['results'].append(result)
   (OUT/(group+'-'+case['id']+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   (OUT/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
   print(json.dumps({'group':group,'id':case['id'],'error':error,'claims':len(answer['claims']),'seconds':round(result['elapsed_seconds'],2)}),flush=True)
   if error=='PermissionError':
    report['not_run']=[{'group':g,'id':c['id'],'reason':'admission paused; preserve budget/unknown and ask operator'} for g,c in cases[len(report['results']):]]
    break
 finally:
  report.update(finished_at=now(),chain=verify_chain(audit.export()),budget_after=ledger.summary())
  (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'audit.json').write_text(json.dumps(audit.export(),indent=2)+'\n')
  ledger.close();store.db.close()
if __name__=='__main__':main()
