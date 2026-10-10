"""Only two original known scope cases; fixture sources/live model, shared new gate."""
import json,time,hashlib
from pathlib import Path
from brain.audit import Audit,verify_chain
from brain.budget import BudgetLedger,TrialAdmissionPaused
from brain.contracts import Actor
from brain.deepseek import check_price_review
from brain.engine import Engine
from brain.keychain import MacKeychain
from brain.store import Store
from brain.synthesis import DeepSeekSynthesisModel
from scripts.business_validation import build_world
from scripts.delivery_trial import Admission
ROOT=Path(__file__).resolve().parents[1]
def main():
 check_price_review()
 out=ROOT/'evidence/runs/delivery-20261011/fixture-scope-two';out.mkdir(exist_ok=False)
 path=ROOT/'evidence/runs/lock-contention-20261008/known12-cooldown-final/cases.json'
 cases=[c for c in json.loads(path.read_text()) if c['id'] in ('holdout_02','holdout_10')]
 (out/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
 world,_=build_world()
 for r in world.resources.values():
  if not r['text'].startswith('[SYNTHETIC]'):r['text']='[SYNTHETIC]\n'+r['text']
 store=Store();store.initialize(world);audit=Audit(store)
 ledger=BudgetLedger(str(ROOT/'.runtime/deepseek-budget.sqlite'))
 bundle=json.loads((ROOT/'.runtime/operator-bundle.json').read_text())
 assert bundle['approved_synthetic_only'] is True and bundle['identity_mapping_reviewed'] is True
 config=json.loads((ROOT/'.runtime'/bundle['sources']['jira']).read_text())
 key=MacKeychain().get('deepseek',config['tenant'],'eng_b','deepseek-flash');assert key
 model=DeepSeekSynthesisModel(key,ledger,synthetic_only=True,reasoning_effort='none',output_tokens=8192);del key
 engine=Engine(store,world,audit,model,mode='fixture_source_live_model_synthesis',retrieval_strategy='bm25',query_expansion='none')
 query=Admission(engine.query,ledger,ROOT/'.runtime/delivery-trial-20261011/.runtime/trial-admission.json')
 report={'mode':engine.mode,'model':'disabled8192','cases_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'results':[]}
 try:
  for case in cases:
   start=time.monotonic();error=None
   try:answer=query(Actor(case['actor']),case['question'])
   except Exception as exc:
    error=type(exc).__name__;events=audit.export()
    answer={'request_id':events[-1]['request_id'] if events else None,'claims':[],'evidence':[]}
   result={'case':case,'error':error,'elapsed_seconds':time.monotonic()-start,'answer':answer}
   report['results'].append(result);(out/(case['id']+'.json')).write_text(json.dumps(result,indent=2)+'\n')
   print(json.dumps({'id':case['id'],'error':error,'claims':len(answer['claims'])}),flush=True)
   if error=='TrialAdmissionPaused':break
 finally:
  report.update(chain=verify_chain(audit.export()),budget_after=ledger.summary())
  (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
  (out/'audit.json').write_text(json.dumps(audit.export(),indent=2)+'\n')
  ledger.close();store.db.close()
if __name__=='__main__':main()
