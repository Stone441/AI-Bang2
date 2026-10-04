"""Actual isolated S-01..S-05 execution. Expected assertions never populate actual output."""
import copy
import hashlib
import json
import platform
import subprocess
import tempfile
import time
from pathlib import Path
from brain.audit import Audit,verify_chain
from scripts.build_metadata import revision,dirty
from brain.contracts import Actor,MODE,now
from brain.engine import Engine
from brain.ingestion import Ingestion
from brain.sources import FixtureWorld
from brain.store import Store


def run(output):
    started=now(); world=FixtureWorld();store=Store();store.initialize(world)
    audit=Audit(store);engine=Engine(store,world,audit);ingest=Ingestion(store,world)
    scenarios=[]
    def execute(sid,operation):
        start=time.perf_counter()
        try:
            actual=operation()
            scenarios.append({'id':sid,'status':'passed_local_subset','actual':actual,'duration_ms':round((time.perf_counter()-start)*1000,3)})
        except Exception as error:
            scenarios.append({'id':sid,'status':'failed','error':str(error)})
            raise
    def s1():
        question='What caused the payment-service incident, which early explanation was ruled out, what follow-up remains open, and which runbook should I use?'
        answer=engine.query(Actor('eng_a'),question)
        texts=' '.join(c['text'] for c in answer['claims'])
        for fact in ['timeout budget','withdrawn','In Progress','Runbook v1']:assert fact in texts
        assert {e['source'] for e in answer['evidence']}=={'confluence','jira','slack','drive'}
        assert not {'C-03','J-01-comment-sec'} & {e['resource_id'] for e in answer['evidence']}
        product=engine.query(Actor('product_ops'),'Can we offer payment-retry to all customers today?')
        assert 'not approved' in json.dumps(product)
        return {'question':question,'answer':answer,'product_answer':product}
    def s2():
        changes=dict(world.baseline['updates']['C-01']);changes['source_updated_at']=now()
        event=world.mutate('C-01','content',**changes);sync=ingest.process(event)
        answer=engine.query(Actor('eng_a'),'What is the latest payment-service runbook, including the new failover check?')
        evidence=next(e for e in answer['evidence'] if e['resource_id']=='C-01')
        assert evidence['version']==2 and 'standby processing queue' in evidence['text']
        assert sync['processed_objects']==1
        return {'sync':sync,'answer':answer,'trigger':'direct fixture event, no live API or automatic source webhook'}
    def s3():
        answer=engine.query(Actor('contractor'),'Show me the Q3 security incident report.')
        assert answer['evidence']==[]
        assert 'CANARY_SEC' not in json.dumps(answer)
        return {'answer':answer,'model_input':engine.model.calls[-1]}
    def s4():
        first=engine.query(Actor('eng_a'),'Summarize the payment-service incident thread.')
        assert 'S-01' in {e['resource_id'] for e in first['evidence']}
        event=world.mutate('S-01','revoke',user_id='eng_a')
        answer=engine.query(Actor('eng_a'),'Repeat the details from the incident thread you just used.',first['request_id'])
        assert 'S-01' not in {e['resource_id'] for e in answer['evidence']}
        assert 'CANARY_THREAD' not in json.dumps(engine.model.calls[-1])
        history=engine.safe_history(Actor('eng_a'),first['request_id'])
        assert history[0]['unavailable']
        try:engine.evidence(Actor('eng_a'),'S-01@1')
        except PermissionError:preview='denied'
        else:raise AssertionError('revoked preview allowed')
        return {'prior_request_id':first['request_id'],'source_event_id':event['event_id'],'local_acl_refreshed':False,'answer':answer,'model_input':engine.model.calls[-1],'history':history,'preview':preview}
    def s5():
        from brain.audit_query import parse_inquiry
        question='Show everything jdoe accessed related to payment-service in the last 30 days.'
        filters=parse_inquiry(question); filters['page_size']=7
        before=audit.export()
        requests={e['request_id'] for e in before if e['actor']=='eng_a' and e['payload'].get('resource_scope')=='payment-service'}
        expected=[e['seq'] for e in before if e['actor']=='eng_a' and e['request_id'] in requests]
        page=audit.inquire(Actor('auditor'),filters);events=list(page['events']);pages=1;actual_filters=page['filters']
        while page['next_after']:
            page=audit.inquire(Actor('auditor'),dict(page['filters'],after=page['next_after']));events.extend(page['events']);pages+=1
        assert [e['seq'] for e in events]==expected
        assert any(e['event_type']=='response_committed' for e in events)
        chain=audit.export();head={'through_seq':len(chain),'head_hash':chain[-1]['hash']}
        tampered=copy.deepcopy(chain);tampered[0]['payload']['query']='modified copy'
        checks={'original':verify_chain(chain,head),'modified':verify_chain(tampered,head),'middle_deleted':verify_chain(chain[:2]+chain[3:],head),'covered_tail_deleted':verify_chain(chain[:-1],head)}
        assert checks['original']['valid'] and all(not checks[k]['valid'] for k in ['modified','middle_deleted','covered_tail_deleted'])
        return {'question':question,'filters':actual_filters,'pages':pages,'event_ids':[e['seq'] for e in events],'events':events,'checks':checks,
                'limitations':['Checkpoint held in test memory, not signed or independently operated.','A-02 database role isolation and A-03/A-04 signed checkpoint acceptance remain blocked.']}
    try:
        for sid,fn in [('S-01',s1),('S-02',s2),('S-03',s3),('S-04',s4),('S-05',s5)]:execute(sid,fn)
    finally:
        tracked={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['brain','fixtures','web','scripts','tests'] for p in sorted(Path(folder).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
        report={'started_at':started,'finished_at':now(),'mode':MODE,'model':engine.model.name,'python':platform.python_version(),
                'commit':revision(),'source_hashes':tracked,
                'worktree_dirty':dirty(),
                'scenarios':scenarios,'live_api':'not_run','live_model':'not_run','human_G1':'not_run','codebuddy':'verified_local_delivery_separate_from_scenario_run','codebuddy_evidence_index':'evidence/tool-usage/README.md'}
        output.mkdir(parents=True,exist_ok=True)
        (output/'scenarios.json').write_text(json.dumps(report,indent=2)+'\n')
        (output/'audit.json').write_text(json.dumps(audit.export(),indent=2)+'\n')
        store.db.close()
    print(json.dumps({'mode':MODE,'scenarios':[{k:s[k] for k in ['id','status']} for s in scenarios],'report':str(output/'scenarios.json')},indent=2))
    return report

if __name__=='__main__':run(Path('evidence/runs/local-latest'))
