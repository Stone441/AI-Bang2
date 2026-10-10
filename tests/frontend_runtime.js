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
 console.log('PASS: real elapsed timer, duplicate submit, stale query/runtime response, classified retry, preserved question, History/navigation/expiry cleanup');
})().catch(e=>{console.error(e);process.exitCode=1;});
