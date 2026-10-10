'use strict';
const $=id=>document.getElementById(id);
let session=null,health=null,viewRevision=0;
const viewToken=()=>({revision:viewRevision,session});
const currentView=token=>token.revision===viewRevision&&token.session===session;
let pendingQuery=null,waitTimer=null,runtimeTimer=null,runtimeSequence=0,runtimeApplied=0,resumeOnRuntime=false,resumeInputValue='';
const clockNow=()=>typeof performance!=='undefined'?performance.now():Date.now();
function stopRuntime(){runtimeApplied=++runtimeSequence;if(runtimeTimer!==null&&typeof clearInterval!=='undefined')clearInterval(runtimeTimer);runtimeTimer=null;$('runtime').hidden=true;$('runtimeModel').textContent='';$('runtimeDetails').textContent='';$('runtimeSources').replaceChildren();}
function stopWaiting(){if(waitTimer!==null&&typeof clearInterval!=='undefined')clearInterval(waitTimer);waitTimer=null;pendingQuery=null;$('question').readOnly=false;$('runningQuestion').textContent='';$('queryForm').setAttribute('aria-busy','false');$('progress').hidden=true;}
function savedQuestion(){try{return JSON.parse(sessionStorage.getItem('brain.pending.'+session.csrf)||'null');}catch(_){return null;}}
function saveQuestion(requestId=null,question=null){try{question=question??pendingQuery?.question??savedQuestion()?.question;if(question!==null&&question!==undefined)sessionStorage.setItem('brain.pending.'+session.csrf,JSON.stringify({question,requestId}));}catch(_){}}
function forgetQuestion(){try{if(session){sessionStorage.removeItem('brain.pending.'+session.csrf);sessionStorage.removeItem('brain.answer.'+session.csrf);}}catch(_){}}
function answerReference(){try{return JSON.parse(sessionStorage.getItem('brain.answer.'+session.csrf)||'null');}catch(_){return null;}}
function rememberAnswer(answer){if(answer.unavailable)return;try{sessionStorage.setItem('brain.answer.'+session.csrf,JSON.stringify({requestId:answer.request_id,question:answer.question||''}));}catch(_){}}
function armResume(){resumeOnRuntime=true;resumeInputValue=$('question').value;}
function renderQueryError(err){
  $('answer').replaceChildren();const panel=el('div',undefined,'error-panel');
  panel.append(el('h2',err.code==='source_refreshing'?'Sources are changing':err.code==='model_output_unavailable'?'Answer did not pass validation':'Question could not be completed'),el('p',err.message));
  if(err.requestId)panel.append(el('p','Request '+err.requestId,'muted'));
  if(!err.sessionExpired&&!['trial_admission_paused','model_request_unavailable','model_budget_unavailable','model_price_review_required','model_input_rejected'].includes(err.code)){const retry=el('button','Try this question again','primary');retry.onclick=()=>{if(!pendingQuery)$('queryForm').onsubmit({preventDefault(){}});};panel.append(retry,el('p','A new attempt may incur a model charge.','muted'));}
  $('answer').append(panel);$('status').textContent=err.message;
}
async function reconnectRun(run){
  if(!run||$('workspace').hidden)return;
  const saved=savedQuestion();
  if(!pendingQuery&&resumeOnRuntime&&run.status!=='running'&&$('question').value!==resumeInputValue){resumeOnRuntime=false;return;}
  if(!pendingQuery&&resumeOnRuntime&&(run.status==='running'||saved&&saved.requestId===run.request_id||typeof run.question==='string'&&(!saved||saved.requestId===null&&saved.question===run.question))){
    resumeOnRuntime=false;$('question').value=typeof run.question==='string'?run.question:(saved?.question||'');
    startWaiting(viewToken(),run.elapsed_seconds||0,true);pendingQuery.requestId=run.request_id;
    if(saved)saveQuestion(run.request_id);$('ask').disabled=true;renderStages(run);
    $('status').textContent='Reconnected to the original request. No new model call was made.';
  }
  const pending=pendingQuery;
  if(pending&&pending.requestId===run.request_id&&currentView(pending.view)&&typeof run.question==='string'){pending.question=run.question;$('runningQuestion').textContent=run.question;$('question').value=run.question;}
  if(!pending?.resumed||pending.requestId!==run.request_id||!currentView(pending.view)||run.status==='running'||pending.fetching)return;
  pending.fetching=true;$('progressPhase').textContent='Checking saved answer access';
  try{
    if(run.status==='failed'){
      const messages={model_output_unavailable:'The original model output did not pass validation. No draft is shown. An explicit new attempt can incur a charge.',model_request_unavailable:'Model delivery or usage is unconfirmed. The reservation is retained; contact the operator before another attempt.',source_refreshing:'Sources were changing. Wait briefly before explicitly trying again.',source_unconfirmed:'Current access or source integrity could not be confirmed. Try later or contact the operator.',trial_admission_paused:'The trial allowance is paused. Contact the operator.',model_budget_unavailable:'The model budget is unavailable. Contact the operator.',model_price_review_required:'The model needs a price review. Contact the operator.',model_input_rejected:'This question cannot be sent within the approved model boundary. Contact the operator.'};const error=Error(messages[run.error_code]||'The original request stopped. No draft is shown. Contact the operator.');error.code=run.error_code;error.requestId=run.request_id;throw error;
    }
    const result=await api('/api/history?request_id='+encodeURIComponent(run.request_id));
    if(pendingQuery!==pending||!currentView(pending.view))return;
    const answer=result.history.find(a=>a.request_id===run.request_id);
    if(!answer)throw Error('The saved answer is unavailable. No new model call was made.');
    renderAnswer(answer);rememberAnswer(answer);if(answer.question)$('question').value=answer.question;
    $('status').textContent=answer.unavailable?answer.message:answerStatus(answer);
  }catch(err){if(pendingQuery===pending&&currentView(pending.view))renderQueryError(err);}
  finally{if(pendingQuery===pending&&currentView(pending.view)){try{sessionStorage.removeItem('brain.pending.'+session.csrf);}catch(_){}stopWaiting();$('ask').disabled=false;}}
}
const phaseLabels={queued:'Waiting to start',retrieval:'Retrieving evidence',authorization:'Checking current access',refreshing:'Reading changed sources once',generation:'Generating an answer',review:'Reviewing the evidence',final_checks:'Checking current evidence before delivery'};
function renderStages(run){
  $('progressPhase').textContent='Current stage: '+(phaseLabels[run.phase]||'Working');
  const stages=$('progressSteps');stages.replaceChildren();
  const observed=new Set(run.phases||[run.phase]);
  for(const phase of ['retrieval','authorization','generation','review','final_checks']){
    const item=el('li',phaseLabels[phase],phase===run.phase?'stage current':observed.has(phase)?'stage observed':'stage');
    if(phase===run.phase)item.setAttribute('aria-current','step');
    item.append(el('span',phase===run.phase?'Current':observed.has(phase)?'Observed':'Not yet reported'));stages.append(item);
  }
}
async function refreshRuntime(){
  if(!session)return;const owner=session,queryAtPoll=pendingQuery,sequence=++runtimeSequence;
  try{const r=await api('/api/runtime');if(session!==owner||sequence<runtimeApplied)return;runtimeApplied=sequence;
    $('runtime').hidden=false;
    const sourceMode=r.mode.includes('fixture')?'Synthetic fixture sources':r.mode.includes('mock_http')?'Mock source APIs':r.mode.includes('live_api')?'Native source APIs':'Source mode unconfirmed';
    const modelName=r.model.startsWith('deepseek-flash')?'DeepSeek Flash':r.model==='fake-extractive-v1'?'Fake extractive model':r.model;
    const answerMode=r.model.includes('grounded-synthesis')?'Reviewed synthesis':r.model==='fake-extractive-v1'?'Synthetic excerpts':'Source excerpts';
    $('runtimeModel').textContent=modelName+' · '+sourceMode+' · '+answerMode;
    $('runtimeDetails').textContent=r.model+' · '+r.mode;
    const list=$('runtimeSources');list.replaceChildren();
    for(const source of r.sources){const card=el('div',undefined,'runtime-source');
      card.append(el('strong',source.source),el('span',source.configured?'Configured · '+source.mode:'Not configured'),
        el('span',source.checking?'Checking now':source.last_check_at?'Last check: '+source.last_check_result+' · '+new Date(source.last_check_at).toLocaleTimeString():'Current source check unconfirmed'),
        el('span',source.snapshot_status==='current'?'Local candidate snapshot current · access checked per question':'Current candidate snapshot unconfirmed'),
        el('span',source.used_in_answer?'Cited in the last completed answer':'Not recorded as used in the last completed answer','muted'));list.append(card);}
    if(!r.run&&resumeOnRuntime&&$('workspace').hidden===false){
      resumeOnRuntime=false;const reference=answerReference(),view=viewToken();
      if(reference&&$('question').value===resumeInputValue){
        $('answer').replaceChildren(el('p','Checking current access before restoring the saved answer…'));
        try{const saved=await api('/api/history?request_id='+encodeURIComponent(reference.requestId));if(!currentView(view)||$('question').value!==resumeInputValue)return;const answer=saved.history.find(a=>a.request_id===reference.requestId);if(!answer)throw Error('The saved answer is unavailable.');renderAnswer(answer);if(answer.question)$('question').value=answer.question;}
        catch(err){if(currentView(view)&&$('question').value===resumeInputValue)renderQueryError(err);}
      }
    }
    await reconnectRun(r.run);
    if(pendingQuery&&pendingQuery===queryAtPoll&&currentView(pendingQuery.view)&&r.run?.status==='running'&&(!pendingQuery.requestId||pendingQuery.requestId===r.run.request_id)){
      pendingQuery.requestId=r.run.request_id;saveQuestion(r.run.request_id);renderStages(r.run);}
  }catch(_){if(session===owner&&sequence>=runtimeApplied){runtimeApplied=sequence;$('runtimeModel').textContent='Runtime status unavailable';}}
}
function startWaiting(view,elapsed=0,resumed=false){
  const started=clockNow()-elapsed*1000;pendingQuery={view,started,requestId:null,resumed,question:$('question').value};$('progress').hidden=false;$('progressPhase').textContent='Submitting question';$('progressSteps').replaceChildren();
  $('question').readOnly=true;$('runningQuestion').textContent=pendingQuery.question;
  $('queryForm').setAttribute('aria-busy','true');
  const tick=()=>{if(pendingQuery&&currentView(view))$('elapsed').textContent=((clockNow()-started)/1000).toFixed(1)+' s elapsed';};tick();
  if(typeof setInterval!=='undefined')waitTimer=setInterval(tick,100);
}
const bootstrapTicket=new URLSearchParams(location.hash.slice(1)).get('ticket');
if(location.hash)history.replaceState(null,'',location.pathname+location.search);
$('loginForm').querySelector('button').disabled=true;
const versionLabel=e=>e.locator?.content_sha256?'Content snapshot '+e.locator.content_sha256.slice(0,12):'Version '+e.version;
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
function expiredSession(){forgetQuestion();$('question').value='';stopWaiting();stopRuntime();session=null;$('answer').replaceChildren();$('other').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();$('identity').textContent='Not signed in';$('auditNav').hidden=true;$('sourcesNav').hidden=true;show('login');const error=Error(health?.auth_kind==='operator'?'This session ended. Open the latest one-time link from the running operator terminal.':'This session ended. Sign in again.');error.sessionExpired=true;$('status').textContent=error.message;return error;}
async function api(path,data){const requestSession=session;const options={credentials:'same-origin',headers:{}};if(data!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.headers['X-CSRF-Token']=session?.csrf||'';options.body=JSON.stringify(data);}const response=await fetch(path,options);const result=await response.json();if(!response.ok){if(requestSession!==session)throw Error('Stale response discarded');if(response.status===403&&session&&path!=='/api/session'){const current=await fetch('/api/session',{credentials:'same-origin'});if(current.status===403)throw expiredSession();}const error=Error(result.error||'Request unavailable. Ask again or contact the operator if it persists.');error.status=response.status;error.code=result.code;error.requestId=result.request_id;throw error;}return result;}
function show(name){resumeOnRuntime=false;stopWaiting();viewRevision++;$('ask').disabled=false;$('previewBody').replaceChildren();if($('preview').open)$('preview').close();for(const id of ['login','workspace','other'])$(id).hidden=id!==name;$('status').textContent='';}
function identity(){const box=$('identity');box.replaceChildren(el('span',session.actor));const logout=el('button',health?.auth_kind==='operator'?'Sign out':'Switch demo identity');logout.onclick=async()=>{forgetQuestion();$('question').value='';stopWaiting();stopRuntime();viewRevision++;$('answer').replaceChildren();$('other').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();await api('/api/logout',{});session=null;$('answer').replaceChildren();$('other').replaceChildren();$('auditNav').hidden=true;$('sourcesNav').hidden=true;box.textContent='Not signed in';show('login');};box.append(logout);$('auditNav').hidden=session.actor!=='auditor';$('sourcesNav').hidden=session.actor!=='auditor';show('workspace');const saved=savedQuestion();$('question').value=saved?.question||'';armResume();refreshRuntime();if(runtimeTimer===null&&typeof setInterval!=='undefined')runtimeTimer=setInterval(refreshRuntime,1500);}
function diagnostics(label,...content){const box=el('details',undefined,'diagnostics');box.append(el('summary',label),...content);return box;}
function originalLink(e){
  // Only a fresh, authorized preview supplies this URL; never claims/model text.
  try{
    const url=new URL(e.source_url);
    const host=url.hostname.toLowerCase();
    const atlassian=(host.endsWith('.atlassian.net')&&host!=='.atlassian.net');
    const allowed=((e.source==='confluence'||e.source==='jira')&&atlassian)
      ||(e.source==='slack'&&(host==='app.slack.com'||host.endsWith('.slack.com')))
      ||(e.source==='drive'&&(host==='drive.google.com'||host==='docs.google.com'));
    if(url.protocol!=='https:'||url.username||url.password||url.port||!allowed)return null;
    const link=el('a','Open original in '+e.source);link.href=url.href;
    link.target='_blank';link.rel='noopener noreferrer';return link;
  }catch(_){return null;}
}
async function preview(id){
  stopWaiting();viewRevision++;const view=viewToken();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();
  $('status').textContent='Checking current access and loading the exact source passage…';
  try{
    const e=await api('/api/evidence/'+encodeURIComponent(id));if(!currentView(view))return;
    const body=$('previewBody');body.replaceChildren(el('h2',e.title),el('p',e.text),el('p',versionLabel(e),'muted'));
    const link=originalLink(e);body.append(link||el('p','Original platform link unavailable for this source.','muted'));
    body.append(diagnostics('Source diagnostics',el('p',e.evidence_id,'muted'),el('pre',JSON.stringify(e.locator,null,2))));
    $('preview').showModal();$('status').textContent='Current access checked. Exact source passage ready.';
  }catch(e){
    if(!currentView(view))return;$('answer').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();
    if(e.sessionExpired){$('status').textContent=e.message;return;}
    $('other').replaceChildren(el('p','Evidence is unavailable or has changed. Ask again for current sources.','notice'));
    $('status').textContent='Evidence is unavailable or has changed. Ask again for current sources.';
  }
}

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
function renderAnswer(answer,target=$('answer')){
  target.replaceChildren();if(answer.unavailable){target.append(el('p',answer.message,'notice'));return;}
  const grid=el('div',undefined,'receipt'),main=el('div',undefined,'panel'),side=el('aside',undefined,'panel');
  const head=el('div',undefined,'receipt-head');head.append(el('h2',answer.claim_format==='grounded_synthesis_v1'?'Evidence-backed answer':'Evidence-backed excerpts'),el('span',modelLabel(answer),'tag'));main.append(head);
  main.append(el('h3',answer.question||'Question not recorded for this older answer.'));
  const date=typeof answer.answered_at==='string'?new Date(answer.answered_at):null;
  main.append(el('p',date&&!Number.isNaN(date.getTime())?'Answered '+date.toLocaleString():'Generation time not recorded for this older answer.','muted'));
  const byId=new Map(answer.evidence.map(e=>[e.evidence_id,e]));
  for(const c of answer.claims){
    const block=el('div',undefined,'claim');block.append(el('p',c.text));
    if(c.supports?.length){const quotes=el('details');quotes.append(el('summary','Exact supporting quotes'));for(const support of c.supports)quotes.append(el('p',support.quote),el('p',byId.get(support.evidence_id)?.title||'Source reference','muted'));block.append(quotes);}
    for(const id of c.evidence_ids){const b=el('button',byId.get(id)?.title||'View source passage','citation');b.onclick=()=>preview(id);block.append(b);}main.append(block);
  }
  for(const u of answer.uncertainties)main.append(el('p',u,'notice'));
  const debug=diagnostics('Answer diagnostics',el('p','Receipt '+answer.request_id,'muted'));renderModelUsage(answer,debug);main.append(debug);
  side.append(el('h3','Key references'));
  const citedIds=new Set(answer.claims.flatMap(c=>c.evidence_ids));
  const otherEvidence=diagnostics('Other checked evidence');let hasOtherEvidence=false;
  for(const e of answer.evidence){
    const card=el('div',undefined,'source-card');card.append(el('span',e.source,'source-name'));
    const b=el('button',e.title);b.onclick=()=>preview(e.evidence_id);
    card.append(b,el('p',versionLabel(e)),el('p','Source updated '+new Date(e.source_updated_at).toLocaleString()),
      diagnostics('Source diagnostics',el('p',e.evidence_id,'muted'),el('pre',JSON.stringify(e.locator,null,2)),el('p','Indexed '+new Date(e.indexed_at).toLocaleString())));
    if(citedIds.has(e.evidence_id))side.append(card);else{otherEvidence.append(card);hasOtherEvidence=true;}
  }
  if(hasOtherEvidence)side.append(otherEvidence);
  if(!answer.evidence.length)side.append(el('p','No supporting evidence is available for this answer.'));
  grid.append(main,side);target.append(grid);
}

