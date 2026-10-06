'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
  constructor(tag='div'){this.tagName=tag;this.children=[];this.textContent='';this.value='';this.hidden=false;this.open=false;}
  replaceChildren(...children){this.children=children;this.textContent='';for(const c of children)c.parent=this;}
  append(...children){this.children.push(...children);for(const c of children)c.parent=this;}
  querySelector(){return new Element('button');}
  setAttribute(){} focus(){} close(){this.open=false;} showModal(){this.open=true;}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(c=>c!==this);}
}
const elements=new Map();const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const ctx=vm.createContext({document:{getElementById:get,createElement:t=>new Element(t),querySelectorAll:()=>[]},location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8'),ctx);
const text=e=>[e.textContent,...e.children.map(text)].join(' ');
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};};
const response=data=>({ok:true,json:async()=>data});
const result=(label,next=null)=>({filters:{actor:'eng_b',as_of:8},as_of:8,total:1,next_after:next,events:[{seq:1,actor:'eng_b',timestamp:'2026-10-05',event_type:'request_started',request_id:label,payload:{query:label}}]});
(async()=>{
  vm.runInContext("session={actor:'auditor',csrf:'fixture'};health={auth_kind:'demo'}",ctx);
  get('auditNav').onclick();
  const form=get('other').children.find(c=>c.tagName==='form');
  const one=deferred(),two=deferred();let calls=0;ctx.fetch=()=>++calls===1?one.promise:two.promise;
  const p1=form.onsubmit({preventDefault(){}}),p2=form.onsubmit({preventDefault(){}});
  two.resolve(response(result('NEW_QUERY')));await p2;
  one.resolve(response(result('OLD_QUERY')));await p1;
  assert.match(text(get('other')),/NEW_QUERY/);
  assert.doesNotMatch(text(get('other')),/OLD_QUERY/);
  ctx.fetch=async()=>response(result('INITIAL_PAGE',1));
  await form.onsubmit({preventDefault(){}});
  const output=get('other').children.at(-1),next=output.children.find(c=>c.tagName==='button');
  const delayedPage=deferred();let pageCalls=0;
  ctx.fetch=(path,options)=>{
    if(path==='/api/audit/events'){
      pageCalls++;const body=JSON.parse(options.body);
      assert.equal(body.as_of,8);assert.equal(body.after,1);
      return delayedPage.promise;
    }
    return Promise.resolve(response(result('LATEST_SCOPE')));
  };
  const pending=next.onclick();await next.onclick();assert.equal(pageCalls,1);
  await form.onsubmit({preventDefault(){}});
  delayedPage.resolve(response(result('STALE_PAGE')));await pending;
  assert.match(text(get('other')),/LATEST_SCOPE/);
  assert.doesNotMatch(text(get('other')),/INITIAL_PAGE|STALE_PAGE/);
  ctx.event={seq:9,event_type:'response_committed',request_id:'audit-test',actor:'eng_b',timestamp:'now',payload:{response:{model:'fake',claims:[{text:'<img src=x onerror=bad> source text'}]}}};
  const rendered=vm.runInContext('auditEvent(event)',ctx);
  assert.match(text(rendered),/<img src=x onerror=bad> source text/);
  const tags=e=>[e.tagName,...e.children.flatMap(tags)];
  assert.ok(!tags(rendered).includes('img'));assert.ok(!tags(rendered).includes('script'));
  ctx.event={seq:10,event_type:'authorization_decided',request_id:'audit-test',actor:'eng_b',timestamp:'now',payload:{source:'jira',resource_id:'jira:issue',result:'allow',phase:'before_model',version:9007199254740993}};
  const versionEvent=text(vm.runInContext('auditEvent(event)',ctx));
  assert.match(versionEvent,/Exact version is retained by the backend/);
  assert.match(versionEvent,/Exact integer unavailable in browser/);
  assert.doesNotMatch(versionEvent,/9007199254740992/);
  for(const stage of ['sent_to_model','sent_to_review','prepared_for_answer','prepared_for_review']){
    ctx.event={seq:11,event_type:'evidence_used',actor:'eng_b',payload:{stage,evidence_id:'test@1'}};
    const renderedStage=text(vm.runInContext('auditEvent(event)',ctx));
    assert.match(renderedStage,/Prepared for.*not proof of sending/);
    assert.doesNotMatch(renderedStage,/Sent to answer model|Sent to evidence review/);
  }
  for(const [type,label] of [['model_dispatch_intent','send intent persisted'],['model_dispatch_attempted','send attempted'],['model_usage_received','Validated model usage received']]){
    ctx.event={seq:12,event_type:type,actor:'eng_b',payload:{stage:'answer'}};
    assert.ok(text(vm.runInContext('auditEvent(event)',ctx)).includes(label));
  }
  // Navigation invalidates an otherwise fresh inquiry too.
  const late=deferred();ctx.fetch=()=>late.promise;
  const querying=form.onsubmit({preventDefault(){}});get('workspaceNav').onclick();
  late.resolve(response(result('AFTER_NAVIGATION')));await querying;
  assert.doesNotMatch(text(get('other')),/AFTER_NAVIGATION/);
  console.log('PASS: audit query races, stale pagination, repeated clicks, escaped payloads, version precision notice and navigation guards');
})().catch(e=>{console.error(e);process.exitCode=1;});
