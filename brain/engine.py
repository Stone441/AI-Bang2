import uuid
from dataclasses import asdict
from .contracts import Actor, Evidence, MODE, TENANT
from .sources import policy_allows
from .model_receipt import public_receipt

from .retrieval import tokens, ranked_windows, window_evidence, resolve_window


class FakeExtractiveModel:
    name='fake-extractive-v1'
    def __init__(self):
        self.calls=[]  # Test probe: synthetic only; no third-party traces.
    def generate(self, question, evidence):
        self.calls.append({'question':question,'evidence':[e.to_dict() for e in evidence]})
        return {'claims':[{'text':e.text,'evidence_ids':[e.evidence_id]} for e in evidence],
                'uncertainties':['These are source excerpts from synthetic fixtures, not a live AI synthesis.'] if evidence else ['Insufficient evidence in the currently accessible material.']}


class Engine:
    def __init__(self, store, world, audit, model=None, *, tenant=TENANT, mode=MODE):
        self.store,self.world,self.audit=store,world,audit
        self.model=model or FakeExtractiveModel()
        self.tenant,self.mode=tenant,mode
        self.before_dispatch=None

    def prefilter(self, actor, resource):
        if hasattr(self.world, 'prefilter'):
            return self.world.prefilter(actor, resource)
        return policy_allows(actor.user_id,self.world.users[actor.user_id],resource['policy'])

    def validate_actor(self, actor):
        if actor.tenant!=self.tenant or actor.user_id not in self.world.users:
            raise PermissionError('Unavailable')

    def check(self, actor, resource, request_id, phase):
        decision=self.world.adapter(resource['source']).check_read(actor,resource['id'])
        self.audit.append('authorization_decided',actor.user_id,request_id,
                          {'resource_id':resource['id'],'source':resource['source'],'version':resource['version'],
                           'phase':phase,'resource_scope':'payment-service',**asdict(decision)})
        return decision.result=='allow'

    def query(self, actor:Actor, question, history_id=None):
        self.validate_actor(actor)
        if not isinstance(question,str) or not question.strip() or len(question)>4000:
            raise ValueError('Question must contain 1–4000 characters')
        rid=uuid.uuid4().hex
        self.audit.append('request_started',actor.user_id,rid,{'query':question,'mode':self.mode,'candidate_strategy':'authority prefilter + lexical aliases + exact windows + authorized one-hop links','history_id':None,'query_kind':'independent'})
        try:
            if hasattr(self.world, 'prepare'):
                self.world.prepare(actor,self.store,self.audit,rid)
            query_tokens=tokens(question)
            # Legacy in-process history_id is accepted for old harness compatibility only.
            # Independent queries never read or supplement previous answer dependencies.
            candidates=[]
            for resource in self.store.resources():
                if resource['tenant']!=actor.tenant: continue
                if not self.prefilter(actor,resource): continue
                windows=ranked_windows(resource,query_tokens)
                score=windows[0][0] if windows else 0
                if score: candidates.append((score,resource))
            candidates.sort(key=lambda pair:(-pair[0],pair[1]['id']))
            # Expand only links from currently authorized seeds. Targets still receive their
            # own local prefilter and final source check below; links never grant access.
            seed_ids={r['id'] for _,r in candidates}
            expansions=[]
            for _,seed in candidates[:12]:
                # This check only authorizes link expansion. Linkless candidates
                # still receive before_model, model_dispatch and before_dispatch
                # native checks; avoid a full source read for an empty operation.
                if not seed.get('links'): continue
                if not self.check(actor,seed,rid,'link_seed'): continue
                if self.world.resources[seed['id']]['version']!=seed['version']: continue
                for target_id in seed.get('links',[]):
                    if target_id in seed_ids: continue
                    target=self.store.get(target_id)
                    if (target and target['tenant']==actor.tenant
                            and self.prefilter(actor,target)):
                        expansions.append((0,target));seed_ids.add(target_id)
            candidates=candidates[:16]+expansions[:8]
            selected=[]; budget=16000
            for score,r in candidates[:24]:
                self.audit.append('candidate_evaluated',actor.user_id,rid,{'resource_id':r['id'],'source':r['source'],'score':score,'resource_scope':'payment-service'})
                if not self.check(actor,r,rid,'before_model'): continue
                current=self.world.resources[r['id']]
                if current['version']!=r['version'] or not current['active']: continue
                for _,start,end in ranked_windows(r,query_tokens,supplementary=True):
                    eid,locator,text=window_evidence(r,start,end)
                    if len(selected)>=24: break
                    if len(text)>budget: continue
                    budget-=len(text)
                    selected.append(Evidence(eid,r['id'],r['version'],r['source'],r['title'],locator,text,r['source_updated_at'],r['indexed_at'],r['source_url']))
            # Recheck the complete selected set immediately before model dispatch.
            # A later candidate read may have observed a permission/content change.
            for e in selected:
                resource=self.store.get(e.resource_id)
                if (not resource or not self.check(actor,resource,rid,'model_dispatch')
                        or self.world.resources[e.resource_id]['version']!=e.version):
                    raise PermissionError('Evidence changed; please ask again')
            for e in selected:
                self.audit.append('evidence_used',actor.user_id,rid,{'evidence_id':e.evidence_id,'resource_id':e.resource_id,'source':e.source,'version':e.version,'stage':'prepared_for_answer','resource_scope':'payment-service'})
            def authorize_model_stage(phase):
                if phase!='review_dispatch': raise ValueError('Invalid model stage')
                for e in selected:
                    resource=self.store.get(e.resource_id)
                    if (not resource or not self.check(actor,resource,rid,phase)
                            or self.world.resources[e.resource_id]['version']!=e.version):
                        raise PermissionError('Evidence changed; please ask again')
                for e in selected:
                    self.audit.append('evidence_used',actor.user_id,rid,
                                      {'evidence_id':e.evidence_id,'resource_id':e.resource_id,
                                       'source':e.source,'version':e.version,'stage':'prepared_for_review',
                                       'resource_scope':'payment-service'})
            if hasattr(self.model,'generate_with_provenance'):
                from .synthetic_provenance import SyntheticProvenance
                provenance = SyntheticProvenance(
                    getattr(self.world, 'approved_synthetic_resource_ids', ()), self.world.resources.get)
                def observe_model(event, payload):
                    if event not in ('model_dispatch_intent','model_dispatch_attempted','model_usage_received',
                                     'model_output_accepted','model_output_rejected'):
                        raise ValueError('Invalid model event')
                    self.audit.append(event,actor.user_id,rid,{**payload,'resource_scope':'payment-service'})
                draft=self.model.generate_with_provenance(question,selected,rid,provenance,authorize_model_stage,observe_model)
            elif hasattr(self.model,'generate_with_authorization'):
                draft=self.model.generate_with_authorization(question,selected,rid,authorize_model_stage)
            elif hasattr(self.model,'generate_for_request'):
                draft=self.model.generate_for_request(question,selected,rid)
            else:
                draft=self.model.generate(question,selected)
            by_id={e.evidence_id:e for e in selected}
            # Exact extractive support is intentionally strict for this provider.
            claims=[]
            synthesis=draft.get('claim_format')=='grounded_synthesis_v1'
            if synthesis:
                if (getattr(self.model,'claim_format',None)!='grounded_synthesis_v1'
                        or draft.get('review_status')!='accepted'):
                    raise ValueError('Unreviewed synthesis')
                review_receipt=public_receipt(draft.get('model_review'),rid)
                if review_receipt['called'] is not True: raise ValueError('Missing review receipt')
            for claim in draft.get('claims',[]):
                ids=claim.get('evidence_ids',[])
                if not ids or any(i not in by_id for i in ids): raise ValueError('Unsupported model citation')
                if synthesis:
                    from .synthesis import validate_claim
                    validate_claim(claim,selected)
                    claims.append(claim)
                    continue
                if not isinstance(claim.get('text'),str) or not any(claim['text']==by_id[i].text for i in ids):
                    raise ValueError('Unsupported model claim')
                claims.append({'text':claim['text'],'evidence_ids':ids})
            generation={'model':self.model.name,'cited':[i for c in claims for i in c['evidence_ids']]}
            if 'model_call' in draft:
                receipt=public_receipt(draft['model_call'],rid)
                if receipt['called'] is False and selected:
                    raise ValueError('No-call receipt contradicts model input')
                generation['model_call']=receipt
            if synthesis:
                if generation['model_call']['reservation_id']==review_receipt['reservation_id']:
                    raise ValueError('Model review must be a separate request')
                generation.update(claim_format='grounded_synthesis_v1',model_review=review_receipt,
                                  review_status='accepted')
            self.audit.append('generation_completed',actor.user_id,rid,generation)
            if self.before_dispatch: self.before_dispatch()
            for e in selected:
                resource=self.store.get(e.resource_id)
                if (not resource or resource['version']!=e.version or not self.check(actor,resource,rid,'before_dispatch')
                        or self.world.resources[e.resource_id]['version']!=e.version):
                    raise PermissionError('Evidence changed; please ask again')
            response={'request_id':rid,'mode':self.mode,'model':self.model.name,'claims':claims,
                      'uncertainties':[getattr(self.model,'answer_notice','Source excerpts only; live AI synthesis is not enabled.')] if claims else ['Insufficient evidence in the currently accessible material.'],
                      'evidence':[e.to_dict() for e in selected], 'actor':actor.user_id}
            if 'model_call' in generation: response['model_call']=generation['model_call']
            if synthesis:
                response.update(claim_format=generation['claim_format'],model_review=review_receipt,
                                review_status='accepted')
            self.audit.append('response_committed',actor.user_id,rid,{'response':response})
            self.store.save_run(rid,actor.user_id,response)
            return response
        except Exception as error:
            from .deepseek import PriceReviewRequired, ModelInputRejected, ModelUnavailable
            from .budget import BudgetExceeded
            reason = ('model_price_review_required' if isinstance(error,PriceReviewRequired)
                      else 'model_budget_unavailable' if isinstance(error,BudgetExceeded)
                      else 'model_input_rejected' if isinstance(error,ModelInputRejected)
                      else 'model_input_or_output_unavailable' if isinstance(error,ModelUnavailable)
                      else 'request_stopped')
            self.audit.append('request_failed',actor.user_id,rid,{'reason':reason})
            raise

    def evidence(self, actor, eid):
        self.validate_actor(actor)
        try:
            resource_id,version=eid.rsplit('@',1)
            version=version.split('#',1)[0]
            r=self.store.get(resource_id)
            if not r or r['version']!=int(version): raise ValueError()
            if not self.check(actor,r,'evidence','preview'): raise ValueError()
            if self.world.resources[resource_id]['version']!=r['version']: raise ValueError()
            locator,text=resolve_window(r,eid)
        except (KeyError,ValueError):
            raise PermissionError('Unavailable') from None
        return {'evidence_id':eid,'title':r['title'],'text':text,'locator':locator,'version':r['version'],'source_url':r['source_url']}

    def safe_history(self, actor, request_id=None):
        self.validate_actor(actor)
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
