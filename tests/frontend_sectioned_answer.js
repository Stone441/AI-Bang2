'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(tagName='div'){this.tagName=tagName;this.children=[];this.textContent='';this.hidden=false;}
 append(...items){this.children.push(...items);} replaceChildren(...items){this.children=items;this.textContent='';}
 setAttribute(){} querySelector(){return new Element();} close(){} focus(){}
}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const ctx=vm.createContext({document:{getElementById:get,createElement:t=>new Element(t),querySelectorAll:()=>[]},
 location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,URL,Date,fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8').replace(/boot\(\);\s*$/,''),ctx);
const nodes=e=>[e,...e.children.flatMap(nodes)],text=e=>nodes(e).map(n=>n.textContent).join(' ');
const claim={text:'Fix done; general release is not approved.',evidence_ids:['J@1'],supports:[{evidence_id:'J@1',quote:'Code completion does not approve general release.'}]};
ctx.answer={request_id:'part-test',question:'Is the fix complete and when is GA?',model:'deepseek-flash-grounded-synthesis-by-part-v1',
 mode:'fixture_mock_model_synthesis',answer_kind:'sectioned_synthesis',claim_format:'grounded_synthesis_v1',review_status:'accepted',
 model_call:{called:true},model_review:{called:true},claims:[claim],evidence:[{evidence_id:'J@1',title:'Fix status',source:'jira',version:1,locator:{}}],uncertainties:[],
 answer_parts:[{question:'Is the fix complete',status:'supported',claim_indices:[0]},{question:'when is GA',status:'insufficient',claim_indices:[]}]};
vm.runInContext('renderAnswer(answer)',ctx);
let sections=nodes(get('answer')).filter(e=>e.tagName==='section');
assert.equal(sections.length,2);assert.equal(sections[0].children[0].textContent,'Is the fix complete');
assert.equal(nodes(get('answer')).filter(e=>e.textContent===claim.text).length,1,'Conclusions are not duplicated as background excerpts');
assert.match(text(sections[0]),/general release is not approved/);assert.match(text(sections[0]),/Exact supporting quotes/);
assert.match(text(sections[1]),/provided evidence is insufficient/);assert.match(text(sections[1]),/does not establish.*does not exist/);
assert.match(text(get('answer')),/MOCK MODEL OUTPUTS/);assert.doesNotMatch(text(get('answer')),/LIVE MODEL/);
vm.runInContext('preview=id=>{globalThis.opened=id}',ctx);
nodes(sections[0]).find(e=>e.tagName==='button').onclick();assert.equal(ctx.opened,'J@1');
// A grounded explanation of an unavailable value is visible and cited, but never counts as answered.
ctx.answer.claims.push({text:'No general release date is confirmed.',evidence_ids:['J@1'],supports:[{evidence_id:'J@1',quote:'No general release date is confirmed.'}]});
ctx.answer.answer_parts[1].gap_claim_indices=[1];
vm.runInContext('renderAnswer(answer)',ctx);
sections=nodes(get('answer')).filter(e=>e.tagName==='section');
assert.match(text(get('answer')),/Partial answer/);
assert.match(text(sections[1]),/provided evidence is insufficient/);
assert.match(text(sections[1]),/No general release date is confirmed/);
assert.equal(nodes(sections[1]).filter(e=>e.tagName==='button').length,1);
nodes(sections[1]).find(e=>e.tagName==='button').onclick();assert.equal(ctx.opened,'J@1');
ctx.answer.answer_parts=[ctx.answer.answer_parts[1]];
ctx.answer.claims=[ctx.answer.claims[1]];ctx.answer.answer_parts[0].gap_claim_indices=[0];
vm.runInContext('renderAnswer(answer)',ctx);
assert.match(text(get('answer')),/Insufficient evidence/);
assert.doesNotMatch(text(get('answer')),/Partial answer/);
ctx.answer.answer_status='evidence_only';vm.runInContext('renderAnswer(answer)',ctx);
assert.doesNotMatch(text(get('answer')),/Each part is answered separately/);
assert.ok(!nodes(get('answer')).some(e=>e.tagName==='h3'&&e.textContent==='when is GA'),'Failed output does not retain per-part conclusions');
ctx.answer.answer_status=undefined;ctx.answer.claims=[];ctx.answer.answer_parts=[{question:ctx.answer.question,status:'insufficient',claim_indices:[]}];
vm.runInContext('renderAnswer(answer)',ctx);
assert.match(text(get('answer')),/Insufficient evidence/);
assert.doesNotMatch(text(get('answer')),/Evidence-backed answer|Expand its supporting quotes|Key references/);
ctx.answer={unavailable:true,message:'Unavailable'};vm.runInContext('renderAnswer(answer)',ctx);
assert.doesNotMatch(text(get('answer')),/general release|GA|Fix status/);
console.log('PASS: concise per-part conclusions, exact quotes, scoped insufficient notices, citation actions, mock labels and revoked/failed cleanup');
