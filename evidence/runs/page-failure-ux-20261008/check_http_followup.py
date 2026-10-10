"""Authorized read-only HTTP previews/history after six fixed native questions."""
import http.client,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'evidence/runs/page-failure-ux-20261008/http-followup.json'
session=json.loads((ROOT/'.runtime/page-failure-ux-logs/http-session.json').read_text())
def call(path):
 c=http.client.HTTPConnection('127.0.0.1',49161,timeout=180);start=time.monotonic()
 c.request('GET',path,headers={'Cookie':session['cookie']});r=c.getresponse();body=json.loads(r.read());c.close()
 return {'http_status':r.status,'seconds':time.monotonic()-start,'response':body}
from urllib.parse import quote
r=json.loads((ROOT/'evidence/runs/page-failure-ux-20261008/http-fixed-six/q2-attempt3.json').read_text())['response']
checks=[]
for eid in dict.fromkeys(e for claim in r['claims'] for e in claim['evidence_ids']):
 result=call('/api/evidence/'+quote(eid,safe=''));assert result['http_status']==200;assert result['response']['evidence_id']==eid;checks.append(result)
history=call('/api/history');assert history['http_status']==200
assert any(a['request_id']==r['request_id'] and not a.get('unavailable') for a in history['response']['history'])
OUT.write_text(json.dumps({'mode':'native_api_product_HTTP_not_browser','previews':checks,'history':history,'runtime':call('/api/runtime'),'human_observation':'not_run'},indent=2)+'\n')
print(json.dumps({'previews':len(checks),'history':history['http_status'],'boundary':'HTTP only, no human/browser acceptance'}))
