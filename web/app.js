'use strict';
const $=id=>document.getElementById(id);
const insufficientPartText='The provided evidence is insufficient to answer this part. This does not establish that the event or information does not exist.';
let session=null,health=null,viewRevision=0;
let modelPaused=false;
let sourcesPaused=false;
const viewToken=()=>({revision:viewRevision,session});
const currentView=token=>token.revision===viewRevision&&token.session===session;
let pendingQuery=null,waitTimer=null,runtimeTimer=null,runtimeSequence=0,runtimeApplied=0,resumeOnRuntime=false,resumeInputValue='',admissionPaused=false,admissionInfo=null;
const clockNow=()=>typeof performance!=='undefined'?performance.now():Date.now();
function stopRuntime(){runtimeApplied=++runtimeSequence;if(runtimeTimer!==null&&typeof clearInterval!=='undefined')clearInterval(runtimeTimer);runtimeTimer=null;$('runtime').hidden=true;$('runtimeModel').textContent='';$('runtimeDetails').textContent='';$('runtimeSources').replaceChildren();}
function stopWaiting(){if(waitTimer!==null&&typeof clearInterval!=='undefined')clearInterval(waitTimer);waitTimer=null;pendingQuery=null;$('question').readOnly=false;$('runningQuestion').textContent='';$('queryForm').setAttribute('aria-busy','false');$('progress').hidden=true;}
function savedQuestion(){try{return JSON.parse(sessionStorage.getItem('brain.pending.'+session.csrf)||'null');}catch(_){return null;}}
function saveQuestion(requestId=null,question=null){try{question=question??pendingQuery?.question??savedQuestion()?.question;if(question!==null&&question!==undefined)sessionStorage.setItem('brain.pending.'+session.csrf,JSON.stringify({question,requestId}));}catch(_){}}
function forgetQuestion(){try{if(session){sessionStorage.removeItem('brain.pending.'+session.csrf);sessionStorage.removeItem('brain.answer.'+session.csrf);}}catch(_){}}
function answerReference(){try{return JSON.parse(sessionStorage.getItem('brain.answer.'+session.csrf)||'null');}catch(_){return null;}}
function rememberAnswer(answer){if(answer.unavailable)return;try{sessionStorage.setItem('brain.answer.'+session.csrf,JSON.stringify({requestId:answer.request_id,question:answer.question||''}));}catch(_){}}
function armResume(){resumeOnRuntime=true;resumeInputValue=$('question').value;}
function updateAsk(){ $('ask').disabled=Boolean(pendingQuery)||admissionPaused||modelPaused||sourcesPaused||session?.demo_role==='auditor'; }
function renderAdmission(admission){
  if(admission!==undefined){admissionInfo=admission;admissionPaused=Boolean(admission&&!admission.allowed);}const notice=$('trialStatus');notice.hidden=!admission&&!admissionPaused;
  if(admission?.human_unlimited){notice.textContent=(admissionPaused?'Human queries paused. ':'Human queries have no count limit. ')+admission.attempts_used+' submissions recorded. '+(typeof admission.settlement_remaining_usd==='number'?'Trial budget: $'+admission.settlement_remaining_usd.toFixed(4)+' remaining of $'+admission.settlement_limit_usd.toFixed(2)+' (before pending reservations). ':'')+(admissionPaused?'No new model call will be made. Saved answers remain available.':'Cost and unconfirmed-usage protections remain active.');}
  else if(admission)notice.textContent=(admissionPaused?'Trial queries paused. ':'Trial query attempts: ')+admission.attempts_used+'/'+admission.attempts_limit+' used. '+(admissionPaused?'No new model call will be made. Saved answers remain available.':admission.attempts_remaining+' remaining.');
  updateAsk();
}
function renderQueryError(err){
  if(err.code==='trial_admission_paused'){admissionPaused=true;$('trialStatus').hidden=false;$('trialStatus').textContent='Trial queries paused at an approved cost, unconfirmed-usage or trial limit. No new model call was made. Saved answers remain available.';if(admissionInfo)renderAdmission({...admissionInfo,allowed:false});}
  $('answer').replaceChildren();const panel=el('div',undefined,'error-panel');
  panel.append(el('h2',err.code==='source_refreshing'?'Sources are changing':err.code==='model_output_unavailable'?'Answer did not pass validation':'Question could not be completed'),el('p',err.message));
  panel.append(el('h3',err.run?.question||$('question').value));
  if(err.run){panel.append(el('p',(err.run.phase==='queued'?'Stopped before retrieval':'Stopped during '+(phaseLabels[err.run.phase]||'the request'))+' · '+Number(err.run.elapsed_seconds||0).toFixed(1)+' s elapsed','muted'));}
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
    if(run.status==='running'){
      startWaiting(viewToken(),run.elapsed_seconds||0,true);pendingQuery.requestId=run.request_id;
      if(saved)saveQuestion(run.request_id);renderStages(run);
      $('status').textContent='Reconnected to the original request. No new model call was made.';
    }else{
      // Restoring a terminal answer performs access checks, never a running timer.
      pendingQuery={view:viewToken(),requestId:run.request_id,resumed:true,question:$('question').value};
      $('progress').hidden=true;$('question').readOnly=true;$('queryForm').setAttribute('aria-busy','true');
      $('status').textContent='Checking current access before restoring the saved result…';
    }
    $('ask').disabled=true;
  }
  const pending=pendingQuery;
  if(pending&&pending.requestId===run.request_id&&currentView(pending.view)&&typeof run.question==='string'){pending.question=run.question;$('runningQuestion').textContent=run.question;$('question').value=run.question;}
  if(!pending?.resumed||pending.requestId!==run.request_id||!currentView(pending.view)||run.status==='running'||pending.fetching)return;
  pending.fetching=true;$('progressPhase').textContent='Checking saved answer access';
  try{
    if(run.status==='failed'){
      const messages={model_output_unavailable:'The original model output did not pass validation. No draft is shown. An explicit new attempt can incur a charge.',model_request_unavailable:'Model delivery or usage is unconfirmed. The reservation is retained; contact the operator before another attempt.',source_refreshing:'Sources were changing. Wait briefly before explicitly trying again.',source_unconfirmed:'Current access or source integrity could not be confirmed. Try later or contact the operator.',trial_admission_paused:'The trial allowance is paused. Contact the operator.',model_budget_unavailable:'The model budget is unavailable. Contact the operator.',model_price_review_required:'The model needs a price review. Contact the operator.',model_input_rejected:'This question cannot be sent within the approved model boundary. Contact the operator.'};const error=Error(messages[run.error_code]||'The original request stopped. No draft is shown. Contact the operator.');error.code=run.error_code;error.requestId=run.request_id;error.run=run;throw error;
    }
    const result=await api('/api/history?request_id='+encodeURIComponent(run.request_id));
    if(pendingQuery!==pending||!currentView(pending.view))return;
    const answer=result.history.find(a=>a.request_id===run.request_id);
    if(!answer)throw Error('The saved answer is unavailable. No new model call was made.');
    renderAnswer(answer);rememberAnswer(answer);if(answer.question)$('question').value=answer.question;
    $('status').textContent=answer.unavailable?answer.message:answerStatus(answer);
  }catch(err){if(pendingQuery===pending&&currentView(pending.view))renderQueryError(err);}
  finally{if(pendingQuery===pending&&currentView(pending.view)){try{sessionStorage.removeItem('brain.pending.'+session.csrf);}catch(_){}stopWaiting();updateAsk();}}
}
const phaseLabels={queued:'Waiting to start',retrieval:'Retrieving evidence',authorization:'Checking current access',refreshing:'Reading changed sources once',generation:'Generating an answer',review:'Reviewing the evidence',final_checks:'Checking current evidence before delivery'};
function renderStages(run){
  const labelsForRun={...phaseLabels,generation:health?.mode?.endsWith('_live_model_source_review')?'Preparing source passages':phaseLabels.generation};
  $('progressPhase').textContent=(run.status==='completed'?'Completed: ':run.status==='failed'?'Stopped: ':run.status==='evidence_only'?'Synthesis blocked; source checks finished: ':'Current stage: ')+(labelsForRun[run.phase]||'Working');
  const stages=$('progressSteps');stages.replaceChildren();
  const observed=new Set(run.phases||[run.phase]);
  for(const phase of ['retrieval','authorization','generation','review','final_checks']){
    const state=run.stage_states?.[phase]||(phase===run.phase&&(!run.status||run.status==='running')?'running':observed.has(phase)?'observed':'pending');
    const labels={completed:'✓ Completed',running:'In progress',failed:'! Failed',pending:'Not yet reported',not_run:'Not run',observed:'Observed · result not reported'};
    const item=el('li',labelsForRun[phase],'stage '+state);
    if(state==='running')item.setAttribute('aria-current','step');
    item.append(el('span',labels[state]||'Result not reported'));stages.append(item);
  }
}
function sourceTime(value){
  if(typeof value!=='string'||!value.trim())return 'Not recorded';
  const date=new Date(value);return Number.isNaN(date.getTime())?'Not recorded':date.toLocaleString();
}
function sourceCheckText(source){
  if(source.mode==='fixture')return 'Synthetic data · native update timing not measured';
  if(source.checking)return 'Checking source now';
  const result={complete:'Latest check completed',failed:'Latest check failed',backlog:'Latest sync incomplete'}[source.last_check_result];
  if(source.last_check_result==='complete')return result+' · '+sourceTime(source.last_successful_check_at);
  return result?result+' · Started '+sourceTime(source.last_check_at):'Source check not confirmed';
}
function sourceSnapshotText(source){
  if(source.mode==='fixture')return 'This demo does not check live platform changes';
  if(source.snapshot_status==='current')return 'Recent source snapshot · access rechecked for every question';
  if(source.last_check_result==='failed')return 'Latest content cannot be confirmed until the source recovers';
  if(source.last_check_result==='backlog')return 'Sync incomplete · latest content cannot be confirmed';
  return 'Snapshot needs a new check · latest content cannot be confirmed';
}
async function refreshRuntime(){
  if(!session)return;const owner=session,queryAtPoll=pendingQuery,sequence=++runtimeSequence;
  try{const r=await api('/api/runtime');if(session!==owner||sequence<runtimeApplied)return;runtimeApplied=sequence;
    $('runtime').hidden=false;renderAdmission(r.query_admission);
    const sourceMode=r.mode.includes('fixture')?'Synthetic fixture sources':r.mode.includes('mock_http')?'Mock source APIs':r.mode.includes('live_api')?'Native source APIs':'Source mode unconfirmed';
    const modelName=r.mode.includes('mock_model')?'Mock model outputs':r.model.startsWith('deepseek-flash')?'DeepSeek Flash':r.model==='fake-extractive-v1'?'Fake extractive model':r.model;
    const answerMode=r.model.includes('reviewed-excerpts')?'Reviewed verbatim sources':r.model.includes('grounded-synthesis')?'Reviewed synthesis':r.model==='fake-extractive-v1'?'Synthetic excerpts':'Source excerpts';
    $('runtimeModel').textContent=modelName+' · '+sourceMode+' · '+answerMode;
    modelPaused=r.model_readiness?.ready===false;
    sourcesPaused=r.query_readiness?.code==='source_unconfirmed';
    $('runtimeDetails').textContent=r.model+' · '+r.mode+(modelPaused?' · Model paused: operator price review required. Saved answers remain available.':sourcesPaused?' · Waiting for current source checks. This page checks readiness automatically; no question is resubmitted.':'');
    updateAsk();
    const list=$('runtimeSources');list.replaceChildren();
    for(const source of r.sources){const card=el('div',undefined,'runtime-source');
      card.append(el('strong',source.source),el('span',source.configured?'Configured · '+source.mode:'Not configured'),
        el('span',sourceCheckText(source)),el('span',sourceSnapshotText(source)));
      if(source.mode!=='fixture'&&source.last_check_result!=='complete'&&source.last_successful_check_at)card.append(el('span','Last complete sync: '+sourceTime(source.last_successful_check_at)));
      if(source.mode!=='fixture'&&Number.isFinite(source.next_check_in_seconds))card.append(el('span','Next check due in '+Math.ceil(source.next_check_in_seconds)+' s','muted'));
      card.append(el('span',source.used_in_answer?'Cited in the last completed answer':'Not recorded as used in the last completed answer','muted'));list.append(card);}
    if((!r.run||['completed','evidence_only'].includes(r.run.status)&&!savedQuestion()&&answerReference())&&resumeOnRuntime&&$('workspace').hidden===false){
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
function expiredSession(){forgetQuestion();$('question').value='';stopWaiting();stopRuntime();session=null;admissionPaused=false;admissionInfo=null;$('trialStatus').hidden=true;admissionPaused=false;$('trialStatus').hidden=true;$('answer').replaceChildren();$('other').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();$('identity').textContent='Not signed in';$('auditNav').hidden=true;$('sourcesNav').hidden=true;show('login');const error=Error(health?.auth_kind==='reviewer'?'This session ended. Sign in with your demo account.':health?.auth_kind==='operator'?'This session ended. Open the latest one-time link from the running operator terminal.':'This session ended. Sign in again.');error.sessionExpired=true;$('status').textContent=error.message;return error;}
async function api(path,data){const requestSession=session;const options={credentials:'same-origin',headers:{}};if(data!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.headers['X-CSRF-Token']=session?.csrf||'';options.body=JSON.stringify(data);}const response=await fetch(path,options);const result=await response.json();if(!response.ok){if(requestSession!==session)throw Error('Stale response discarded');if(response.status===403&&session&&path!=='/api/session'){const current=await fetch('/api/session',{credentials:'same-origin'});if(current.status===403)throw expiredSession();}const error=Error(result.error||'Request unavailable. Ask again or contact the operator if it persists.');error.status=response.status;error.code=result.code;error.requestId=result.request_id;error.run=result.run;throw error;}return result;}
function show(name){resumeOnRuntime=false;stopWaiting();viewRevision++;updateAsk();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();for(const id of ['login','workspace','other'])$(id).hidden=id!==name;$('status').textContent='';}
function identity(){const box=$('identity');box.replaceChildren(el('span',health?.auth_kind==='reviewer'?(session.display_name||session.actor.split(':')[1])+' · '+({engineer:'Engineer',eng_b:'Engineer',product:'Product & Operations',product_ops:'Product & Operations',partner:'External Partner',contractor:'External Partner',auditor:'Scoped Auditor'}[session.demo_role]||'Demo account'):session.actor));const logout=el('button',['operator','reviewer'].includes(health?.auth_kind)?'Sign out':'Switch demo identity');logout.onclick=async()=>{forgetQuestion();$('question').value='';stopWaiting();stopRuntime();viewRevision++;$('answer').replaceChildren();$('other').replaceChildren();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();await api('/api/logout',{});session=null;admissionPaused=false;admissionInfo=null;$('trialStatus').hidden=true;$('answer').replaceChildren();$('other').replaceChildren();$('auditNav').hidden=true;$('sourcesNav').hidden=true;box.textContent='Not signed in';show('login');};box.append(logout);$('auditNav').hidden=!(session.can_audit||session.actor==='auditor');$('sourcesNav').hidden=session.actor!=='auditor';show('workspace');const saved=savedQuestion();$('question').value=saved?.question||'';armResume();refreshRuntime();if(runtimeTimer===null&&typeof setInterval!=='undefined')runtimeTimer=setInterval(refreshRuntime,1500);if(session.demo_role==='auditor')$('auditNav').onclick();}
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
    body.append(el('p','Source last edited: '+sourceTime(e.source_updated_at),'muted'),
      el('p','Indexed locally: '+sourceTime(e.indexed_at),'muted'),
      el('p','Access and version checked: '+sourceTime(e.checked_at),'muted'));
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
  if(answer.answer_status==='evidence_only')return answer.answer_kind==='reviewed_excerpts'?'ANSWER BLOCKED · SOURCE EVIDENCE':'SYNTHESIS BLOCKED · SOURCE EVIDENCE';
  if(answer.mode?.includes('mock_model'))return 'MOCK MODEL OUTPUTS';
  if(answer.model==='fake-extractive-v1')return 'FAKE MODEL';
  if(answer.model_call?.called===false)return 'NO MODEL CALL';
  if((answer.model_call?.called===true||answer.model_review?.called===true)&&answer.answer_kind==='reviewed_excerpts'&&answer.review_status==='accepted')return 'LIVE MODEL · REVIEWED SOURCES';
  if(answer.model_call?.called===true)return answer.claim_format==='grounded_synthesis_v1'?'LIVE MODEL · REVIEWED SYNTHESIS':'LIVE MODEL · SOURCE EXCERPTS';
  return 'MODEL CALL NOT RECORDED';
}
function renderModelUsage(answer,target){
  if(answer.answer_status==='evidence_only'){target.append(el('p','No validated answer is available. This does not establish that the requested information does not exist. Original usage and failure remain in the audit; no automatic model retry was made.','notice'));return;}
  const receipt=answer.model_call||answer.model_review;
  if(answer.model==='fake-extractive-v1')return;
  if(receipt?.called===false){target.append(el('p','No external model request was sent.','muted'));return;}
  if(receipt?.called!==true){target.append(el('p','Model usage was not recorded for this answer.','muted'));return;}
  const receipts=[receipt];
  if(answer.model_review?.called===true&&answer.model_review!==receipt)receipts.push(answer.model_review);
  for(const [index,item] of receipts.entries()){
    const details=el('details',undefined,'model-usage');
    details.append(el('summary',index||!answer.model_call?'Evidence review usage receipt':'Model usage receipt'),
      el('p',item.prompt_tokens+' input + '+item.completion_tokens+' output = '+item.total_tokens+' tokens'),
      el('p','Conservative cost estimate: US$'+(item.accounted_upper_micro_usd/1000000).toFixed(6)),
      el('p','This is an accounting upper estimate, not the provider invoice.','muted'));
    target.append(details);
  }

}
function answerStatus(answer){
  if(answer.answer_status==='evidence_only')return 'Answer failed validation. Current source evidence is available; no validated answer was produced.';
  if(answer.model_call?.called===false)return 'No supporting evidence found. No external model request was sent.';
  if(!answer.claims.length)return answer.model_call?.called===true?'The model checked authorized sources but found insufficient support.':'Insufficient supporting evidence.';
  if(answer.answer_kind==='reviewed_excerpts'&&answer.review_status==='accepted'&&answer.model_review?.called===true)return 'Answer recorded. Verbatim source passages and answer coverage were reviewed; latest ordering is not inferred.';
  if(answer.model==='fake-extractive-v1')return 'Answer recorded. Authorized synthetic source excerpts; fake model.';
  return answer.model_call?.called===true?(answer.claim_format==='grounded_synthesis_v1'?'Answer recorded. Grounded synthesis and model review completed.':'Answer recorded. Live model selected authorized source excerpts.'):'Answer recorded. Model usage was not recorded.';
}
function answerTopics(question,groups){
  // Navigation hints only; matches never assert facts, approval or semantic completeness.
  const topics=[
    ['Incident cause',/\b(?:cause|caused|root cause|why.*(?:incident|outage))\b|事故原因|根因|故障原因/i,/\b(?:root cause|caused|postmortem|hypothesis|incident report)\b|根因|事故原因|故障原因/i],
    ['Response steps',/\b(?:runbook|mitigations?|remediation|procedures?|workarounds?|steps|actions)\b|处理步骤|缓解措施|操作手册|应急措施/i,/\b(?:runbook|playbook|mitigation|remediation|procedure|workaround|response steps)\b|操作手册|处理步骤|缓解措施|应急措施/i],
    ['Work status',/\b(?:status|tickets?|follow[- ]?ups?|fix(?:es)?|completed?|done|blockers?)\b|任务状态|工单|修复|完成|后续任务/i,/\b(?:status|tickets?|follow[- ]?ups?|fix(?:es)?|done|in progress|blockers?)\b|任务状态|工单|修复|完成|后续任务/i],
    ['Release scope',/\b(?:release|launch|rollout|pilot|availability|offer|customers?)\b|发布|上线|试点|所有客户|客户开放/i,/\b(?:release|launch|rollout|pilot|general availability|GA|eligibility)\b|发布|上线|试点|全面开放/i]
  ];
  return topics.filter(([,requested])=>requested.test(question||'')).map(([label,,matches])=>({label,
    groups:groups.filter(group=>matches.test(group.searchText))}));
}
function renderAnswer(answer,target=$('answer')){
  target.replaceChildren();if(answer.unavailable){target.append(el('p',answer.message,'notice'));return;}
  if(answer.answer_status==='evidence_only'){const failure=el('div',undefined,'error-panel');failure.append(el('h2',answer.answer_kind==='reviewed_excerpts'?'Source answer was blocked':'Synthesis was blocked'),el('p','The model output did not pass validation. The original source passages below were checked for current access and version. They are not a validated summary; latest ordering is not inferred.'));target.append(failure);}
  const grid=el('div',undefined,'receipt'),main=el('div',undefined,'panel'),side=el('aside',undefined,'panel');
  const head=el('div',undefined,'receipt-head');head.append(el('h2',answer.answer_kind==='reviewed_excerpts'?(answer.review_status==='accepted'&&answer.model_review?.called===true?'Reviewed source answer':'Source evidence'):answer.claim_format==='grounded_synthesis_v1'?'Evidence-backed answer':'Evidence-backed excerpts'),el('span',modelLabel(answer),'tag'));main.append(head);
  main.append(el('h3',answer.question||'Question not recorded for this older answer.'));
  const date=typeof answer.answered_at==='string'?new Date(answer.answered_at):null;
  main.append(el('p',date&&!Number.isNaN(date.getTime())?'Answered '+date.toLocaleString():'Generation time not recorded for this older answer.','muted'));
  const guide=el('nav',undefined,'answer-guide');guide.setAttribute('aria-label','Find evidence by question');
  if(answer.answer_status!=='evidence_only'&&answer.claim_format!=='grounded_synthesis_v1')main.append(guide);
  const byId=new Map(answer.evidence.map(e=>[e.evidence_id,e]));
  const parts=answer.answer_kind==='sectioned_synthesis'&&answer.claim_format==='grounded_synthesis_v1'
    &&answer.review_status==='accepted'&&answer.answer_status!=='evidence_only'?answer.answer_parts:null;
  if(parts){
    main.append(el('p','Each part is answered separately. Expand its supporting quotes to check the conclusion.','muted'));
    for(const part of parts){
      const block=el('section',undefined,'answer-section');block.append(el('h3',part.question));
      if(part.status==='insufficient')block.append(el('p',insufficientPartText,'notice'));
      for(const index of part.claim_indices){
        const c=answer.claims[index];block.append(el('p',c.text));
        const quotes=el('details');quotes.append(el('summary','Exact supporting quotes'));
        for(const support of c.supports)quotes.append(el('p',support.quote));block.append(quotes);
        for(const id of c.evidence_ids){const link=el('button',byId.get(id)?.title||'Check source passage','citation');link.onclick=()=>preview(id);block.append(link);}
      }
      main.append(block);
    }
  }
  const excerpts=answer.claim_format!=='grounded_synthesis_v1';
  const groups=[];
  let section=null,previousIds=null;
  for(const [index,c] of (parts||answer.answer_status==='evidence_only'?[]:answer.claims).entries()){
    // Keep source order and every qualification; group only adjacent identical citations.
    const ids=JSON.stringify(c.evidence_ids);
    if(!excerpts||ids!==previousIds){
      section=el('section',undefined,'answer-section');
      if(excerpts){
        const sources=c.evidence_ids.map(id=>byId.get(id)).filter(Boolean);
        section.append(el('h3',[...new Set(sources.map(e=>e.title))].join(' · ')||'Source passage'));
        section.append(el('p',[...new Set(sources.map(e=>e.source))].join(' · '),'source-name'));
        groups.push({section,title:sources.map(e=>e.title).join(' · ')||'Source passage',searchText:sources.map(e=>e.title).join('\n')});
        section.setAttribute('tabindex','-1');
      }
      main.append(section);previousIds=ids;
    }
    const block=el('div',undefined,'claim');block.append(el('p',c.text));
    if(c.supports?.length&&answer.answer_kind!=='reviewed_excerpts'){const quotes=el('details');quotes.append(el('summary','Exact supporting quotes'));for(const support of c.supports)quotes.append(el('p',support.quote),el('p',byId.get(support.evidence_id)?.title||'Source reference','muted'));block.append(quotes);}
    section.append(block);
    if(excerpts)groups[groups.length-1].searchText+='\n'+c.text;
    const next=answer.claims[index+1];
    if(!excerpts||!next||JSON.stringify(next.evidence_ids)!==ids){
      for(const id of c.evidence_ids){const label=excerpts&&c.evidence_ids.length===1?'Check source passage':byId.get(id)?.title||'View source passage';const b=el('button',label,'citation');b.onclick=()=>preview(id);section.append(b);}
    }
  }
  const topics=answerTopics(answer.question,groups);
  if(topics.length&&groups.length){
    guide.append(el('h3','Find in this answer'),el('p','Jump to matching source passages. Read the full passage and its limits before drawing a conclusion.','muted'));
    for(const topic of topics){
      if(topic.groups.length){
        const item=el('details',undefined,'answer-topic');
        item.append(el('summary',topic.label+' · '+topic.groups.length+' source section'+(topic.groups.length===1?'':'s')));
        for(const group of topic.groups){
          const link=el('button',group.title,'citation');
          link.onclick=()=>{group.section.scrollIntoView({block:'start'});group.section.focus({preventScroll:true});};
          item.append(link);
        }
        guide.append(item);
      }else guide.append(el('p',topic.label+': no matching passage identified here. This does not establish the answer.','notice'));
    }
  }else guide.hidden=true;
  for(const u of answer.uncertainties)main.append(el('p',u,'notice'));
  const debug=diagnostics('Answer diagnostics',el('p','Receipt '+answer.request_id,'muted'));renderModelUsage(answer,debug);main.append(debug);
  side.append(el('h3','Key references'));
  if(answer.evidence.length)side.append(el('p','Source edit time is when the content changed. Index time is when this local version was stored.','muted'));
  const citedIds=new Set(answer.answer_status==='evidence_only'?[]:answer.claims.flatMap(c=>c.evidence_ids));
  const otherEvidence=diagnostics('Other checked evidence');let hasOtherEvidence=false;
  for(const e of answer.evidence){
    const card=el('div',undefined,'source-card');card.append(el('span',e.source,'source-name'));
    const b=el('button',e.title);b.onclick=()=>preview(e.evidence_id);
    card.append(b,el('p',versionLabel(e)),el('p','Source last edited: '+sourceTime(e.source_updated_at)),
      el('p','Indexed locally: '+sourceTime(e.indexed_at)),
      diagnostics('Source diagnostics',el('p',e.evidence_id,'muted'),el('pre',JSON.stringify(e.locator,null,2))));
    if(citedIds.has(e.evidence_id))side.append(card);else{otherEvidence.append(card);hasOtherEvidence=true;}
  }
  if(hasOtherEvidence)side.append(otherEvidence);
  if(!answer.evidence.length)side.append(el('p','No supporting evidence is available for this answer.'));
  grid.append(main,side);target.append(grid);
}

$('loginForm').onsubmit=async e=>{e.preventDefault();try{let credentials;if(health?.auth_kind==='reviewer')credentials={username:$('reviewerUsername').value,password:$('reviewerPassword').value};else if(health?.auth_kind==='demo')credentials={user:$('user').value};else throw Error('Open the one-time link from the operator terminal.');session=await api(health.login_path,credentials);$('reviewerPassword').value='';identity();}catch(err){$('reviewerPassword').value='';$('status').textContent=health?.auth_kind==='reviewer'?'Sign-in unavailable. Check your credentials or contact the team.':err.message;}};
$('queryForm').onsubmit=async e=>{
  e.preventDefault();if(pendingQuery||admissionPaused)return;
  const priorSaved=savedQuestion(),submittedQuestion=$('question').value;
  viewRevision++;const view=viewToken();$('previewBody').replaceChildren();if($('preview').open)$('preview').close();
  $('answer').replaceChildren();$('other').replaceChildren();$('ask').disabled=true;saveQuestion(null,submittedQuestion);startWaiting(view);$('status').textContent='Working on your question…';
  try{const a=await api('/api/query',{question:submittedQuestion});if(!currentView(view))return;resumeOnRuntime=false;forgetQuestion();rememberAnswer(a);renderAnswer(a);$('status').textContent=answerStatus(a);}
  catch(err){if(currentView(view)){
    if(err.status===409){if(priorSaved){saveQuestion(priorSaved.requestId,priorSaved.question);$('question').value=priorSaved.question;}else forgetQuestion();armResume();$('status').textContent='Reconnecting to the original request…';}
    else{resumeOnRuntime=false;forgetQuestion();renderQueryError(err);}
  }}
  finally{if(currentView(view)){stopWaiting();updateAsk();refreshRuntime();}}

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
function auditTimeline(rows){
  const labels={request_started:'Question received',candidate_evaluated:'Retrieval candidate recorded',
    evidence_used:'Evidence prepared (not proof of sending)',model_dispatch_intent:'Model send intent recorded',
    model_dispatch_attempted:'Model send attempted (delivery unknown)',model_usage_received:'Validated model usage received',
    model_output_accepted:'Model output accepted',model_output_rejected:'Model output rejected',
    generation_completed:'Generation completed',response_committed:'Answer stored',
    response_dispatch_attempted:'Response delivery attempted (reading unknown)',request_failed:'Request stopped',
    version_recovery:'Source version recovery recorded'};
  const groups=[];
  for(const event of [...rows].sort((a,b)=>a.seq-b.seq)){
    const p=event.payload||{};
    const label=event.event_type==='authorization_decided'?'Access check: '+(p.phase||'phase not recorded'):
      labels[event.event_type]||'Recorded event: '+event.event_type;
    const key=JSON.stringify([event.event_type,p.phase||'',p.stage||'']);
    let group=groups.at(-1);
    if(!group||group.key!==key){group={key,label,first:event,last:event,count:0,decisions:[]};groups.push(group);}
    group.last=event;group.count++;
    if(event.event_type==='authorization_decided')group.decisions.push((p.result||'unknown').toUpperCase());
  }
  const view=el('details',undefined,'audit-timeline');view.append(el('summary','Request timeline · '+groups.length+' recorded stages'));
  view.append(el('p','Only loaded events are shown in sequence. Missing stages are not assumed complete. Times describe records, not user reading or verified delivery.','muted'));
  const list=el('ol');
  for(const group of groups){
    const item=el('li');item.append(el('strong',group.label));
    const decisions=[...new Set(group.decisions)].map(result=>result+': '+group.decisions.filter(d=>d===result).length).join(' / ');
    if(decisions)item.append(el('p',decisions));
    item.append(el('p','Events '+group.first.seq+(group.last.seq!==group.first.seq?'–'+group.last.seq:'')+
      ' · '+sourceTime(group.first.timestamp)+(group.last!==group.first?' — '+sourceTime(group.last.timestamp):'')+
      (group.count>1?' · '+group.count+' records':''),'muted'));
    list.append(item);
  }
  view.append(list);return view;
}
function auditRequest(rows){
  const first=rows[0],last=rows[rows.length-1];
  const identityAnchor=rows.find(e=>e.event_type==='reviewer_query');
  const started=rows.find(e=>e.event_type==='request_started');
  const committed=rows.filter(e=>e.event_type==='response_committed').at(-1);
  const failed=rows.filter(e=>e.event_type==='request_failed').at(-1);
  const answer=committed?.payload?.response;
  const question=started?.payload?.query||identityAnchor?.payload?.query||answer?.question||'Question not present in loaded events';
  const stopped=failed&&(!committed||failed.seq>committed.seq);
  const outcome=stopped?'Request stopped':answer?.answer_status==='evidence_only'?'Source evidence only':committed?'Answer stored':'Outcome not present in loaded events';
  const card=el('details',undefined,'audit-request');
  card.append(el('summary',question+' · '+first.actor+' · '+outcome));
  card.append(el('h3','Question'),el('p',question),el('p','Source identity: '+(identityAnchor?.payload?.effective_source_actor||first.actor)),
    el('p','Request: '+first.request_id,'muted'),
    el('p','Loaded event range: '+sourceTime(first.timestamp)+' — '+sourceTime(last.timestamp),'muted'));
  const viewer=rows.find(e=>e.payload?.application_viewer)?.payload||(identityAnchor?{
    application_viewer:identityAnchor.actor,application_role:identityAnchor.payload.application_role}:null);
  if(viewer)card.append(el('p','Application viewer: '+viewer.application_viewer+' · Role: '+(viewer.application_role||'Not recorded')));
  card.append(auditTimeline(rows));
  card.append(el('h3','Source authorization checks'));
  const decisions=rows.filter(e=>e.event_type==='authorization_decided');
  if(!decisions.length)card.append(el('p','No authorization decisions in loaded events.','muted'));
  else{
    const resources=new Map();
    for(const event of decisions){const p=event.payload||{},key=JSON.stringify([p.source,p.resource_id]);if(!resources.has(key))resources.set(key,[]);resources.get(key).push(p);}
    for(const checks of resources.values()){
      const source=checks[0].source||'Source not recorded',resource=checks[0].resource_id||'Resource not recorded';
      const results=[...new Set(checks.map(p=>(p.result||'unknown').toUpperCase()))];
      const item=el('details');item.append(el('summary',source+' · '+resource+' · '+results.join(' / ')+' · '+checks.length+' checks'));
      const phases=el('ul');
      for(const p of checks)phases.append(el('li',(p.result||'unknown').toUpperCase()+' · '+source+' · '+resource+' · '+(p.phase||'Phase not recorded')));
      item.append(phases);card.append(item);
    }
  }
  card.append(el('h3','Evidence and model activity'));
  const prepared=[...new Set(rows.filter(e=>e.event_type==='evidence_used').map(e=>e.payload?.evidence_id).filter(Boolean))];
  card.append(el('p',prepared.length?'Evidence prepared: '+prepared.join(', '):'No prepared evidence IDs in loaded events.'));
  const attempts=rows.filter(e=>e.event_type==='model_dispatch_attempted').length;
  card.append(el('p','Model send attempts recorded: '+attempts+'. Preparation alone does not prove a send.','muted'));
  const cited=[...new Set((answer?.claims||[]).flatMap(c=>c.evidence_ids||[]))];
  card.append(el('p',cited.length?'Citations in stored answer: '+cited.join(', '):'No stored-answer citations in loaded events.'));
  card.append(el('h3','Recorded outcome'),el('p',outcome));
  if(failed)card.append(el('p',(stopped?'Stop reason: ':'Earlier stop event: ')+(failed.payload?.reason||'Not recorded')));
  if(answer){
    card.append(el('p','Recorded model: '+(answer.model||'Not recorded'),'muted'));
    if(answer.answer_parts){
      for(const part of answer.answer_parts){
        card.append(el('h4',part.question));
        if(part.status==='insufficient')card.append(el('p',insufficientPartText,'notice'));
        for(const index of part.claim_indices)if(answer.claims?.[index])card.append(el('p',answer.claims[index].text));
      }
    }else for(const claim of answer.claims||[])card.append(el('p',claim.text));
    if(!answer.claims?.length)card.append(el('p','Stored answer contains no supported claims.'));
    for(const notice of answer.uncertainties||[])card.append(el('p',notice,'notice'));
  }
  if(rows.some(e=>e.event_type==='response_dispatch_attempted'))card.append(el('p','Delivery attempted; recipient reading is not established.','muted'));
  const raw=el('details');raw.append(el('summary','Original events · '+rows.length));
  for(const row of rows)raw.append(auditEvent(row));card.append(raw);
  return card;
}
$('auditNav').onclick=()=>{
  show('other');const view=viewToken(),root=$('other');
  const applicationAudit=Array.isArray(session.audit_viewer_ids);
  root.replaceChildren(el('h1','Audit explorer'),el('p',applicationAudit?'Scoped to the exact demo accounts configured for this auditor. Events describe application activity, not proof of human reading.':'Scoped to eng_a, eng_b and product_ops. Events describe application activity, not proof that a person read the answer.','lede'));
  const form=el('form',undefined,'audit-form'),input=el(applicationAudit?'select':'input');input.setAttribute('aria-label',applicationAudit?'Application account to audit':'Audit inquiry');
  if(applicationAudit){for(const id of session.audit_viewer_ids){const option=el('option',id);option.value=id;input.append(option);}input.value=session.audit_viewer_ids[0]||'';}else input.value='Show everything jdoe accessed related to payment-service in the last 30 days.';
  const button=el('button','Find events','primary');form.append(input,button);const output=el('div');root.append(form,output);
  let inquiryRevision=0;
  let loaded=[],snapshot=null;
  const active=revision=>currentView(view)&&revision===inquiryRevision;
  function display(result,revision,append=false){
    if(!active(revision))return;
    if(!append){loaded=[];snapshot=result.as_of;}
    else if(result.as_of!==snapshot)throw Error('Audit snapshot changed. Run the inquiry again.');
    const seen=new Set(loaded.map(e=>e.seq));
    loaded.push(...result.events.filter(e=>!seen.has(e.seq)));loaded.sort((a,b)=>a.seq-b.seq);
    output.replaceChildren(el('h2','Query scope'),el('pre',JSON.stringify(result.filters,null,2)),
      el('p',loaded.length+' of '+result.total+' matching events loaded · stable snapshot '+snapshot));
    output.append(el('p','Request summaries describe loaded events under these filters. Missing questions or outcomes may be on another page or excluded by the filters.','notice'),
      el('p','Preparation, model sends, stored citations and delivery are separate stages. These summaries do not verify a signature or independent checkpoint.','muted'));
    const requests=new Map();
    for(const row of loaded){const key=JSON.stringify(applicationAudit?[row.request_id]:[row.actor,row.request_id]);if(!requests.has(key))requests.set(key,[]);requests.get(key).push(row);}
    for(const rows of requests.values())output.append(auditRequest(rows));
    if(result.next_after){
      const next=el('button','Load next page');
      next.onclick=async()=>{
        if(!active(revision)||next.disabled)return;
        next.disabled=true;
        try{
          const page=await api('/api/audit/events',{...result.filters,after:result.next_after});
          if(!active(revision))return;
          display(page,revision,true);
        }catch(err){if(active(revision)){next.disabled=false;$('status').textContent=err.message;}}
      };
      output.append(next);
    }
  }
  form.onsubmit=async event=>{
    event.preventDefault();const revision=++inquiryRevision;
    output.replaceChildren();$('status').textContent='Finding scoped audit events…';
    try{
      const result=await api(applicationAudit?'/api/audit/events':'/api/audit/inquire',applicationAudit?{application_identity:input.value,resource_scope:session.audit_resource_scope,page_size:50}:{question:input.value});
      if(!active(revision))return;
      display(result,revision);$('status').textContent=result.total?'Audit events ready.':'No events match these filters.';
    }catch(err){if(active(revision)){output.replaceChildren();$('status').textContent='Use the shown inquiry template. '+err.message;}}
  };
};
$('closePreview').onclick=()=>{viewRevision++;$('previewBody').replaceChildren();$('preview').close();};
async function boot(){
  try{
    health=await api('/api/health');
    if(['operator','reviewer'].includes(health.auth_kind)){
      $('modeBadge').textContent=health.mode.includes('mock_http')?'MOCK API PILOT':'LIVE API PILOT';
      $('modeDescription').textContent=health.mode.endsWith('_live_model_source_review')?'Synthetic allowlisted resources · Code source quotes with model review · Local operator':health.mode.endsWith('_live_model_reviewed_excerpts')?'Synthetic allowlisted resources · Verbatim sources with model review · Local operator':health.mode.endsWith('_live_model_synthesis')?'Synthetic allowlisted resources · Grounded synthesis with model review · Local operator':health.mode.endsWith('_live_model_selection')?'Synthetic allowlisted resources · Live model selects excerpts · Local operator':'Synthetic allowlisted resources · Fake model · Local operator';
      $('modeFooter').textContent='Operator pilot · not employee SSO';
      $('user').hidden=true;$('loginForm').querySelector('label').hidden=true;
      $('loginForm').querySelector('button').hidden=true;
      $('loginNote').textContent='Open the one-time link from the server terminal. Token stays in the server process. This is a local operator pilot, not employee SSO.';
    if(health.auth_kind==='reviewer'){$('modeBadge').textContent=health.mode.startsWith('fixture')?'SYNTHETIC / FAKE MODEL':'LIVE API DEMO';$('reviewerCredentials').hidden=false;$('loginForm').querySelector('button').hidden=false;$('loginForm').querySelector('button').disabled=false;$('modeDescription').textContent=health.identity_boundary==='application_demo_roles_intersect_native_connection'?'Real source connections · Synthetic resources · Application role permissions within the team connection’s native access':'Synthetic demo resources · Access checked under the signed-in demo role';$('modeFooter').textContent='Fictional demo people · individually configured access · not employee SSO';$('loginNote').textContent='Use the demo username and password provided by the team. Each account represents a fictional person with individually configured access; job titles do not define access for all employees.';}
    }else if(health.auth_kind==='demo'){$('loginForm').querySelector('button').disabled=false;}
    else{throw Error('Unsupported authentication mode.');}
    try{session=await api('/api/session');}
    catch(err){if(err.status===403&&bootstrapTicket&&health.auth_kind==='operator')session=await api(health.login_path,{ticket:bootstrapTicket});else throw err;}
    identity();
  }catch(err){show('login');if(health?.auth_kind==='reviewer'&&err.status===403){$('status').textContent='Sign in with your demo account. Sessions expire after 1 hour.';return;}$('status').textContent=['operator','reviewer'].includes(health?.auth_kind)&&err.status===403?(bootstrapTicket?'This one-time operator link has expired or was already used. Ask the operator to refresh the entry, then reopen the launch command.':'No active operator session. Sessions expire after 1 hour. Ask the operator to refresh the entry, then reopen the launch command. Saved answers remain stored.'): 'Could not connect to the local service. Refresh to reconnect; no new question was submitted.';}
}
boot();
