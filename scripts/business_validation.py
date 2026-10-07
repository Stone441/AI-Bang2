"""Create-only local business baseline; no source/network/model credentials.

Fake claims are excerpts: coverage is a retrieval/support diagnostic, never a
semantic answer-quality pass. Keep all per-question answers and audit records.
"""
import argparse
import copy
import hashlib
import json
import resource as process_resource
import sys
import time
from pathlib import Path

from brain.audit import Audit, verify_chain
from brain.confluence import StorageText
from brain.contracts import Actor, now
from brain.engine import Engine
from brain.sources import FixtureWorld
from brain.store import Store
from brain.budget import BudgetLedger
from brain.deepseek import check_price_review
from brain.keychain import MacKeychain
from scripts.quality_acceptance import CapturedSynthesis
from scripts.build_metadata import revision
from scripts.run_cost import usage_cost
from brain.retrieval import bm25_windows, spans, tokens

FACTS = [
    ('authentication','Token rotation decision','Rotation uses overlapping signing keys; sessions remain valid for fifteen minutes.'),
    ('authentication','Migration blocker','AUTH-204 is Blocked because mobile clients cannot refresh expired tokens. Owner: Lena.'),
    ('authentication','Rejected design thread','The shared-secret proposal was withdrawn. Per-client asymmetric signing was accepted.'),
    ('authentication','Cutover scope','Enterprise SSO cutover applies to internal employees only; contractors remain on the legacy gateway.'),
    ('authentication','Future policy','Beginning 2026-11-01, service tokens expire after thirty minutes; before that date they expire after sixty minutes.'),
    ('integration','SGD account eligibility','The Atlas connector supports Singapore business SGD accounts, not personal accounts.'),
    ('integration','USD exception','Singapore business USD accounts require a separate connector approval; SGD approval does not include USD.'),
    ('integration','Partner channel rule','Partner-led onboarding requires manual verification; direct onboarding supports automated verification.'),
    ('integration','Launch ticket','INT-210 implementation is Done; commercial launch remains Pending approval. Owner: Noor.'),
    ('integration','Scope confirmation','Atlas approval covers the Singapore pilot only. Malaysia expansion has no confirmed approval date.'),
    ('migration','Database design rationale','Ledger migration chose a shadow table to allow rollback without blocking existing writes.'),
    ('migration','Cutover ticket','MIG-301 is In Progress. Owner: Chen. The remaining blocker is unmatched settlement totals.'),
    ('migration','Rollback signal','Roll back the ledger migration if settlement differences exceed five basis points.'),
    ('migration','Past rehearsal','The September rehearsal used a ten-basis-point threshold; it is superseded by the October five-basis-point rule.'),
    ('migration','Unapproved alternative','Dual-region active writes were proposed but not approved; the accepted migration uses one writer.'),
    ('webhook','Webhook incident cause','The webhook backlog came from an exhausted worker pool, not DNS resolution.'),
    ('webhook','Webhook fix status','HOOK-410 worker expansion is Done. HOOK-411 load shedding is In Progress. Owner: Ravi.'),
    ('webhook','Withdrawn explanation','A webhook DNS explanation was withdrawn at 08:40; the worker pool was confirmed at 09:10.'),
    ('webhook','Current response procedure','For webhook backlog, pause noncritical jobs before adding workers; do not retry every webhook.'),
    ('webhook','External commitment','Webhook latency targets apply to the pilot only; no general customer latency guarantee is approved.'),
    ('reconciliation','Ownership decision','Mina owns reconciliation exceptions; the platform team owns ingestion failures.'),
    ('reconciliation','Batch deadline','For Singapore weekday batches the deadline is 18:00 SGT; weekend batches have no same-day deadline.'),
    ('reconciliation','Missing input','A batch with missing bank files must remain Pending, not be marked reconciled.'),
    ('reconciliation','Pilot blocker','REC-502 is Blocked by an unsigned bank-file agreement. Owner: Mina.'),
    ('reconciliation','Old operating note','The old 17:00 deadline applies only to the retired September pilot, not current weekday batches.'),
    ('access','Partner channel membership','The private partner-escalation channel is available to eng_a but not eng_b despite their shared engineering role.'),
    ('access','Security comment','CANARY_BV_RESTRICTED: security-only authentication investigation; no general employee disclosure.'),
    ('access','Approved public guidance','Partner users may read approved integration eligibility guidance; incident details are not public guidance.'),
    ('access','Offboarding rule','Removal from a source channel prevents future citation and history access; previously saved copies cannot be recalled.'),
    ('access','Unknown authority','When current source access cannot be verified, do not treat a prior allow decision as current permission.'),
    ('settlement','Settlement scope','Same-day settlement is approved for Singapore SGD pilot accounts; MYR accounts are outside this scope.'),
    ('settlement','Future settlement schedule','The proposed November hourly schedule is not approved. Current settlement is daily.'),
    ('settlement','Settlement dependency','SET-610 is In Progress because bank confirmation is missing. Owner: Eva.'),
    ('settlement','Contradictory proposal','An unsigned draft says MYR settlement is available; it is a proposal, not the approved operating rule.'),
    ('settlement','Escalation guidance','If bank confirmation is absent, ask Eva for status; do not promise a completed settlement.'),
]


