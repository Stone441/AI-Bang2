"""One explicit frozen native question; AUTH036 allowance remains server-enforced.

Private evidence only. This measures HTTP completion, not browser rendering.
Never retries a submitted question. Waits for all four current sources first.
"""
import argparse
import http.cookiejar
import json
import time
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPCookieProcessor

from scripts.local_entry import renew
from scripts.performance_trial import ROOT, PRIVATE, PLAN, private_directory, write_private


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--question', required=True, choices=['Q1', 'Q2', 'SCOPE'])
    parser.add_argument('--run', required=True, choices=['baseline-v1', 'baseline-v2', 'pooled-v1', 'paired-v1', 'compact-v1', 'covered-v1', 'single-v1', 'whole-v1'])
    args = parser.parse_args(argv)
    folder = PRIVATE/(args.run+'-'+args.question)
    if folder.exists():
        raise ValueError('Existing attempt must not be overwritten or automatically repeated')
    private_directory(folder)
    plan = json.loads(PLAN.read_text())
    question = next(item['question'] for item in plan['native_questions'] if item['id'] == args.question)
    configuration = json.loads((PRIVATE/'runtime-configuration.json').read_text())
    expected = {'baseline-v1': ('legacy', 1), 'baseline-v2': ('legacy', 1),
                'pooled-v1': ('pooled', 1), 'paired-v1': ('pooled', 2), 'compact-v1': ('pooled', 2),
                'covered-v1': ('pooled', 2), 'single-v1': ('pooled', 2), 'whole-v1': ('pooled', 4)}[args.run]
    if (configuration['source_transport'], configuration['source_concurrency']) != expected:
        raise ValueError('Running configuration does not match experiment')
    expected_model = {'compact-v1': ('compact', 'none'), 'covered-v1': ('covered', 'none'),
                      'single-v1': ('covered', 'low'), 'whole-v1': ('whole', 'none')}.get(args.run, ('legacy', 'low'))
    if (configuration.get('source_review_input', 'legacy'), configuration['reasoning_effort']) != expected_model:
        raise ValueError('Running model input/reasoning does not match experiment')
    if configuration.get('source_review_dispatch', 'legacy') != ('single' if args.run in ('single-v1','whole-v1') else 'legacy'):
        raise ValueError('Running authorization dispatch does not match experiment')
    if args.run == 'whole-v1' and configuration.get('history_read_mode') != 'batch':
        raise ValueError('Whole candidate requires reviewed batch history configuration')
    opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    csrf = None
    def call(path, payload=None, timeout=10):
        headers = {'Origin': 'http://127.0.0.1:49161'}
        if payload is not None:
            headers['Content-Type'] = 'application/json'
        if csrf:
            headers['X-CSRF-Token'] = csrf
        request = Request('http://127.0.0.1:49161'+path,
            data=json.dumps(payload).encode() if payload is not None else None, headers=headers)
        try:
            with opener.open(request, timeout=timeout) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            with error:
                return error.code, json.load(error)
    ticket = renew(ROOT)
    status, login = call('/api/operator/login', {'ticket': ticket})
    if status != 200:
        raise ValueError('Local operator login unavailable')
    csrf = login['csrf']
    status, health = call('/api/health')
    if status != 200:
        raise ValueError('Health unavailable')
    write_private(folder/'runtime-version.json', json.dumps({'runtime_version': health['runtime_version'],
        'evidence_basis': 'live health before query submission'}, indent=2)+'\n')
    deadline = time.monotonic()+180
    while True:
        status, runtime = call('/api/runtime')
        if status != 200:
            raise ValueError('Runtime unavailable')
        if len(runtime['sources']) == 4 and all(s['last_check_result'] == 'complete' and
                s['snapshot_status'] == 'current' for s in runtime['sources']):
            break
        if time.monotonic() >= deadline:
            write_private(folder/'source-not-ready.json', json.dumps(runtime, indent=2)+'\n')
            print(json.dumps({'status': 'not_submitted', 'reason': 'sources_not_current'}))
            return 2
        time.sleep(1)
    write_private(folder/'before-runtime.json', json.dumps(runtime, indent=2)+'\n')
    write_private(folder/'configuration.json', json.dumps(configuration, indent=2)+'\n')
    write_private(folder/'attempt.json', json.dumps({'question_id': args.question,
        'question': question, 'submitted': True, 'mode': 'native_api_live_model_http_not_browser'}, indent=2)+'\n')
    started = time.perf_counter()
    status, response = call('/api/query', {'question': question}, timeout=180)
    elapsed = time.perf_counter()-started
    write_private(folder/'response.json', json.dumps(response, indent=2)+'\n')
    summary = {'question_id': args.question, 'http_status': status, 'seconds': elapsed,
               'browser_render_measured': False, 'response_keys': sorted(response),
               'request_id': response.get('request_id'), 'error_code': response.get('code')}
    write_private(folder/'summary.json', json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary))
    return 0 if status == 200 else 2


if __name__ == '__main__':
    raise SystemExit(main())
