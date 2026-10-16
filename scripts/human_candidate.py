"""Isolated latest-candidate trial. Only human UI submissions may use the existing grant."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import threading


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-root',type=Path,required=True)
    parser.add_argument('--accounts',type=Path,required=True)
    parser.add_argument('--trial-root',type=Path,required=True)
    args=parser.parse_args()
    os.umask(0o077)
    root=args.state_root.resolve();trial=args.trial_root.resolve()
    trial.mkdir(parents=True,exist_ok=True)
    from brain import drive_oauth
    from brain.confluence import SourceUnavailable
    from brain.keychain import MacKeychain
    from scripts.operator_bundle import load_reader
    from brain.store import Store
    from brain.operator_web import OperatorApp
    from brain.reviewer_access import ReviewerApp
    from brain.server import create_server
    from brain.discovery import ContainerDiscovery
    from brain.budget import BudgetLedger
    from scripts.attributed_allowance import AttributedAdmission,AttributedGoalLedger
    from scripts.team_trial_allowance import TeamTrialAdmission
    from brain.sectioned_answer import DeepSeekSectionedSynthesisModel
    from brain.http_pool import install
    from brain.runtime_version import runtime_version
    from brain.deepseek import check_price_review
    check_price_review()
    def no_consent(*a,**k):raise SourceUnavailable('Existing authorization required')
    drive_oauth.authorize=no_consent
    ledger=BudgetLedger(str(root/'.runtime/deepseek-budget.sqlite'))
    readers=load_reader(root/'.runtime/operator-bundle.json','eng_b',oauth_client=root/'.runtime/drive-oauth-client.json',credential_store=MacKeychain())
    store=Store(str(trial/'index.sqlite'));app=OperatorApp(readers,store,'eng_b',live=True)
    rollback=install(app.world.readers,maximum=4);app.world.read_concurrency=4
    app.engine.window_strategy='structured';app.engine.history_read_mode='batch'
    app.engine.source_review_dispatch='legacy';app.engine.evidence_on_model_rejection=True
    gate=AttributedAdmission(app.engine.query,ledger,'human-team-closeout-20261015',policy=TeamTrialAdmission.POLICY,cost_limit=TeamTrialAdmission.COST_LIMIT,max_calls=None)
    key=MacKeychain().get('deepseek',app.actor.tenant,'eng_b','deepseek-flash')
    app.engine.model=DeepSeekSectionedSynthesisModel(key,AttributedGoalLedger(gate),synthetic_only=True,output_tokens=8192,reasoning_effort='none',temperature=0)
    app.engine.mode=app.engine.mode.removesuffix('_fake_model')+'_live_model_synthesis'
    app.engine.query=gate
    worker=ContainerDiscovery(app.pilot,app.actor,bounded_queries=True);worker.start()
    server=create_server(ReviewerApp(app,args.accounts.resolve()),0)
    release=Path(__file__).resolve().parents[1]
    control={'pid':os.getpid(),'url':f'http://127.0.0.1:{server.server_port}/','runtime_version':runtime_version(),
             'release_directory':str(release),'release_commit':json.loads((trial/'RELEASE.json').read_text())['commit'],
             'app_js_sha256':hashlib.sha256((release/'web/app.js').read_bytes()).hexdigest(),
             'model':app.engine.model.name,'human_only':True,'grant':'human-team-closeout-20261015'}
    control_path=trial/'entry.json';control_path.write_text(json.dumps(control,indent=2)+'\n')
    print(json.dumps({'url':control['url'],'model':control['model'],'runtime_version':control['runtime_version']}),flush=True)
    def stop(*_):threading.Thread(target=server.shutdown,daemon=True).start()
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    try:server.serve_forever()
    finally:
        server.server_close();worker.close();rollback();store.db.close();ledger.close()


if __name__=='__main__':main()
