'use strict';
const $=id=>document.getElementById(id);
let session=null,health=null,viewRevision=0;
const viewToken=()=>({revision:viewRevision,session});
const currentView=token=>token.revision===viewRevision&&token.session===session;
const bootstrapTicket=new URLSearchParams(location.hash.slice(1)).get('ticket');
if(location.hash)history.replaceState(null,'',location.pathname+location.search);
$('loginForm').querySelector('button').disabled=true;
const versionLabel=e=>e.locator?.content_sha256?'Content snapshot '+e.locator.content_sha256.slice(0,12):'Version '+e.version;
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
function expiredSession(){session=null;$('answer').replaceChildren();$('other').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();$('identity').textContent='Not signed in';$('auditNav').hidden=true;$('sourcesNav').hidden=true;show('login');const error=Error(health?.auth_kind==='operator'?'This session ended. Open the latest one-time link from the running operator terminal.':'This session ended. Sign in again.');error.sessionExpired=true;$('status').textContent=error.message;return error;}
async function api(path,data){const requestSession=session;const options={credentials:'same-origin',headers:{}};if(data!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.headers['X-CSRF-Token']=session?.csrf||'';options.body=JSON.stringify(data);}const response=await fetch(path,options);const result=await response.json();if(!response.ok){if(requestSession!==session)throw Error('Stale response discarded');if(response.status===403&&session&&path!=='/api/session'){const current=await fetch('/api/session',{credentials:'same-origin'});if(current.status===403)throw expiredSession();}throw Error(result.error||'Request unavailable');}return result;}
function show(name){viewRevision++;$('ask').disabled=false;$('previewBody').replaceChildren();if($('preview').open)$('preview').close();for(const id of ['login','workspace','other'])$(id).hidden=id!==name;$('status').textContent='';}
function identity(){const box=$('identity');box.replaceChildren(el('span',session.actor));const logout=el('button',health?.auth_kind==='operator'?'Sign out':'Switch demo identity');logout.onclick=async()=>{viewRevision++;$('answer').replaceChildren();$('other').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();await api('/api/logout',{});session=null;$('answer').replaceChildren();$('other').replaceChildren();$('auditNav').hidden=true;$('sourcesNav').hidden=true;box.textContent='Not signed in';show('login');};box.append(logout);$('auditNav').hidden=session.actor!=='auditor';$('sourcesNav').hidden=session.actor!=='auditor';show('workspace');}
async function preview(id){viewRevision++;const view=viewToken();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();try{const e=await api('/api/evidence/'+encodeURIComponent(id));if(!currentView(view))return;const body=$('previewBody');body.replaceChildren(el('h2',e.title),el('p',e.text),el('p',versionLabel(e),'muted'),el('pre',JSON.stringify(e.locator,null,2)),el('p',e.source_url,'muted'));$('preview').showModal();}catch(e){if(!currentView(view))return;$('answer').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();if(e.sessionExpired){$('status').textContent=e.message;return;}$('other').replaceChildren(el('p','Evidence is unavailable or has changed. Ask again for current sources.','notice'));$('status').textContent='Evidence is unavailable or has changed. Ask again for current sources.';}}
function modelLabel(answer){
  if(answer.model==='fake-extractive-v1')return 'FAKE MODEL';
  if(answer.model_call?.called===false)return 'NO MODEL CALL';
  if(answer.model_call?.called===true)return answer.claim_format==='grounded_synthesis_v1'?'LIVE MODEL · REVIEWED SYNTHESIS':'LIVE MODEL · SOURCE EXCERPTS';
  return 'MODEL CALL NOT RECORDED';
}
function renderModelUsage(answer,target){
  const receipt=answer.model_call;
  if(answer.model==='fake-extractive-v1')return;
  if(receipt?.called===false){target.append(el('p','No external model request was sent.','muted'));return;}
  if(receipt?.called!==true){target.append(el('p','Model usage was not recorded for this answer.','muted'));return;}
  const receipts=[receipt];
  if(answer.model_review?.called===true)receipts.push(answer.model_review);
  for(const [index,item] of receipts.entries()){
    const details=el('details',undefined,'model-usage');
    details.append(el('summary',index?'Evidence review usage receipt':'Model usage receipt'),
      el('p',item.prompt_tokens+' input + '+item.completion_tokens+' output = '+item.total_tokens+' tokens'),
      el('p','Conservative cost estimate: US$'+(item.accounted_upper_micro_usd/1000000).toFixed(6)),
      el('p','This is an accounting upper estimate, not the provider invoice.','muted'));
    target.append(details);
  }

}
function answerStatus(answer){
  if(answer.model_call?.called===false)return 'No supporting evidence found. No external model request was sent.';
  if(!answer.claims.length)return answer.model_call?.called===true?'The model checked authorized sources but found insufficient support.':'Insufficient supporting evidence.';
  if(answer.model==='fake-extractive-v1')return 'Answer recorded. Authorized synthetic source excerpts; fake model.';
  return answer.model_call?.called===true?(answer.claim_format==='grounded_synthesis_v1'?'Answer recorded. Grounded synthesis and model review completed.':'Answer recorded. Live model selected authorized source excerpts.'):'Answer recorded. Model usage was not recorded.';
}
function renderAnswer(answer,target=$('answer')){target.replaceChildren();if(answer.unavailable){target.append(el('p',answer.message,'notice'));return;}const grid=el('div',undefined,'receipt'),main=el('div',undefined,'panel'),side=el('aside',undefined,'panel');const head=el('div',undefined,'receipt-head');head.append(el('h2',answer.claim_format==='grounded_synthesis_v1'?'Evidence-backed answer':'Evidence-backed excerpts'),el('span',modelLabel(answer),'tag'));main.append(head);for(const c of answer.claims){const block=el('div',undefined,'claim');block.append(el('p',c.text));if(c.supports?.length){const quotes=el('details');quotes.append(el('summary','Exact supporting quotes'));for(const support of c.supports)quotes.append(el('p',support.quote),el('p',support.evidence_id,'muted'));block.append(quotes);}for(const id of c.evidence_ids){const b=el('button',id,'citation');b.onclick=()=>preview(id);block.append(b);}main.append(block);}for(const u of answer.uncertainties)main.append(el('p',u,'notice'));main.append(el('p','Receipt '+answer.request_id,'muted'));renderModelUsage(answer,main);side.append(el('h3','Source evidence'));for(const e of answer.evidence){const card=el('div',undefined,'source-card');card.append(el('span',e.source,'source-name'));const b=el('button',e.title);b.onclick=()=>preview(e.evidence_id);card.append(el('p'),b,el('p',versionLabel(e)+' · '+JSON.stringify(e.locator)),el('p','Source updated '+new Date(e.source_updated_at).toLocaleString()),el('p','Indexed '+new Date(e.indexed_at).toLocaleString()));side.append(card);}if(!answer.evidence.length)side.append(el('p','No supporting evidence is available for this answer.'));grid.append(main,side);target.append(grid);}
$('loginForm').onsubmit=async e=>{e.preventDefault();try{if(health?.auth_kind!=='demo')throw Error('Open the one-time link from the operator terminal.');session=await api(health.login_path,{user:$('user').value});identity();}catch(err){$('status').textContent=err.message;}};
$('queryForm').onsubmit=async e=>{e.preventDefault();viewRevision++;const view=viewToken();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();$('answer').replaceChildren();$('other').replaceChildren();$('ask').disabled=true;$('status').textContent='Checking access and assembling evidence…';try{const data={question:$('question').value};const a=await api('/api/query',data);if(!currentView(view))return;renderAnswer(a);$('status').textContent=answerStatus(a);}catch(err){if(currentView(view)){$('answer').replaceChildren();$('status').textContent=err.message;}}finally{if(currentView(view))$('ask').disabled=false;}};
for(const b of document.querySelectorAll('[data-question]'))b.onclick=()=>{$('question').value=b.dataset.question;$('question').focus();};
$('workspaceNav').onclick=()=>{$('answer').replaceChildren();$('other').replaceChildren();show(session?'workspace':'login');};
$('historyNav').onclick=async()=>{if(!session)return;$('answer').replaceChildren();show('other');const view=viewToken();$('other').replaceChildren(el('h1','Recent answers'),el('p','Access and versions are checked again before answers are displayed.','lede'));try{const result=await api('/api/history');if(!currentView(view))return;for(const a of result.history){const item=el('div',undefined,'history-item');renderAnswer(a,item);$('other').append(item);}if(!result.history.length)$('other').append(el('p','No answers yet.'));}catch(e){if(!currentView(view))return;$('status').textContent=e.message;}};
$('sourcesNav').onclick=async()=>{show('other');const view=viewToken();$('other').replaceChildren(el('h1','Source coverage'),el('p','Fixture adapters are active. Live integrations are blocked pending explicit authorization.','lede'));try{const r=await api('/api/sources/status');if(!currentView(view))return;for(const s of r.sources){const card=el('div',undefined,'panel');card.append(el('h2',s.source),el('p','Status: '+s.status),el('p','Live: '+s.live),el('p',s.authority));$('other').append(card);}}catch(e){if(!currentView(view))return;$('status').textContent=e.message;}};
function auditEvent(row){
  const labels={request_started:'Question',candidate_evaluated:'Retrieval candidate',authorization_decided:'Authorization decision',evidence_used:'Model evidence',generation_completed:'Generation and citations',response_committed:'Stored answer',response_dispatch_attempted:'Delivery attempt',request_failed:'Request stopped',audit_inquiry:'Audit inquiry',source_changed:'Source change'};
  const item=el('details',undefined,'history-item');
  item.append(el('summary',row.seq+' · '+(labels[row.event_type]||row.event_type)+' · '+row.actor+' · '+row.timestamp));
  item.append(el('p','Request: '+row.request_id,'muted'));
  const p=row.payload||{};
  if(row.event_type==='request_started')item.append(el('p',p.query));
  if(row.event_type==='candidate_evaluated')item.append(el('p','Candidate only — not proof of source access or model use.'));
  if(row.event_type==='authorization_decided'){
    item.append(el('p',(p.result||'unknown').toUpperCase()+' · '+p.phase+' · '+p.source+' · '+p.resource_id));
    if(p.version!==undefined&&p.version!==null)item.append(el('p',Number.isSafeInteger(p.version)?'Version: '+p.version:'Exact version is retained by the backend; use the string evidence ID to verify its fingerprint.','muted'));
  }
  if(row.event_type==='evidence_used')item.append(el('p',(p.stage==='sent_to_review'?'Sent to evidence review':p.stage==='sent_to_model'?'Sent to answer model':p.stage)+' · '+p.evidence_id));
  if(row.event_type==='generation_completed'){
    item.append(el('p','Model: '+p.model));
    item.append(el('p','Citations listed: '+(p.cited||[]).join(', ')));
  }
  if(row.event_type==='response_committed'){
    const answer=p.response||{};
    item.append(el('p','Recorded model: '+answer.model));
    for(const claim of answer.claims||[])item.append(el('p',claim.text));
    if(!(answer.claims||[]).length)item.append(el('p','No supported answer was stored.'));
  }
  if(row.event_type==='response_dispatch_attempted')item.append(el('p','Delivery was attempted; this does not prove the recipient read it.'));
  const raw=el('details');
  const payload=JSON.stringify(p,(_key,value)=>typeof value==='number'&&Number.isInteger(value)&&!Number.isSafeInteger(value)?'Exact integer unavailable in browser; consult backend export or string evidence ID':value,2);
  raw.append(el('summary','Event payload (browser view)'),el('pre',payload));item.append(raw);
  return item;
}
$('auditNav').onclick=()=>{
  show('other');const view=viewToken(),root=$('other');
  root.replaceChildren(el('h1','Audit explorer'),el('p','Scoped to eng_a, eng_b and product_ops. Events describe application activity, not proof that a person read the answer.','lede'));
  const form=el('form',undefined,'audit-form'),input=el('input');input.setAttribute('aria-label','Audit inquiry');
  input.value='Show everything jdoe accessed related to payment-service in the last 30 days.';
  const button=el('button','Find events','primary');form.append(input,button);const output=el('div');root.append(form,output);
  let inquiryRevision=0;
  const active=revision=>currentView(view)&&revision===inquiryRevision;
  function display(result,revision,append=false){
    if(!active(revision))return;
    if(!append){
      output.replaceChildren(el('h2','Query scope'),el('pre',JSON.stringify(result.filters,null,2)),el('p',result.total+' matching events · stable snapshot '+result.as_of));
      output.append(el('p','Candidates, authorization, model input, citations and delivery are separate stages. A readable timeline does not verify a signature or independent checkpoint.','notice'));
    }
    for(const row of result.events)output.append(auditEvent(row));
    if(result.next_after){
      const next=el('button','Load next page');
      next.onclick=async()=>{
        if(!active(revision)||next.disabled)return;
        next.disabled=true;
        try{
          const page=await api('/api/audit/events',{...result.filters,after:result.next_after});
          if(!active(revision))return;
          next.remove();display(page,revision,true);
        }catch(err){if(active(revision)){next.disabled=false;$('status').textContent=err.message;}}
      };
      output.append(next);
    }
  }
  form.onsubmit=async event=>{
    event.preventDefault();const revision=++inquiryRevision;
    output.replaceChildren();$('status').textContent='Finding scoped audit events…';
    try{
      const result=await api('/api/audit/inquire',{question:input.value});
      if(!active(revision))return;
      display(result,revision);$('status').textContent=result.total?'Audit events ready.':'No events match these filters.';
    }catch(err){if(active(revision)){output.replaceChildren();$('status').textContent='Use the shown inquiry template. '+err.message;}}
  };
};
$('closePreview').onclick=()=>{viewRevision++;$('previewBody').replaceChildren();$('preview').close();};
async function boot(){
  try{
    health=await api('/api/health');
    if(health.auth_kind==='operator'){
      $('modeBadge').textContent=health.mode.includes('mock_http')?'MOCK API PILOT':'LIVE API PILOT';
      $('modeDescription').textContent=health.mode.endsWith('_live_model_synthesis')?'Synthetic allowlisted resources · Grounded synthesis with model review · Local operator':health.mode.endsWith('_live_model_selection')?'Synthetic allowlisted resources · Live model selects excerpts · Local operator':'Synthetic allowlisted resources · Fake model · Local operator';
      $('modeFooter').textContent='Operator pilot · not employee SSO';
      $('user').hidden=true;$('loginForm').querySelector('label').hidden=true;
      $('loginForm').querySelector('button').hidden=true;
      $('loginNote').textContent='Open the one-time link from the server terminal. Token stays in the server process. This is a local operator pilot, not employee SSO.';
    }else if(health.auth_kind==='demo'){$('loginForm').querySelector('button').disabled=false;}
    else{throw Error('Unsupported authentication mode.');}
    try{session=await api('/api/session');}
    catch(err){if(bootstrapTicket&&health.auth_kind==='operator')session=await api(health.login_path,{ticket:bootstrapTicket});else throw err;}
    identity();
  }catch(err){show('login');if(health?.auth_kind==='operator')$('status').textContent='Operator link is missing, expired or already used. Restart the server for a new link.';}
}
boot();