def build_world():
    world = FixtureWorld()
    templates = {s: next(r for r in world.resources.values() if r['source'] == s)
                 for s in ('confluence', 'jira', 'slack', 'drive')}
    ids = []
    for i, (topic, title, text) in enumerate(FACTS):
        source = 'slack' if i in (17,25) else ('confluence', 'jira', 'slack', 'drive')[i % 4]
        r = copy.deepcopy(templates[source]); rid = f'BV-{i+1:02}'
        r.update(id=rid, native_id='synthetic-'+rid, title=topic+' / '+title,
                 text='[SYNTHETIC]\n'+text, links=[], parent='bv',
                 source_url=f'fixture://synthetic-demo/{source}/{rid}',
                 locator={'section':title}, source_updated_at='2026-10-07T12:00:00+08:00')
        # Preserve source-specific shape, but keep general business cards staff-only.
        if source == 'confluence': r['policy']['page_groups']=['staff']
        elif source == 'jira': r['policy']['issue_groups']=['staff']
        elif source == 'slack': r['policy']['members']=['eng_a','product_ops','security']
        else: r['policy']['inherited_groups']=['staff']
        if i == 25: r['policy']['members']=['eng_a','security']
        if i == 26:
            r['policy']['members']=['security']
        world.resources[rid]=r; ids.append(rid)
    # Explicit source-authored structures, not extra retrieval-only words.
    table='<h2>Atlas account eligibility</h2><table><tr><th>Account</th><th>Scope</th></tr><tr><td><p>Singapore business SGD</p></td><td><p>Pilot supported</p></td></tr><tr><td><p>Personal SGD</p></td><td><p>Not supported</p></td></tr></table>'
    parser=StorageText();parser.feed(table)
    world.resources['BV-06'].update(source='confluence',policy=copy.deepcopy(templates['confluence']['policy']),
                                    workspace='demo-confluence',source_url='fixture://synthetic-demo/confluence/BV-06',
                                    test_source_html=table,text='[SYNTHETIC]\n'+FACTS[5][2]+'\n'+''.join(parser.parts))
    world.resources['BV-06']['policy']['page_groups']=['staff']
    world.resources['BV-03'].update(text='[SYNTHETIC]\n09:00 authentication signing design: shared-secret proposal under consideration.',links=['BV-18'],locator={'channel':'synthetic-auth','root':'BV-03','message':'BV-03'})
    world.resources['BV-18'].update(title='Authentication signing design reply',parent='BV-03',
                                    text='[SYNTHETIC]\n10:00 authentication signing reply: '+FACTS[2][2],
                                    locator={'channel':'synthetic-auth','root':'BV-03','message':'BV-18'})
    archive='\n'.join(f'Archived migration rehearsal entry {i}: batch {i*17}, checksum {i*31}; no current decision recorded.' for i in range(180))
    world.resources['BV-11']['text']='[SYNTHETIC]\n# Retired webhook rehearsal\nDNS was a historical webhook hypothesis.\n'+archive+'\n# Current ledger migration decision\n'+FACTS[10][2]
    world.approved_synthetic_resource_ids=frozenset(world.resources)
    return world, ids


