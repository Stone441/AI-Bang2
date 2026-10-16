'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(){this.children=[];this.textContent='';this.hidden=false;this.open=false;}
 append(...items){this.children.push(...items);} replaceChildren(...items){this.children=items;this.textContent='';}
 setAttribute(){} querySelector(){return new Element();} showModal(){this.open=true;} close(){this.open=false;} focus(){}
}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const ctx=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},
 location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,URL,Date,fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8').replace(/boot\(\);\s*$/,''),ctx);
const text=e=>[e.textContent,...e.children.map(text)].join(' ');
const response=body=>({ok:true,status:200,json:async()=>body});
(async()=>{
 for(const value of [null,undefined,'','not-a-time']){ctx.value=value;assert.equal(vm.runInContext('sourceTime(value)',ctx),'Not recorded');}
 const source={source:'jira',configured:true,mode:'delegated',last_check_result:'failed',last_check_at:'2026-10-14T01:00:00Z',
  last_successful_check_at:'2026-10-14T00:59:00Z',snapshot_status:'unconfirmed',next_check_in_seconds:60.2};
 ctx.fetch=async()=>response({mode:'multi_mock_http_fake_model',model:'fake-extractive-v1',sources:[source],run:null});
 vm.runInContext("session={actor:'eng_b',csrf:'test'}",ctx);await vm.runInContext('refreshRuntime()',ctx);
 assert.match(text(get('runtimeSources')),/Latest check failed/);
 assert.match(text(get('runtimeSources')),/Last complete sync:/);
 assert.match(text(get('runtimeSources')),/Next check due in 61 s/);
 assert.doesNotMatch(text(get('runtimeSources')),/snapshot current|Recent source snapshot/);
 const sourceCard=get('runtimeSources').children[0],summary=sourceCard.children[0];sourceCard.open=true;
 source.mode='fixture';source.snapshot_status='current';await vm.runInContext('refreshRuntime()',ctx);
 assert.equal(get('runtimeSources').children[0],sourceCard,'Polling preserves disclosure identity and keyboard focus');
 assert.equal(sourceCard.children[0],summary);assert.equal(sourceCard.open,true);
 assert.match(text(get('runtimeSources')),/native update timing not measured/);
 assert.doesNotMatch(text(get('runtimeSources')),/Next check|Last complete sync|Recent source snapshot/);
 source.mode='delegated';source.snapshot_status='unconfirmed';source.last_check_result='complete';await vm.runInContext('refreshRuntime()',ctx);
 assert.match(text(get('runtimeSources')),/Snapshot needs a new check/);
 const evidence={evidence_id:'test@1',source:'jira',title:'Runbook',text:'Keep the limiting condition.',version:1,locator:{},source_updated_at:'2026-10-01T00:00:00Z',indexed_at:'2026-10-14T01:00:00Z',checked_at:'2026-10-14T01:00:05Z'};
 ctx.fetch=async()=>response(evidence);await vm.runInContext("preview('test@1')",ctx);
 const shown=text(get('previewBody'));
 for(const label of ['Source last edited:','Indexed locally:','Access and version checked:','Keep the limiting condition.'])assert.ok(shown.includes(label));
 assert.doesNotMatch(shown,/Invalid Date|1970/);
 ctx.fetch=async()=>({ok:false,status:403,json:async()=>({error:'Unavailable'})});await vm.runInContext("preview('test@1')",ctx);
 assert.equal(get('previewBody').children.length,0,'Denied previews remove old timestamps and content');
 console.log('PASS: distinct edit/index/check timestamps, failed/expired/fixture states, missing dates and denied-preview cleanup');
})().catch(error=>{console.error(error);process.exitCode=1;});