$('loginForm').onsubmit=async e=>{e.preventDefault();try{if(health?.auth_kind!=='demo')throw Error('Open the one-time link from the operator terminal.');session=await api(health.login_path,{user:$('user').value});identity();}catch(err){$('status').textContent=err.message;}};
$('queryForm').onsubmit=async e=>{
  e.preventDefault();if(pendingQuery)return;
  const priorSaved=savedQuestion(),submittedQuestion=$('question').value;
  viewRevision++;const view=viewToken();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();
  $('answer').replaceChildren();$('other').replaceChildren();$('ask').disabled=true;saveQuestion(null,submittedQuestion);startWaiting(view);$('status').textContent='Working on your question…';
  try{const a=await api('/api/query',{question:submittedQuestion});if(!currentView(view))return;resumeOnRuntime=false;forgetQuestion();rememberAnswer(a);renderAnswer(a);$('status').textContent=answerStatus(a);}
  catch(err){if(currentView(view)){
    if(err.status===409){if(priorSaved){saveQuestion(priorSaved.requestId,priorSaved.question);$('question').value=priorSaved.question;}else forgetQuestion();armResume();$('status').textContent='Reconnecting to the original request…';}
    else{resumeOnRuntime=false;forgetQuestion();renderQueryError(err);}
  }}
  finally{if(currentView(view)){stopWaiting();$('ask').disabled=false;refreshRuntime();}}

};
for(const b of document.querySelectorAll('[data-question]'))b.onclick=()=>{if(pendingQuery)return;$('question').value=b.dataset.question;$('question').focus();};
$('workspaceNav').onclick=()=>{$('answer').replaceChildren();$('other').replaceChildren();show(session?'workspace':'login');if(session)armResume();};
$('historyNav').onclick=async()=>{
  if(!session)return;$('answer').replaceChildren();show('other');const view=viewToken();
  const heading=el('h1','Recent answers'),message=el('p','Loading your saved questions…','lede');$('other').replaceChildren(heading,message);
  try{
    const result=await api('/api/history/recent');if(!currentView(view))return;
    message.textContent=result.history.length?'Select an answer. Current source access and versions are checked before its contents are shown.':'No answers yet.';
    for(const summary of result.history){
      const item=el('div',undefined,'history-item'),open=el('button',summary.question||'Saved question','history-open'),body=el('div');
      const date=new Date(summary.answered_at);item.append(open,el('p',Number.isNaN(date.getTime())?'Saved answer':date.toLocaleString(),'muted'),body);$('other').append(item);
      open.onclick=async()=>{
        if(open.disabled||!currentView(view))return;open.disabled=true;body.replaceChildren(el('p','Checking current access and versions for this answer…'));
        try{const saved=await api('/api/history?request_id='+encodeURIComponent(summary.request_id));if(!currentView(view))return;
          const answer=saved.history.find(a=>a.request_id===summary.request_id);if(!answer)throw Error('This saved answer is unavailable.');renderAnswer(answer,body);rememberAnswer(answer);
        }catch(err){if(currentView(view))body.replaceChildren(el('p',err.message,'notice'));}
        finally{if(currentView(view))open.disabled=false;}
      };
    }
  }catch(err){if(currentView(view)){message.textContent=err.message;message.className='notice';}}
};
$('sourcesNav').onclick=async()=>{show('other');const view=viewToken();$('other').replaceChildren(el('h1','Source coverage'),el('p','Current source status for this running instance. Fixture and native checks are reported separately.','lede'));try{const r=await api('/api/sources/status');if(!currentView(view))return;for(const s of r.sources){const card=el('div',undefined,'panel');card.append(el('h2',s.source),el('p','Status: '+s.status),el('p','Live: '+s.live),el('p',s.authority));$('other').append(card);}}catch(e){if(!currentView(view))return;$('status').textContent=e.message;}};
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
  if(row.event_type==='evidence_used')item.append(el('p',((p.stage==='sent_to_review'||p.stage==='prepared_for_review')?'Prepared for evidence review (not proof of sending)':(p.stage==='sent_to_model'||p.stage==='prepared_for_answer')?'Prepared for answer model (not proof of sending)':p.stage)+' · '+p.evidence_id));
  const modelStages={model_dispatch_intent:'Model send intent persisted (delivery unknown)',model_dispatch_attempted:'Model send attempted (delivery unknown)',model_usage_received:'Validated model usage received (answer may still be rejected)',model_output_accepted:'Model output accepted',model_output_rejected:'Model output rejected'};
  if(modelStages[row.event_type])item.append(el('p',modelStages[row.event_type]+' · '+p.stage));
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
