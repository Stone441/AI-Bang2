"""Small frozen question set: final claims, exact supports and explicit review.

--live-model uses AUTH-003/014 synthetic fixtures, saved app-owned model key and
original budget. No native source API, source write, prompt/consent or user service.
Automatic fact probes are diagnostics; the retained answers require semantic review.
"""
import argparse
import hashlib
import json
from pathlib import Path
from brain.audit import Audit, verify_chain
from brain.budget import BudgetLedger
from brain.contracts import Actor, now
from brain.deepseek import check_price_review
from brain.engine import Engine
from brain.keychain import MacKeychain
from brain.sources import FixtureWorld
from brain.store import Store
from brain.synthesis import DeepSeekSynthesisModel, validate_claim
from scripts.build_metadata import revision

CASES = [
    ('safeguard', 'eng_a', 'What must the operator check before using the approved payment-service failover procedure?', ['inspect timeout budget before approved failover']),
    ('cause_and_counterevidence', 'eng_a', 'Which fault actually produced duplicate payment requests, and what earlier explanation was ruled out?', ['retry configuration mismatched timeout budget', 'duplicate requests backlog', 'early cache hypothesis withdrawn']),
    ('followup_status', 'eng_a', 'For the payment-service follow-up work, separate the completed repair from safeguards still being worked on, and name the safeguard owner.', ['PAY-102 Done', 'PAY-103 In Progress', 'Maya safeguard owner']),
    ('product_scope_date', 'product_ops', 'Can support promise payment-retry to customers outside the pilot, or give them a general launch date?', ['controlled pilot only', 'GA not approved', 'general date unconfirmed']),
    ('code_not_release', 'product_ops', 'Does PAY-102 being done authorize a general customer rollout?', ['no; code completion is not release approval']),
    ('withdrawn_explanation', 'eng_a', 'Is the original cache theory still the payment-service incident’s accepted explanation?', ['cache hypothesis withdrawn', 'final retry configuration / timeout budget mismatch']),
    ('missing_evidence', 'eng_a', 'unfindablezebra', ['no claims and no evidence']),
    ('long_similar_entity', 'eng_a', 'In the Orion incident, which early explanation was withdrawn and what caused the duplicate requests?', ['Orion cache explanation withdrawn', 'Orion retry budget mismatch', 'do not answer Vega DNS cause']),
]


class CapturedSynthesis(DeepSeekSynthesisModel):
    # Operator-only synthetic evaluation diagnostic, never an HTTP user feature.
    draft_output = None
    def parse_output(self, output, evidence):
        self.draft_output = output
        return super().parse_output(output, evidence)