def cases(ids):
    data = [
        ('cause','eng_a','What caused the payment-service duplicate requests?', ['D-01'], ['retry configuration mismatched the timeout budget']),
        ('withdrawn','eng_a','Which payment-service explanation was withdrawn?', ['S-01'], ['cache hypothesis was withdrawn']),
        ('followup','eng_a','What is the payment-service safeguard status and owner?', ['J-03'], ['In Progress','Maya']),
        ('release','product_ops','Does PAY-102 Done authorize general customer release?', ['J-02','D-02'], ['Code completion does not approve general customer release','GA) not approved']),
        ('no_information','eng_a','unfindablebusinesszebra', [], []),
        ('restricted','product_ops','CANARY_BV_RESTRICTED', [], []),
    ]
    questions = {
        0:'Why does token rotation preserve sessions?',
        1:'What blocks AUTH-204 and who owns it?',
        2:'Which authentication signing proposal was rejected?',
        3:'Does enterprise SSO cutover include contractors?',
        4:'Before November, how long do service tokens last?',
        5:'Can the Atlas connector serve personal Singapore SGD accounts?',
        6:'Does SGD connector approval cover business USD accounts?',
        7:'How does partner onboarding differ from direct onboarding?',
        8:'Does INT-210 Done mean commercial launch is approved?',
        10:'Why did ledger migration select a shadow table?',
        11:'Who owns MIG-301 and what is still blocking cutover?',
        12:'When should the ledger migration be rolled back?',
        15:'Was DNS the cause of the webhook backlog?',
        16:'Which webhook safeguard is still in progress and who owns it?',
        20:'Who owns reconciliation exceptions versus ingestion failures?',
        21:'What is the current Singapore weekday reconciliation deadline?',
        30:'Is same-day settlement approved for MYR accounts?',
        31:'Can we promise the November hourly settlement schedule?',
    }
    for i,q in questions.items():
        if i==4:q='As of 2026-10-07, before November, how long do service tokens last?'
        data.append((f'business_{i+1:02}','product_ops' if i in (5,6,7,8,21,30,31) else 'eng_a',q,[ids[17] if i==2 else ids[i]],[FACTS[i][2]]))
    return [{'id':cid,'actor':actor,'question':q,'question_time':'2026-10-07T12:00:00+08:00',
             'scope':'explicit scope in question; no automatic previous question',
             'required_evidence':required,'required_claim_spans':atoms,
             'forbidden_evidence':['C-03','J-01-comment-sec','BV-27'],
             'expected_behavior':'insufficient_evidence' if cid=='no_information' else 'permission_denial' if cid=='restricted' else 'answer',
             'oracle_kind':'author-defined exact facts for excerpt coverage; not semantic judge'}
            for cid,actor,q,required,atoms in data]


