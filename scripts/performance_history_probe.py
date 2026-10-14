"""AUTH036: re-authorize one existing answer; no query or model call."""
import argparse
import http.cookiejar
import json
import time
from urllib.request import Request, build_opener, HTTPCookieProcessor
from scripts.local_entry import renew
from scripts.performance_trial import ROOT, PRIVATE, private_directory, write_private


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, choices=['serial-v1','batch-v1'])
    args = parser.parse_args()
    target = PRIVATE/('history-'+args.run)
    if target.exists(): raise ValueError('Do not overwrite or automatically repeat an attempt')
    private_directory(target)
    original = json.loads((PRIVATE/'single-v1-Q2/response.json').read_text())
    config = json.loads((PRIVATE/'runtime-configuration.json').read_text())
    expected = ('serial', 2) if args.run == 'serial-v1' else ('batch', 4)
    if (config.get('history_read_mode','serial'), config['source_concurrency']) != expected:
        raise ValueError('Unexpected loaded candidate configuration')
    opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def call(path, data=None, timeout=15):
        request = Request('http://127.0.0.1:49161'+path, data=json.dumps(data).encode() if data is not None else None,
            headers={'Origin':'http://127.0.0.1:49161','Content-Type':'application/json'})
        with opener.open(request, timeout=timeout) as response: return json.load(response)
    call('/api/operator/login', {'ticket':renew(ROOT)})
    health = call('/api/health')
    deadline = time.monotonic()+180
    while True:
        state = call('/api/runtime')
        if len(state['sources']) == 4 and all(s['last_check_result']=='complete' and s['snapshot_status']=='current' for s in state['sources']): break
        if time.monotonic() >= deadline: raise ValueError('Sources not current; no history request submitted')
        time.sleep(1)
    write_private(target/'before-runtime.json',json.dumps(state,indent=2)+'\n')
    write_private(target/'runtime-version.json',json.dumps(health['runtime_version'],indent=2)+'\n')
    write_private(target/'configuration.json',json.dumps(config,indent=2)+'\n')
    before = json.loads((PRIVATE/'.runtime/goal-admission.json').read_text())
    started = time.perf_counter()
    result = call('/api/history?request_id='+original['request_id'], timeout=120)
    elapsed = time.perf_counter()-started
    after = json.loads((PRIVATE/'.runtime/goal-admission.json').read_text())
    write_private(target/'response.json',json.dumps(result,indent=2)+'\n')
    summary = {'mode':'native_current_history_http_not_query_or_browser','seconds':elapsed,
        'original_request_id':original['request_id'],'same_record':result.get('history')==[original],
        'model_call_delta':after['model_calls_used']-before['model_calls_used'],
        'goal_settlement_delta_micro_usd':after['current']['settled_micro_usd']-before['current']['settled_micro_usd']}
    write_private(target/'summary.json',json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))
    return 0 if summary['same_record'] and summary['model_call_delta']==0 else 2


if __name__=='__main__': raise SystemExit(main())
