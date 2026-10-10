"""2026-10-11 independent delivery allowance launcher. Execute only after specific instance authorization.

No candidate source edits. Adds local admission limits around existing query;
original identity/authorization/model/audit code and shared USD20 ledger remain.
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
 def __init__(self,query,ledger,state_path,*,human=False):
  self.human=human
  self.query=query;self.ledger=ledger;self.path=Path(state_path);self.lock=threading.RLock()
  if self.path.exists():self.load(json.loads(self.path.read_text()))
  else:
   with open(self.path.with_suffix('.lock'),'a') as lock:
    os.chmod(self.path.with_suffix('.lock'),0o600);fcntl.flock(lock,fcntl.LOCK_EX)
    if self.path.exists():self.load(json.loads(self.path.read_text()))
    else:
     self.baseline=ledger.summary();self.pending=self.pending_ids();self.attempts=0;self.maximum=12;self.save()
 def load(self,prior):
  self.baseline=prior['baseline'];self.pending=set(prior['original_pending_ids']);self.attempts=prior['attempts'];self.maximum=prior['max_attempts'];self.update_public(prior)
 def update_public(self,body):
  used,maximum=body['attempts'],body['max_attempts']
  reason=('attempt_limit' if used>=(maximum if self.human else 9) else 'cost_limit' if body['current']['settled_micro_usd']-body['baseline']['settled_micro_usd']>=1000000 else 'usage_unconfirmed' if body['new_unknown_reservations'] or body['current']['blocked_for_review'] else None)
  self.public={'allowed':reason is None,'reason':reason,'attempts_used':used,'attempts_limit':maximum,'attempts_remaining':max(0,maximum-used)}
 def pending_ids(self):
  with self.ledger.transaction():return {r[0] for r in self.ledger.db.execute("SELECT id FROM reservations WHERE state IN ('prepared','dispatched')")}
 def save(self):
  body={'original_pending_ids':sorted(self.pending),'attempts':self.attempts,'max_attempts':self.maximum,'baseline':self.baseline,'current':self.ledger.summary(),'settled_stop_threshold_micro_usd':1000000,'new_unknown_reservations':sorted(self.pending_ids()-self.pending),'boundary':f'Admission stops new questions at{self.maximum} attempts, settled threshold, or new unknown usage; in-flight call completes. Not provider billing cap.'}
  self.update_public(body)
  tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(body,indent=2)+'\n');os.chmod(tmp,0o600);tmp.replace(self.path)
 def public_status(self):
  # Another authorized process may consume the shared allowance. Read its atomic
  # snapshot without waiting for query/flock/ledger or polling any business source.
  try:self.update_public(json.loads(self.path.read_text()))
  except (OSError,ValueError,KeyError):pass
  return dict(self.public)
 def __call__(self,*args,**kwargs):
  with self.lock,open(self.path.with_suffix('.lock'),'a') as lock:
   os.chmod(self.path.with_suffix('.lock'),0o600);fcntl.flock(lock,fcntl.LOCK_EX)
   prior=json.loads(self.path.read_text());self.attempts=prior['attempts'];self.maximum=prior['max_attempts']
   if self.maximum != 12:raise ValueError('Unapproved attempt configuration')
   status=self.ledger.summary()
   if self.attempts>=(self.maximum if self.human else 9) or status['settled_micro_usd']-self.baseline['settled_micro_usd']>=1000000 or status['blocked_for_review'] or self.pending_ids()-self.pending:
    self.save();raise TrialAdmissionPaused('Trial limit reached; ask the operator to review before continuing.')
   self.attempts+=1;self.save()
   try:return self.query(*args,**kwargs)
   finally:self.save()

def main(*, human=False, answer_style="synthesis"):
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
   current.engine.query=Admission(current.engine.query,current.engine.model.ledger,runtime/'trial-admission.json',human=human)
   return serve(*a,**kw)
  server.serve_forever=limited_serve;return server
 operator_web.create_server=create;os.chdir(private)
 return operator_web.main(['--source','multi','--config',str(repo/'.runtime'/'operator-bundle.json'),'--actor','eng_b','--oauth-client',str(repo/'.runtime'/'drive-oauth-client.json'),'--port','49161','--live','--model','deepseek','--credential-store','macos-keychain','--answer-style',answer_style,'--reasoning-effort','none','--output-tokens','8192','--discovery-auth017'])
if __name__=='__main__':
 import argparse,sys,re
 parser=argparse.ArgumentParser();parser.add_argument('--human',action='store_true');parser.add_argument('--answer-style',choices=['synthesis','reviewed-excerpts','source-review'],default='synthesis');args=parser.parse_args()
 token_dir=Path(__file__).resolve().parents[1]/'.runtime/page-failure-ux-logs'
 token_dir.mkdir(mode=0o700,exist_ok=True)
 if token_dir.is_symlink():raise ValueError('Private entry directory must not be a symlink')
 token_dir.chmod(0o700)
 class SafeOutput:
  def write(self,value):
   if '#ticket=' in value:
    token=re.search(r'#ticket=([A-Za-z0-9_-]+)',value).group(1)
    target=token_dir/'human-bootstrap-token';target.write_text(token);target.chmod(0o600)
    value='One-time entry prepared privately; use 打开试用页面.command.\n'
   return sys.__stdout__.write(value)
  def flush(self):return sys.__stdout__.flush()
 sys.stdout=SafeOutput()
 raise SystemExit(main(human=args.human,answer_style=args.answer_style))
