const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'..'),html=fs.readFileSync(path.join(root,'preview/all-directions.html'),'utf8'),source=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const images=[],els={},cards=[];
function element(){return {value:'',textContent:'',className:'',append(card){cards.push(card)},getContext(){return {clearRect(){},drawImage(){}}},querySelector(selector){return this.children[selector]??=element()},children:{}}}
const ctx={document:{querySelector:s=>els[s]??=Object.assign(element(),{value:s==='#speed'?'1':''}),createElement:()=>element()},performance:{now:()=>100},requestAnimationFrame(){},Image:class{constructor(){this.complete=true;this.naturalWidth=1024;images.push(this)}}};
vm.createContext(ctx);vm.runInContext(source,ctx);const read=x=>vm.runInContext(x,ctx);
assert.equal(images.length,128);images.forEach(im=>im.onload());assert.equal(read('loaded'),128);
read('tick(99)');assert.equal(read('index'),0);assert.equal(read('elapsed'),0);
for(const speed of [1,4]){els['#speed'].value=String(speed);read('elapsed=0;last=0;playing=true');for(let i=0;i<=16;i++){read('tick('+i*60*speed+')');assert.equal(read('index'),i%16)} }
read('step(-1)');assert.equal(read('index'),15);assert.equal(read('playing'),false);read('step(1)');assert.equal(read('index'),0);
assert.equal(cards.length,8);assert.equal(els['#status'].textContent,'128/128 已载入');
const report={status:'passed',scope:'Actual overview JavaScript with image-load callbacks in DOM mock; not visual acceptance',loaded:128,directions:8,firstAnimationTimestampBeforeLoadCallback:'passed',normal60msAndQuarter240msPerFrame:'passed',wrapAndStep:'passed'};
fs.writeFileSync(path.join(root,'preview/overview-timing-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
