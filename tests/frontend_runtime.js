'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(){this.children=[];this.hidden=false;this.open=false;this.value='';this.textContent='';this.attributes={};}
 replaceChildren(...c){this.children=c;this.textContent='';}append(...c){this.children.push(...c);}querySelector(){return new Element();}
 setAttribute(k,v){this.attributes[k]=v;}focus(){}close(){this.open=false;}showModal(){this.open=true;}
}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
let now=1000,nextTimer=1;const timers=new Map();
const ctx=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},
 location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,URL,Date,
 performance:{now:()=>now},setInterval:fn=>{const id=nextTimer++;timers.set(id,fn);return id;},clearInterval:id=>timers.delete(id),fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8'),ctx);
const response=(body,ok=true,status=ok?200:503)=>({ok,status,json:async()=>body});
const answer={request_id:'new',model:'fake-extractive-v1',claims:[],evidence:[],uncertainties:[]};
const runtime=id=>({model:'safe-model',mode:'mock_http',sources:[],run:{request_id:id,status:'running',phase:'generation'}});
const text=e=>[e.textContent,...e.children.map(text)].join(' ');
(async()=>{
 vm.runInContext("session={actor:'eng_b',csrf:'test'};health={auth_kind:'operator'};show('workspace')",ctx);
 get('question').value='KEEP ORIGINAL QUESTION';let requests=[],resolveA;
 ctx.fetch=path=>{requests.push(path);return new Promise(resolve=>resolveA=resolve);};
 const a=get('queryForm').onsubmit({preventDefault(){}});
 assert.equal(get('ask').disabled,true);assert.equal(get('progress').hidden,false);assert.equal(get('elapsed').textContent,'0.0 s elapsed');
 now+=2350;for(const fn of timers.values())fn();assert.equal(get('elapsed').textContent,'2.4 s elapsed');
 await get('queryForm').onsubmit({preventDefault(){}});assert.deepEqual(requests,['/api/query']);
 let resolvePoll;ctx.fetch=()=>new Promise(resolve=>resolvePoll=resolve);const oldPoll=vm.runInContext('refreshRuntime()',ctx);
 get('workspaceNav').onclick();assert.equal(timers.size,0);assert.equal(get('progress').hidden,true);
 let resolveB;ctx.fetch=()=>new Promise(resolve=>resolveB=resolve);const b=get('queryForm').onsubmit({preventDefault(){}});
 resolvePoll(response(runtime('OLD-A')));await oldPoll;assert.equal(vm.runInContext('pendingQuery.requestId',ctx),null);
 resolveA(response({...answer,claims:[{text:'LATE-A',evidence_ids:[]}]}));await a;
 assert.doesNotMatch(text(get('answer')),/LATE-A/);assert.equal(get('ask').disabled,true);
 ctx.fetch=async()=>response(runtime('CURRENT-B'));
 resolveB(response({error:'No validated draft is shown.',code:'model_output_unavailable',request_id:'CURRENT-B'},false));await b;
 assert.equal(get('question').value,'KEEP ORIGINAL QUESTION');assert.equal(get('ask').disabled,false);assert.equal(timers.size,0);
 assert.match(text(get('answer')),/Answer did not pass validation|CURRENT-B|Try this question again/);
 let resolveC;ctx.fetch=()=>new Promise(resolve=>resolveC=resolve);const c=get('queryForm').onsubmit({preventDefault(){}});
 ctx.fetch=async()=>response({history:[]});await get('historyNav').onclick();assert.equal(get('progress').hidden,true);
 resolveC(response(answer));await c;assert.equal(get('answer').children.length,0);assert.match(text(get('other')),/No answers yet/);
 vm.runInContext("show('workspace')",ctx);let resolveD;ctx.fetch=()=>new Promise(resolve=>resolveD=resolve);const d=get('queryForm').onsubmit({preventDefault(){}});
 vm.runInContext('expiredSession()',ctx);resolveD(response(answer));await d;
 assert.equal(get('runtime').hidden,true);assert.equal(get('progress').hidden,true);assert.equal(get('answer').children.length,0);assert.equal(timers.size,0);
 vm.runInContext("session={actor:'eng_b',csrf:'test'}",ctx);
 let resolveRuntime,resolveLogout;
 ctx.fetch=path=>new Promise(resolve=>{if(path==='/api/runtime')resolveRuntime=resolve;else if(path==='/api/logout')resolveLogout=resolve;});
 vm.runInContext('identity()',ctx);
 const logout=get('identity').children[1].onclick();
 resolveRuntime(response(runtime('OLD-LOGOUT')));await new Promise(resolve=>setImmediate(resolve));
 assert.equal(get('runtime').hidden,true);assert.equal(get('runtimeModel').textContent,'');
 resolveLogout(response({}));await logout;
 assert.equal(get('runtime').hidden,true);assert.equal(get('runtimeModel').textContent,'');assert.equal(timers.size,0);
 const evidenceOnly={request_id:'blocked',question:'Original question',model:'deepseek-flash-grounded-synthesis-v13',answer_status:'evidence_only',synthesis_failure:'model_output_unavailable',claims:[{text:'Original approved source passage.',evidence_ids:[]}],evidence:[],uncertainties:['No validated synthesis.']};
 ctx.evidenceOnly=evidenceOnly;vm.runInContext('renderAnswer(evidenceOnly)',ctx);
 assert.match(text(get('answer')),/Synthesis was blocked/);
 assert.doesNotMatch(text(get('answer')),/Original approved source passage/,'Rejected historical claims must not reappear as answer prose');
 assert.match(text(get('answer')),/No validated answer is available/);
 assert.match(vm.runInContext('answerStatus(evidenceOnly)',ctx),/failed validation/);
 assert.match(vm.runInContext('modelLabel(evidenceOnly)',ctx),/SYNTHESIS BLOCKED/);
 assert.ok(!text(get('answer')).includes('Grounded synthesis and model review completed'));
 ctx.sourceOnly={...evidenceOnly,answer_kind:'reviewed_excerpts'};vm.runInContext('renderAnswer(sourceOnly)',ctx);
 assert.ok(!text(get('answer')).includes('Reviewed source answer'));assert.match(text(get('answer')),/Source answer was blocked/);
 const sourceReview={request_id:'review-only',question:'Original question',model:'deepseek-flash-reviewed-excerpts-all-sources-v1',answer_kind:'reviewed_excerpts',claim_format:'reviewed_source_v1',review_status:'accepted',claims:[{text:'Checked source passage.',evidence_ids:[]}],evidence:[],uncertainties:[],model_review:{called:true,reservation_id:'one-review',prompt_tokens:100,completion_tokens:20,total_tokens:120,accounted_upper_micro_usd:54}};
 ctx.sourceReview=sourceReview;vm.runInContext('renderAnswer(sourceReview)',ctx);
 assert.match(text(get('answer')),/Reviewed source answer/);
 assert.match(text(get('answer')),/Evidence review usage receipt/);
 assert.equal((text(get('answer')).match(/Conservative cost estimate/g)||[]).length,1);
 assert.match(vm.runInContext('modelLabel(sourceReview)',ctx),/LIVE MODEL · REVIEWED SOURCES/);
 assert.ok(!text(get('answer')).includes('Model usage was not recorded'));
 ctx.openHuman={allowed:true,human_unlimited:true,attempts_used:8,attempts_limit:null,attempts_remaining:null};vm.runInContext('renderAdmission(openHuman)',ctx);
 assert.equal(get('trialStatus').hidden,true);assert.equal(get('trialStatus').textContent,'');assert.ok(!get('trialStatus').textContent.includes('null'));assert.equal(get('ask').disabled,false);
 vm.runInContext("renderAdmission({...openHuman,allowed:false,reason:'cost_limit'})",ctx);assert.equal(get('ask').disabled,true);assert.match(get('trialStatus').textContent,/temporarily unavailable/);assert.equal(get('trialStatus').hidden,false);
 ctx.attributed={allowed:true,human_unlimited:false,attempts_used:null,attempts_limit:null,attempts_remaining:null,model_calls_used:4};vm.runInContext('renderAdmission(attributed)',ctx);
 assert.equal(get('trialStatus').hidden,true);assert.equal(get('ask').disabled,false);assert.doesNotMatch(get('trialStatus').textContent,/null|undefined/);
 vm.runInContext('renderAdmission({...attributed,human_unlimited:true})',ctx);assert.doesNotMatch(get('trialStatus').textContent,/null|undefined/);assert.equal(get('trialStatus').hidden,true);assert.equal(get('ask').disabled,false);
 console.log('PASS: real elapsed timer, duplicate submit, stale query/runtime response, classified retry, preserved question, History/navigation/expiry cleanup');
})().catch(e=>{console.error(e);process.exitCode=1;});
