// Exercise the actual preview clock functions without browser or pixel changes.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'preview/index.html'),'utf8');
const groups=JSON.parse(fs.readFileSync(path.join(root,'preview/data.js'),'utf8').replace(/^window.PREVIEW_DATA=/,'').replace(/;$/,''));
const durationFunction=html.match(/^function durations\(\).*$/m)[0];
const tickFunction=html.match(/^function tick\(t\).*?(?=load\(\);requestAnimationFrame\(tick\);)/m)[0];
assert(!html.includes('id="cycle"')&&!html.includes('id="timing"'));
const results=[];
for(const g of groups){
  const period=g.ms*g.frames.length;
  assert.equal(period,g.key.startsWith('run/')?960:g.key.startsWith('hit/')?240:g.key.startsWith('attack/')?360:720);
  for(const speed of [1,0.25]){
    const seen=[];
    const c={g,index:0,playing:true,elapsed:0,last:0,$:()=>({value:String(speed)}),requestAnimationFrame:()=>{},show:()=>seen.push(c.index)};
    vm.createContext(c);vm.runInContext(durationFunction+'\n'+tickFunction,c);
    for(let t=1;t<=period/speed;t++)c.tick(t);
    assert.deepEqual(seen,[...Array.from({length:g.frames.length-1},(_,i)=>i+1),0]);
    assert.equal(c.index,0);assert.equal(c.elapsed,0);
    results.push({group:g.key,speed,wallCycleMs:period/speed,framesSeen:seen.length,seamDelayMs:0});
  }
}
const report={checkedAt:new Date().toISOString(),pass:true,source:'actual inline durations() and tick() from current preview',normalRunMs:960,runFrameMs:60,oldSpeedControlsRemoved:true,results};
fs.writeFileSync(path.join(root,'provenance/preview-timing-verification.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify({pass:true,checkedGroups:groups.length,speedCases:results.length,normalRunMs:960,runFrameMs:60,seamDelayMs:0}));
