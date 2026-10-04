import re
import uuid
from dataclasses import asdict
from .contracts import Actor, Evidence, MODE, TENANT
from .sources import policy_allows

STOP=set('what which the a an of is are was were to in on and or from with can we i me you your my do does it for all today latest current including caused use show details just'.split())


def tokens(text):
    return {t for t in re.findall(r'[a-z0-9]+(?:-[a-z0-9]+)*',text.lower()) if t not in STOP}


class FakeExtractiveModel:
    name='fake-extractive-v1'
    def __init__(self):
        self.calls=[]  # Test probe: synthetic only; no third-party traces.
    def generate(self, question, evidence):
        self.calls.append({'question':question,'evidence':[e.to_dict() for e in evidence]})
        return {'claims':[{'text':e.text,'evidence_ids':[e.evidence_id]} for e in evidence],
                'uncertainties':['These are source excerpts from synthetic fixtures, not a live AI synthesis.'] if evidence else ['Insufficient evidence in the currently accessible material.']}


class Engine:
    def __init__(self, store, world, audit, model=None):
        self.store,self.world,self.audit=store,world,audit
        self.model=model or FakeExtractiveModel()
        self.before_dispatch=None

    def check(self, actor, resource, request_id, phase):
        decision=self.world.adapter(resource['source']).check_read(actor,resource['id'])
        self.audit.append('authorization_decided',actor.user_id,request_id,
                          {'resource_id':resource['id'],'source':resource['source'],'version':resource['version'],
                           'phase':phase,'resource_scope':'payment-service',**asdict(decision)})
        return decision.result=='allow'

    def query(self, actor:Actor, question, history_id=None):
        if actor.tenant!=TENANT or actor.user_id not in self.world.users:
            raise PermissionError('Unavailable')
        if not isinstance(question,str) or not question.strip() or len(question)>4000:
            raise ValueError('Question must contain 1–4000 characters')
        rid=uuid.uuid4().hex
        self.audit.append('request_started',actor.user_id,rid,{'query':question,'mode':MODE,'candidate_strategy':'local ACL snapshot + keyword overlap + authorized one-hop links','history_id':history_id})
        try:
            query_tokens=tokens(question)
            # No previous assistant prose enters retrieval or a model. Only reauthorized dependency IDs can supplement a follow-up.
            previous=self.store.run(history_id,actor.user_id) if history_id else None
            dependency_ids={e['resource_id'] for e in previous.get('evidence',[])} if previous else set()
            candidates=[]
            for resource in self.store.resources():
                if resource['tenant']!=actor.tenant: continue
                if not policy_allows(actor.user_id,self.world.users[actor.user_id],resource['policy']): continue
                score=len(query_tokens & tokens(resource['title']+' '+resource['text']))
                if resource['id'] in dependency_ids: score+=1
                if score: candidates.append((score,resource))
            candidates.sort(key=lambda pair:(-pair[0],pair[1]['id']))
            # Expand only links from currently authorized seeds. Targets still receive their
            # own local prefilter and final source check below; links never grant access.
            seed_ids={r['id'] for _,r in candidates}
            expansions=[]
            for _,seed in candidates[:12]:
                if not self.check(actor,seed,rid,'link_seed'): continue
                if self.world.resources[seed['id']]['version']!=seed['version']: continue
                for target_id in seed.get('links',[]):
                    if target_id in seed_ids: continue
                    target=self.store.get(target_id)
                    if (target and target['tenant']==actor.tenant
                            and policy_allows(actor.user_id,self.world.users[actor.user_id],target['policy'])):
                        expansions.append((0,target));seed_ids.add(target_id)
            candidates=candidates[:16]+expansions[:8]
            selected=[]; budget=16000
            for score,r in candidates[:24]:
                self.audit.append('candidate_evaluated',actor.user_id,rid,{'resource_id':r['id'],'source':r['source'],'score':score,'resource_scope':'payment-service'})
                if not self.check(actor,r,rid,'before_model'): continue
                current=self.world.resources[r['id']]
                if current['version']!=r['version'] or not current['active']: continue
                if len(r['text'])>budget: continue
                budget-=len(r['text'])
                selected.append(Evidence(r['id']+'@'+str(r['version']),r['id'],r['version'],r['source'],r['title'],r['locator'],r['text'],r['source_updated_at'],r['indexed_at'],r['source_url']))
            for e in selected:
                self.audit.append('evidence_used',actor.user_id,rid,{'evidence_id':e.evidence_id,'resource_id':e.resource_id,'source':e.source,'version':e.version,'stage':'sent_to_model','resource_scope':'payment-service'})
            draft=self.model.generate(question,selected)
            by_id={e.evidence_id:e for e in selected}
            # Exact extractive support is intentionally strict for this provider.
            claims=[]
            for claim in draft.get('claims',[]):
                ids=claim.get('evidence_ids',[])
                if not ids or any(i not in by_id for i in ids): raise ValueError('Unsupported model citation')
                if not isinstance(claim.get('text'),str) or not any(claim['text']==by_id[i].text for i in ids):
                    raise ValueError('Unsupported model claim')
                claims.append({'text':claim['text'],'evidence_ids':ids})
            self.audit.append('generation_completed',actor.user_id,rid,{'model':self.model.name,'cited':[i for c in claims for i in c['evidence_ids']]})
            if self.before_dispatch: self.before_dispatch()
            for e in selected:
                resource=self.store.get(e.resource_id)
                if (not resource or resource['version']!=e.version or not self.check(actor,resource,rid,'before_dispatch')
                        or self.world.resources[e.resource_id]['version']!=e.version):
                    raise PermissionError('Evidence changed; please ask again')
            response={'request_id':rid,'mode':MODE,'model':self.model.name,'claims':claims,
                      'uncertainties':['Source excerpts only; live AI synthesis is not enabled.'] if selected else ['Insufficient evidence in the currently accessible material.'],
                      'evidence':[e.to_dict() for e in selected], 'actor':actor.user_id}
            self.audit.append('response_committed',actor.user_id,rid,{'response':response})
            self.store.save_run(rid,actor.user_id,response)
            return response
        except Exception:
            self.audit.append('request_failed',actor.user_id,rid,{'reason':'request_stopped'})
            raise

    def evidence(self, actor, eid):
        try:
            resource_id,version=eid.rsplit('@',1)
            r=self.store.get(resource_id)
            if not r or r['version']!=int(version): raise ValueError()
            if not self.check(actor,r,'evidence','preview'): raise ValueError()
            if self.world.resources[resource_id]['version']!=r['version']: raise ValueError()
        except (KeyError,ValueError):
            raise PermissionError('Unavailable') from None
        return {'evidence_id':eid,'title':r['title'],'text':r['text'],'locator':r['locator'],'version':r['version'],'source_url':r['source_url']}

    def safe_history(self, actor, request_id=None):
        records=[self.store.run(request_id,actor.user_id)] if request_id else self.store.history(actor.user_id)
        result=[]
        for record in records:
            if not record: continue
            allowed=True
            for e in record['evidence']:
                try: self.evidence(actor,e['evidence_id'])
                except PermissionError: allowed=False; break
            result.append(record if allowed else {'request_id':record['request_id'],'unavailable':True,'message':'This answer is no longer available. Ask again for current evidence.'})
        return result
