const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'}),page=await browser.newPage({viewport:{width:1250,height:1050}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(__dirname,'all.html')).href);
 await page.waitForFunction(()=>window.animationReview?.getState().loaded>0);
 const sequences=await page.evaluate(()=>window.ALL_SEQUENCES.sequences.filter(s=>s.complete));
 const options=await page.locator('#rate option').evaluateAll(es=>es.map(e=>Number(e.value)));
 if(JSON.stringify(options)!=='[1,0.25]')throw Error('Unexpected playback options');
 const checks=[];
 // A step during async image loading must never poison the next sequence index.
 await page.evaluate(()=>{window.animationReview.select('run','E');window.animationReview.step(1)});
 await page.waitForFunction(()=>window.animationReview.getState().loaded===16);
 if(!await page.evaluate(()=>Number.isFinite(window.animationReview.getState().index)))throw Error('Loading step corrupted index');
 for(const s of sequences){
  await page.evaluate(([a,d])=>window.animationReview.select(a,d),[s.action,s.direction]);
  await page.waitForFunction(n=>window.animationReview.getState().loaded===n,s.expectedFrames);
  await page.locator('#play').click();
  await page.evaluate(()=>window.animationReview.step(-window.animationReview.getState().index));
  for(let i=0;i<s.expectedFrames;i++)await page.locator('#next').click();
  if((await page.evaluate(()=>window.animationReview.getState().index))!==0)throw Error('Step wrap mismatch');
  await page.locator('#prev').click();if((await page.evaluate(()=>window.animationReview.getState().index))!==s.expectedFrames-1)throw Error('Reverse wrap mismatch');
  await page.locator('#next').click();await page.locator('#play').click();
  const observed=await page.evaluate(ms=>new Promise(resolve=>{
   const out=[],start=performance.now();let previous=-1;
   function read(t){const v=window.animationReview.getState().index;if(v!==previous){out.push({frame:v+1,time:t-start});previous=v}if(t-start<ms)requestAnimationFrame(read);else resolve(out)}requestAnimationFrame(read);
  }),s.cycleMs*2.2);
  await page.locator('#play').click();
  fs.writeFileSync(path.join(__dirname,'last-playback-observation.json'),JSON.stringify({sequence:s.action+'/'+s.direction,observed},null,2)+'\n');
  if(observed.some((v,i)=>i&&v.frame!==(observed[i-1].frame%s.expectedFrames)+1))throw Error('Dropped/reordered frames '+s.action+s.direction);
  const boundaries=observed.filter(v=>v.frame===1),measured=boundaries.length>=2?boundaries[1].time-boundaries[0].time:null;
  if(measured===null||Math.abs(measured-s.cycleMs)>45)throw Error('Wrong actual cycle '+s.action+s.direction);
  checks.push({action:s.action,direction:s.direction,frames:s.expectedFrames,frameMs:s.frameMs,cycleMs:s.cycleMs,measuredMs:measured,ordered:true,loaded:true});
 }
 await page.locator('#size').selectOption('128');if(await page.locator('canvas').evaluate(c=>c.getBoundingClientRect().width)!==128)throw Error('128 scale');
 await page.locator('#size').selectOption('256');
 await page.screenshot({path:path.join(__dirname,'all-preview-256.png'),fullPage:true});
 if(errors.length)throw Error(errors.join(';'));
 fs.writeFileSync(path.join(__dirname,'verification-all.json'),JSON.stringify({checkedAt:new Date().toISOString(),checks,options,pageErrors:errors,clientRuntimeVerified:false,artDynamicAcceptance:false},null,2)+'\n');
 console.log(JSON.stringify({verifiedCompleteSequences:checks.length,checks,pageErrors:errors}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
