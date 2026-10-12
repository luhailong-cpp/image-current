const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {pathToFileURL} = require('node:url');
const {chromium} = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sharp = require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');

(async () => {
  const browser = await chromium.launch({headless:true,channel:'chrome'});
  const page = await browser.newPage({viewport:{width:1480,height:1580},deviceScaleFactor:1});
  const errors=[];
  page.on('pageerror', error=>errors.push(error.message));
  await page.goto(pathToFileURL(path.join(__dirname,'index.html')).href);
  await page.waitForFunction(()=>window.GROUNDING_PREVIEW);
  const comparisonsCollapsedByDefault=await page.locator('details').first().evaluate(el=>!el.open);
  if(!comparisonsCollapsedByDefault)throw Error('Comparison section should be collapsed by default');
  await page.locator('#play').click();
  const initialState=await page.evaluate(()=>window.GROUNDING_PREVIEW.getState());
  if(initialState.frames.length<9)throw Error('Expected at least 9 lanes');
  if(initialState.laneKinds.filter(s=>s==='old-uniform').length!==4 || initialState.laneKinds.filter(s=>s==='native-uniform').length!==4 || initialState.laneKinds.filter(s=>s==='native-phase').length!==1)throw Error('Wrong old/native/phase lane layout');
  if(JSON.stringify(initialState.cycleDurations.slice(0,8))!==JSON.stringify([480,640,720,800,480,640,720,800]))throw Error('Uniform comparison cycle durations differ');
  const checks = await page.evaluate(() => {
    const p=window.GROUNDING_PREVIEW, failures=[];
    for(const total of [480,640,720,800]) {
      const durations=Array(16).fill(total/16);
      for(let i=0;i<16;i++) {
        const start=p.frameStart(i,durations);
        if(p.frameAt(start,durations)!==i)failures.push(`boundary ${total}/${i}`);
        if(p.frameAt(start+durations[i]/2,durations)!==i)failures.push(`midpoint ${total}/${i}`);
      }
      if(p.frameAt(total,durations)!==0)failures.push(`loop ${total}`);
      if(p.frameAt(total-0.001,durations)!==15)failures.push(`wrap-before ${total}`);
    }
    const durations=[60,60,55,45,40,35,30,35,60,60,55,45,40,35,30,35];
    for(let i=0;i<16;i++)if(p.frameAt(p.frameStart(i,durations)+0.01,durations)!==i)failures.push(`nonuniform ${i}`);
    return {failures, selectedSlots:p.getState().selectedSlots};
  });
  if(checks.failures.length)throw Error(checks.failures.join(', '));
  // Exercise all actual image references, preserving null slots in all five native lanes.
  for(let i=1;i<=16;i++)await page.locator('#scrub').fill(String(i));
  const expectedImages=await page.evaluate(()=>new Set([
    ...window.PREVIEW_DATA.baseline.frames.map(f=>new URL(f.path,location.href).href),
    ...window.PREVIEW_DATA.selection.frames.filter(f=>f&&!f.previewFileError).map(f=>new URL('../'+f.path,location.href).href)
  ]).size);
  await page.waitForFunction(expected=>{
    const s=window.GROUNDING_PREVIEW.getState();
    return s.loadedImageCount+s.failedImageCount>=expected;
  },expectedImages,{timeout:15000});
  const loadedState=await page.evaluate(()=>window.GROUNDING_PREVIEW.getState());
  if(loadedState.failedImageCount)throw Error('One or more image sources failed to load');
  await page.locator('#scrub').fill('16');
  let state=await page.evaluate(()=>window.GROUNDING_PREVIEW.getState());
  if(!state.frames.every(n=>n===15))throw Error('Scrub did not retain slot 16');
  await page.locator('#next').click();
  state=await page.evaluate(()=>window.GROUNDING_PREVIEW.getState());
  if(!state.frames.every(n=>n===0))throw Error('Step did not wrap 16 to 01');
  await page.locator('#prev').click();
  state=await page.evaluate(()=>window.GROUNDING_PREVIEW.getState());
  if(!state.frames.every(n=>n===15))throw Error('Previous did not wrap 01 to 16');
  const sizes=[];
  for(const n of [128,256,512]) {
    await page.locator('#size').selectOption(String(n));
    sizes.push(await page.locator('#native-lane canvas').evaluate(el=>({css:el.getBoundingClientRect().width,backing:el.width})));
    if(sizes.at(-1).css!==n)throw Error(`CSS canvas not ${n}`);
  }
  await page.locator('#debug').check();
  await page.locator('#debug').uncheck();
  await page.locator('#scrub').fill('1');
  await page.locator('#size').selectOption('128');
  await page.screenshot({path:path.join(__dirname,'browser-preview-128.png')});
  await page.locator('#size').selectOption('256');
  await page.screenshot({path:path.join(__dirname,'browser-preview-256.png')});
  // Inspect the optional comparison surface through its UI, then restore its collapsed state.
  const comparisonCanvasSizes=[];
  await page.locator('details').first().locator('summary').click();
  for(const n of [128,256,512]) {
    await page.locator('#size').selectOption(String(n));
    const widths=await page.locator('canvas').evaluateAll(elements=>elements.map(el=>el.getBoundingClientRect().width));
    if(widths.length!==9 || widths.some(width=>width!==n))throw Error(`Comparison canvas size mismatch at ${n}`);
    comparisonCanvasSizes.push({css:n,widths});
  }
  await page.locator('details').first().locator('summary').click();
  await page.locator('#speed').selectOption('0.25');
  await page.locator('#play').click();
  await page.waitForTimeout(250);
  state=await page.evaluate(()=>window.GROUNDING_PREVIEW.getState());
  if(state.speed!==0.25 || !state.playing)throw Error('Speed/play control failed');
  await page.locator('#play').click();
  const pausedBefore=await page.evaluate(()=>window.GROUNDING_PREVIEW.getState().times);
  await page.waitForTimeout(100);
  const pausedAfter=await page.evaluate(()=>window.GROUNDING_PREVIEW.getState().times);
  if(JSON.stringify(pausedBefore)!==JSON.stringify(pausedAfter))throw Error('Pause clock continues');
  const normalSamples=[];
  const transitionPairs=[[2,3],[3,4],[4,5],[7,8],[10,11],[11,12],[12,13],[16,1]];
  for(const n of [128,256]) {
    await page.locator('#size').selectOption(String(n));
    await page.locator('#speed').selectOption('1');
    await page.locator('#reset').click();
    const overlays=[];
    const targets=transitionPairs.flat().map(frame=>frame-1);
    for(let j=0;j<targets.length;j++) {
      const sample=await page.evaluate(async target=>{
        document.getElementById('play').click();
        await new Promise(resolve=>{
          function sampleFrame() {
            if(window.GROUNDING_PREVIEW.getState().frames.at(-1)===target) {
              document.getElementById('play').click();resolve();
            } else requestAnimationFrame(sampleFrame);
          }
          requestAnimationFrame(sampleFrame);
        });
        const state=window.GROUNDING_PREVIEW.getState();
        return {frame:state.frames.at(-1)+1,elapsedMs:state.times.at(-1),speed:state.speed};
      },targets[j]);
      const picture=await page.locator('#native-lane canvas').screenshot();
      const x=(j%2)*n,y=Math.floor(j/2)*(n+28);
      const title=Buffer.from(`<svg width="${n}" height="28"><rect width="100%" height="100%" fill="#182c38"/><text x="8" y="20" fill="white" font-family="Arial" font-size="14">E${String(sample.frame).padStart(2,'0')} | 1x | ${n}px</text></svg>`);
      overlays.push({input:title,left:x,top:y},{input:picture,left:x,top:y+28});
      normalSamples.push({size:n,...sample});
    }
    await sharp({create:{width:n*2,height:(n+28)*transitionPairs.length,channels:3,background:'#182c38'}}).composite(overlays).png().toFile(path.join(__dirname,`playback-transition-samples-${n}.png`));
  }
  const report={builtAtUtc:new Date().toISOString(),browser:'Playwright installed Google Chrome headless',
    selectionSha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'../review/run-E-selection.json'))).digest('hex'),
    fileProtocol:true,syntax:true,timingBoundaryChecks:checks.failures.length===0,
    laneCount:initialState.frames.length,laneKinds:initialState.laneKinds,
    cyclesMs:initialState.cycleDurations,loadedImageCount:loadedState.loadedImageCount,
    failedImageCount:loadedState.failedImageCount,
    wrap16to1:true,wrap1to16:true,missingSlotsPreserved:true,canvasSizes:sizes,
    comparisonsCollapsedByDefault,comparisonCanvasSizes,
    pauseClock:true,quarterSpeed:true,sourcePngMutations:false,pageErrors:errors,
    selectedSlotsAtVerification:checks.selectedSlots,
    screenshots:['browser-preview-128.png','browser-preview-256.png'],
    normalPlaybackSamples:normalSamples,
    sampledTransitionPairs:transitionPairs,
    normalPlaybackSampleMethod:'Run at 1x, pause on the requested actual displayed frame, capture canvas; diagnostic composites preserve the captured pixels. This samples transitions, not a claim that an entire movie was visually accepted.',
    visualReview:'Screenshot produced for layout and source visibility; no animation artistry acceptance inferred from automated controls.',
    clientRuntimeVerified:false};
  fs.writeFileSync(path.join(__dirname,'verification.json'),JSON.stringify(report,null,2)+'\n');
  await browser.close();
  if(errors.length)throw Error(errors.join('\n'));
  console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exit(1);});
