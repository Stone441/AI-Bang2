const labels={baseline:'Read the current runbook',update:'Publish a changed runbook',revoke:'Revoke access and check again',audit:'Inspect the recorded audit'};
const checks={runbook_v1_returned:'Version 1 was returned',one_object_processed:'Only the changed object was processed',runbook_v2_returned:'Version 2 includes the new standby-queue instruction',old_version_preview_blocked:'The old version preview is blocked',old_version_history_hidden:'The old version history is hidden',new_query_excludes_runbook:'The new answer excludes the revoked runbook',old_preview_blocked:'The earlier citation is blocked',old_history_hidden:'The earlier employee answer is hidden',other_authorized_evidence_remains:'Other authorized evidence remains available',local_chain_valid:'The local audit chain is valid',scoped_audit_has_events:'The scoped auditor can find the recorded events',three_answers_recorded:'All three answers were recorded'};
let state=null,busy=false;
const get=id=>document.getElementById(id);
function node(tag,text){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;}
function render(){
  const controls=get('controls');controls.replaceChildren();
  for(const [key,label] of Object.entries(labels)){
    const li=node('li'),button=node('button',label);button.disabled=busy||state.next_action!==key;
    button.onclick=()=>step(key);li.append(button);controls.append(li);
  }
  const results=get('results');results.replaceChildren();
  for(const record of state.steps){
    const item=node('article');item.append(node('h2',labels[record.action]),node('p',record.passed?'Checks passed in this synthetic run':'A check failed; keep this result for investigation'));
    const list=node('ul');list.className='checks';
    for(const [key,value] of Object.entries(record.checks)){const li=node('li',(value?'Passed: ':'Failed: ')+(checks[key]||key));li.className=value?'pass':'fail';list.append(li);}item.append(list);
    const events=node('div');events.className='events';
    for(const event of record.source_events)events.append(node('p',event.event+' · '+event.at));
    events.append(node('p','Observation completed · '+record.finished_at));item.append(events);
    if(record.answer){
      const details=node('details');details.append(node('summary','Recorded operator observation · '+record.request_id));
      for(const evidence of record.answer.evidence){details.append(node('h3',evidence.title+' · Version '+evidence.version),node('p',evidence.text));}
      details.append(node('p','Earlier observations remain in this lab transcript; this is not employee History.'));item.append(details);
    }
    results.append(item);
  }
  get('status').textContent=state.failure?'Lab stopped: '+state.failure:busy?'Running the next local stage…':state.next_action?'Ready: '+labels[state.next_action]:'Rehearsal complete. Save the transcript to inspect the actual events.';
}
async function step(action){
  if(busy)return;busy=true;render();
  try{
    const response=await fetch('/api/lab/step',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':state.csrf},body:JSON.stringify({action})});
    const body=await response.json();if(!response.ok)throw Error(body.error||'Lab step failed');state=body;
  }catch(error){busy=false;await load();get('status').textContent=error.message;return;}
  busy=false;render();
}
async function load(){try{const response=await fetch('/api/lab/state');if(!response.ok)throw Error('The lab state could not be loaded.');state=await response.json();render();}catch(error){get('status').textContent=error.message;}}
load();
