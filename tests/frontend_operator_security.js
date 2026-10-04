'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
  constructor(){this.children=[];this.hidden=false;this.open=false;this.value='';this.textContent='';}
  replaceChildren(...children){this.children=children;this.textContent='';}
  append(...children){this.children.push(...children);}
  querySelector(){return new Element();}
  setAttribute(){}
  focus(){}
  close(){this.open=false;}
  showModal(){this.open=true;}
}
const elements=new Map();const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const context=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},
  location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,
  fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8'),context);
function seed(){for(const id of ['answer','other','previewBody'])get(id).append(new Element());get('preview').open=true;}
(async()=>{
  vm.runInContext("session={actor:'eng_b',csrf:'synthetic'};health={auth_kind:'operator'}",context);
  seed();get('workspaceNav').onclick();
  assert.equal(get('answer').children.length,0);assert.equal(get('other').children.length,0);
  seed();context.fetch=async()=>({ok:false,json:async()=>({error:'Unavailable'})});
  await vm.runInContext("preview('jira:10013@1')",context);
  assert.equal(get('answer').children.length,0);assert.equal(get('previewBody').children.length,0);
  assert.equal(get('preview').open,false);assert.equal(get('other').children.length,1);
  assert.match(get('status').textContent,/unavailable/);
  seed();context.fetch=()=>new Promise(()=>{});
  get('queryForm').onsubmit({preventDefault(){}});
  assert.equal(get('answer').children.length,0);assert.equal(get('other').children.length,0);
  seed();get('historyNav').onclick();
  assert.equal(get('answer').children.length,0);
  function visibleText(element){return [element.textContent,...element.children.map(visibleText)].join(' ');}
  vm.runInContext("renderAnswer({model:'deepseek-flash-evidence-selection-v1',claims:[],evidence:[{source:'drive',title:'Synthetic',evidence_id:'drive:test@1',version:1,locator:{},source_updated_at:'2026-10-05',indexed_at:'2026-10-05'}],uncertainties:[],request_id:'synthetic'})",context);
  assert.match(visibleText(get('answer')),/LIVE MODEL · SOURCE EXCERPTS/);
  assert.doesNotMatch(visibleText(get('answer')),/FAKE MODEL/);
  vm.runInContext("renderAnswer({model:'deepseek-flash-evidence-selection-v1',claims:[],evidence:[],uncertainties:[],request_id:'synthetic'})",context);
  assert.match(visibleText(get('answer')),/NO MODEL CALL/);
  assert.doesNotMatch(visibleText(get('answer')),/LIVE MODEL · SOURCE EXCERPTS/);
  vm.runInContext("renderAnswer({model:'fake-extractive-v1',claims:[],evidence:[],uncertainties:[],request_id:'synthetic'})",context);
  assert.match(visibleText(get('answer')),/FAKE MODEL/);
  console.log('PASS: workspace navigation, denied preview, pending query and history navigation discard stale views');
})().catch(e=>{console.error(e);process.exitCode=1;});
