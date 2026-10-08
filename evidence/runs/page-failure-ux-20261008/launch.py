"""AUTH029 bounded operator-only launcher. Execute only after specific instance authorization.

No candidate source edits. Adds local admission limits around existing query;
original identity/authorization/model/audit code and shared USD20 ledger remain.
"""
import json,os,threading,fcntl
from brain.budget import TrialAdmissionPaused
from pathlib import Path

class Admission:
 def __init__(self,query,ledger,state_path):
  self.query=query;self.ledger=ledger;self.path=Path(state_path);self.lock=threading.RLock()
  if self.path.exists():
   prior=json.loads(self.path.read_text());self.baseline=prior['baseline'];self.pending=set(prior['original_pending_ids']);self.attempts=prior['attempts'];self.maximum=prior['max_attempts']
  else:self.baseline=ledger.summary();self.pending=self.pending_ids();self.attempts=0;self.maximum=42
  if not self.path.exists():self.save()
 def pending_ids(self):
  with self.ledger.transaction():return {r[0] for r in self.ledger.db.execute("SELECT id FROM reservations WHERE state IN ('prepared','dispatched')")}
 def save(self):
  body={'original_pending_ids':sorted(self.pending),'attempts':self.attempts,'max_attempts':self.maximum,'baseline':self.baseline,'current':self.ledger.summary(),'settled_stop_threshold_micro_usd':500000,'new_unknown_reservations':sorted(self.pending_ids()-self.pending),'boundary':'Admission stops new questions at42 attempts, settled threshold, or new unknown usage; in-flight call completes. Not provider billing cap.'}
  tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(body,indent=2)+'\n');os.chmod(tmp,0o600);tmp.replace(self.path)
 def __call__(self,*args,**kwargs):
  with self.lock,open(self.path.with_suffix('.lock'),'a') as lock:
   os.chmod(self.path.with_suffix('.lock'),0o600);fcntl.flock(lock,fcntl.LOCK_EX)
   prior=json.loads(self.path.read_text());self.attempts=prior['attempts'];self.maximum=prior['max_attempts']
   if self.maximum not in (42,48):raise ValueError('Unapproved attempt configuration')
   status=self.ledger.summary()
   if self.attempts>=self.maximum or status['settled_micro_usd']-self.baseline['settled_micro_usd']>=500000 or status['blocked_for_review'] or self.pending_ids()-self.pending:
    self.save();raise TrialAdmissionPaused('Trial limit reached; ask the operator to review before continuing.')
   self.attempts+=1;self.save()
   try:return self.query(*args,**kwargs)
   finally:self.save()

def main():
 import subprocess
 from brain import operator_web
 repo=Path(__file__).resolve().parents[3]
 # AUTH029 approves this changed working tree; startup fingerprint records bytes.
 private=repo/'.runtime'/'page-failure-ux-20261008'
 private.mkdir(mode=0o700,exist_ok=True);runtime=private/'.runtime';runtime.mkdir(mode=0o700,exist_ok=True)
 ledger=repo/'.runtime'/'deepseek-budget.sqlite';assert ledger.is_file();
 if not (runtime/'deepseek-budget.sqlite').exists():(runtime/'deepseek-budget.sqlite').symlink_to(ledger)
 original_create=operator_web.create_server
 def create(app,port):
  server=original_create(app,port);serve=server.serve_forever
  def limited_serve(*a,**kw):
   current=server.application
   model=current.engine.model;generate=model.generate_with_provenance
   def capture(question,evidence,request_id,provenance,authorize,observe=None):
    # Approved synthetic generation only. Store validated draft privately for a
    # failed review, never internal reasoning, upstream body, credentials or URL.
    parsed=model.parse_output;draft=[]
    def parse(output,evidence):
     claims=parsed(output,evidence);draft[:]=claims;return claims
    model.parse_output=parse
    try:return generate(question,evidence,request_id,provenance,authorize,observe)
    except Exception:
     if draft:
      diagnostic=runtime/('rejected-draft-'+request_id+'.json')
      diagnostic.write_text(json.dumps({'request_id':request_id,'validated_generation_claims':draft},indent=2)+'\n');diagnostic.chmod(0o600)
     raise
    finally:model.parse_output=parsed
   model.generate_with_provenance=capture
   current.engine.query=Admission(current.engine.query,current.engine.model.ledger,runtime/'trial-admission.json')
   return serve(*a,**kw)
  server.serve_forever=limited_serve;return server
 operator_web.create_server=create;os.chdir(private)
 return operator_web.main(['--source','multi','--config',str(repo/'.runtime'/'operator-bundle.json'),'--actor','eng_b','--oauth-client',str(repo/'.runtime'/'drive-oauth-client.json'),'--port','49161','--live','--model','deepseek','--credential-store','macos-keychain','--answer-style','synthesis','--reasoning-effort','low','--output-tokens','8192','--discovery-auth017'])
if __name__=='__main__':raise SystemExit(main())
