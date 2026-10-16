"""2026-10-11 independent delivery allowance launcher. Execute only after specific instance authorization.

No candidate source edits. Adds local admission limits around existing query;
original identity/authorization/model/audit code and shared USD20 ledger remain.
Legacy Admission uses conservative global ledger deltas: another grant can
consume its apparent allowance. Use attributed_allowance only after checked migration.
"""
import json,os,threading,fcntl
from brain.budget import TrialAdmissionPaused
from pathlib import Path

def rejected_generation_diagnostic(output):
 # Private diagnostic only: never capture arbitrary keys or reasoning fields.
 # Bounds match the answer contract; this object is never sent to the UI.
 claims=output.get('claims') if isinstance(output,dict) else None
 if not isinstance(claims,list):return {'claims_shape':'invalid'}
 safe=[]
 for claim in claims[:4]:
  if not isinstance(claim,dict):continue
  text=claim.get('text');ids=claim.get('evidence_ids');supports=claim.get('supports')
  safe.append({'text':text[:600] if isinstance(text,str) else None,
   'evidence_ids':[i[:200] for i in ids[:4] if isinstance(i,str)] if isinstance(ids,list) else None,
   'supports':[{'evidence_id':s.get('evidence_id','')[:200] if isinstance(s.get('evidence_id'),str) else None,
                'quote':s.get('quote','')[:1200] if isinstance(s.get('quote'),str) else None}
               for s in supports[:4] if isinstance(s,dict)] if isinstance(supports,list) else None})
 return {'claim_count':len(claims),'claims':safe}

class Admission:
 MAXIMUM=12
 AUTOMATIC_LIMIT=9
 COST_LIMIT=1000000
 def __init__(self,query,ledger,state_path,*,human=False):
  self.human=human
  self.query=query;self.ledger=ledger;self.path=Path(state_path);self.lock=threading.RLock()
  if self.path.exists():self.load(json.loads(self.path.read_text()))
  else:
   with open(self.path.with_suffix('.lock'),'a') as lock:
    os.chmod(self.path.with_suffix('.lock'),0o600);fcntl.flock(lock,fcntl.LOCK_EX)
    if self.path.exists():self.load(json.loads(self.path.read_text()))
    else:
     self.baseline=ledger.summary();self.pending=self.pending_ids();self.attempts=0;self.maximum=self.MAXIMUM;self.save()
 def load(self,prior):
  self.baseline=prior['baseline'];self.pending=set(prior['original_pending_ids']);self.attempts=prior['attempts'];self.maximum=prior['max_attempts']
  if self.maximum!=self.MAXIMUM:raise ValueError('Unapproved attempt configuration')
  self.update_public(prior)
 def update_public(self,body):
  used,maximum=body['attempts'],body['max_attempts']
  limit=maximum if self.human else self.AUTOMATIC_LIMIT
  reason=('attempt_limit' if limit is not None and used>=limit else 'cost_limit' if body['current']['settled_micro_usd']-body['baseline']['settled_micro_usd']>=self.COST_LIMIT else 'usage_unconfirmed' if body['new_unknown_reservations'] or body['current']['blocked_for_review'] else None)
  self.public={'allowed':reason is None,'reason':reason,'attempts_used':used,'attempts_limit':maximum,'attempts_remaining':None if maximum is None else max(0,maximum-used)}
 def pending_ids(self):
  with self.ledger.transaction():return {r[0] for r in self.ledger.db.execute("SELECT id FROM reservations WHERE state IN ('prepared','dispatched')")}
 def save(self):
  body={'original_pending_ids':sorted(self.pending),'attempts':self.attempts,'max_attempts':self.maximum,'baseline':self.baseline,'current':self.ledger.summary(),'settled_stop_threshold_micro_usd':self.COST_LIMIT,'new_unknown_reservations':sorted(self.pending_ids()-self.pending),'boundary':f'Admission stops new questions at{self.maximum} attempts, settled threshold, or new unknown usage; in-flight call completes. Not provider billing cap.'}
  body.update(self.state_extra())
  self.update_public(body)
  tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(body,indent=2)+'\n');os.chmod(tmp,0o600);tmp.replace(self.path)
 def state_extra(self):return {}
 def additional_stop(self):return False
 def public_status(self):
  # Another authorized process may consume the shared allowance. Read its atomic
  # snapshot without waiting for query/flock/ledger or polling any business source.
  try:self.update_public(json.loads(self.path.read_text()))
  except (OSError,ValueError,KeyError):pass
  return dict(self.public)
 def __call__(self,*args,**kwargs):
  with self.lock,open(self.path.with_suffix('.lock'),'a') as lock:
   os.chmod(self.path.with_suffix('.lock'),0o600);fcntl.flock(lock,fcntl.LOCK_EX)
   prior=json.loads(self.path.read_text());self.load(prior)
   status=self.ledger.summary()
   limit=self.maximum if self.human else self.AUTOMATIC_LIMIT
   if (limit is not None and self.attempts>=limit) or status['settled_micro_usd']-self.baseline['settled_micro_usd']>=self.COST_LIMIT or status['blocked_for_review'] or self.pending_ids()-self.pending or self.additional_stop():
    self.save();raise TrialAdmissionPaused('Trial limit reached; ask the operator to review before continuing.')
   self.attempts+=1;self.save()
   try:return self.query(*args,**kwargs)
   finally:self.save()

