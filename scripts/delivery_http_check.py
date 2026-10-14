"""Two original native product questions, once each; no browser automation."""
import http.client,json,time,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/runs/delivery-20261011/native-original-two'
QUESTIONS=[
 'What is the latest approved mitigation for the payment incident?',
 'For payment-service, which code fix is complete, which preventive work remains in progress, and is general customer release approved?']
def main(*, label="native-original-two", q1_only=False):
 global OUT
 OUT=ROOT/"evidence/runs/delivery-20261011"/label
 OUT.mkdir(exist_ok=False)
 cookie='';csrf=''
 def request(path,data=None):
  nonlocal cookie,csrf
  conn=http.client.HTTPConnection('127.0.0.1',49161,timeout=180)
  headers={'Cookie':cookie,'X-CSRF-Token':csrf}
  if data is not None:headers['Content-Type']='application/json'
  conn.request('POST' if data is not None else 'GET',path,json.dumps(data) if data is not None else None,headers)
  response=conn.getresponse();body=json.loads(response.read());status=response.status
  if response.getheader('Set-Cookie'):cookie=response.getheader('Set-Cookie').split(';')[0]
  conn.close();return status,body
 token=(ROOT/'.runtime/page-failure-ux-logs/human-bootstrap-token').read_text().strip()
 status,login=request('/api/operator/login',{'ticket':token});del token
 assert status==200;csrf=login['csrf'];del login
 session=ROOT/'.runtime/delivery-trial-20261011/http-session.json'
 session.write_text(json.dumps({'cookie':cookie,'csrf':csrf}));session.chmod(0o600)
 results=[]
 for n,q in enumerate(QUESTIONS[:1] if q1_only else QUESTIONS,1):
  deadline=time.monotonic()+180
  while time.monotonic()<deadline:
   st,state=request('/api/runtime')
   if st==200 and all(s['snapshot_status']=='current' and not s['checking'] for s in state['sources']):break
   time.sleep(.5)
  else:raise RuntimeError('Normal background snapshot not ready')
  (OUT/f'q{n}-runtime-before.json').write_text(json.dumps(state,indent=2)+'\n')
  start=time.monotonic();st,answer=request('/api/query',{'question':q})
  result={'question':q,'http_status':st,'elapsed_seconds':time.monotonic()-start,'response':answer}
  (OUT/f'q{n}.json').write_text(json.dumps(result,indent=2)+'\n');results.append(result)
  print(json.dumps({'q':n,'status':st,'seconds':round(result['elapsed_seconds'],2),'claims':len(answer.get('claims',[]))}),flush=True)
  if state.get('query_admission',{}).get('allowed') is False:break
 (OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
 db=sqlite3.connect('file:'+str(ROOT/'.runtime/delivery-trial-20261011/.runtime/multi-auth017-web.sqlite')+'?mode=ro',uri=True)
 ids={r['response'].get('request_id') for r in results}
 events=[json.loads(row[0]) for row in db.execute('SELECT body FROM audit') if json.loads(row[0]).get('request_id') in ids]
 (OUT/'audit.json').write_text(json.dumps(events,indent=2)+'\n');db.close()
 if any(r['http_status']!=200 or not r['response'].get('claims') for r in results):return 1
 return 0
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--label',default='native-original-two');parser.add_argument('--q1-only',action='store_true')
 args=parser.parse_args()
 if not __import__('re').fullmatch('[a-z0-9-]+',args.label):raise ValueError('Invalid output label')
 raise SystemExit(main(label=args.label,q1_only=args.q1_only))
