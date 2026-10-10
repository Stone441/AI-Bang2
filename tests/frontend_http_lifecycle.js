'use strict';
// Actual product HTTP + app.js in a DOM stub. This is not a browser or live model test.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const base=process.argv[2],storage=new Map();let cookie='';
class Element{constructor(){this.children=[];this.hidden=false;this.open=false;this.value='';this.textContent='';this.attributes={};}replaceChildren(...c){this.children=c;this.textContent='';}append(...c){this.children.push(...c);}querySelector(){return new Element();}setAttribute(k,v){this.attributes[k]=v;}focus(){}close(){this.open=false;}}
async function request(path,options={}){const r=await fetch(base+path,{...options,headers:{...options.headers,Cookie:cookie}});if(r.headers.get('set-cookie'))cookie=r.headers.get('set-cookie').split(';')[0];return r;}
async function login(){const r=await request('/api/demo/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user:'eng_b'})});assert.equal(r.status,200);return r.json();}
function page(session){const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};const ctx=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,URL,Date,performance,setInterval:()=>1,clearInterval(){},sessionStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},fetch:()=>new Promise(()=>{})});vm.runInContext(fs.readFileSync('web/app.js','utf8'),ctx);ctx.fetch=request;vm.runInContext('session='+JSON.stringify(session)+";health={auth_kind:'demo'};show('workspace')",ctx);return {ctx,get};}
const text=e=>[e.textContent,...e.children.map(text)].join(' ');
const watchdog=setTimeout(()=>{console.error('FAIL: HTTP lifecycle timed out');process.exitCode=1;},10000);
(async()=>{
 const session=await login(),first=page(session),question='payment-service';first.get('question').value=question;
 const query=first.get('queryForm').onsubmit({preventDefault(){}});
 let running;for(let i=0;i<30;i++){running=await (await request('/api/runtime')).json();if(running.run?.status==='running')break;await new Promise(resolve=>setTimeout(resolve,5));}
 assert.equal(running.run.status,'running');const rid=running.run.request_id;
 const refreshed=page(session);vm.runInContext('armResume()',refreshed.ctx);await vm.runInContext('refreshRuntime()',refreshed.ctx);
 assert.equal(refreshed.get('question').value,question);assert.equal(refreshed.get('runningQuestion').textContent,question);assert.equal(refreshed.get('ask').disabled,true);assert.match(refreshed.get('elapsed').textContent,/^[0-9.]+ s elapsed$/);assert.ok(refreshed.get('progressPhase').textContent.startsWith('Current stage: '));
 await query;const completed=await (await request('/api/runtime')).json();assert.equal(completed.run.status,'completed');assert.equal(completed.run.phase,'final_checks');assert.ok(!completed.run.phases.includes('review'));await vm.runInContext('refreshRuntime()',refreshed.ctx);assert.ok(text(refreshed.get('answer')).includes('Evidence-backed excerpts'));
 const terminal=page(session);vm.runInContext('armResume()',terminal.ctx);await vm.runInContext('refreshRuntime()',terminal.ctx);assert.ok(text(terminal.get('answer')).includes(question));
 await terminal.get('historyNav').onclick();const item=terminal.get('other').children[2];assert.equal(item.children[0].textContent,question);await item.children[0].onclick();assert.ok(text(item).includes('Evidence-backed excerpts'));
 // A direct rejected request tests actual 503 payload; paused UI itself never submits again.
 const rejected=await request('/api/query',{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':session.csrf},body:JSON.stringify({question:'REJECTED QUESTION'})});assert.equal(rejected.status,503);const failure=await rejected.json();assert.equal(failure.code,'trial_admission_paused');assert.equal(failure.run.phase,'queued');assert.notEqual(failure.request_id,rid);
 const failedRefresh=page(session);vm.runInContext('armResume()',failedRefresh.ctx);await vm.runInContext('refreshRuntime()',failedRefresh.ctx);assert.equal(failedRefresh.get('question').value,'REJECTED QUESTION');assert.ok(text(failedRefresh.get('answer')).includes('Stopped before retrieval'));assert.ok(text(failedRefresh.get('answer')).includes(failure.request_id));assert.equal(failedRefresh.get('ask').disabled,true);assert.equal(failedRefresh.get('progress').hidden,true);
 await failedRefresh.get('queryForm').onsubmit({preventDefault(){}});const unchanged=await (await request('/api/runtime')).json();assert.equal(unchanged.run.request_id,failure.request_id);assert.equal(unchanged.query_admission.attempts_used,1);
 const other=await login();assert.notEqual(other.csrf,session.csrf);const isolated=await (await request('/api/runtime')).json();assert.equal(isolated.run,null);
 console.log('PASS: real fixture product HTTP + app.js running/terminal refresh, History open, paused 503 and failure refresh, session isolation; one fake query only, no live/model fee');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>clearTimeout(watchdog));
