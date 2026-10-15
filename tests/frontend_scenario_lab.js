'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{constructor(tagName='div'){this.tagName=tagName;this.children=[];this.textContent='';}append(...x){this.children.push(...x);}replaceChildren(...x){this.children=x;this.textContent='';}}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const ctx=vm.createContext({document:{getElementById:get,createElement:t=>new Element(t)},fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/scenario_lab.js','utf8').replace(/load\(\);\s*$/,''),ctx);
const nodes=e=>[e,...e.children.flatMap(nodes)],text=e=>nodes(e).map(n=>n.textContent).join(' ');
ctx.sample={next_action:'baseline',steps:[],csrf:'x'};vm.runInContext('state=sample;render()',ctx);
let buttons=nodes(get('controls')).filter(n=>n.tagName==='button');assert.equal(buttons.filter(b=>!b.disabled).length,1);
assert.ok(text(get('status')).includes('Read the current runbook'));
ctx.sample={next_action:null,failure:null,steps:[{action:'revoke',passed:true,checks:{old_history_hidden:true,old_preview_blocked:true},source_events:[],finished_at:'2026-10-14',request_id:'r',answer:{evidence:[{title:'<img src=x>',version:2,text:'<script>bad</script>'}]}}]};
vm.runInContext('state=sample;render()',ctx);assert.ok(text(get('results')).includes('earlier employee answer is hidden'));
assert.ok(text(get('results')).includes('not employee History'));assert.ok(!nodes(get('results')).some(n=>['img','script'].includes(n.tagName)));
assert.ok(text(get('status')).includes('Rehearsal complete'));
vm.runInContext("state.failure='A check failed';render()",ctx);assert.ok(text(get('status')).includes('Lab stopped'));
console.log('PASS: ordered lab actions, observed checks, operator transcript boundary, stopped state and safe text rendering');
