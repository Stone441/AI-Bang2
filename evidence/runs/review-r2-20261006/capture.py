"""Actual offline discovery trace. Run PYTHONPATH=tests:. python3 <new-run>/capture.py."""
import copy
import json
import time
from pathlib import Path
from brain.contracts import Actor,now
from brain.discovery import ContainerDiscovery
from brain.audit import verify_chain
from test_container_discovery import setup


def main():
    store,pilot,http,readers=setup();actor=Actor('eng_b','pilot')
    discovery=ContainerDiscovery(pilot,actor)
    output={'mode':'four_source_mock_http_fake_model','started_at':now(),
            'real_source_api_calls':0,'real_model_calls':0,'initial_fixed_id_query':pilot.query(actor,'novelty')}
    try:
        output['initial_discovery']=discovery.run_once()
        output['first_answer_started_at']=now();output['first_answer']=pilot.query(actor,'novelty')
        output['first_answer_returned_at']=now()
        output['first_indexed_resources']=store.resources()
        page=http['confluence'].content['98565'];page['version']['number']=2
        page['body']['storage']['value']='<p>[SYNTHETIC] novelty revision two standby queue</p>'
        http['drive'].fail_native.add('FILE2')
        discovery.due={s:0 for s in discovery.scope}  # Local scheduler only; no price/date/ledger override.
        output['updated_discovery']=discovery.run_once()
        output['updated_answer']=pilot.query(actor,'novelty')
        output['previous_answer_history']=pilot.history(actor,output['first_answer']['request_id'])
        output['product_ops_query']=pilot.query(Actor('product_ops','pilot'),'novelty')
        before=discovery.last['jira']['last_successful_checkpoint_at']
        http['jira'].list_status=429;discovery.due={s:0 for s in discovery.scope}
        output['rate_limit_cycle']=discovery.run_once()
        output['jira_previous_checkpoint']=before
        output['audit']=pilot.audit.export();output['chain_actual']=verify_chain(output['audit'])
        output['catalog_actual']=[dict(row) for row in store.db.execute('SELECT * FROM discovery_catalog ORDER BY source,native_id')]
        output['transport_attempts_actual']={s:len(t.calls) for s,t in http.items()}
        output['finished_at']=now()
        target=Path(__file__).parent/'actual.json'
        with target.open('x') as f:json.dump(output,f,ensure_ascii=False,indent=2);f.write('\n')
        print(json.dumps({'mode':output['mode'],'discovery_status':{s:r['status'] for s,r in output['initial_discovery'].items()},
                          'answer_sources':sorted({e['source'] for e in output['first_answer']['evidence']}),
                          'rate_limit_status':output['rate_limit_cycle']['jira']['status'],
                          'audit_chain_valid':output['chain_actual']['valid']}))
    finally:discovery.close();store.db.close()


if __name__=='__main__':main()
