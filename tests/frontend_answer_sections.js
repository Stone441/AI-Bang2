'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(tagName='div'){this.tagName=tagName;this.children=[];this.textContent='';this.hidden=false;}
 append(...items){this.children.push(...items);} replaceChildren(...items){this.children=items;this.textContent='';}
 setAttribute(){} querySelector(){return new Element();} close(){} focus(){this.focused=true;} scrollIntoView(){this.scrolled=true;}
}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const ctx=vm.createContext({document:{getElementById:get,createElement:t=>new Element(t),querySelectorAll:()=>[]},
 location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,URL,Date,fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8').replace(/boot\(\);\s*$/,''),ctx);
const nodes=e=>[e,...e.children.flatMap(nodes)];
const evidence=id=>({evidence_id:id,title:id==='C@1'?'Release scope':'Issue status',source:id==='C@1'?'confluence':'jira',locator:{},version:1});
ctx.answer={request_id:'test',question:'Can we launch?',answer_kind:'reviewed_excerpts',model:'fake-extractive-v1',
 evidence:['C@1','J@1'].map(evidence),uncertainties:['General availability is not established.'],claims:[
 {text:'Pilot approved.',evidence_ids:['C@1']},{text:'Only for trial customers. <img src=x>',evidence_ids:['C@1']},
 {text:'Fix is Done.',evidence_ids:['J@1']},{text:'General availability NOT approved.',evidence_ids:['C@1']}]};
vm.runInContext('renderAnswer(answer)',ctx);
let sections=nodes(get('answer')).filter(e=>e.tagName==='section');
assert.equal(sections.length,3,'Only adjacent citations can merge; never reorder evidence');
const texts=sections.flatMap(s=>nodes(s).filter(e=>e.className==='claim').map(e=>e.children[0].textContent));
assert.deepEqual(texts,ctx.answer.claims.map(c=>c.text),'Preserve all text and qualifications verbatim');
assert.ok(sections.every(s=>s.children.filter(e=>e.tagName==='details').every(e=>e.open!==true)),'Original passages are collapsed by default');
assert.equal(sections[0].children.filter(e=>e.tagName==='button').length,1);
assert.equal(sections[0].children[0].textContent,'Release scope');
assert.ok(!nodes(get('answer')).some(e=>e.tagName==='img'));
vm.runInContext("preview=id=>{globalThis.opened=id}",ctx);
sections[0].children.find(e=>e.tagName==='button').onclick();assert.equal(ctx.opened,'C@1');
// Topics are navigation over existing text, never generated conclusions or hidden filters.
ctx.answer.question='What caused the incident, is the fix done, and can we offer it to all customers?';
vm.runInContext('renderAnswer(answer)',ctx);
let guide=nodes(get('answer')).find(e=>e.className==='answer-guide');
let entries=guide.children.filter(e=>e.className==='answer-topic');
assert.equal(entries.length,2,'Work status and release scope match the supplied passages');
assert.ok(guide.children.some(e=>e.textContent.startsWith('Incident cause: no matching passage identified here.')));
assert.ok(!nodes(guide).some(e=>e.textContent==='Fix is Done.'),'Guide never invents a short factual conclusion');
const work=entries.find(e=>e.children[0].textContent.startsWith('Work status'));
work.children.find(e=>e.tagName==='button').onclick();
sections=nodes(get('answer')).filter(e=>e.tagName==='section');
assert.equal(sections[1].scrolled,true);assert.equal(sections[1].focused,true);
const release=entries.find(e=>e.children[0].textContent.startsWith('Release scope'));
assert.equal(release.children.filter(e=>e.tagName==='button').length,2,'Every matching source section remains reachable');
release.children.filter(e=>e.tagName==='button')[1].onclick();assert.equal(sections[2].scrolled,true);
assert.deepEqual(sections.flatMap(s=>nodes(s).filter(e=>e.className==='claim').map(e=>e.children[0].textContent)),ctx.answer.claims.map(c=>c.text));
ctx.answer.question='事故原因是什么？修复完成了吗？可以向所有客户开放吗？';vm.runInContext('renderAnswer(answer)',ctx);
assert.ok(nodes(get('answer')).some(e=>e.textContent.startsWith('Release scope ·')),'Chinese questions can navigate English evidence');
ctx.answer.question='Who owns the invoice?';vm.runInContext('renderAnswer(answer)',ctx);
assert.equal(nodes(get('answer')).find(e=>e.className==='answer-guide').hidden,true,'Unrecognized questions retain the normal full answer');
ctx.answer.answer_status='evidence_only';vm.runInContext('renderAnswer(answer)',ctx);
assert.ok(nodes(get('answer')).some(e=>e.textContent==='Source answer was blocked'));
assert.ok(!nodes(get('answer')).some(e=>e.className==='answer-guide'),'Failed review has no answer topic guide');
assert.equal(nodes(get('answer')).filter(e=>e.tagName==='section').length,0,'Rejected historical output cannot become answer prose');
assert.ok(nodes(get('answer')).some(e=>e.textContent==='Other checked evidence'),'Checked evidence remains available for inspection');
delete ctx.answer.answer_status;
ctx.answer.claim_format='grounded_synthesis_v1';vm.runInContext('renderAnswer(answer)',ctx);
assert.equal(nodes(get('answer')).filter(e=>e.tagName==='section').length,4,'Synthesis claims keep individual supports');
ctx.answer={unavailable:true,message:'Unavailable'};vm.runInContext('renderAnswer(answer)',ctx);
assert.equal(nodes(get('answer')).filter(e=>e.tagName==='section').length,0,'Revoked answers remove prior text');
assert.ok(!nodes(get('answer')).some(e=>e.className==='answer-guide'),'Revocation removes topic titles too');
console.log('PASS: exact source grouping, topic navigation, missing topics, Chinese questions, citation actions and revoked/failed history');
