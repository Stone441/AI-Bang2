'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{constructor(){this.children=[];this.hidden=false;this.open=false;this.value='';this.textContent='';this.attributes={};}replaceChildren(...c){this.children=c;this.textContent='';}append(...c){this.children.push(...c);}querySelector(){return new Element();}setAttribute(k,v){this.attributes[k]=v;}focus(){}close(){this.open=false;}}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const ctx=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,URL,Date,performance:{now:()=>1000},setInterval:()=>1,clearInterval(){},fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8'),ctx);vm.runInContext("session={actor:'eng_b',csrf:'own'};health={auth_kind:'operator'};show('workspace')",ctx);
const response=body=>({ok:true,status:200,json:async()=>body});
const text=e=>[e.textContent,...e.children.map(text)].join(' ');
const summary={request_id:'a'.repeat(32),question:'MY ORIGINAL QUESTION',answered_at:'2026-10-10T05:50:00Z'};
const answer={...summary,model:'fake-extractive-v1',claims:[],evidence:[],uncertainties:[]};
const watchdog=setTimeout(()=>{console.error('FAIL: history test did not finish');process.exitCode=1;},3000);
(async()=>{
 let sourceReads=0;ctx.fetch=async path=>{assert.equal(path,'/api/history/recent');return response({history:[summary]});};
 await get('historyNav').onclick();assert.ok(text(get('other')).includes(summary.question));assert.ok(!text(get('other')).includes('Checking current access…'));assert.equal(sourceReads,0);
 const item=get('other').children[2],open=item.children[0],body=item.children[2];let finish;
 ctx.fetch=path=>{assert.equal(path,'/api/history?request_id='+summary.request_id);sourceReads++;return new Promise(resolve=>finish=resolve);};
 const opening=open.onclick();assert.equal(open.disabled,true);assert.ok(text(body).includes('Checking current access'));await open.onclick();assert.equal(sourceReads,1);
 finish(response({history:[answer]}));await opening;assert.ok(text(body).includes('Evidence-backed excerpts'));assert.equal(open.disabled,false);
 ctx.fetch=async()=>({ok:false,status:503,json:async()=>({error:'Current source check unavailable'})});await open.onclick();assert.equal(text(body).trim(),'Current source check unavailable');assert.equal(open.disabled,false);
 ctx.fetch=async()=>response({history:[]});await get('historyNav').onclick();assert.ok(text(get('other')).includes('No answers yet.'));
 ctx.fetch=async()=>{throw Error('Connection unavailable');};await get('historyNav').onclick();assert.ok(text(get('other')).includes('Connection unavailable'));
 vm.runInContext("renderStages({phase:'review',phases:['queued','retrieval','authorization','generation','review']})",ctx);
 assert.equal(get('progressSteps').children[3].attributes['aria-current'],'step');assert.ok(text(get('progressSteps').children[4]).includes('Not yet reported'));
 vm.runInContext("renderStages({phase:'generation',phases:['queued','retrieval','generation']})",ctx);assert.ok(text(get('progressSteps').children[1]).includes('Not yet reported'));assert.equal(get('progressSteps').children[2].attributes['aria-current'],'step');
 console.log('PASS: own question summaries load without source reads; explicit current-access answer opening, errors/empty states, no duplicate click; only actual observed stages');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>clearTimeout(watchdog));
