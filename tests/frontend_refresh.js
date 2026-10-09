'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{constructor(){this.children=[];this.hidden=false;this.open=false;this.value='';this.textContent='';this.attributes={};}replaceChildren(...c){this.children=c;this.textContent='';}append(...c){this.children.push(...c);}querySelector(){return new Element();}setAttribute(k,v){this.attributes[k]=v;}focus(){}close(){this.open=false;}}
const storage=new Map(),response=body=>({ok:true,status:200,json:async()=>body});
let paid=0;
function page(){const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};let now=1000;
 const ctx=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,URL,Date,performance:{now:()=>now},setInterval:()=>1,clearInterval(){},sessionStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)},fetch:()=>new Promise(()=>{})});
 vm.runInContext(fs.readFileSync('web/app.js','utf8'),ctx);vm.runInContext("session={actor:'eng_b',csrf:'same-session'};health={auth_kind:'operator'};show('workspace')",ctx);
 return {ctx,get,tick:()=>{now+=2000;}};}
const run=(status='running',id='a'.repeat(32))=>({mode:'mock_http',model:'fake-extractive-v1',sources:[],run:{request_id:id,status,phase:'review',elapsed_seconds:42,error_code:status==='failed'?'model_output_unavailable':null}});
const answer={request_id:'a'.repeat(32),question:'ORIGINAL QUESTION',claims:[],evidence:[],uncertainties:[],model:'fake-extractive-v1'};
const watchdog=setTimeout(()=>{console.error('FAIL: refresh test did not finish');process.exitCode=1;},3000);
(async()=>{
 const original=page();original.get('question').value='ORIGINAL QUESTION';let finish;
 original.ctx.fetch=path=>{assert.equal(path,'/api/query');paid++;return new Promise(resolve=>finish=resolve);};
 const query=original.get('queryForm').onsubmit({preventDefault(){}});assert.equal(paid,1);
 original.get('question').value='EDITED WHILE WAITING';original.ctx.fetch=async path=>{assert.equal(path,'/api/runtime');return response(run());};await vm.runInContext('refreshRuntime()',original.ctx);assert.equal(JSON.parse(storage.get('brain.pending.same-session')).question,'ORIGINAL QUESTION');
 // New JS realm, same authenticated session and tab-local storage; old HTTP still running.
 const refreshed=page();refreshed.ctx.fetch=async path=>{assert.equal(path,'/api/runtime');return response(run());};
 vm.runInContext('resumeOnRuntime=true',refreshed.ctx);await vm.runInContext('refreshRuntime()',refreshed.ctx);
 assert.equal(refreshed.get('question').value,'ORIGINAL QUESTION');assert.equal(refreshed.get('ask').disabled,true);assert.equal(refreshed.get('elapsed').textContent,'42.0 s elapsed');assert.equal(refreshed.get('progressPhase').textContent,'Reviewing the evidence');
 await refreshed.get('queryForm').onsubmit({preventDefault(){}});assert.equal(paid,1);
 let checks=0;refreshed.ctx.fetch=async path=>{if(path==='/api/runtime')return response(run('completed'));assert.equal(path,'/api/history?request_id='+answer.request_id);checks++;return response({history:[answer]});};
 await vm.runInContext('refreshRuntime()',refreshed.ctx);assert.equal(checks,1);assert.equal(refreshed.get('ask').disabled,false);assert.equal(refreshed.get('progress').hidden,true);assert.equal(storage.size,0);assert.equal(paid,1);
 await vm.runInContext('refreshRuntime()',refreshed.ctx);assert.equal(checks,1);
 finish(response(answer));await query;
 // Failure resumes preserve the question, stop timers, and do not retrieve or regenerate a draft.
 storage.set('brain.pending.same-session',JSON.stringify({question:'KEEP FAILED QUESTION',requestId:answer.request_id}));
 const failed=page();vm.runInContext('resumeOnRuntime=true',failed.ctx);failed.ctx.fetch=async path=>{assert.equal(path,'/api/runtime');return response(run('failed'));};await vm.runInContext('refreshRuntime()',failed.ctx);
 assert.equal(failed.get('question').value,'KEEP FAILED QUESTION');assert.equal(failed.get('ask').disabled,false);assert.equal(storage.size,0);assert.equal(paid,1);
 // A different login cannot restore another session's question.
 storage.set('brain.pending.same-session',JSON.stringify({question:'PRIVATE OLD QUESTION',requestId:answer.request_id}));
 const other=page();vm.runInContext("session={actor:'product_ops',csrf:'different'};resumeOnRuntime=true",other.ctx);other.ctx.fetch=async()=>response({...run(),run:null});await vm.runInContext('refreshRuntime()',other.ctx);assert.equal(other.get('question').value,'');
 // An unknown pre-dispatch ID cannot mistake an older completed answer for the new submission.
 storage.set('brain.pending.same-session',JSON.stringify({question:'UNBOUND NEW QUESTION',requestId:null}));
 const unbound=page();vm.runInContext('resumeOnRuntime=true',unbound.ctx);unbound.ctx.fetch=async path=>{assert.equal(path,'/api/runtime');return response(run('completed'));};await vm.runInContext('refreshRuntime()',unbound.ctx);assert.equal(vm.runInContext('pendingQuery',unbound.ctx),null);
 // Fresh retrieval can revoke a completed answer, and must not expose cached claims.
 storage.set('brain.pending.same-session',JSON.stringify({question:'ORIGINAL QUESTION',requestId:answer.request_id}));
 const revoked=page();vm.runInContext('resumeOnRuntime=true',revoked.ctx);revoked.ctx.fetch=async path=>response(path==='/api/runtime'?run('completed'):{history:[{request_id:answer.request_id,unavailable:true,message:'Current evidence unavailable'}]});await vm.runInContext('refreshRuntime()',revoked.ctx);assert.equal(revoked.get('answer').children[0].textContent,'Current evidence unavailable');
 // A result that arrives after History navigation cannot repopulate the workspace.
 storage.set('brain.pending.same-session',JSON.stringify({question:'ORIGINAL QUESTION',requestId:answer.request_id}));
 const late=page();let resolveResult;vm.runInContext('resumeOnRuntime=true',late.ctx);
 late.ctx.fetch=path=>path==='/api/runtime'?Promise.resolve(response(run('completed'))):path==='/api/history'?Promise.resolve(response({history:[]})):new Promise(resolve=>resolveResult=resolve);
 const recovery=vm.runInContext('refreshRuntime()',late.ctx);await new Promise(resolve=>setImmediate(resolve));
 await late.get('historyNav').onclick();resolveResult(response({history:[answer]}));await recovery;assert.equal(late.get('answer').children.length,0);assert.equal(paid,1);
 // 409 reconnects without overwriting the original saved question.
 storage.set('brain.pending.same-session',JSON.stringify({question:'ORIGINAL QUESTION',requestId:answer.request_id}));
 const duplicate=page();duplicate.get('question').value='SECOND QUESTION';duplicate.ctx.fetch=async path=>path==='/api/query'?{ok:false,status:409,json:async()=>({error:'A question is already running.'})}:response(run());
 await duplicate.get('queryForm').onsubmit({preventDefault(){}});await new Promise(resolve=>setImmediate(resolve));assert.equal(duplicate.get('question').value,'ORIGINAL QUESTION');assert.equal(duplicate.get('ask').disabled,true);assert.equal(JSON.parse(storage.get('brain.pending.same-session')).question,'ORIGINAL QUESTION');assert.equal(paid,1);
 // Same JS realm expiry/logout clears the old user's question before another login.
 vm.runInContext('expiredSession()',duplicate.ctx);assert.equal(duplicate.get('question').value,'');assert.equal(storage.has('brain.pending.same-session'),false);
 vm.runInContext("session={actor:'product_ops',csrf:'different'}",duplicate.ctx);duplicate.ctx.fetch=async()=>response({...run(),run:null});vm.runInContext('identity()',duplicate.ctx);assert.equal(duplicate.get('question').value,'');
 duplicate.get('question').value='PRIVATE CURRENT QUESTION';vm.runInContext('saveQuestion(null,"PRIVATE CURRENT QUESTION")',duplicate.ctx);duplicate.ctx.fetch=async path=>response(path==='/api/logout'?{}:{...run(),run:null});await duplicate.get('identity').children[1].onclick();assert.equal(duplicate.get('question').value,'');assert.equal(storage.has('brain.pending.different'),false);
 console.log('PASS: refresh reconnects original work, elapsed and question; one fresh authorized result fetch, no model retry; failure and cross-session isolation');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>clearTimeout(watchdog));
