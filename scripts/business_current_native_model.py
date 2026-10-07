"""Two current-candidate native plus model probes in an isolated, read-only worker.
Original credentials/budget only; no service startup, source writes or browser.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path
from brain.audit import verify_chain
from brain.budget import BudgetLedger
from brain.contracts import Actor,now
from brain.deepseek import check_price_review
from brain.delegated_query import DelegatedQueryPilot
from brain.discovery import ContainerDiscovery
from brain.keychain import MacKeychain
from brain.store import Store
from scripts.build_metadata import revision
from scripts.run_cost import usage_cost
from scripts.native_discovery_acceptance import prepare,saved_credentials
from scripts.quality_acceptance import CapturedSynthesis


def run(output, temperature=0):
    output.mkdir(parents=True,exist_ok=False)
    def save(name,value):(output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    report={'started_at':now(),'commit':revision(),'mode':'native_api_live_model_synthesis',
            'actor':'eng_b','source_writes':False,'service_restarts':False,'browser':'blocked_saved_site_denial',
            'G1':'not_run','G2':'not_run','semantic_quality':'pending_readonly_review',
            'sampling_temperature':temperature,
            'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [Path(__file__),*sorted(Path('brain').glob('*.py'))]}}
    ledger=store=worker=None
    try:
        check_price_review()
        path=Path('.runtime/deepseek-budget.sqlite')
        if not path.is_file():raise ValueError('Original budget required')
        ledger=BudgetLedger(str(path));report['budget_before']=ledger.summary()
        if report['budget_before']['blocked_for_review'] or report['budget_before']['available_micro_usd']<4*CapturedSynthesis.reservation:
            raise ValueError('Original budget unavailable')
        readers,configs=prepare('.runtime/operator-bundle.json')
        saved_credentials(readers,configs,'.runtime/drive-oauth-client.json',MacKeychain())
        store=Store(output/'isolated-index.sqlite');pilot=DelegatedQueryPilot(readers,store,live=True)
        actor=Actor('eng_b',pilot.authority.tenant)
        worker=ContainerDiscovery(pilot,actor,bounded_queries=True);worker.start()
        cycles=worker.run_once();save('cycles.json',cycles)
        if any(v['status']!='complete' for v in cycles.values()):raise RuntimeError('Incomplete publication')
        key=MacKeychain().get('deepseek',actor.tenant,'eng_b','deepseek-flash')
        if not key:raise ValueError('Approved key unavailable')
        model=CapturedSynthesis(key,ledger,synthetic_only=True,temperature=temperature);pilot.engine.model=model
        pilot.engine.mode=report['mode'];results=[]
        for label,question in [('slack_latest','For the BV-20261007 Slack probe thread, which value is approved after the final correction, and which earlier correction does it supersede?'),
                               ('product_scope','Can we offer payment-retry to all customers now, does PAY-102 Done approve general availability, and what approved scope and confirmed release date can we communicate?')]:
            start=time.monotonic();model.draft_output=None;model.response_diagnostics=[];error=None
            try:
                answer=pilot.query(actor,question)
                previews=[pilot.evidence(actor,e['evidence_id']) for e in answer['evidence']]
                save(label+'-previews.json',previews)
            except Exception as exc:
                error=type(exc).__name__;answer={'request_id':pilot.audit.export()[-1]['request_id'],'claims':[],'evidence':[]}
            save(label+'-answer.json',answer)
            save(label+'-diagnostic.json',{'draft':model.draft_output,'vendor_responses':model.response_diagnostics})
            results.append({'case':label,'question':question,'error_type':error,'elapsed_including_previews_seconds':time.monotonic()-start})
            save('progress.json',results);print(label,error or 'answer',flush=True)
        worker.close();events=pilot.audit.export();save('audit.json',events);save('resources.json',store.resources())
        report['results']=results;report['chain']=verify_chain(events);report['status']='captured_for_review'
    except Exception as exc:
        report['status']='failed';report['error_type']=type(exc).__name__
        if store and 'pilot' in locals():
            if worker:worker.close()
            save('audit.json',pilot.audit.export())
        print('capture_failed:',type(exc).__name__,flush=True)
    finally:
        if worker:worker.close()
        if ledger:
            report['budget_after']=ledger.summary()
            if store and 'pilot' in locals():report['run_usage_cost']=usage_cost(pilot.audit.export())
            ledger.close()
        if store:store.db.close()
        report['finished_at']=now();save('verification.json',report)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--live',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--temperature',type=float,choices=[0,1],default=0);args=parser.parse_args()
    if not args.live:raise SystemExit('not_run: explicit --live required')
    run(args.output,args.temperature)
