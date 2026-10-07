"""Explicit fixed-implementation evaluation of released Agent-held synthetic questions.

No runtime product API. Run only after implementation freeze; raw failures retained.
Oracle diagnostics do not certify semantic quality. Native access/browser are not run.
"""
import argparse
import hashlib
import json
import time
from pathlib import Path
from brain.audit import Audit, verify_chain
from brain.budget import BudgetLedger
from brain.contracts import Actor, now
from brain.deepseek import check_price_review
from brain.engine import Engine, FakeExtractiveModel
from brain.keychain import MacKeychain
from brain.store import Store
from scripts.build_metadata import revision
from scripts.business_validation import build_world
from scripts.quality_acceptance import CapturedSynthesis


def run(cases_path, output, live=False):
    raw=cases_path.read_bytes();cases=json.loads(raw)
    if len(cases)!=12:raise ValueError('Released 12-question set required')
    output.mkdir(parents=True,exist_ok=False)
    def save(name,value):
        (output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    report={'started_at':now(),'implementation_commit':revision(),
            'mode':'fixture_source_live_model_synthesis' if live else 'fixture_fake_excerpts',
            'questions_sha256':hashlib.sha256(raw).hexdigest(),
            'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [Path(__file__),*sorted(Path('brain').glob('*.py'))]},
            'retention':'Agent-held until f8ecbed implementation freeze; not human blind evaluation',
            'native':'not_run','browser':'blocked_saved_site_denial','G1':'not_run','G2':'not_run',
            'semantic_quality':'pending_readonly_review' if live else 'not_evaluated_fake'}
    world,_=build_world();ledger=None;store=None;results=[]
    try:
        if live:
            check_price_review()
            bundle=json.loads(Path('.runtime/operator-bundle.json').read_text())
            if bundle.get('approved_synthetic_only') is not True or bundle.get('identity_mapping_reviewed') is not True:
                raise ValueError('Reviewed synthetic config required')
            budget=Path('.runtime/deepseek-budget.sqlite')
            if not budget.is_file():raise ValueError('Original budget required')
            ledger=BudgetLedger(str(budget));report['budget_before']=ledger.summary()
            if report['budget_before']['blocked_for_review'] or report['budget_before']['available_micro_usd']<2*len(cases)*CapturedSynthesis.reservation:
                raise ValueError('Original budget unavailable')
            config=json.loads((Path('.runtime')/bundle['sources']['jira']).read_text())
            key=MacKeychain().get('deepseek',config['tenant'],'eng_b','deepseek-flash')
            if not key:raise ValueError('Approved model key unavailable')
            model=CapturedSynthesis(key,ledger,synthetic_only=True)
            for resource in world.resources.values():
                if not resource['text'].startswith('[SYNTHETIC]'):resource['text']='[SYNTHETIC]\n'+resource['text']
        else:model=FakeExtractiveModel()
        store=Store();store.initialize(world);audit=Audit(store)
        engine=Engine(store,world,audit,model)
        engine.mode=report['mode'];save('world.json',{'resources':list(world.resources.values()),'users':world.users})
        save('cases.json',cases)
        for case in cases:
            faults=case.get('fixture_setup',{}).get('fault_sources',[])
            if set(faults)-{'confluence','jira','slack','drive'}:raise ValueError('Invalid fixture fault')
            world.faults=set(faults);start=time.monotonic();error=None
            if live:model.draft_output=None;model.response_diagnostics=[]
            try:answer=engine.query(Actor(case['actor']),case['question'])
            except Exception as exc:
                error=type(exc).__name__;answer={'request_id':audit.export()[-1]['request_id'],'claims':[],'evidence':[]}
            ids={e['resource_id'] for e in answer['evidence']}
            events=[e for e in audit.export() if e['request_id']==answer['request_id']]
            prepared={e['payload']['resource_id'] for e in events if e['event_type']=='evidence_used'
                      and e['payload'].get('stage')=='prepared_for_answer'}
            results.append({'id':case['id'],'error_type':error,'expected_behavior':case['expected_behavior'],
                'unsupported_facts':case.get('unsupported',False),'injected_fixture_faults':faults,
                'prepared_resource_ids':sorted(prepared),'returned_resource_ids':sorted(ids),
                'forbidden_evidence_used':sorted(ids.intersection(case['forbidden_evidence'])),
                'required_model_input_missing_diagnostic':sorted(set(case['required_evidence'])-prepared),
                'elapsed_seconds':time.monotonic()-start,'quality':'pending_semantic_review' if live else 'not_evaluated_fake'})
            save(case['id']+'-answer.json',answer)
            if live:save(case['id']+'-diagnostic.json',{'draft':model.draft_output,'vendor_responses':model.response_diagnostics})
            save('progress.json',results);print(case['id'],error or 'answer',flush=True)
        save('audit.json',audit.export());report['chain']=verify_chain(audit.export())
        report['status']='captured_for_review';report['results']=results
    except Exception as exc:
        report['status']='failed';report['error_type']=type(exc).__name__
        if store:save('audit.json',Audit(store).export())
        raise
    finally:
        if ledger:report['budget_after']=ledger.summary();ledger.close()
        if store:store.db.close()
        report['finished_at']=now();save('verification.json',report)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--live-model',action='store_true');args=parser.parse_args()
    run(args.cases,args.output,args.live_model)
