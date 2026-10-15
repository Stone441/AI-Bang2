'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{constructor(tagName='div'){this.tagName=tagName;this.children=[];this.textContent='';}append(...items){this.children.push(...items);}replaceChildren(...items){this.children=items;this.textContent='';}setAttribute(){}querySelector(){return new Element();}focus(){}close(){}}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const ctx=vm.createContext({document:{getElementById:get,createElement:t=>new Element(t),querySelectorAll:()=>[]},location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8').replace(/boot\(\);\s*$/,''),ctx);
const all=e=>[e,...e.children.flatMap(all)],text=e=>all(e).map(n=>n.textContent).join(' ');
const e=(seq,event_type,payload={})=>({seq,event_type,payload,actor:'eng_a',request_id:'request',timestamp:'2026-10-14T01:00:00Z'});
ctx.rows=[e(8,'request_failed',{reason:'denied'}),e(1,'request_started',{query:'<script>bad</script>'}),
 e(2,'authorization_decided',{phase:'before_model',result:'allow'}),e(3,'authorization_decided',{phase:'before_model',result:'deny'}),
 e(4,'evidence_used',{stage:'prepared_for_answer'}),e(5,'model_dispatch_attempted',{stage:'answer'}),e(6,'model_output_rejected',{stage:'answer'})];
const timeline=vm.runInContext('auditTimeline(rows)',ctx),shown=text(timeline),items=timeline.children.at(-1).children;
assert.ok(shown.includes('ALLOW: 1 / DENY: 1'));assert.ok(shown.includes('Events 2–3'));
assert.ok(shown.includes('Evidence prepared (not proof of sending)'));assert.ok(shown.includes('Model output rejected'));
assert.ok(shown.includes('Missing stages are not assumed complete'));assert.doesNotMatch(shown,/Answer stored|reading confirmed|succeeded/);
assert.ok(text(items[0]).includes('Question received'));assert.ok(text(items.at(-1)).includes('Request stopped'));
assert.equal(ctx.rows[0].seq,8,'Timeline must not mutate raw event order');
ctx.rows=[e(7,'authorization_decided',{phase:'before_dispatch',result:'unknown'})];
const partial=text(vm.runInContext('auditTimeline(rows)',ctx));assert.ok(partial.includes('UNKNOWN: 1'));assert.doesNotMatch(partial,/Question received|Answer stored/);
const card=vm.runInContext('auditRequest(rows)',ctx);assert.ok(text(card).includes('Request timeline'));
assert.ok(!all(card).some(n=>['script','img'].includes(n.tagName)));
console.log('PASS: chronological loaded-event timeline, mixed decisions, partial/failure boundaries, raw order and safe text rendering');
