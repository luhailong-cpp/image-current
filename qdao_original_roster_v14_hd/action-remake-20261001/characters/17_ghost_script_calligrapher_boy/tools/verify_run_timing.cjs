const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const base=path.resolve(__dirname,'..');
const manifest=JSON.parse(fs.readFileSync(path.join(base,'preview/manifest-preview.json'),'utf8'));
const html=fs.readFileSync(path.join(base,'preview/index.html'),'utf8');
const code=[...html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/g)].filter(x=>!x[1].includes('application/json')).map(x=>x[2]).join('\n');
const ids=new Map();
class Element {
  constructor(){this.value='';this.style={};this.dataset={};this.children=[];this.classList={toggle(){}};this.tagName='DIV';}
  append(...xs){this.children.push(...xs);}
  replaceChildren(...xs){this.children=xs;}
  removeAttribute(){}
  click(){if(this.onclick)this.onclick();}
}
const get=id=>{if(!ids.has(id))ids.set(id,new Element());return ids.get(id);};
get('data').textContent=JSON.stringify(manifest);get('speed').value='1';get('mode').value='slots';
let now=0,next=null;
const context=vm.createContext({document:{getElementById:get,createElement:()=>new Element(),querySelectorAll:()=>[],addEventListener(){},activeElement:{tagName:'BODY'}},Option:function(t,v){this.text=t;this.value=v;},performance:{now:()=>now},setTimeout(fn,delay){next={fn,delay};return 1;},clearTimeout(){next=null;},console});
new vm.Script(code).runInContext(context);
const results=[];
for(const direction of manifest.actions.run.directions){
  now=0;vm.runInContext(`stop();action='run';direction='${direction}';frame=1;render();$('play').click();`,context);
  const frames=[1],delays=[];
  for(let n=0;n<16;n++){assert(next);const job=next;delays.push(job.delay);now+=job.delay;next=null;job.fn();frames.push(vm.runInContext('frame',context));}
  assert.deepStrictEqual(frames,[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,1]);assert.deepStrictEqual(delays,Array(16).fill(75));assert.strictEqual(now,1200);
  vm.runInContext('stop()',context);results.push({direction,cycleMs:now,frames,delaysMs:delays});
}
for(const action of ['hit','attack','cast'])assert.strictEqual(manifest.actions[action].duration_ms,{hit:40,attack:30,cast:45}[action]);
assert.strictEqual(manifest.slots.filter(s=>s.action==='run').length,128);
assert(manifest.slots.filter(s=>s.action==='run').every(s=>s.duration_ms===75));
assert(!html.includes('value="research"'));
const grounding=JSON.parse(fs.readFileSync(path.join(base,'preview/timing-grounding-data.json'),'utf8'));
assert.deepStrictEqual(grounding.cycles_ms,[1200]);
const report={checkedAt:new Date().toISOString(),normalRun:{frameMs:75,cycleMs:1200,uniform:true},directions:results,combatDurationsUnchanged:true,fullRunSlotsRetained:true,clientTested:false,visualPlaybackAccepted:false};
fs.writeFileSync(path.join(base,'review/timing-1200-verification.json'),JSON.stringify(report,null,2)+'\n');
console.log('PASS: all8run directions traverse01–16→01 at75ms each,1200ms total; combat unchanged; no fast/research options.');
