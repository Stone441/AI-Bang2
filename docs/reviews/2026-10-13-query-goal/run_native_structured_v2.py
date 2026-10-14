"""Frozen HTTP-only acceptance driver. No automatic retries or process changes.

Cold segments require distinct owned process fingerprints/start times; normal
background discovery remains enabled, so this is process-cold, not a claim that
all network connections or provider caches are cold. Run warm and concurrent
segments on the same process after cold-SCOPE. Browser measurement is separate.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import http.cookiejar
import json
from pathlib import Path
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request,build_opener,HTTPCookieProcessor
from scripts import performance_acceptance as acceptance
from scripts.performance_trial import ROOT,PRIVATE,PLAN,write_private,private_directory
from scripts.local_entry import renew


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('segment',choices=['cold-Q1','cold-Q2','cold-SCOPE','warm','concurrent-1','concurrent-2'])
    args=parser.parse_args()
    acceptance.select_candidate('structured-v2');manifest=acceptance.validate_frozen()
    base=PRIVATE/'final-native-structured-v2';private_directory(base)
    output=base/args.segment
    if output.exists():raise ValueError('Never overwrite or repeat an acceptance segment')
    private_directory(output)
    control=json.loads((PRIVATE/'entry-server.json').read_text())
    if control['runtime_version']['startup_source_sha256']!=manifest['runtime_version']['startup_source_sha256']:
        raise ValueError('Wrong running source version')
    configuration=json.loads((PRIVATE/'runtime-configuration.json').read_text())
    if any(configuration.get(k)!=v for k,v in manifest['configuration'].items()):raise ValueError('Wrong configuration')
    if args.segment.startswith('cold-'):
        for old in base.glob('cold-*/start.json'):
            if json.loads(old.read_text())['runtime_version']==control['runtime_version']:
                raise ValueError('Cold segment requires a fresh process')
    write_private(output/'start.json',json.dumps({'runtime_version':control['runtime_version'],
        'configuration':configuration,'driver_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'candidate_sha256':hashlib.sha256(acceptance.MANIFEST.read_bytes()).hexdigest(),
        'boundary':'HTTP completion only; process-cold with normal background sync, provider/network caches uncontrolled'},indent=2)+'\n')

    class Client:
        def __init__(self):
            self.opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()));self.csrf=None
            status,reply=self.call('/api/operator/login',{'ticket':renew(ROOT)})
            if status!=200:raise ValueError('Login unavailable')
            self.csrf=reply['csrf']

        def call(self,path,payload=None,timeout=20):
            headers={'Origin':'http://127.0.0.1:49161'}
            if payload is not None:headers['Content-Type']='application/json'
            if self.csrf:headers['X-CSRF-Token']=self.csrf
            request=Request('http://127.0.0.1:49161'+path,headers=headers,
                data=json.dumps(payload).encode() if payload is not None else None)
            try:
                with self.opener.open(request,timeout=timeout) as response:return response.status,json.load(response)
            except HTTPError as error:
                with error:return error.code,json.load(error)

        def ready(self):
            deadline=time.monotonic()+120
            while True:
                code,data=self.call('/api/runtime')
                if code==200 and len(data['sources'])==4 and all(s['last_check_result']=='complete' and s['snapshot_status']=='current' for s in data['sources']):return data
                if time.monotonic()>deadline:raise ValueError('Four sources not current; no query submitted')
                time.sleep(1)

    plan=json.loads(PLAN.read_text());questions=plan['native_questions']
    if args.segment.startswith('cold-'):questions=[q for q in questions if q['id']==args.segment[5:]]
    clients=[Client() for _ in questions]
    before=clients[0].ready();write_private(output/'before-runtime.json',json.dumps(before,indent=2)+'\n')
    barrier=threading.Barrier(3) if args.segment.startswith('concurrent-') else None

    def query(pair):
        client,question=pair
        if barrier:barrier.wait(timeout=20)
        write_private(output/(question['id']+'-attempt.json'),json.dumps({'question':question,'submitted':True})+'\n')
        started=time.perf_counter()
        code,answer=client.call('/api/query',{'question':question['question']},timeout=180)
        elapsed=time.perf_counter()-started
        write_private(output/(question['id']+'-answer.json'),json.dumps(answer,ensure_ascii=False,indent=2)+'\n')
        text='\n'.join(c['text'] for c in answer.get('claims',[])).lower()
        expected={'Q1':['inspect the payment-service timeout budget','approved failover procedure'],
                  'Q2':['pay-102','done','pay-103','in progress','pilot','not approved'],
                  'SCOPE':['pilot','not approved']}[question['id']]
        missing=[s for s in expected if s not in text]
        notice=' '.join(answer.get('uncertainties',[])).lower()
        check=(code==200 and answer.get('review_status')=='accepted' and bool(answer.get('claims'))
               and not missing and (question['id']!='Q1' or 'latest ordering is not inferred' in notice))
        result={'question':question['id'],'http_status':code,'seconds':elapsed,'request_id':answer.get('request_id'),
                'mechanical_oracle_pass':check,'missing_claim_spans':missing,'browser_render_measured':False,
                'semantic_review':'pending','within_3_seconds':elapsed<=3}
        write_private(output/(question['id']+'-result.json'),json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
        return result

    if barrier:
        with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(query,zip(clients,questions)))
    else:
        results=[]
        for pair in zip(clients,questions):
            result=query(pair);results.append(result)
            if not result['mechanical_oracle_pass']:break
    code,after=clients[0].call('/api/runtime')
    write_private(output/'after-runtime.json',json.dumps(after,indent=2)+'\n')
    write_private(output/'report.json',json.dumps({'results':results,'status':'pending_semantic_review',
        'all_mechanical_pass':all(r['mechanical_oracle_pass'] for r in results),'expected_queries':len(questions)},indent=2)+'\n')


if __name__=='__main__':main()
