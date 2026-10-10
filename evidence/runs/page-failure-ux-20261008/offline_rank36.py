"""Offline fixture ranking comparison. No provider, credentials or native requests."""
import hashlib,json
from pathlib import Path
from brain.audit import Audit
from brain.contracts import Actor
from brain.engine import Engine
from brain.retrieval import tokens,ranking_terms,subject_related,bm25_windows
from brain.store import Store
from scripts.business_validation import build_world
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).with_name('action-ranking-quality36-offline.json')
def main():
 world,_=build_world();store=Store();store.initialize(world)
 engine=Engine(store,world,Audit(store));rows=[];hashes={}
 try:
  for group in ('core24','known12'):
   path=Path(__file__).with_name('quality36')/(group+'-cases.json');raw=path.read_bytes();hashes[group]=hashlib.sha256(raw).hexdigest()
   for case in json.loads(raw):
    query=tokens(case['question']);actor=Actor(case['actor']);engine.validate_actor(actor)
    visible=subject_related([r for r in store.resources() if r['active'] and r['tenant']==actor.tenant and engine.prefilter(actor,r)],query)
    def rank(strategy):
     scores=bm25_windows(visible,ranking_terms(query,strategy))
     return sorted([{'id':r['id'],'windows':scores.get(r['id'],[])} for r in visible if scores.get(r['id'])],key=lambda r:(-r['windows'][0][0],r['id']))
    old,new=rank('none'),rank('action-terms-v1')
    rows.append({'group':group,'id':case['id'],'question':case['question'],'terms_changed':ranking_terms(query,'none')!=ranking_terms(query,'action-terms-v1'),'ranking_changed':old!=new,'none':old,'candidate':new})
 finally:store.db.close()
 report={'mode':'fixture lexical ranking only','model_calls':0,'native_requests':0,'case_hashes':hashes,'cases':len(rows),'changed_cases':[{'group':r['group'],'id':r['id']} for r in rows if r['ranking_changed']],'limits':['Not answer/review coverage or current source permission evidence','Topic filtering and prefilter identical; downstream finite windows and budget may affect selected evidence','Requires paid native6 and quality36 before candidate promotion'],'results':rows}
 OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='results'}))
if __name__=='__main__':main()