class HumanRetestAdmission(Admission):
 """Explicit 11 October authorization: two human questions, two calls, USD0.10.

 Separate durable state; original twelve-attempt allowance is never rewritten.
 Only the single-call source-review launcher can construct this admission gate.
 """
 MAXIMUM=2
 AUTOMATIC_LIMIT=0
 COST_LIMIT=100000
 POLICY='2026-10-11-human-retest-two'
 def __init__(self,query,ledger,state_path,*,human=False):
  if not human:raise ValueError('Retest requires human mode')
  self.ledger=ledger;self.baseline_model_calls=self.call_count()
  super().__init__(query,ledger,state_path,human=human)
 def call_count(self):
  with self.ledger.transaction():
   return self.ledger.db.execute("SELECT count(*) FROM reservations WHERE state IN ('dispatched','settled')").fetchone()[0]
 def load(self,prior):
  if (prior.get('authorization')!=self.POLICY or prior.get('max_model_calls')!=2
      or type(prior.get('baseline_model_calls')) is not int):
   raise ValueError('Unapproved retest configuration')
  self.baseline_model_calls=prior['baseline_model_calls']
  super().load(prior)
 def state_extra(self):
  return {'authorization':self.POLICY,'baseline_model_calls':self.baseline_model_calls,
          'max_model_calls':2,'model_calls_used':self.call_count()-self.baseline_model_calls,
          'boundary':'Two human submissions only; new settlement USD0.10 or new unknown stops admission. Original allowance/ledger retained; in-flight call finishes.'}
 def additional_stop(self):return self.call_count()-self.baseline_model_calls>=2
 def update_public(self,body):
  super().update_public(body)
  if body.get('model_calls_used',0)>=2 and self.public['allowed']:
   self.public.update(allowed=False,reason='model_call_limit')

