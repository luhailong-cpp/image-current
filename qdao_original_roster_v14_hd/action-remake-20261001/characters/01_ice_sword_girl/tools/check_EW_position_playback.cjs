const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const R=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1000,height:880}}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.join(R,'review/run-EW-position-player.html')).href);
 await page.waitForFunction(()=>window.ewReview&&ewReview.getState().loaded);
 const loops=[];
 for(const direction of ['E','W'])for(const size of ['128','256']){
  await page.selectOption('#size',size);
  await page.selectOption('#speed','1');
  await page.evaluate(d=>{ewReview.select(d);ewReview.play()},direction);
  await page.waitForTimeout(2630);
  const s=await page.evaluate(()=>ewReview.getState());
  const orderCorrect=s.history.every((f,i,a)=>i===0||f.index===a[i-1].index%16+1);
  const starts=s.history.filter(f=>f.index===1),cycles=starts.slice(1).map((f,i)=>f.time-starts[i].time);
  loops.push({direction,size:Number(size),frameChanges:s.history.length,observedFrames:[...new Set(s.history.map(f=>f.index))],orderCorrect,cyclesMs:cycles,pass:orderCorrect&&cycles.length>=2&&cycles.every(t=>Math.abs(t-1200)<45),history:s.history});
 }
 await page.evaluate(()=>{ewReview.select('W');ewReview.step(-1)});
 const reverseWrap=await page.evaluate(()=>ewReview.getState().index===16&&!ewReview.getState().playing);
 await page.click('#next');
 const forwardWrap=await page.evaluate(()=>ewReview.getState().index===1&&!ewReview.getState().playing);
 await page.selectOption('#speed','.25');
 const quarterSpeed=await page.evaluate(()=>ewReview.getState().speed===.25);
 const availableSpeeds=await page.locator('#speed option').evaluateAll(xs=>xs.map(x=>x.value));
 await page.selectOption('#size','256');
 await page.screenshot({path:path.join(R,'review/run-EW-position-playback.png')});
 const result={createdAt:new Date().toISOString(),tool:'Playwright Chromium headless',loaded32WholeCanvas1024:true,loops,reverseWrap,forwardWrap,quarterSpeed,availableSpeeds,errors,technicalPlaybackPassed:loops.every(x=>x.pass)&&reverseWrap&&forwardWrap&&quarterSpeed&&errors.length===0,scope:'Offline browser playback order, timing, loading and controls. Does not establish client runtime or subjective motion acceptance.'};
 fs.writeFileSync(path.join(R,'review/run-EW-position-playback.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({...result,loops:loops.map(({history,...x})=>x)}));
 await browser.close();
 if(!result.technicalPlaybackPassed)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
