import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const main=await readFile(path.join(root,'preview/index.html'),'utf8');
const runPage=await readFile(path.join(root,'preview/timing-grounding-final.html'),'utf8');
const timing=JSON.parse(await readFile(path.join(root,'animation-timing.json'),'utf8'));
const runTiming=timing.run;
assert.equal(runTiming.frames,16);
assert.equal(runTiming.frameMs,60);
assert.equal(runTiming.cycleMs,960);
assert.equal(runTiming.uniform,true);
assert.equal(runTiming.frames*runTiming.frameMs,runTiming.cycleMs);
for(const [action,frames,frameMs,cycleMs] of [['hit',6,40,240],['attack',12,30,360],['cast',16,45,720]]){
  assert.equal(timing[action].frames,frames);
  assert.equal(timing[action].frameMs,frameMs);
  assert.equal(timing[action].cycleMs,cycleMs);
}
// Execute the shipped scheduler functions under a controlled clock.
const scheduler=main.slice(main.indexOf('function frameDelay()'),main.indexOf('function step(amount)'));
assert(scheduler.includes('function playOnce()'));
const checks=[];
for(const action of ['run','hit','attack','cast'])for(const speed of [1,0.5,0.25]){
  let now=0,id=0,queue=[],frames=[],stoppedAt=null;
  const controls={speed:{value:String(speed)},loop:{checked:true},play:{textContent:'播放'}};
  const ctx={sequence:{frameMs:timing[action].frameMs,frames:Array(timing[action].frames)},frameIndex:7,playing:false,timer:null,nextDeadline:0,
    performance:{now:()=>now},el:k=>controls[k],
    setTimeout:(fn,delay)=>{const task={id:++id,fn,due:now+delay};queue.push(task);return task.id},
    clearTimeout:taskId=>{queue=queue.filter(task=>task.id!==taskId)},
    render:()=>frames.push({frame:ctx.frameIndex+1,time:now}),
    pause:()=>{ctx.playing=false;queue=[];stoppedAt=now;controls.play.textContent='播放'}};
  vm.createContext(ctx);vm.runInContext(scheduler,ctx);ctx.playOnce();
  while(queue.length){queue.sort((a,b)=>a.due-b.due);const task=queue.shift();now=task.due;task.fn();assert(now<=20000)}
  const spec=timing[action];
  assert.deepEqual(frames.map(f=>f.frame),Array.from({length:spec.frames},(_,i)=>i+1));
  assert.deepEqual(frames.map(f=>f.time),Array.from({length:spec.frames},(_,i)=>i*spec.frameMs/speed));
  assert.equal(stoppedAt,spec.cycleMs/speed);
  checks.push({action,speed,frames:frames.length,singleClipMs:stoppedAt,firstFrameDelayMs:frames[0].time,extraEndHoldMs:0});
  if(action==='run'&&speed===1){
    const loops=3,continuousDurationMs=loops*runTiming.cycleMs;
    now=0;queue=[];frames=[];ctx.frameIndex=0;controls.loop.checked=true;ctx.render();ctx.togglePlayback();
    while(queue.length&&queue[0].due<=continuousDurationMs){const task=queue.shift();now=task.due;task.fn()}
    assert.equal(frames.length,loops*runTiming.frames+1);
    for(let i=0;i<frames.length;i++){assert.equal(frames[i].frame,i%runTiming.frames+1);assert.equal(frames[i].time,i*runTiming.frameMs)}
    checks.push({action:'run',threeContinuousLoopsMs:continuousDurationMs,loopBoundaryFrames:[frames[runTiming.frames-1],frames[runTiming.frames]],pass:true});
  }
}
// Check the independently generated run inspector at its actual cycle boundary.
const runScript=runPage.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(runScript);
const drawAndClock=runScript.slice(runScript.indexOf('function draw('),runScript.indexOf('function reset('));
const runData=JSON.parse(await readFile(path.join(root,'preview/timing-grounding-final-data.json'),'utf8'));
const view={ms:runTiming.cycleMs,img:{style:{},removeAttribute(){}},info:{},last:-1};
const controls={speed:{value:'1'},play:{textContent:'暂停'}};
const ctx={seq:runData.sequences,direction:{value:'E'},views:[view],durations:[runTiming.cycleMs],running:true,start:0,pausedElapsed:0,forced:null,once:true,document:{getElementById:k=>controls[k]},requestAnimationFrame(){}};
vm.createContext(ctx);vm.runInContext(drawAndClock,ctx);
for(let i=0;i<runTiming.frames;i++){ctx.tick(i*runTiming.frameMs);assert.equal(view.last,i);assert.equal(ctx.running,true)}
ctx.tick(runTiming.cycleMs-0.01);assert.equal(view.last,runTiming.frames-1);assert.equal(ctx.running,true);
ctx.tick(runTiming.cycleMs);assert.equal(view.last,runTiming.frames-1);assert.equal(ctx.running,false);assert.equal(ctx.pausedElapsed,runTiming.cycleMs);
assert.equal(controls.play.textContent,'播放');
assert.deepEqual(runData.uniformCycleDurationsMs,[runTiming.cycleMs]);assert.equal(runData.frameMs,runTiming.frameMs);assert.equal(runData.phaseWeightsApplied,false);
assert(!/480ms|640ms|720ms|800ms|phaseTiming|phaseMs/.test(runPage));
checks.push({runInspectorSingleCycleMs:runTiming.cycleMs,frameCount:runTiming.frames,all16Frames:true,oldFastOptionsRemoved:true,phaseWeightsApplied:false,pass:true});
const report={checkedAt:new Date().toISOString(),method:'Actual generated JavaScript schedulers executed in Node VM with deterministic clock; this is not browser or client visual acceptance.',timingSource:'animation-timing.json',runTiming,checks,clientValidated:false};
await writeFile(path.join(root,`provenance/run/timing-${runTiming.cycleMs}-checks.json`),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:true,checks:checks.length,runCycleMs:runTiming.cycleMs,runFrameMs:runTiming.frameMs,combatUnchanged:true}));
