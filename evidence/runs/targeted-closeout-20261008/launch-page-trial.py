"""Prepared operator-only launcher. Execute only after specific instance authorization.

No candidate source edits. Adds local admission limits around existing query;
original identity/authorization/model/audit code and shared USD20 ledger remain.
"""
import json,os,threading
from pathlib import Path

class Admission:
 def __init__(self,query,ledger,state_path):
  self.query=query;self.ledger=ledger;self.path=Path(state_path);self.lock=threading.RLock()
  if self.path.exists():raise ValueError('Trial state exists; do not reset/reuse instance authorization')
  self.baseline=ledger.summary();self.pending=self.pending_ids();self.attempts=0;self.save()
 def pending_ids(self):
  with self.ledger.transaction():return {r[0] for r in self.ledger.db.execute("SELECT id FROM reservations WHERE state IN ('prepared','dispatched')")}
 def save(self):
  body={'attempts':self.attempts,'max_attempts':6,'baseline':self.baseline,'current':self.ledger.summary(),'settled_stop_threshold_micro_usd':200000,'new_unknown_reservations':sorted(self.pending_ids()-self.pending),'boundary':'Admission stops new questions at6 attempts, settled threshold, or new unknown usage; in-flight call completes. Not provider billing cap.'}
  tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(body,indent=2)+'\n');os.chmod(tmp,0o600);tmp.replace(self.path)
 def __call__(self,*args,**kwargs):
  with self.lock:
   status=self.ledger.summary()
   if self.attempts>=6 or status['settled_micro_usd']-self.baseline['settled_micro_usd']>=200000 or status['blocked_for_review'] or self.pending_ids()-self.pending:
    self.save();raise PermissionError('Trial limit reached; ask the operator to review before continuing.')
   self.attempts+=1;self.save()
   try:return self.query(*args,**kwargs)
   finally:self.save()

def main():
 import subprocess
 from brain import operator_web
 repo=Path(__file__).resolve().parents[3]
 # Refuse launching a different application under the reviewed candidate label.
 for directory in ('brain','scripts','tests','web'):
  if subprocess.check_output(['git','diff','cdbd62b','--',directory],cwd=repo):raise ValueError('Candidate changed')
 private=repo/'.runtime'/'page-trial-20261008'
 private.mkdir(mode=0o700,exist_ok=False);runtime=private/'.runtime';runtime.mkdir(mode=0o700)
 ledger=repo/'.runtime'/'deepseek-budget.sqlite';assert ledger.is_file();(runtime/'deepseek-budget.sqlite').symlink_to(ledger)
 original_create=operator_web.create_server
 def create(app,port):
  server=original_create(app,port);serve=server.serve_forever
  def limited_serve(*a,**kw):
   current=server.application
   current.engine.query=Admission(current.engine.query,current.engine.model.ledger,runtime/'trial-admission.json')
   return serve(*a,**kw)
  server.serve_forever=limited_serve;return server
 operator_web.create_server=create;os.chdir(private)
 return operator_web.main(['--source','multi','--config',str(repo/'.runtime'/'operator-bundle.json'),'--actor','eng_b','--oauth-client',str(repo/'.runtime'/'drive-oauth-client.json'),'--port','49161','--live','--model','deepseek','--credential-store','macos-keychain','--answer-style','synthesis','--reasoning-effort','low','--output-tokens','8192','--discovery-auth017'])
if __name__=='__main__':raise SystemExit(main())
