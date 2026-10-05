'use strict';
const $=id=>document.getElementById(id);
let session=null,historyId=null,health=null;
const bootstrapTicket=new URLSearchParams(location.hash.slice(1)).get('ticket');
if(location.hash)history.replaceState(null,'',location.pathname+location.search);
$('loginForm').querySelector('button').disabled=true;
const versionLabel=e=>e.locator?.content_sha256?'Content snapshot '+e.locator.content_sha256.slice(0,12):'Version '+e.version;
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
function expiredSession(){session=null;historyId=null;$('answer').replaceChildren();$('other').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();$('identity').textContent='Not signed in';$('auditNav').hidden=true;$('sourcesNav').hidden=true;show('login');const error=Error(health?.auth_kind==='operator'?'This session ended. Open the latest one-time link from the running operator terminal.':'This session ended. Sign in again.');error.sessionExpired=true;return error;}
async function api(path,data,raw=false){const options={credentials:'same-origin',headers:{}};if(data!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.headers['X-CSRF-Token']=session?.csrf||'';options.body=JSON.stringify(data);}const response=await fetch(path,options);const text=raw?await response.text():null;const result=raw?JSON.parse(text):await response.json();if(!response.ok){if(response.status===403&&session&&path!=='/api/session'){const current=await fetch('/api/session',{credentials:'same-origin'});if(current.status===403)throw expiredSession();}throw Error(result.error||'Request unavailable');}return raw?{parsed:result,text}:result;}
function show(name){for(const id of ['login','workspace','other'])$(id).hidden=id!==name;$('status').textContent='';}
function identity(){const box=$('identity');box.replaceChildren(el('span',session.actor));const logout=el('button',health?.auth_kind==='operator'?'Sign out':'Switch demo identity');logout.onclick=async()=>{await api('/api/logout',{});session=null;historyId=null;$('answer').replaceChildren();$('other').replaceChildren();$('auditNav').hidden=true;$('sourcesNav').hidden=true;box.textContent='Not signed in';show('login');};box.append(logout);$('auditNav').hidden=session.actor!=='auditor';$('sourcesNav').hidden=session.actor!=='auditor';show('workspace');}
async function preview(id){try{const e=await api('/api/evidence/'+encodeURIComponent(id));const body=$('previewBody');body.replaceChildren(el('h2',e.title),el('p',e.text),el('p',versionLabel(e),'muted'),el('pre',JSON.stringify(e.locator,null,2)),el('p',e.source_url,'muted'));$('preview').showModal();}catch(e){$('answer').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();if(e.sessionExpired){$('status').textContent=e.message;return;}$('other').replaceChildren(el('p','Evidence is unavailable or has changed. Ask again for current sources.','notice'));$('status').textContent='Evidence is unavailable or has changed. Ask again for current sources.';}}
async function exportAnswer(id){$('answer').replaceChildren();$('other').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();$('status').textContent='Checking current access before export…';try{if(!/^[0-9a-f]{32}$/.test(id))throw Error('Answer unavailable for export.');const result=await api('/api/export/'+id,undefined,true);const answer=result.parsed.history?.[0];if(!answer||answer.unavailable||answer.request_id!==id)throw Error('Answer unavailable for export. Ask again for current evidence.');const url=URL.createObjectURL(new Blob([result.text+'\n'],{type:'application/json'}));try{const link=el('a');link.href=url;link.download='ContextLedger-'+id+'.json';link.click();}finally{URL.revokeObjectURL(url);}$('status').textContent='Download requested after current access checks. Saved copies cannot be withdrawn later.';}catch(error){$('status').textContent=error.message;}}
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
  return answer.model_call?.called===true?'Answer recorded. Live model selected authorized source excerpts.':'Answer recorded. Model usage was not recorded.';
}
function renderAnswer(answer,target=$('answer')){target.replaceChildren();if(answer.unavailable){target.append(el('p',answer.message,'notice'));return;}const grid=el('div',undefined,'receipt'),main=el('div',undefined,'panel'),side=el('aside',undefined,'panel');const head=el('div',undefined,'receipt-head');head.append(el('h2',answer.claim_format==='grounded_synthesis_v1'?'Evidence-backed answer':'Evidence-backed excerpts'),el('span',modelLabel(answer),'tag'));main.append(head);for(const c of answer.claims){const block=el('div',undefined,'claim');block.append(el('p',c.text));if(c.supports?.length){const quotes=el('details');quotes.append(el('summary','Exact supporting quotes'));for(const support of c.supports)quotes.append(el('p',support.quote),el('p',support.evidence_id,'muted'));block.append(quotes);}for(const id of c.evidence_ids){const b=el('button',id,'citation');b.onclick=()=>preview(id);block.append(b);}main.append(block);}for(const u of answer.uncertainties)main.append(el('p',u,'notice'));main.append(el('p','Receipt '+answer.request_id,'muted'));const exportButton=el('button','Export answer');exportButton.onclick=()=>exportAnswer(answer.request_id);main.append(exportButton);renderModelUsage(answer,main);side.append(el('h3','Source evidence'));for(const e of answer.evidence){const card=el('div',undefined,'source-card');card.append(el('span',e.source,'source-name'));const b=el('button',e.title);b.onclick=()=>preview(e.evidence_id);card.append(el('p'),b,el('p',versionLabel(e)+' · '+JSON.stringify(e.locator)),el('p','Source updated '+new Date(e.source_updated_at).toLocaleString()),el('p','Indexed '+new Date(e.indexed_at).toLocaleString()));side.append(card);}if(!answer.evidence.length)side.append(el('p','No supporting evidence is available for this answer.'));grid.append(main,side);target.append(grid);}
$('loginForm').onsubmit=async e=>{e.preventDefault();try{if(health?.auth_kind!=='demo')throw Error('Open the one-time link from the operator terminal.');session=await api(health.login_path,{user:$('user').value});identity();}catch(err){$('status').textContent=err.message;}};
$('queryForm').onsubmit=async e=>{e.preventDefault();$('answer').replaceChildren();$('other').replaceChildren();$('ask').disabled=true;$('status').textContent='Checking access and assembling evidence…';try{const data={question:$('question').value};if(historyId)data.history_id=historyId;const a=await api('/api/query',data);historyId=a.request_id;renderAnswer(a);$('status').textContent=answerStatus(a);}catch(err){$('answer').replaceChildren();$('status').textContent=err.message;}finally{$('ask').disabled=false;}};
for(const b of document.querySelectorAll('[data-question]'))b.onclick=()=>{$('question').value=b.dataset.question;$('question').focus();};
$('workspaceNav').onclick=()=>{$('answer').replaceChildren();$('other').replaceChildren();show(session?'workspace':'login');};
$('historyNav').onclick=async()=>{if(!session)return;$('answer').replaceChildren();show('other');$('other').replaceChildren(el('h1','Recent answers'),el('p','Access and versions are checked again before answers are displayed.','lede'));try{const result=await api('/api/history');for(const a of result.history){const item=el('div',undefined,'history-item');renderAnswer(a,item);$('other').append(item);}if(!result.history.length)$('other').append(el('p','No answers yet.'));}catch(e){$('status').textContent=e.message;}};
$('sourcesNav').onclick=async()=>{show('other');$('other').replaceChildren(el('h1','Source coverage'),el('p','Fixture adapters are active. Live integrations are blocked pending explicit authorization.','lede'));try{const r=await api('/api/sources/status');for(const s of r.sources){const card=el('div',undefined,'panel');card.append(el('h2',s.source),el('p','Status: '+s.status),el('p','Live: '+s.live),el('p',s.authority));$('other').append(card);}}catch(e){$('status').textContent=e.message;}};
$('auditNav').onclick=()=>{show('other');const root=$('other');root.replaceChildren(el('h1','Audit explorer'),el('p','Scoped to eng_a, eng_b and product_ops. Events describe application activity, not proof that a person read the answer.','lede'));const form=el('form',undefined,'audit-form'),input=el('input');input.setAttribute('aria-label','Audit inquiry');input.value='Show everything jdoe accessed related to payment-service in the last 30 days.';const button=el('button','Find events','primary');form.append(input,button);const output=el('div');root.append(form,output);let filters=null;async function display(result,append=false){if(!append)output.replaceChildren(el('pre',JSON.stringify(result.filters,null,2)),el('p',result.total+' exact matching events · snapshot '+result.as_of));for(const row of result.events){const d=el('details',undefined,'history-item');d.append(el('summary',row.seq+' · '+row.event_type+' · '+row.actor+' · '+row.timestamp),el('pre',JSON.stringify(row.payload,null,2)));output.append(d);}filters=result.filters;if(result.next_after){const next=el('button','Load next page');next.onclick=async()=>{next.remove();try{await display(await api('/api/audit/events',{...filters,after:result.next_after}),true);}catch(e){$('status').textContent=e.message;}};output.append(next);}}form.onsubmit=async e=>{e.preventDefault();try{await display(await api('/api/audit/inquire',{question:input.value}));}catch(err){$('status').textContent='Use the shown inquiry template. '+err.message;}};};
$('closePreview').onclick=()=>$('preview').close();
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
