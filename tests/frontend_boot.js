'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{constructor(){this.children=[];this.hidden=false;this.open=false;this.value='';this.textContent='';}replaceChildren(...c){this.children=c;}append(...c){this.children.push(...c);}querySelector(){return new Element();}close(){}setAttribute(){}focus(){}}
async function check({status,hash='',loginStatus=200}){
 const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};const calls=[];
 const ctx=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},location:{hash,pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,URL,Date,setInterval:()=>1,clearInterval(){},fetch:async path=>{calls.push(path);const code=path==='/api/session'?status:path==='/api/operator/login'?loginStatus:200;return {ok:code===200,status:code,json:async()=>path==='/api/health'?{auth_kind:'operator',login_path:'/api/operator/login',mode:'mock_http'}:path==='/api/runtime'?{sources:[],run:null}:{actor:'eng_b',csrf:'test'}};}});
 vm.runInContext(fs.readFileSync('web/app.js','utf8').replace(/boot\(\);\s*$/,''),ctx);await vm.runInContext('boot()',ctx);return {get,calls};
}
(async()=>{
 let r=await check({status:403});assert.match(r.get('status').textContent,/Sessions expire after 1 hour/);assert.ok(!r.calls.includes('/api/operator/login'));
 r=await check({status:503,hash:'#ticket=synthetic'});assert.match(r.get('status').textContent,/Could not connect/);assert.ok(!r.calls.includes('/api/operator/login'));
 r=await check({status:200,hash:'#ticket=already-used'});assert.equal(r.get('workspace').hidden,false);assert.ok(!r.calls.includes('/api/operator/login'));
 r=await check({status:403,hash:'#ticket=expired',loginStatus:403});assert.match(r.get('status').textContent,/one-time operator link/);assert.equal(r.calls.filter(p=>p==='/api/operator/login').length,1);assert.ok(!r.calls.includes('/api/query'));
 console.log('PASS: valid refresh session wins over used ticket; expired session, invalid link and transient service failure distinguished; no query');
})().catch(err=>{console.error(err);process.exitCode=1;});
