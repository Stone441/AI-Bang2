"""AUTH032 native current-access HTTP follow-up, no query/model call."""
import json,http.client,time
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).with_name('action-ranking-http-followup.json')
if __name__=='__main__':
 session=json.loads((ROOT/'.runtime/page-failure-ux-logs/http-session.json').read_text())
 def call(path):
  connection=http.client.HTTPConnection('127.0.0.1',49161,timeout=120);start=time.monotonic();connection.request('GET',path,headers={'Cookie':session['cookie']});r=connection.getresponse();body=json.loads(r.read());connection.close();return {'http_status':r.status,'seconds':time.monotonic()-start,'response':body}
 answer=json.loads(Path(__file__).with_name('action-ranking-native-six').joinpath('q2-attempt3.json').read_text())['response']
 report={'boundary':'Native product HTTP/current access; not browser or human acceptance','query_calls':0,'previews':[]}
 for eid in dict.fromkeys(e for claim in answer['claims'] for e in claim['evidence_ids']):
  result=call('/api/evidence/'+quote(eid,safe=''));assert result['http_status']==200 and result['response']['evidence_id']==eid;report['previews'].append(result)
 report['recent']=call('/api/history/recent');assert report['recent']['http_status']==200
 report['answer']=call('/api/history?request_id='+answer['request_id']);assert report['answer']['http_status']==200
 assert any(r['request_id']==answer['request_id'] and not r.get('unavailable') for r in report['answer']['response']['history'])
 report['runtime']=call('/api/runtime');OUT.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'previews':len(report['previews']),'history':report['answer']['http_status'],'recent':report['recent']['http_status'],'boundary':report['boundary']}))
