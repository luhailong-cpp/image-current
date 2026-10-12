const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const page=await browser.newPage({viewport:{width:1250,height:900}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(__dirname,'index.html')).href);
 await page.waitForFunction(()=>window.GROUNDING_PREVIEW);
 if(await page.locator('canvas').count()!==1)throw Error('Removed old fast comparison canvases expected');
 const options=await page.locator('#speed option').evaluateAll(es=>es.map(e=>e.value));
 if(JSON.stringify(options)!==JSON.stringify(['1','0.25']))throw Error('Wrong speed options');
 await page.locator('#play').click();
 for(let i=1;i<=16;i++)await page.locator('#scrub').fill(String(i));
 await page.waitForFunction(()=>window.GROUNDING_PREVIEW.getState().loadedImageCount===16);
 const timings=await page.evaluate(()=> {
  const p=window.GROUNDING_PREVIEW,d=window.PREVIEW_DATA.selection.timing.frameDurationsMs;
  if(d.length!==16||d.some(n=>n!==75))throw Error('Not 16 equal 75ms frames');
  const checks=Array.from({length:16},(_,i)=>[p.frameAt(i*75,d),p.frameAt((i+1)*75-0.001,d)]);
  if(checks.some((x,i)=>x[0]!==i||x[1]!==i)||p.frameAt(1200,d)!==0)throw Error('Bad cycle boundaries');
  return {durationMs:d,cycleMs:d.reduce((a,b)=>a+b,0),noBoundaryHold:true};
 });
 const sizes=[];
 for(const n of [128,256]){
  await page.locator('#size').selectOption(String(n));await page.locator('#scrub').fill('1');
  const width=await page.locator('#native-lane canvas').evaluate(c=>c.getBoundingClientRect().width);
  if(width!==n)throw Error('Wrong display size');
  await page.screenshot({path:path.join(__dirname,'normal-1200-'+n+'.png')});sizes.push(width);
 }
 await page.locator('#speed').selectOption('1');await page.locator('#reset').click();await page.locator('#play').click();
 const observed=await page.evaluate(()=>new Promise(resolve=>{
  const p=window.GROUNDING_PREVIEW,out=[],start=performance.now();let last=-1;
  function tick(now){const s=p.getState(),f=s.frames[0];if(f!==last){out.push({frame:f+1,timeMs:s.times[0]});last=f;}
   if(now-start<2550)requestAnimationFrame(tick);else resolve(out);
  }requestAnimationFrame(tick);
 }));
 await page.locator('#play').click();
 const firstLoop=observed.slice(observed.findIndex(x=>x.frame===1));
 const sequential=firstLoop.slice(0,17).every((x,i)=>x.frame===i%16+1);
 if(!sequential)throw Error('Actual 1x playback did not traverse all16 and wrap');
 const loopMs=firstLoop[16].timeMs-firstLoop[0].timeMs;
 if(Math.abs(loopMs-1200)>35)throw Error('Measured actual cycle differs from1200');
 await page.locator('#speed').selectOption('0.25');await page.locator('#play').click();
 const a=await page.evaluate(()=>window.GROUNDING_PREVIEW.getState().times[0]);await page.waitForTimeout(240);
 const b=await page.evaluate(()=>window.GROUNDING_PREVIEW.getState().times[0]);
 await page.locator('#play').click();if(b-a<40||b-a>85)throw Error('Quarter speed mismatch');
 await page.locator('#scrub').fill('16');await page.locator('#next').click();
 if((await page.evaluate(()=>window.GROUNDING_PREVIEW.getState().frames[0]))!==0)throw Error('16 to1 failed');
 await page.locator('#prev').click();
 if((await page.evaluate(()=>window.GROUNDING_PREVIEW.getState().frames[0]))!==15)throw Error('1 to16 failed');
 if(errors.length)throw Error(errors.join(';'));
 const report={checkedAt:new Date().toISOString(),...timings,removedFastOptions:true,normalRate:1,slowRate:.25,actualPlaybackAll16InOrder:true,actualCycleMs:loopMs,observed,sizes,loadedImages:16,pageErrors:errors,combatTimingsChanged:false,clientRuntimeVerified:false};
 fs.writeFileSync(path.join(__dirname,'verification-current-timing.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({cycleMs:timings.cycleMs,frameMs:75,actualCycleMs:loopMs,all16AndWrap:sequential,oldFastOptionsRemoved:true,errors}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});