def run(output, live_model=False, only_case=None):
    if output.exists():
        raise FileExistsError('Choose a new quality evidence directory')
    # Freeze questions before model execution; never tune expectations to outputs.
    output.mkdir(parents=True, exist_ok=False)
    cases = [c for c in CASES if only_case is None or c[0] == only_case]
    if not cases:raise ValueError('Unknown frozen case')
    report = {'started_at': now(), 'commit': revision(),
              'mode': 'fixture_source_live_model_synthesis' if live_model else 'fixture_fake_excerpts_quality_diagnostic',
              'source_state': 'Current worktree hashes are authoritative; commit identifies baseline until committed.',
              'case_origin': 'First six variants authored by read-only review agent before evaluation; not human blind benchmark.',
              'native_source_api': 'not_run', 'native_permission_persona': 'not_run',
              'browser': 'not_run', 'G1': 'not_run', 'G2': 'not_run',
              'semantic_review': 'pending', 'results': [], 'status': 'capturing',
              'source_hashes': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                (Path(__file__),Path('brain/engine.py'),Path('brain/retrieval.py'),Path('brain/synthesis.py'),Path('brain/deepseek.py'),Path('brain/budget.py'),Path('fixtures/baseline.json'))}}
    (output/'frozen-cases.json').write_text(json.dumps(cases, ensure_ascii=False, indent=2)+'\n')
    ledger = model = None
    try:
        if live_model:
            check_price_review()  # Current date; no injected historic test clock.
            bundle=json.loads(Path('.runtime/operator-bundle.json').read_text())
            if bundle.get('approved_synthetic_only') is not True or bundle.get('identity_mapping_reviewed') is not True:
                raise ValueError('Reviewed synthetic mapping required')
            ref=Path('.runtime')/bundle['sources']['jira']
            config=json.loads(ref.read_text())
            budget=Path('.runtime/deepseek-budget.sqlite')
            if not budget.is_file():raise ValueError('Original approved ledger required')
            ledger=BudgetLedger(str(budget))
            report['budget_before']=ledger.summary()
            if report['budget_before']['blocked_for_review']:
                raise ValueError('Original ledger is frozen for review; do not read model key or run')
            # Ensure the maximum of two reservations for each question fits first.
            key=MacKeychain().get('deepseek',config['tenant'],'eng_b','deepseek-flash')
            if not key:raise ValueError('Saved approved model key unavailable')
            model=CapturedSynthesis(key,ledger,synthetic_only=True)
            if ledger.summary()['available_micro_usd'] < 2*len(cases)*model.reservation:
                raise ValueError('Insufficient remaining approved budget')
        for label, actor, question, required in cases:
            if live_model:model.draft_output=None
            world=FixtureWorld()
            # Explicit synthetic test copies; no original source/evidence is rewritten.
            for r in world.resources.values():r['text']='[SYNTHETIC]\n'+r['text']
            if label=='long_similar_entity':
                r=world.resources['C-01'];r['links']=[];r['title']='Synthetic incident archive'
                r['text']='[SYNTHETIC]\n'+'Routine housekeeping.\n'*1000+'Vega incident: DNS caused packet loss; no cache theory was withdrawn.\n'+'Appendix.\n'*300+'Orion incident: cache explanation withdrawn; retry budget mismatch caused duplicate requests.\n'+'Appendix.\n'*500
            store=Store();store.initialize(world);audit=Audit(store)
            engine=Engine(store,world,audit,model)
            if live_model:engine.mode='fixture_source_live_model_synthesis'
            answer=None;error=None
            try:
                answer=engine.query(Actor(actor),question)
                if live_model and answer['claims']:
                    from brain.contracts import Evidence
                    evidence=[Evidence(**e) for e in answer['evidence']]
                    for claim in answer['claims']:validate_claim(claim,evidence)
            except Exception as exc:error=type(exc).__name__
            finally:
                events=audit.export();store.db.close()
            (output/(label+'-answer.json')).write_text(json.dumps(answer,ensure_ascii=False,indent=2)+'\n')
            (output/(label+'-audit.json')).write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n')
            result={'case':label,'actor_mode':'fixture_'+actor,'question':question,'required_atomic_facts':required,
                    'error_type':error,'request_id':next(e['request_id'] for e in events if e['event_type']=='request_started'),
                    'claims_only':[c['text'] for c in answer['claims']] if answer else [],
                    'draft_diagnostic': model.draft_output if live_model else None,
                    'exact_supports_validated':True if live_model and answer and answer['claims'] else 'not_applicable',
                    'audit_chain':verify_chain(events), 'semantic_recall_coverage_support_errors':'pending_separate_review'}
            report['results'].append(result)
            (output/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            print(label, 'answer' if answer else error,flush=True)
        report['status']='captured_for_semantic_review'
    except Exception as exc:
        report.update(status='failed',failure_type=type(exc).__name__)
    finally:
        if ledger:
            report['budget_after']=ledger.summary();ledger.close()
        report['finished_at']=now()
        (output/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report['status']=='captured_for_semantic_review'


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live-model',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--only-case',choices=[c[0] for c in CASES])
    args=parser.parse_args()
    raise SystemExit(0 if run(args.output,args.live_model,args.only_case) else 1)