class HumanOpenAdmission(HumanRetestAdmission):
 """Explicit human count-limit removal; retain existing cost baseline/unknowns."""
 MAXIMUM=None
 POLICY='2026-10-11-human-no-count-limit'
 def __init__(self,query,ledger,state_path,*,human=False,previous_state_path=None):
  if not human:raise ValueError('Open human trial requires human mode')
  path=Path(state_path)
  if not path.exists():
   with open(path.with_suffix('.lock'),'a') as lock:
    os.chmod(path.with_suffix('.lock'),0o600);fcntl.flock(lock,fcntl.LOCK_EX)
    if not path.exists():
     prior=json.loads(Path(previous_state_path).read_text())
     if (prior.get('authorization')!=HumanRetestAdmission.POLICY
         or prior.get('max_attempts')!=2 or prior.get('max_model_calls')!=2
         or type(prior.get('baseline_model_calls')) is not int):
      raise ValueError('Original approved human retest state required')
     prior.update(authorization=self.POLICY,max_attempts=None,max_model_calls=None)
     tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(prior,indent=2)+'\n');tmp.chmod(0o600);tmp.replace(path)
  super().__init__(query,ledger,path,human=True)
 def load(self,prior):
  if (prior.get('authorization')!=self.POLICY or prior.get('max_model_calls') is not None
      or type(prior.get('baseline_model_calls')) is not int):
   raise ValueError('Unapproved open human configuration')
  self.baseline_model_calls=prior['baseline_model_calls'];Admission.load(self,prior)
 def state_extra(self):
  return {**super().state_extra(),'max_model_calls':None,
          'boundary':'Human count limits explicitly removed; original counters/cost baseline retained. USD0.10 new settlement or new unknown still stops admission; no automatic questions.'}
 def additional_stop(self):return False
 def update_public(self,body):
  Admission.update_public(self,body);self.public['human_unlimited']=True

def main(*, human=False, answer_style="synthesis", human_retest=False, human_open=False, review_reasoning_effort="none", timing_dir=None):
 if review_reasoning_effort not in ('none','low') or (review_reasoning_effort!='none' and (not human or answer_style!='source-review')):
  raise ValueError('Review fallback requires human source-review with unchanged cap')
 if (human_retest or human_open) and (not human or answer_style!="source-review"):
  raise ValueError("Approved human retest requires single-call source-review")
 if human_retest and human_open:raise ValueError("Select one approved allowance")
 query_expansion="none"
 from brain.retrieval import ranking_terms
 ranking_terms(set(),query_expansion)
 import subprocess
 from brain import operator_web
 repo=Path(__file__).resolve().parents[1]
 # AUTH029 approves this changed working tree; startup fingerprint records bytes.
 private=repo/'.runtime'/'delivery-trial-20261011'
 private.mkdir(mode=0o700,exist_ok=True)
 if private.is_symlink():raise ValueError('Private runtime must not be a symlink')
 private.chmod(0o700)
 runtime=private/'.runtime';runtime.mkdir(mode=0o700,exist_ok=True)
 ledger=repo/'.runtime'/'deepseek-budget.sqlite';assert ledger.is_file();
 if not (runtime/'deepseek-budget.sqlite').exists():(runtime/'deepseek-budget.sqlite').symlink_to(ledger)
 original_create=operator_web.create_server
 def create(app,port):
  server=original_create(app,port);serve=server.serve_forever
  import signal,tempfile
  token_dir=repo/'.runtime/page-failure-ux-logs'
  def renew_entry(_signal,_frame):
   current=server.application
   if current is None or current.auth_kind!='operator':return
   try:
    ticket=current.renew_bootstrap_ticket()
    fd,name=tempfile.mkstemp(prefix='.entry-',dir=token_dir)
    try:
     with os.fdopen(fd,'w') as output:output.write(ticket)
     os.replace(name,token_dir/'human-bootstrap-token')
    finally:
     if os.path.exists(name):os.unlink(name)
   except OSError:
    # Failed renewal must not stop an active server/request; the helper times out.
    import sys
    print('Local entry renewal failed; existing sessions retained.',file=sys.stderr,flush=True)
  signal.signal(signal.SIGUSR1,renew_entry)
  def limited_serve(*a,**kw):
   current=server.application
   control=private/'entry-server.json'
   control.write_text(json.dumps({'pid':os.getpid(),'port':port,
    'runtime_version':operator_web.runtime_version()},indent=2)+'\n');control.chmod(0o600)
   current.engine.query_expansion=query_expansion
   current.engine.evidence_on_model_rejection=True
   model=current.engine.model;generate=model.generate_with_provenance
   def capture(question,evidence,request_id,provenance,authorize,observe=None):
    # Approved synthetic generation only. Store validated draft privately for a
    # failed review, never internal reasoning, upstream body, credentials or URL.
    parsed=model.parse_output;draft=[];rejected=[]
    def parse(output,evidence):
     try:claims=parsed(output,evidence)
     except Exception:
      rejected[:]=[rejected_generation_diagnostic(output)];raise
     draft[:]=claims;return claims
    model.parse_output=parse
    try:return generate(question,evidence,request_id,provenance,authorize,observe)
    except Exception:
     if draft or rejected:
      diagnostic=runtime/('rejected-draft-'+request_id+'.json')
      diagnostic.write_text(json.dumps({'request_id':request_id,'validated_generation_claims':draft,
       'unvalidated_generation_output':rejected[0] if rejected else None},indent=2)+'\n');diagnostic.chmod(0o600)
     raise
    finally:model.parse_output=parsed
   model.generate_with_provenance=capture
   if human_retest or human_open:
    original=json.loads((runtime/'trial-admission.json').read_text())
    if original['attempts']!=12 or original['max_attempts']!=12 or original['new_unknown_reservations']:
     raise ValueError('Original allowance must remain exhausted without new unknown')
    if getattr(current.engine.model,'claim_format',None)!='reviewed_source_v1':
     raise ValueError('Retest requires single-review model')
   gate=HumanOpenAdmission if human_open else HumanRetestAdmission if human_retest else Admission
   state=runtime/('human-open-admission.json' if human_open else 'human-retest-admission.json' if human_retest else 'trial-admission.json')
   extra={'previous_state_path':runtime/'human-retest-admission.json'} if human_open else {}
   current.engine.query=gate(current.engine.query,current.engine.model.ledger,state,human=human,**extra)
   return serve(*a,**kw)
  server.serve_forever=limited_serve;return server
 timing_args=['--timing-dir',str(Path(timing_dir).absolute())] if timing_dir else []
 operator_web.create_server=create;os.chdir(private)
 return operator_web.main(['--source','multi','--config',str(repo/'.runtime'/'operator-bundle.json'),'--actor','eng_b','--oauth-client',str(repo/'.runtime'/'drive-oauth-client.json'),'--port','49161','--live','--model','deepseek','--credential-store','macos-keychain','--answer-style',answer_style,'--reasoning-effort',review_reasoning_effort,'--output-tokens','8192','--discovery-auth017',*timing_args])
