'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(tagName='div'){this.tagName=tagName;this.children=[];this.textContent='';this.value='';this.hidden=false;}
 append(...items){this.children.push(...items);} replaceChildren(...items){this.children=items;this.textContent='';}
 setAttribute(){} querySelector(){return new Element();} focus(){} close(){}
}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const ctx=vm.createContext({document:{getElementById:get,createElement:t=>new Element(t),querySelectorAll:()=>[]},
 location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8').replace(/boot\(\);\s*$/,''),ctx);
const nodes=e=>[e,...e.children.flatMap(nodes)],text=e=>nodes(e).map(n=>n.textContent).join(' ');
const event=(seq,type,payload={},actor='eng_b',request_id='same-request')=>({seq,event_type:type,payload,actor,request_id,timestamp:'2026-10-14T01:00:00Z'});
const entries=[event(1,'request_started',{query:'Can we launch?'}),
 event(2,'authorization_decided',{resource_id:'C-01',source:'confluence',phase:'before_model',result:'allow',application_viewer:'reviewer:blair',application_role:'engineer'}),
 event(3,'authorization_decided',{resource_id:'J-02',source:'jira',phase:'before_model',result:'deny'}),
 event(4,'evidence_used',{evidence_id:'C-01@1',stage:'prepared_for_review'}),
 event(5,'model_dispatch_attempted',{stage:'review'}),
 event(6,'response_committed',{response:{question:'Can we launch?',claims:[{text:'Pilot only. GA is not approved. <img src=x>',evidence_ids:['C-01@1']}],uncertainties:[]}}),
 event(7,'response_dispatch_attempted')];
const render=rows=>{ctx.rows=rows;return vm.runInContext('auditRequest(rows)',ctx);};
let card=render(entries),shown=text(card);
for(const expected of ['Can we launch?','reviewer:blair','Source identity: eng_b','ALLOW · confluence · C-01','DENY · jira · J-02',
 'Evidence prepared: C-01@1','Citations in stored answer: C-01@1','Model send attempts recorded: 1',
 'Answer stored','GA is not approved.','Delivery attempted; recipient reading is not established.','Original events · 7'])assert.ok(shown.includes(expected),expected);
assert.ok(!nodes(card).some(n=>['img','script'].includes(n.tagName)));
shown=text(render([event(1,'authorization_decided',{source:'jira',resource_id:'J-01',result:'allow',phase:'before_model'}),
 event(2,'authorization_decided',{source:'jira',resource_id:'J-01',result:'deny',phase:'before_dispatch'})]));
assert.match(shown,/jira · J-01 · ALLOW \/ DENY · 2 checks/,'Later denial never disappears in the grouped summary');
shown=text(render(entries.slice(0,4)));
assert.match(shown,/Outcome not present in loaded events/);assert.match(shown,/Model send attempts recorded: 0/);
assert.match(shown,/No stored-answer citations/);
shown=text(render([event(1,'request_started',{query:'Restricted question'}),event(2,'request_failed',{reason:'source_unconfirmed'})]));
assert.match(shown,/Request stopped/);assert.match(shown,/Stop reason: source_unconfirmed/);
shown=text(render([event(1,'request_failed',{reason:'model_output_rejected'}),event(2,'response_committed',{response:{answer_status:'evidence_only',claims:[]}})]));
assert.match(shown,/Source evidence only/);assert.match(shown,/Earlier stop event: model_output_rejected/);
shown=text(render([...entries,event(8,'request_failed',{reason:'delivery_unavailable'})]));
assert.match(shown,/Request stopped/);assert.match(shown,/Stop reason: delivery_unavailable/);
const response=body=>({ok:true,json:async()=>body});
(async()=>{
 vm.runInContext("session={actor:'auditor',csrf:'test'};health={auth_kind:'demo'}",ctx);
 get('auditNav').onclick();const form=get('other').children.find(e=>e.tagName==='form');
 const filters={actor:'eng_b',as_of:8,page_size:4};
 ctx.fetch=async()=>response({filters,as_of:8,total:8,events:entries.slice(0,4),next_after:4});
 await form.onsubmit({preventDefault(){}});
 const output=get('other').children.at(-1);assert.equal(output.children.filter(n=>n.className==='audit-request').length,1);
 assert.match(text(output),/Outcome not present in loaded events/);
 ctx.fetch=async()=>response({filters,as_of:8,total:8,events:[...entries.slice(4),event(8,'request_started',{query:'Another identity'},'eng_a')],next_after:null});
 await output.children.find(n=>n.tagName==='button').onclick();
 const cards=output.children.filter(n=>n.className==='audit-request');
 assert.equal(cards.length,2,'Same request ID under another actor never merges');
 assert.match(text(cards[0]),/Answer stored/);assert.doesNotMatch(cards[0].children[0].textContent,/Outcome not present/);
 assert.match(text(output),/8 of 8 matching events loaded/);
 // Reject a page from another snapshot, retaining the current summary and retry control.
 ctx.fetch=async()=>response({filters,as_of:8,total:8,events:entries.slice(0,4),next_after:4});await form.onsubmit({preventDefault(){}});
 ctx.fetch=async()=>response({filters,as_of:9,total:8,events:entries.slice(4),next_after:null});
 const next=output.children.find(n=>n.tagName==='button');await next.onclick();
 assert.match(get('status').textContent,/snapshot changed/);assert.equal(next.disabled,false);
 assert.ok(output.children.includes(next));assert.match(text(output),/4 of 8 matching events loaded/);
 console.log('PASS: request reconstruction, authorization, evidence/send distinctions, outcomes, pagination merge, identity isolation and stable snapshots');
})().catch(error=>{console.error(error);process.exitCode=1;});