def run(output, strategy='lexical', noise=0, live_model=False, selected_cases=None, temperature=0):
    output.mkdir(parents=True,exist_ok=False)
    started_at=now()
    loaded_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [Path(__file__),*sorted(Path('brain').glob('*.py'))]}
    world,ids=build_world(); questions=cases(ids) if selected_cases is None else selected_cases
    if not isinstance(questions,list) or not 1<=len(questions)<=24:
        raise ValueError('Bounded development case list required')
    ledger=model=None;budget_before=None
    if live_model:
        if noise:raise ValueError('Live runs are core only; no paid scale loop')
        # All originals are explicitly labeled local synthetic test copies.
        # Never insert a marker into a selected window to make it pass guard.
        for r in world.resources.values():
            if not r['text'].startswith('[SYNTHETIC]'):r['text']='[SYNTHETIC]\n'+r['text']
    for i in range(noise):
        template=copy.deepcopy(world.resources['BV-01']);rid=f'NOISE-{i:04}'
        template.update(id=rid,native_id='synthetic-'+rid,title=f'Synthetic unrelated catalog {i}',
                        text=f'SYNTHETIC catalog entry {i}: warehouse rack {i%37}, inspection interval {i%19+1} days, '
                             f'owner catalog-worker-{i%43}. Token rotation migration payment scope status and approval '
                             f'are catalog column labels, not business decisions. Inventory code SKU-{10000+i}.',
                        links=[],source_url='fixture://synthetic-demo/confluence/'+rid)
        world.resources[rid]=template
    def save(name,data): (output/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    save('world.json',{'synthetic':True,'users':world.users,'resources':list(world.resources.values())})
    save('development-cases.json',questions)
    if live_model:
        check_price_review()
        bundle=json.loads(Path('.runtime/operator-bundle.json').read_text())
        if bundle.get('approved_synthetic_only') is not True or bundle.get('identity_mapping_reviewed') is not True:
            raise ValueError('Existing reviewed synthetic configuration required')
        budget=Path('.runtime/deepseek-budget.sqlite')
        if not budget.is_file():raise ValueError('Original approved ledger required')
        ledger=BudgetLedger(str(budget));budget_before=ledger.summary()
        if budget_before['blocked_for_review'] or budget_before['available_micro_usd']<2*len(questions)*CapturedSynthesis.reservation:
            raise ValueError('Original budget unavailable; no key read or dispatch')
        config=json.loads((Path('.runtime')/bundle['sources']['jira']).read_text())
        key=MacKeychain().get('deepseek',config['tenant'],'eng_b','deepseek-flash')
        if not key:raise ValueError('Approved app-owned model key unavailable')
        model=CapturedSynthesis(key,ledger,synthetic_only=True,temperature=temperature)
    index_started=time.perf_counter()
    store=Store();store.initialize(world)
    index_seconds=time.perf_counter()-index_started
    audit=Audit(store);engine=Engine(store,world,audit,model,retrieval_strategy=strategy)
    if live_model:engine.mode='fixture_source_live_model_synthesis'
    results=[]
    for case in questions:
        start=time.perf_counter();error=None
        if live_model:model.draft_output=None;model.response_diagnostics=[]
        try:answer=engine.query(Actor(case['actor']),case['question'])
        except Exception as exc:
            error=type(exc).__name__;answer={'request_id':audit.export()[-1]['request_id'],'evidence':[],'claims':[]}
        evidence={e['resource_id'] for e in answer['evidence']}
        prepared={event['payload']['resource_id'] for event in audit.export()
                  if event['request_id']==answer['request_id']
                  and event['event_type']=='evidence_used'
                  and event['payload'].get('stage')=='prepared_for_answer'}
        claims=[c['text'] for c in answer['claims']]
        required=set(case['required_evidence']); forbidden=set(case['forbidden_evidence'])
        required_spans=case['required_claim_spans']
        results.append({'case':case['id'],'request_id':answer['request_id'],
                        'error_type':error,
                        'prepared_evidence_ids':sorted(prepared),
                        'required_model_input_evidence_missing':sorted(required-prepared),
                        'required_evidence_missing':sorted(required-evidence),
                        'returned_evidence_diagnostic':'no final response after '+error if error else 'actual final evidence',
                        'forbidden_evidence_used':sorted(evidence & forbidden),
                        'required_claim_spans_missing':[a for a in required_spans if not any(a in c for c in claims)],
                        'unexpected_answer':case['expected_behavior']!='answer' and bool(claims),
                        'elapsed_seconds':time.perf_counter()-start,'claims_only':claims,
                        'answer_quality':'pending_semantic_review' if live_model else 'not_evaluated_fake_excerpts'})
        save(case['id']+'-answer.json',answer)
        if live_model:
            save(case['id']+'-diagnostic.json',{'draft':model.draft_output,'vendor_responses':model.response_diagnostics})
            save('progress.json',results)
            print(case['id'],error or 'answer',flush=True)
    parser=StorageText();parser.feed('<h2>Eligibility</h2><table><tr><th>Account</th><th>Scope</th></tr><tr><td>SGD</td><td>Pilot only</td></tr></table>')
    text=''.join(parser.parts)
    save('parser-probe.json',{'input':'synthetic table and heading','actual_text':text,
                           'cell_boundary_preserved':'SGD\tPilot only' in text or 'SGD | Pilot only' in text})
    save('resource-inquiry.json',audit.inquire(Actor('auditor'),{'resource_id':'J-03'}))
    save('actor-inquiry.json',audit.inquire(Actor('auditor'),{'actor':'eng_a','resource_scope':'payment-service'}))
    save('audit.json',audit.export())
    failures=[r['case'] for r in results if r['required_evidence_missing'] or r['forbidden_evidence_used'] or r['required_claim_spans_missing'] or r['unexpected_answer']]
    peak=process_resource.getrusage(process_resource.RUSAGE_SELF).ru_maxrss
    report={'started_mode':'fixture_source_live_model_synthesis' if live_model else 'fixture_fake_excerpts_business_baseline','started_at':started_at,'recorded_at':now(),'baseline_commit':revision(),
            'source_hashes':loaded_hashes,
            'scale_measurements':{'objects':len(world.resources),
                'exact_windows':sum(len(spans(r['text'])) for r in world.resources.values()),
                'source_utf8_bytes':sum(len(r['text'].encode('utf-8')) for r in world.resources.values()),
                'initialize_index_seconds':index_seconds,
                'process_peak_rss_bytes':peak if sys.platform=='darwin' else peak*1024,
                'memory_measurement':'process peak, includes Python and evaluation artifacts; not index-only',
                'source_native_calls':0,'model_network_calls':'see actual audit attempts' if live_model else 0,
                'paid_query_cost':usage_cost(audit.export()) if live_model else 0},
            'core_objects':len(world.resources)-noise,'noise_objects':noise,'retrieval_strategy':strategy,
            'development_questions':len(questions),
            'sampling_temperature':temperature,
            'sampling_scope':'same value for generation/review; None omits parameter; not a determinism guarantee',
            'held_out':'Not run by this development harness; see separate retained-set records',
            'diagnostic_failures':failures,'results':results,'audit_chain':verify_chain(audit.export()),
            'live_model':'captured_pending_semantic_review' if live_model else 'not_run','native':'not_run','browser':'blocked_saved_site_denial','G1':'not_run','G2':'not_run',
            'quality_semantic_pass':'not_claimed; exact-span probes are not a semantic judge'}
    if ledger:
        report.update(budget_before=budget_before,budget_after=ledger.summary());ledger.close()
    save('verification.json',report)
    print(json.dumps({'objects':len(world.resources),'strategy':strategy,'questions':len(questions),'diagnostic_failures':failures,'parser_cell_boundaries': 'SGD\tPilot only' in text}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--strategy',choices=['lexical','bm25'],default='lexical')
    parser.add_argument('--noise',type=int,choices=[0,1000],default=0)
    parser.add_argument('--live-model',action='store_true')
    parser.add_argument('--cases-file',type=Path)
    parser.add_argument('--temperature',type=float,choices=[0,1],default=0)
    args=parser.parse_args()
    selected=json.loads(args.cases_file.read_text()) if args.cases_file else None
    run(args.output,args.strategy,args.noise,args.live_model,selected,args.temperature)