if __name__=='__main__':
 import argparse,sys,re
 parser=argparse.ArgumentParser();parser.add_argument('--human',action='store_true');parser.add_argument('--human-retest',action='store_true');parser.add_argument('--human-open',action='store_true');parser.add_argument('--answer-style',choices=['synthesis','reviewed-excerpts','source-review'],default='synthesis');parser.add_argument('--review-reasoning-effort',choices=['none','low'],default='none');parser.add_argument('--timing-dir',help='Opt-in private local timing directory; default off');args=parser.parse_args()
 token_dir=Path(__file__).resolve().parents[1]/'.runtime/page-failure-ux-logs'
 token_dir.mkdir(mode=0o700,exist_ok=True)
 if token_dir.is_symlink():raise ValueError('Private entry directory must not be a symlink')
 token_dir.chmod(0o700)
 class SafeOutput:
  def write(self,value):
   if '#ticket=' in value:
    token=re.search(r'#ticket=([A-Za-z0-9_-]+)',value).group(1)
    target=token_dir/'human-bootstrap-token';target.write_text(token);target.chmod(0o600)
    value='One-time entry prepared privately; use the local entry helper.\n'
   return sys.__stdout__.write(value)
  def flush(self):return sys.__stdout__.flush()
 sys.stdout=SafeOutput()
 raise SystemExit(main(human=args.human,answer_style=args.answer_style,human_retest=args.human_retest,human_open=args.human_open,review_reasoning_effort=args.review_reasoning_effort,timing_dir=args.timing_dir))
