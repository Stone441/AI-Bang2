"""AUTH036 frozen candidate acceptance. Explicit freeze/fixture actions; no retries."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from brain.audit import Audit, verify_chain
from brain.budget import BudgetLedger
from brain.contracts import Actor
from brain.deepseek import check_price_review
from brain.engine import Engine
from brain.keychain import MacKeychain
from brain.runtime_version import source_fingerprint
from brain.store import Store
from brain.synthesis import DeepSeekWholeSourceReviewModel, DeepSeekStructuredSourceReviewModel
from scripts.business_validation import build_world, cases
from scripts.local_entry import renew
from scripts.performance_allowance import PerformanceAdmission, GoalLedger
from scripts.performance_trial import ROOT, PRIVATE, PLAN, private_directory, write_private

MANIFEST = ROOT/'.runtime/validation/CANDIDATE_WHOLE_V1.json'
EXPECTED = {'source_transport':'pooled','source_concurrency':4,'reasoning_effort':'none',
            'source_review_input':'whole','source_review_dispatch':'single','history_read_mode':'batch'}
CANDIDATE = 'whole-v1'
MODEL = DeepSeekWholeSourceReviewModel


def select_candidate(candidate):
    global CANDIDATE, MANIFEST, MODEL, EXPECTED
    if candidate not in ('whole-v1','structured-v2'):raise ValueError('Unknown candidate')
    CANDIDATE=candidate
    structured=candidate=='structured-v2'
    MANIFEST=ROOT/'.runtime/validation'/('CANDIDATE_STRUCTURED_V2.json' if structured else 'CANDIDATE_WHOLE_V1.json')
    MODEL=DeepSeekStructuredSourceReviewModel if structured else DeepSeekWholeSourceReviewModel
    EXPECTED={'source_transport':'pooled','source_concurrency':4,'reasoning_effort':'none',
              'source_review_input':'structured' if structured else 'whole',
              'source_review_dispatch':'single','history_read_mode':'batch'}
    if structured:EXPECTED['window_strategy']='structured'


def inputs():
    plan=json.loads(PLAN.read_text())
    world, ids=build_world()
    for resource in world.resources.values():
        if not resource['text'].startswith('[SYNTHETIC]'):
            resource['text']='[SYNTHETIC]\n'+resource['text']
    by_id={c['id']:c for c in cases(ids)}
    selected=[by_id[cid] for cid in plan['final_fixture_live_model_development_case_ids']]
    return world, selected


def file_hashes():
    files=[PLAN, ROOT/'fixtures/baseline.json']
    for directory in ('brain','scripts','web'):
        files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and p.suffix in ('.py','.js','.css','.html'))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def validate_frozen():
    manifest=json.loads(MANIFEST.read_text())
    if manifest['files'] != file_hashes(): raise ValueError('Frozen candidate changed; do not continue acceptance')
    if manifest['configuration'] != EXPECTED: raise ValueError('Frozen configuration mismatch')
    return manifest


def freeze():
    if MANIFEST.exists(): raise ValueError('Never overwrite a frozen candidate')
    renew(ROOT,check_only=True)
    config=json.loads((PRIVATE/'runtime-configuration.json').read_text())
    if any(config.get(k)!=v for k,v in EXPECTED.items()): raise ValueError('Candidate not loaded')
    control=json.loads((PRIVATE/'entry-server.json').read_text())
    if control['runtime_version']['startup_source_sha256'] != source_fingerprint(ROOT):
        raise ValueError('Current source snapshot must be loaded before freeze')
    for question in (('Q1','Q2','SCOPE') if CANDIDATE=='whole-v1' else ()):
        oracle=json.loads((PRIVATE/f'whole-v1-{question}/oracle-review.json').read_text())
        if oracle.get('business_oracle_pass') is not True: raise ValueError('Diagnostic business review incomplete')
    _, selected=inputs()
    value={'candidate':CANDIDATE,'configuration':EXPECTED,'files':file_hashes(),
           'runtime_version':control['runtime_version'],'plan_sha256':hashlib.sha256(PLAN.read_bytes()).hexdigest(),
           'fixture_cases':selected,'boundary':'Known authored development cases, not blind; fixture API is simulated. Native/browser acceptance separate; three-second target unproven.'}
    MANIFEST.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'candidate_frozen':True,'fixture_cases':len(selected),'model_calls':0}))


def fixture():
    manifest=validate_frozen();check_price_review()
    output=PRIVATE/('final-fixture-'+CANDIDATE)
    if output.exists(): raise ValueError('Existing acceptance run must not be repeated or overwritten')
    private_directory(output)
    bundle=json.loads((ROOT/'.runtime/operator-bundle.json').read_text())
    if bundle.get('approved_synthetic_only') is not True or bundle.get('identity_mapping_reviewed') is not True:
        raise ValueError('Approved synthetic configuration required')
    native_config=json.loads((ROOT/'.runtime'/bundle['sources']['jira']).read_text())
    budget=ROOT/'.runtime/deepseek-budget.sqlite'
    if not budget.is_file(): raise ValueError('Original shared budget required')
    ledger=BudgetLedger(str(budget));store=None;results=[]
    report={'candidate_sha256':hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
        'mode':'fixture_source_live_model_not_native_or_browser','results':results,'status':'running'}
    def save(): write_private(output/'report.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    try:
        world, selected=inputs()
        if selected != manifest['fixture_cases']: raise ValueError('Frozen questions changed')
        key=MacKeychain().get('deepseek',native_config['tenant'],'eng_b','deepseek-flash')
        if not key: raise ValueError('Existing approved key required')
        model=MODEL(key,ledger,synthetic_only=True,reasoning_effort='none',output_tokens=8192)
        del key
        store=Store();store.initialize(world);audit=Audit(store)
        engine=Engine(store,world,audit,model,source_review_dispatch='single',history_read_mode='batch',
                      evidence_on_model_rejection=True, mode=report['mode'],
                      window_strategy=EXPECTED.get('window_strategy','fixed'))
        gate=PerformanceAdmission(engine.query,ledger,PRIVATE/'.runtime/goal-admission.json',plan_sha256=manifest['plan_sha256'])
        model.ledger=GoalLedger(gate)
        report['before']=gate.state_extra();report['budget_before']=ledger.summary();save()
        for case in selected:
            validate_frozen()
            if not gate.public_status()['allowed']:
                report['status']='stopped_admission';break
            started=time.perf_counter();error=None;answer=None
            try: answer=gate(Actor(case['actor']),case['question'])
            except Exception as exc: error=type(exc).__name__
            elapsed=time.perf_counter()-started
            rid=answer['request_id'] if answer else audit.export()[-1]['request_id']
            events=[e for e in audit.export() if e['request_id']==rid]
            evidence={e['resource_id'] for e in answer.get('evidence',[])} if answer else set()
            claims=[c['text'] for c in answer.get('claims',[])] if answer else []
            missing=[s for s in case['required_claim_spans'] if not any(s in text for text in claims)]
            case_result={'case':case['id'],'request_id':rid,'seconds':elapsed,'error_type':error,
                'answer_status':answer.get('answer_status') if answer else None,
                'missing_evidence':sorted(set(case['required_evidence'])-evidence),
                'forbidden_evidence':sorted(set(case['forbidden_evidence']) & evidence),
                'missing_claim_spans':missing,'unexpected_claims':case['expected_behavior']!='answer' and bool(claims),
                'semantic_review':'pending','actual_model_calls':sum(e['event_type']=='model_dispatch_attempted' for e in events)}
            case_result['mechanical_oracle_pass']=not(error or case_result['answer_status']=='evidence_only'
                or case_result['missing_evidence'] or case_result['forbidden_evidence'] or missing or case_result['unexpected_claims'])
            results.append(case_result)
            write_private(output/(case['id']+'-answer.json'),json.dumps(answer,ensure_ascii=False,indent=2)+'\n')
            write_private(output/(case['id']+'-audit.json'),json.dumps(events,ensure_ascii=False,indent=2)+'\n')
            save();print(json.dumps({'case':case['id'],'mechanical_oracle_pass':case_result['mechanical_oracle_pass'],
                                   'seconds':elapsed,'actual_model_calls':case_result['actual_model_calls']}),flush=True)
            if not gate.public_status()['allowed']:
                report['status']='stopped_admission';break
            if not case_result['mechanical_oracle_pass']:
                # A failed frozen candidate needs diagnosis, not paid repetitions.
                report['status']='stopped_quality_failure';break
        else: report['status']='completed_pending_semantic_review'
        report['audit_chain']=verify_chain(audit.export())
        report['after']=gate.state_extra();report['budget_after']=ledger.summary();save()
    finally:
        if store is not None:store.db.close()
        ledger.close()
    return 0 if report['status']=='completed_pending_semantic_review' else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['freeze','fixture'])
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--candidate',choices=['whole-v1','structured-v2'],default='whole-v1')
    args=parser.parse_args()
    select_candidate(args.candidate)
    if args.action=='fixture' and not args.live:parser.error('Explicit --live required for budgeted fixture model calls')
    if args.action=='freeze':freeze()
    else:raise SystemExit(fixture())
