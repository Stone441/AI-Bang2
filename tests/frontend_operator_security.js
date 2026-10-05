'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const downloads=[];const revokedUrls=[];const exportBlobs=[];
class Element{
  constructor(){this.children=[];this.hidden=false;this.open=false;this.value='';this.textContent='';}
  replaceChildren(...children){this.children=children;this.textContent='';}
  append(...children){this.children.push(...children);}
  querySelector(){return new Element();}
  setAttribute(){}
  focus(){}
  close(){this.open=false;}
  showModal(){this.open=true;}
  click(){downloads.push({href:this.href,filename:this.download});}
}
const elements=new Map();const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const context=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},
  location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,
  Blob,URL:{createObjectURL:blob=>{exportBlobs.push(blob);return 'blob:synthetic-export';},revokeObjectURL:url=>revokedUrls.push(url)},
  fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8'),context);
function seed(){for(const id of ['answer','other','previewBody'])get(id).append(new Element());get('preview').open=true;}
(async()=>{
  vm.runInContext("session={actor:'eng_b',csrf:'synthetic'};health={auth_kind:'operator'}",context);
  seed();get('workspaceNav').onclick();
  assert.equal(get('answer').children.length,0);assert.equal(get('other').children.length,0);
  seed();context.fetch=async()=>({ok:false,json:async()=>({error:'Unavailable'})});
  await vm.runInContext("preview('jira:10013@1')",context);
  assert.equal(get('answer').children.length,0);assert.equal(get('previewBody').children.length,0);
  assert.equal(get('preview').open,false);assert.equal(get('other').children.length,1);
  assert.match(get('status').textContent,/unavailable/);
  seed();context.fetch=()=>new Promise(()=>{});
  get('queryForm').onsubmit({preventDefault(){}});
  assert.equal(get('answer').children.length,0);assert.equal(get('other').children.length,0);
  seed();get('historyNav').onclick();
  assert.equal(get('answer').children.length,0);
  function visibleText(element){return [element.textContent,...element.children.map(visibleText)].join(' ');}
  vm.runInContext("renderAnswer({model:'deepseek-flash-evidence-selection-v1',claims:[],evidence:[{source:'drive',title:'Synthetic',evidence_id:'drive:test@1',version:1,locator:{},source_updated_at:'2026-10-05',indexed_at:'2026-10-05'}],uncertainties:[],request_id:'synthetic',model_call:{called:true,prompt_tokens:100,completion_tokens:20,total_tokens:120,accounted_upper_micro_usd:54}})",context);
  assert.match(visibleText(get('answer')),/LIVE MODEL · SOURCE EXCERPTS/);
  assert.doesNotMatch(visibleText(get('answer')),/FAKE MODEL/);
  assert.match(visibleText(get('answer')),/100 input \+ 20 output = 120 tokens/);
  assert.match(visibleText(get('answer')),/US\$0\.000054/);
  assert.match(visibleText(get('answer')),/not the provider invoice/);
  vm.runInContext("renderAnswer({model:'deepseek-flash-evidence-selection-v1',claims:[],evidence:[],uncertainties:[],request_id:'synthetic',model_call:{called:false,reason:'no_authorized_evidence'}})",context);
  assert.match(visibleText(get('answer')),/NO MODEL CALL/);
  assert.doesNotMatch(visibleText(get('answer')),/LIVE MODEL · SOURCE EXCERPTS/);
  vm.runInContext("renderAnswer({model:'fake-extractive-v1',claims:[],evidence:[],uncertainties:[],request_id:'synthetic'})",context);
  assert.match(visibleText(get('answer')),/FAKE MODEL/);
  vm.runInContext("renderAnswer({model:'deepseek-flash-evidence-selection-v1',claims:[],evidence:[],uncertainties:[],request_id:'legacy'})",context);
  assert.match(visibleText(get('answer')),/MODEL CALL NOT RECORDED/);
  assert.doesNotMatch(visibleText(get('answer')),/NO MODEL CALL|US\$/);
  assert.match(vm.runInContext("answerStatus({claims:[],model_call:{called:true}})",context),/model checked authorized sources/);
  vm.runInContext("renderAnswer({request_id:'revoked',unavailable:true,message:'No longer available'})",context);
  assert.doesNotMatch(visibleText(get('answer')),/tokens|cost estimate|Model usage/);
  vm.runInContext("renderAnswer({model:'deepseek-flash-grounded-synthesis-v1',claim_format:'grounded_synthesis_v1',claims:[{text:'Pilot only.',evidence_ids:['drive:test@1'],supports:[{evidence_id:'drive:test@1',quote:'GA is not approved.'}]}],evidence:[],uncertainties:[],request_id:'synthetic',model_call:{called:true,prompt_tokens:100,completion_tokens:20,total_tokens:120,accounted_upper_micro_usd:54},model_review:{called:true,prompt_tokens:110,completion_tokens:10,total_tokens:120,accounted_upper_micro_usd:45}})",context);
  assert.match(visibleText(get('answer')),/Evidence-backed answer/);
  assert.match(visibleText(get('answer')),/REVIEWED SYNTHESIS/);
  assert.match(visibleText(get('answer')),/Exact supporting quotes/);
  assert.match(visibleText(get('answer')),/GA is not approved/);
  assert.match(visibleText(get('answer')),/Evidence review usage receipt/);
  assert.match(visibleText(get('answer')),/US\$0\.000045/);
  vm.runInContext("renderAnswer({request_id:'revoked',unavailable:true,message:'No longer available'})",context);
  assert.doesNotMatch(visibleText(get('answer')),/GA is not approved|review usage|Pilot only/);
  const receiptId='0123456789abcdef0123456789abcdef';
  seed();let requested=[];
  context.fetch=async path=>{requested.push(path);return {ok:true,status:200,text:async()=>JSON.stringify({history:[{request_id:receiptId,unavailable:true}]})};};
  await vm.runInContext(`exportAnswer('${receiptId}')`,context);
  assert.deepEqual(requested,['/api/export/'+receiptId]);assert.equal(downloads.length,0);
  assert.equal(get('answer').children.length,0);assert.equal(get('other').children.length,0);
  assert.equal(get('preview').open,false);assert.match(get('status').textContent,/unavailable for export/);
  const rawExport='{"history":[{"request_id":"'+receiptId+'","claims":[],"evidence":[{"version":903088382970380097}]}]}';
  context.fetch=async()=>({ok:true,status:200,text:async()=>rawExport});
  await vm.runInContext(`exportAnswer('${receiptId}')`,context);
  assert.equal(downloads.length,1);assert.equal(downloads[0].filename,'ContextLedger-'+receiptId+'.json');
  assert.deepEqual(revokedUrls,['blob:synthetic-export']);assert.equal(await exportBlobs[0].text(),rawExport+'\n');assert.match(get('status').textContent,/current access checks/);
  vm.runInContext("session={actor:'eng_b',csrf:'synthetic'}",context);seed();requested=[];
  context.fetch=async path=>{requested.push(path);return {ok:path==='/api/session',status:path==='/api/session'?200:403,json:async()=>({error:'Unavailable'})};};
  await vm.runInContext("preview('slack:synthetic@1')",context);
  assert.deepEqual(requested,['/api/evidence/slack%3Asynthetic%401','/api/session']);
  assert.equal(vm.runInContext('session.actor',context),'eng_b');
  seed();context.fetch=async()=>({ok:false,status:403,json:async()=>({error:'Unavailable'})});
  await vm.runInContext("preview('slack:synthetic@1')",context);
  assert.equal(vm.runInContext('session',context),null);assert.equal(vm.runInContext('historyId',context),null);
  assert.equal(get('other').children.length,0);assert.equal(get('previewBody').children.length,0);
  assert.equal(get('workspace').hidden,true);assert.equal(get('login').hidden,false);
  assert.equal(get('identity').textContent,'Not signed in');assert.match(get('status').textContent,/latest one-time link/);
  vm.runInContext("session={actor:'eng_b',csrf:'synthetic'};show('workspace')",context);
  let resolveLatePreview;
  context.fetch=()=>new Promise(resolve=>resolveLatePreview=resolve);
  const latePreview=vm.runInContext("preview('synthetic@1')",context);
  vm.runInContext('expiredSession()',context);
  resolveLatePreview({ok:true,json:async()=>({title:'LATE-RESTRICTED-TITLE',text:'LATE-RESTRICTED-BODY',version:1,locator:{},source_url:'https://example.com'})});
  await latePreview;
  assert.equal(get('preview').open,false,'A response after session expiry must not reopen a preview');
  assert.equal(get('previewBody').children.length,0);
  vm.runInContext("session={actor:'eng_b',csrf:'synthetic'};historyId=null;show('workspace')",context);
  let resolveOldQuery;
  context.fetch=()=>new Promise(resolve=>resolveOldQuery=resolve);
  const oldQuery=get('queryForm').onsubmit({preventDefault(){}});
  get('workspaceNav').onclick();
  let resolveNewQuery;
  context.fetch=()=>new Promise(resolve=>resolveNewQuery=resolve);
  const newQuery=get('queryForm').onsubmit({preventDefault(){}});
  resolveOldQuery({ok:true,json:async()=>({request_id:'late',model:'fake-extractive-v1',claims:[{text:'LATE-OLD-ANSWER',evidence_ids:[]}],evidence:[],uncertainties:[]})});
  await oldQuery;
  assert.equal(get('ask').disabled,true,'Old request must not unlock a newer pending query');
  assert.doesNotMatch(visibleText(get('answer')),/LATE-OLD-ANSWER/);
  assert.equal(vm.runInContext('historyId',context),null);
  resolveNewQuery({ok:true,json:async()=>({request_id:'new',model:'fake-extractive-v1',claims:[],evidence:[],uncertainties:[]})});
  await newQuery;assert.equal(get('ask').disabled,false);assert.equal(vm.runInContext('historyId',context),'new');
  let resolveLateHistory;
  context.fetch=()=>new Promise(resolve=>resolveLateHistory=resolve);
  const oldHistory=get('historyNav').onclick();get('workspaceNav').onclick();
  resolveLateHistory({ok:true,json:async()=>({history:[{request_id:'late',model:'fake-extractive-v1',claims:[{text:'LATE-HISTORY',evidence_ids:[]}],evidence:[],uncertainties:[]}]})});
  await oldHistory;assert.equal(get('other').children.length,0);
  let resolveLateExport;
  context.fetch=()=>new Promise(resolve=>resolveLateExport=resolve);
  const oldExport=vm.runInContext(`exportAnswer('${receiptId}')`,context);
  vm.runInContext('expiredSession()',context);
  resolveLateExport({ok:true,text:async()=>rawExport});
  await oldExport;assert.equal(downloads.length,1,'A delayed export after session expiry must not create a download');
  assert.match(vm.runInContext("answerStatus({claims:[{}],claim_format:'grounded_synthesis_v1',model_call:{called:true}})",context),/Grounded synthesis and model review completed/);
  console.log('PASS: workspace navigation, denied preview, pending query and history navigation discard stale views');
})().catch(e=>{console.error(e);process.exitCode=1;});
