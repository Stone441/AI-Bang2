'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{constructor(){this.children=[];this.hidden=false;this.value='';this.textContent='';this.button=null;this.label=null;}replaceChildren(...c){this.children=c;}append(...c){this.children.push(...c);}querySelector(s){if(s==='button')return this.button||(this.button=new Element());if(s==='label')return this.label||(this.label=new Element());return new Element();}setAttribute(){}close(){}focus(){}}
const es=new Map(),get=id=>{if(!es.has(id))es.set(id,new Element());return es.get(id);};
let logged=false,requests=[];
const ctx=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,URL,Date,setInterval:()=>1,clearInterval(){},fetch:async(path,options={})=>{
 requests.push([path,options.body]);
 const status=path==='/api/session'&&!logged?403:200;
 const body=path==='/api/health'?{auth_kind:'reviewer',login_path:'/api/reviewer/login',mode:'fixture_fake_model'}:path==='/api/runtime'?{sources:[],run:null,query_admission:{allowed:true,human_unlimited:true,attempts_used:70,settlement_remaining_usd:.98,settlement_limit_usd:1}}:{actor:'reviewer:engineer:1111111111111111',demo_role:'eng_b',display_name:'Blair',csrf:'fixture'};
 if(path==='/api/reviewer/login')logged=true;
 return {ok:status===200,status,json:async()=>body};
}});
(async()=>{
 vm.runInContext(fs.readFileSync('web/app.js','utf8').replace(/boot\(\);\s*$/,''),ctx);
 await vm.runInContext('boot()',ctx);
 assert.equal(get('reviewerCredentials').hidden,false);assert.equal(get('user').hidden,true);
 assert.equal(get('loginForm').querySelector('button').disabled,false);
 assert.equal(get('modeBadge').textContent,'SYNTHETIC / FAKE MODEL');
 get('reviewerUsername').value='engineer_blair';get('reviewerPassword').value='fixture-password';
 await get('loginForm').onsubmit({preventDefault(){}});
 assert.equal(get('reviewerPassword').value,'');assert.equal(get('workspace').hidden,false);
 assert.equal(get('identity').children[0].textContent,'Blair · Engineer');
 const sent=JSON.parse(requests.find(r=>r[0]==='/api/reviewer/login')[1]);
 assert.deepEqual(sent,{username:'engineer_blair',password:'fixture-password'});
 await vm.runInContext('refreshRuntime()',ctx);
 assert.equal(get('trialStatus').hidden,true);assert.equal(get('trialStatus').textContent,'');assert.equal(get('ask').disabled,false);
 vm.runInContext('renderAdmission({allowed:false,human_unlimited:true})',ctx);assert.equal(get('trialStatus').hidden,false);assert.match(get('trialStatus').textContent,/temporarily unavailable/);assert.equal(get('ask').disabled,true);
 vm.runInContext('renderAdmission({allowed:true,human_unlimited:true})',ctx);assert.equal(get('trialStatus').hidden,true);assert.equal(get('ask').disabled,false);
 assert.ok(!requests.some(r=>r[0]==='/api/query'));
 console.log('PASS: password form, server role label, cleared secret, explicit fixture mode, unlimited human count with budget; no automatic query');
})().catch(e=>{console.error(e);process.exitCode=1;});
