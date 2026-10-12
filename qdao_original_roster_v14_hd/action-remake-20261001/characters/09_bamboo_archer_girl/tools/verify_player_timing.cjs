const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(__dirname,'..');let tick,now=0;
class Element{constructor(id){this.id=id;this.children=[];this.style={};this.value='';this.checked=false;this.textContent='';this.classList={toggle(){}};}append(e){this.children.push(e)}replaceChildren(){this.children=[]}get options(){return this.children}querySelector(){return this.body??=new Element('tbody')}getContext(){return new Proxy({},{get:()=>()=>{}})}}
const ids=['dark','light','sequence','speed','runCycle','displaySize','groundY','summary','inventoryNotice','anchorInfo','groups','missingList','slots','timeline','position','slotInfo','guides','playStatus','playOne','playAll','pause','prev','next'];
const el=Object.fromEntries(ids.map(x=>[x,new Element(x)]));el.speed.value='1';el.runCycle.value='1200';el.groundY.value='940';el.displaySize.value='256';
const stages=[new Element('stage0'),new Element('stage1')];
const ctx={window:{},document:{getElementById:id=>el[id],createElement:t=>new Element(t),querySelectorAll:s=>s==='.stage'?stages:[]},performance:{now:()=>now},requestAnimationFrame:fn=>tick=fn,Image:class{},console};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(root,'preview/data.js'),'utf8'),ctx);vm.runInContext(fs.readFileSync(path.join(root,'preview/player.js'),'utf8'),ctx);
assert.equal(el.sequence.children.length,14);
assert.ok(stages.every(x=>x.style.width==='256px'));
const sequences=ctx.window.BAMBOO_PREVIEW.sequences;
const html=fs.readFileSync(path.join(root,'preview/index.html'),'utf8');
const timingSelect=html.match(/<select id="runCycle"[\s\S]*?<\/select>/)[0];
assert.deepEqual([...timingSelect.matchAll(/value="(\d+)"/g)].map(x=>Number(x[1])),[1200]);
const checked=[];
for(let index=0;index<sequences.length;index++){
 const seq=sequences[index];const ms=seq.action==='run'?75:({hit:40,attack:30,cast:45}[seq.action]);
 assert.equal(seq.ms,ms);el.sequence.value=String(index);el.sequence.onchange();
 for(const speed of [1,.25]){
  el.speed.value=String(speed);el.speed.onchange();el.timeline.value='0';el.timeline.oninput();now=0;el.playOne.onclick();
  const period=ms/speed;
  for(let step=0;step<seq.count*3;step++){
   tick(step*period+.01);assert.match(el.position.textContent,new RegExp(`· ${step%seq.count+1}/${seq.count} ·`));
   tick((step+1)*period-.01);assert.match(el.position.textContent,new RegExp(`· ${step%seq.count+1}/${seq.count} ·`));
  }
  tick(seq.count*period*3+.01);assert.match(el.position.textContent,new RegExp(`· 1/${seq.count} ·`));el.pause.onclick();
 }
 checked.push({sequence:seq.label,frameMs:ms,cycleMs:ms*seq.count});
}
el.speed.value='1';el.speed.onchange();el.sequence.value='0';el.sequence.onchange();el.timeline.value='0';el.timeline.oninput();now=0;el.playAll.onclick();
let offset=0;for(const seq of sequences){tick(offset+.01);assert.match(el.position.textContent,new RegExp(`· 1/${seq.count} ·`));offset+=seq.count*seq.ms}tick(offset+.01);assert.match(el.position.textContent,/受击 E · 1\/6/);
const report={passed:true,sequences:checked,slots:196,runFrameMs:75,runCycleMs:1200,slowFrameMs:300,slowCycleMs:4800,threeLoopsAllBoundariesChecked:true,oldRunSpeedOptionsRemoved:true,combatTimingsUnchanged:true,method:'VM mock DOM only; no browser navigation or visual dynamic approval'};
fs.writeFileSync(path.join(root,'audit/player-timing-1200-check.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
