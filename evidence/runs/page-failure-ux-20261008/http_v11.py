"""AUTH031 six fixed original questions via the actual product HTTP boundary.

No browser automation. Ticket/cookie remain local and never enter evidence.
"""
import http.client,json,re,time,threading,sqlite3
from pathlib import Path
BASE=49161
ROOT=Path(__file__).resolve().parents[3]
OUTPUT=ROOT/'evidence/runs/page-failure-ux-20261008/v11-native-six'
QUESTIONS=[
 'What is the latest approved mitigation for the payment incident?',
 'For payment-service, which code fix is complete, which preventive work remains in progress, and is general customer release approved?']

def main(*, private_ticket=None, query_expansion="none"):
 deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  if private_ticket is not None:
   import urllib.request
   try:
    with urllib.request.urlopen('http://127.0.0.1:49161/api/health',timeout=2) as response:
     if json.load(response)['auth_kind']=='operator':break
   except (OSError,ValueError):pass
  elif 'Open once within' in (ROOT/'.runtime/page-failure-ux-logs/v11-server.log').read_text():break
  time.sleep(.5)
 else:raise RuntimeError('Operator startup not ready')
 OUTPUT.mkdir(exist_ok=False)
 (OUTPUT/'schedule.json').write_text(json.dumps({'questions':QUESTIONS,'repetitions_per_question':3,'order':'Q1,Q2 repeated3 times','model':'unchanged low8192','browser':'not_run_saved_denial','human_observation':'not_run','query_expansion':query_expansion},indent=2)+'\n')
 log=''
 if private_ticket is not None:ticket=Path(private_ticket).read_text().strip()
 else:
  log=(ROOT/'.runtime/page-failure-ux-logs/v11-server.log').read_text()
  ticket=re.search(r'#ticket=([A-Za-z0-9_-]+)',log).group(1)
 cookie='';csrf=''
 def request(path,data=None):
  nonlocal cookie,csrf
  conn=http.client.HTTPConnection('127.0.0.1',BASE,timeout=180)
  headers={'Cookie':cookie,'X-CSRF-Token':csrf}
  if data is not None:headers['Content-Type']='application/json'
  conn.request('POST' if data is not None else 'GET',path,json.dumps(data) if data is not None else None,headers)
  response=conn.getresponse();result=json.loads(response.read());status=response.status
  newcookie=response.getheader('Set-Cookie')
  if newcookie:cookie=newcookie.split(';')[0]
  conn.close();return status,result
 st,login=request('/api/operator/login',{'ticket':ticket});assert st==200;csrf=login['csrf'];del ticket,log,login
 private=ROOT/'.runtime/page-failure-ux-20261008/.runtime'
 db=sqlite3.connect('file:'+str(private/'multi-auth017-web.sqlite')+'?mode=ro',uri=True)
 # Wait for normal worker first complete four-source publication, never trigger a cycle.
 deadline=time.monotonic()+180
 while time.monotonic()<deadline:
  rows=[json.loads(row[0]) for row in db.execute('SELECT body FROM discovery_state')]
  if len(rows)==4 and all(row['status']=='complete' for row in rows):break
  time.sleep(1)
 else:raise RuntimeError('Initial discovery not ready')
 sources=[json.loads(row[0]) for row in db.execute('SELECT body FROM resources WHERE active=1')]
 (OUTPUT/'preflight-index.json').write_text(json.dumps({'boundary':'Normal native worker publications for eng_b; per-request current permission checks still mandatory','sources':[{k:r[k] for k in ('id','version','source','title','text','locator')} for r in sources]},indent=2)+'\n')
 assert any('Runbook v1:' in r['text'] and 'approved failover procedure' in r['text'] for r in sources), 'Current native runbook does not support frozen action expectation'
 assert any('PAY-102 code fix: Done' in r['text'] for r in sources), 'Current code fix state missing'
 assert any('Payment-service incident follow-up PAY-103 protective measures: In Progress' in r['text'] for r in sources), 'Current preventive work state missing'
 assert any('General availability (GA) is not approved' in r['text'] for r in sources), 'Current release limit missing'
 (OUTPUT/'preflight-expectations.json').write_text(json.dumps({'frozen_before_business_query':True,'q1':'C01 supports timeout-budget check and approved failover procedure; no supplied globally latest approval time/order established. Answer must scope the known procedure and chronology uncertainty, not infer approval from completed code or release status.','q2':'PAY102 Done; PAY103 In Progress; controlled pilot approved but GA not approved; current source publication and per-request checks required.','boundary':'Normal worker publication support review, not a native permission shortcut or global completeness claim'},indent=2)+'\n')
 (OUTPUT/'runtime-before.json').write_text(json.dumps(request('/api/runtime')[1],indent=2)+'\n')
 results=[]
 stopped=False
 for repetition in range(1,4):
  if stopped:break
  for number,question in enumerate(QUESTIONS,1):
   # Give the normal publisher an opportunity to finish and require fresh
   # complete snapshots. This readiness wait never dispatches a model/retries a query.
   deadline=time.monotonic()+180
   while time.monotonic()<deadline:
    state=request('/api/runtime')[1]
    if all(s['snapshot_status']=='current' and not s['checking'] for s in state['sources']):break
    time.sleep(.5)
   else:raise RuntimeError('Normal background snapshot not ready')
   time.sleep(.2)
   start=time.monotonic();done=threading.Event();progress=[]
   def poll():
    while not done.wait(.5):
     t=time.monotonic();status,state=request('/api/runtime')
     progress.append({'seconds':t-start,'http_seconds':time.monotonic()-t,'status':status,'run':state.get('run')})
   thread=threading.Thread(target=poll);thread.start()
   try:status,answer=request('/api/query',{'question':question})
   finally:done.set();thread.join()
   result={'question_number':number,'repetition':repetition,'question':question,'http_status':status,'elapsed_seconds':time.monotonic()-start,'response':answer,'progress':progress}
   results.append(result);(OUTPUT/f'q{number}-attempt{repetition}.json').write_text(json.dumps(result,indent=2)+'\n')
   rid=answer.get('request_id');events=[json.loads(r[0]) for r in db.execute('SELECT body FROM audit') if json.loads(r[0]).get('request_id')==rid]
   diagnostics=[e for e in events if e['event_type'].startswith('model_') or e['event_type']=='version_recovery' or e['event_type']=='request_failed']
   (OUTPUT/f'q{number}-attempt{repetition}-diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
   print(json.dumps({'q':number,'attempt':repetition,'status':status,'seconds':round(result['elapsed_seconds'],2),'claims':len(answer.get('claims',[])),'diagnostics':[e['payload'].get('diagnostic') for e in diagnostics if e['event_type']=='model_output_rejected']}),flush=True)
   if answer.get('code') in ('trial_admission_paused','model_request_unavailable','model_budget_unavailable','model_price_review_required'):
    stopped=True;break
 (OUTPUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
 if stopped:(OUTPUT/'not-run.json').write_text(json.dumps({'reason':'admission or unknown usage stopped; no retry','remaining':6-len(results)},indent=2)+'\n')
 # Retain private authenticated session for approved follow-up HTTP quote/history checks.
 session=ROOT/'.runtime/page-failure-ux-logs/http-session.json';session.write_text(json.dumps({'cookie':cookie,'csrf':csrf}));session.chmod(0o600)
 db.close()
if __name__=='__main__':main()
