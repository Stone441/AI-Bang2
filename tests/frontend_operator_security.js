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
  assert.doesNotMatch(visibleText(get('answer')),/Export answer/);
  assert.equal(vm.runInContext('typeof exportAnswer',context),'undefined');
  assert.equal(fs.readFileSync('web/index.html','utf8').includes('newQuestion'),false);
  vm.runInContext("session={actor:'eng_b',csrf:'synthetic'}",context);seed();let requested=[];
  context.fetch=async path=>{requested.push(path);return {ok:path==='/api/session',status:path==='/api/session'?200:403,json:async()=>({error:'Unavailable'})};};
  await vm.runInContext("preview('slack:synthetic@1')",context);
  assert.deepEqual(requested,['/api/evidence/slack%3Asynthetic%401','/api/session']);
  assert.equal(vm.runInContext('session.actor',context),'eng_b');
  seed();context.fetch=async()=>({ok:false,status:403,json:async()=>({error:'Unavailable'})});
  await vm.runInContext("preview('slack:synthetic@1')",context);
  assert.equal(vm.runInContext('session',context),null);
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
  vm.runInContext("session={actor:'eng_b',csrf:'synthetic'};show('workspace')",context);
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

  resolveNewQuery({ok:true,json:async()=>({request_id:'new',model:'fake-extractive-v1',claims:[],evidence:[],uncertainties:[]})});
  await newQuery;assert.equal(get('ask').disabled,false);
  const submitted=[];context.fetch=async (_path,options)=>{submitted.push(JSON.parse(options.body));return {ok:true,json:async()=>({request_id:'independent',model:'fake-extractive-v1',claims:[],evidence:[],uncertainties:[]})};};
  get('question').value='First topic';await get('queryForm').onsubmit({preventDefault(){}});
  get('question').value='Second topic';await get('queryForm').onsubmit({preventDefault(){}});
  assert.deepEqual(submitted,[{question:'First topic'},{question:'Second topic'}]);
  let resolveLateHistory;
  context.fetch=()=>new Promise(resolve=>resolveLateHistory=resolve);
  const oldHistory=get('historyNav').onclick();get('workspaceNav').onclick();
  resolveLateHistory({ok:true,json:async()=>({history:[{request_id:'late',model:'fake-extractive-v1',claims:[{text:'LATE-HISTORY',evidence_ids:[]}],evidence:[],uncertainties:[]}]})});
  await oldHistory;assert.equal(get('other').children.length,0);
  assert.match(vm.runInContext("answerStatus({claims:[{}],claim_format:'grounded_synthesis_v1',model_call:{called:true}})",context),/Grounded synthesis and model review completed/);
  context.URL=URL;
  context.source={source:'confluence',source_url:'https://tenant.atlassian.net/wiki/pages/viewpage.action?pageId=123'};
  const platform=vm.runInContext('originalLink(source)',context);
  assert.equal(platform.href,context.source.source_url);assert.equal(platform.target,'_blank');assert.equal(platform.rel,'noopener noreferrer');
  for(const url of ['javascript:alert(1)','data:text/html,secret','http://tenant.atlassian.net/wiki','https://tenant.atlassian.net.evil.example/wiki','https://user:secret@tenant.atlassian.net/wiki','https://tenant.atlassian.net:444/wiki','fixture://synthetic-demo/confluence/C-01']){
    context.source.source_url=url;assert.equal(vm.runInContext('originalLink(source)',context),null,url);
  }
  context.source={source:'drive',source_url:'https://docs.google.com/document/d/approved/edit'};
  assert.ok(vm.runInContext('originalLink(source)',context));
  context.source.source='jira';assert.equal(vm.runInContext('originalLink(source)',context),null);
  vm.runInContext("renderAnswer({question:'<img src=x> Which release?',answered_at:'2026-10-06T00:00:00Z',request_id:'new',model:'fake-extractive-v1',claims:[],evidence:[],uncertainties:[]})",context);
  assert.match(visibleText(get('answer')),/<img src=x> Which release\?/);assert.match(visibleText(get('answer')),/Answered /);
  vm.runInContext("renderAnswer({request_id:'old',model:'fake-extractive-v1',claims:[],evidence:[],uncertainties:[]})",context);
  assert.match(visibleText(get('answer')),/Question not recorded/);assert.match(visibleText(get('answer')),/Generation time not recorded/);
  assert.match(visibleText(get('answer')),/Answer diagnostics/);
  console.log('PASS: workspace navigation, denied preview, pending query and history navigation discard stale views');
})().catch(e=>{console.error(e);process.exitCode=1;});
