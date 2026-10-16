"""Regression support for the original bounded admission gate; no launch or network entry point."""
import json, os, threading, fcntl
from pathlib import Path
from brain.budget import TrialAdmissionPaused

class Admission:
 def __init__(self,query,ledger,state_path):
  self.query=query;self.ledger=ledger;self.path=Path(state_path);self.lock=threading.RLock()
  if self.path.exists():self.load(json.loads(self.path.read_text()))
  else:
   with open(self.path.with_suffix('.lock'),'a') as lock:
    os.chmod(self.path.with_suffix('.lock'),0o600);fcntl.flock(lock,fcntl.LOCK_EX)
    if self.path.exists():self.load(json.loads(self.path.read_text()))
    else:
     self.baseline=ledger.summary();self.pending=self.pending_ids();self.attempts=0;self.maximum=42;self.save()
 def load(self,prior):
  self.baseline=prior['baseline'];self.pending=set(prior['original_pending_ids']);self.attempts=prior['attempts'];self.maximum=prior['max_attempts'];self.update_public(prior)
 def update_public(self,body):
  used,maximum=body['attempts'],body['max_attempts']
  reason=('attempt_limit' if used>=maximum else 'cost_limit' if body['current']['settled_micro_usd']-body['baseline']['settled_micro_usd']>=500000 else 'usage_unconfirmed' if body['new_unknown_reservations'] or body['current']['blocked_for_review'] else None)
  self.public={'allowed':reason is None,'reason':reason,'attempts_used':used,'attempts_limit':maximum,'attempts_remaining':max(0,maximum-used)}
 def pending_ids(self):
  with self.ledger.transaction():return {r[0] for r in self.ledger.db.execute("SELECT id FROM reservations WHERE state IN ('prepared','dispatched')")}
 def save(self):
  body={'original_pending_ids':sorted(self.pending),'attempts':self.attempts,'max_attempts':self.maximum,'baseline':self.baseline,'current':self.ledger.summary(),'settled_stop_threshold_micro_usd':500000,'new_unknown_reservations':sorted(self.pending_ids()-self.pending),'boundary':f'Admission stops new questions at{self.maximum} attempts, settled threshold, or new unknown usage; in-flight call completes. Not provider billing cap.'}
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
   if self.maximum not in (42,48,93,138):raise ValueError('Unapproved attempt configuration')
   status=self.ledger.summary()
   if self.attempts>=self.maximum or status['settled_micro_usd']-self.baseline['settled_micro_usd']>=500000 or status['blocked_for_review'] or self.pending_ids()-self.pending:
    self.save();raise TrialAdmissionPaused('Trial limit reached; ask the operator to review before continuing.')
   self.attempts+=1;self.save()
   try:return self.query(*args,**kwargs)
   finally:self.save()
