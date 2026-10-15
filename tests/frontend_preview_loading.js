'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element{
 constructor(){this.children=[];this.open=false;this.textContent='';}
 replaceChildren(...c){this.children=c;this.textContent='';} append(...c){this.children.push(...c);}
 setAttribute(){} querySelector(){return new Element();} close(){this.open=false;} showModal(){this.open=true;} focus(){}
}
const elements=new Map(),get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
const ctx=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[]},location:{hash:'',pathname:'/',search:''},history:{replaceState(){}},URLSearchParams,URL,Date,fetch:()=>new Promise(()=>{})});
vm.runInContext(fs.readFileSync('web/app.js','utf8').replace(/boot\(\);\s*$/,''),ctx);
vm.runInContext("session={actor:'eng_b',csrf:'x'}",ctx);
const text=e=>e.textContent+' '+e.children.map(text).join(' ');
const watchdog=setTimeout(()=>{console.error('FAIL: pending preview test');process.exit(1);},3000);
(async()=>{
 let resolve;ctx.fetch=path=>path==='/api/session'?Promise.resolve({status:200}):new Promise(r=>resolve=r);
 const pending=vm.runInContext("preview('D-02@1')",ctx);
 assert.equal(get('preview').open,true,'Drawer opens before network resolves');
 assert.match(text(get('previewBody')),/Checking current access/);
 assert.doesNotMatch(text(get('previewBody')),/PRIVATE SOURCE/);
 get('preview').oncancel();get('preview').close();
 resolve({ok:true,json:async()=>({title:'PRIVATE SOURCE',text:'late content',locator:{}})});await pending;
 assert.equal(get('preview').open,false);assert.doesNotMatch(text(get('previewBody')),/late content|PRIVATE/);
 const second=vm.runInContext("preview('D-02@1')",ctx);
 resolve({ok:true,json:async()=>({title:'D-02',text:'checked content',locator:{}})});await second;
 assert.equal(get('preview').open,true);assert.match(text(get('previewBody')),/checked content/);
 const denied=vm.runInContext("preview('D-02@1')",ctx);
 assert.doesNotMatch(text(get('previewBody')),/checked content/);
 resolve({ok:false,status:403,json:async()=>({error:'denied'})});await denied;
 assert.equal(get('preview').open,false);assert.doesNotMatch(text(get('previewBody')),/checked content/);
 clearTimeout(watchdog);
 console.log('PASS: immediate loading, no unchecked text, late-response cancellation, success and denied cleanup');
})().catch(e=>{console.error(e);process.exitCode=1;});
