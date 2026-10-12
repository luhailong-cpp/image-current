const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'preview','timing-grounding.html'),'utf8'),source=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const els={};function el(){return {value:'',disabled:false,textContent:'',className:'',add(){},getContext(){return new Proxy({},{get:()=>()=>{}})}}}
const ctx={document:{querySelector:s=>els[s]??=(s==='#speed'?Object.assign(el(),{value:'1'}):el())},performance:{now:()=>0},requestAnimationFrame:()=>{},Option:function(){},Image:class{constructor(){this.complete=true;this.naturalWidth=1024}},console};
vm.createContext(ctx);vm.runInContext(source,ctx);const read=x=>vm.runInContext(x,ctx),checks=[];
read('last=100;elapsed=0;playing=true;tick(99)');assert.equal(read('index'),0);assert.equal(read('elapsed'),0);
for(const name of read("Object.keys(DATA.groups).filter(k=>k.startsWith('run/'))")){
 els['#group'].value=name;read('load()');
 const full=read('complete()');
 if(full){for(let i=0;i<16;i++){read('tick('+i*60+')');assert.equal(read('index'),i)}
 read('tick(959)');assert.equal(read('index'),15);read('tick(960)');assert.equal(read('index'),0);checks.push({group:name,frames:16,frameMs:60,cycleMs:960,wrapPassed:true})}
 else{assert.equal(read('playing'),false);assert.equal(read('slots.length'),16);checks.push({group:name,missingBlocked:true})}
}
els['#group'].value='run/S';read("DATA.groups['run/S']=DATA.groups['run/S'].slice(0,15);load()");assert.equal(read('playing'),false);assert.equal(read('slots.length'),16);assert.equal(els['#play'].disabled,true);read('tick(960)');assert.equal(read('index'),0);
assert(!html.includes('id="pacing"'));assert(!html.includes('480 ms'));assert(!html.includes('720ms/圈'));
const result={status:'passed',scope:'Actual generated player JavaScript executed in isolated DOM mock; frame duration, all16 time slots, first/last wrap and missing-frame autoplay guard verified. This is not visual or client acceptance.',checks,incompleteSyntheticTest:'passed',firstAnimationTimestampBeforeLoadCallback:'passed',oldSpeedControlsRemoved:true};
fs.writeFileSync(path.join(root,'preview','timing-verification.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
