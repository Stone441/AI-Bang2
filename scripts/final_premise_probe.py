"""Two frozen, known-case live reviews under the original AUTH036 allowance.

Fixture business sources only. No native or browser validation. No retries.
"""
import argparse
import hashlib
import json
from pathlib import Path
from brain.synthesis import DeepSeekExplainedSourceReviewModel
from scripts import performance_acceptance as base

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'docs/reviews/2026-10-13-final-delivery/PREMISE_DIAGNOSTIC_V1.json'


def configure(revision):
    global MANIFEST
    if revision not in (1,2):raise ValueError("Unknown diagnostic revision")
    MANIFEST=MANIFEST.with_name(f"PREMISE_DIAGNOSTIC_V{revision}.json")
    original=base.inputs
    def inputs():
        world,cases=original();by_id={c['id']:c for c in cases}
        return world,[by_id[x] for x in ('business_03','release')]
    base.inputs=inputs
    base.CANDIDATE=f'explained-diagnostic-v{revision}';base.MANIFEST=MANIFEST
    base.MODEL=DeepSeekExplainedSourceReviewModel
    base.EXPECTED={'reasoning_effort':'none','output_tokens':8192,
                   'source_review_dispatch':'single','window_strategy':'structured',
                   'history_read_mode':'batch','source_review_input':'explained'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['freeze','run']);parser.add_argument('--live',action='store_true')
    parser.add_argument('--revision',type=int,choices=[1,2],default=1)
    args=parser.parse_args();configure(args.revision)
    if args.action=='freeze':
        if MANIFEST.exists():raise ValueError('Never overwrite frozen diagnostic')
        _,cases=base.inputs()
        body={'configuration':base.EXPECTED,'files':base.file_hashes(),'fixture_cases':cases,
              'plan_sha256':hashlib.sha256(base.PLAN.read_bytes()).hexdigest(),
              'purpose':'Two calls of four targeted-quality allocation; not final acceptance',
              'semantic_oracles':{'business_03':'Explicit not_established notice; withdrawal must not become rejection; accepted asymmetric proposal retained',
                                  'release':'Done does not authorize GA; pilot/GA distinction retained, no claim that user asserted GA approval'},
              'mode':'fixture_source_live_model_not_native_or_browser'}
        MANIFEST.write_text(json.dumps(body,ensure_ascii=False,indent=2)+'\n')
        print('Frozen two-case premise diagnostic; zero model calls')
        return 0
    if not args.live:parser.error('Explicit --live required')
    return base.fixture()

if __name__=='__main__':raise SystemExit(main())
