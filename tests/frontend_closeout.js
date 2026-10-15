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
 vm.runInContext("session={actor:'eng_b',csrf:'test'};health={auth_kind:'reviewer'};show('workspace')",ctx);
 let readiness={ready:false,code:'model_price_review_required'};const calls=[];
 ctx.fetch=async path=>{calls.push(path);return response({model:'deepseek-flash-test',mode:'live_api',sources:[],run:null,model_readiness:readiness,query_readiness:readiness});};
 await vm.runInContext('refreshRuntime()',ctx);
 assert.equal(get('ask').disabled,true);assert.match(get('runtimeDetails').textContent,/operator price review/);
 readiness={ready:false,code:'source_unconfirmed'};
 ctx.fetch=async path=>{calls.push(path);return response({model:'deepseek-flash-test',mode:'live_api',sources:[],run:null,model_readiness:{ready:true},query_readiness:readiness});};
 await vm.runInContext('refreshRuntime()',ctx);
 assert.equal(get('ask').disabled,true);assert.match(get('runtimeDetails').textContent,/no question is resubmitted/);
 readiness={ready:true,code:null};await vm.runInContext('refreshRuntime()',ctx);assert.equal(get('ask').disabled,false);
 assert.ok(calls.every(path=>path==='/api/runtime'),'Readiness polling never submits a question');
 const viewer='reviewer:first:1111111111111111';ctx.auditViewer=viewer;
 vm.runInContext("session={actor:'application-auditor:inspector:1111111111111111',csrf:'audit',demo_role:'auditor',display_name:'Inspector',can_audit:true,audit_viewer_ids:[auditViewer],audit_resource_scope:'payment-service'}",ctx);
 const auditCalls=[];ctx.fetch=async(path,options)=>{auditCalls.push([path,options?.body&&JSON.parse(options.body)]);return response(path==='/api/runtime'?{model:'not_applicable',mode:'application_audit',sources:[],run:null}:{filters:{application_identity:viewer},events:[],total:0,as_of:0,next_after:null});};
 vm.runInContext('identity()',ctx);
 assert.equal(get('auditNav').hidden,false);assert.equal(get('sourcesNav').hidden,true);
 assert.equal(get('workspace').hidden,true);assert.equal(get('ask').disabled,true);
 const form=get('other').children.find(e=>e.attributes&&e.attributes['aria-label']===undefined&&e.className==='audit-form');
 await form.onsubmit({preventDefault(){}});
 assert.deepEqual(auditCalls.find(c=>c[0]==='/api/audit/events')[1],{application_identity:viewer,resource_scope:'payment-service',page_size:50});
 assert.ok(auditCalls.every(c=>c[0]!=='/api/query'));
 console.log('PASS: price/source readiness without automatic queries and configured scoped auditor navigation');
})().catch(error=>{console.error(error);process.exitCode=1;});
