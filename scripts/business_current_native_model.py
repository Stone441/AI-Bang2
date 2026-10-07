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
from scripts.validation_timing import Measurements,TimedNativeTransport


def run(output, temperature=0, reasoning_effort='none', output_tokens=1024):
    output.mkdir(parents=True,exist_ok=False)
    def save(name,value):(output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    report={'started_at':now(),'commit':revision(),'mode':'native_api_live_model_synthesis',
            'actor':'eng_b','source_writes':False,'service_restarts':False,'browser':'blocked_saved_site_denial',
            'G1':'not_run','G2':'not_run','semantic_quality':'pending_readonly_review',
            'sampling_temperature':temperature,
            'reasoning_effort':reasoning_effort,'output_token_cap':output_tokens,
            'effective_temperature':None if reasoning_effort=='low' else temperature,
            'reservation_per_call_micro_usd':CapturedSynthesis.reservation_for(output_tokens),
            'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [Path(__file__),Path('scripts/validation_timing.py'),*sorted(Path('brain').glob('*.py'))]}}
    ledger=store=worker=None
    try:
        check_price_review()
        path=Path('.runtime/deepseek-budget.sqlite')
        if not path.is_file():raise ValueError('Original budget required')
        ledger=BudgetLedger(str(path));report['budget_before']=ledger.summary()
        if report['budget_before']['blocked_for_review'] or report['budget_before']['available_micro_usd']<4*CapturedSynthesis.reservation_for(output_tokens):
            raise ValueError('Original budget unavailable')
        readers,configs=prepare('.runtime/operator-bundle.json')
        saved_credentials(readers,configs,'.runtime/drive-oauth-client.json',MacKeychain())
        measured=Measurements()
        for source,reader in readers.items():
            reader.transport=TimedNativeTransport(reader.transport,measured,source)
        store=Store(output/'isolated-index.sqlite');pilot=DelegatedQueryPilot(readers,store,live=True)
        actor=Actor('eng_b',pilot.authority.tenant)
        worker=ContainerDiscovery(pilot,actor,bounded_queries=True);worker.start()
        with measured.phase('initial_discovery'):cycles=worker.run_once()
        save('cycles.json',cycles)
        if any(v['status']!='complete' for v in cycles.values()):raise RuntimeError('Incomplete publication')
        key=MacKeychain().get('deepseek',actor.tenant,'eng_b','deepseek-flash')
        if not key:raise ValueError('Approved key unavailable')
        model=CapturedSynthesis(key,ledger,synthetic_only=True,temperature=temperature,
            reasoning_effort=reasoning_effort,output_tokens=output_tokens);pilot.engine.model=model
        pilot.engine.mode=report['mode'];results=[]
        check=pilot.authority.check_read
        def timed_check(actor,resource_id):
            return measured.call('authorization',resource_id.split(':',1)[0],lambda:check(actor,resource_id))
        pilot.authority.check_read=timed_check
        delegate=model.transport
        class TimedModel:
            def _send(_,request):
                stage='generation' if len(model.response_diagnostics)==0 else 'review'
                return measured.call(stage,'deepseek',lambda:delegate._send(request))
        model.transport=TimedModel()
        for label,question in [('slack_latest','For the BV-20261007 Slack probe thread, which value is approved after the final correction, and which earlier correction does it supersede?'),
                               ('product_scope','Can we offer payment-retry to all customers now, does PAY-102 Done approve general availability, and what approved scope and confirmed release date can we communicate?')]:
            start=time.monotonic();model.draft_output=None;model.response_diagnostics=[];error=None
            query_seconds=preview_seconds=None;preview_id=None
            try:
                with measured.phase(label+':query'):
                    with measured.acquire(pilot.lock):answer=pilot.query(actor,question)
                query_seconds=time.monotonic()-start
                if answer['claims']:
                    preview_id=answer['claims'][0]['evidence_ids'][0]
                    preview_started=time.monotonic()
                    with measured.phase(label+':single_preview'):
                        with measured.acquire(pilot.lock):preview=pilot.evidence(actor,preview_id)
                    preview_seconds=time.monotonic()-preview_started
                    save(label+'-single-preview.json',preview)
            except Exception as exc:
                error=type(exc).__name__
                if query_seconds is None:query_seconds=time.monotonic()-start
                answer={'request_id':pilot.audit.export()[-1]['request_id'],'claims':[],'evidence':[]}
            save(label+'-answer.json',answer)
            save(label+'-diagnostic.json',{'draft':model.draft_output,'vendor_responses':model.response_diagnostics})
            results.append({'case':label,'question':question,'error_type':error,'elapsed_including_preview_seconds':time.monotonic()-start,
                'query_to_return_seconds':query_seconds,'single_preview_seconds':preview_seconds,
                'preview_evidence_id':preview_id,'query_timing':measured.summary(label+':query'),
                'preview_timing':measured.summary(label+':single_preview')})
            save('progress.json',results);print(label,error or 'answer',flush=True)
        worker.close();events=pilot.audit.export();save('audit.json',events);save('resources.json',store.resources())
        report['results']=results;report['timing_samples']=measured.samples;report['chain']=verify_chain(events);report['status']='captured_for_review'
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
    parser.add_argument('--temperature',type=float,choices=[0,1],default=0)
    parser.add_argument('--reasoning-effort',choices=['none','low'],default='none')
    parser.add_argument('--output-tokens',type=int,choices=[1024,2048,4096,8192],default=1024);args=parser.parse_args()
    if not args.live:raise SystemExit('not_run: explicit --live required')
    run(args.output,args.temperature,args.reasoning_effort,args.output_tokens)
