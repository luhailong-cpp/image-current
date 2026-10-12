const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {pathToFileURL}=require('node:url');
const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sharp=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const char=path.resolve(__dirname,'..'),selectionPath=path.join(char,'review/run-E-selection.json');
 const before=hash(selectionPath),selected=JSON.parse(fs.readFileSync(selectionPath,'utf8').replace(/^\uFEFF/,''));
 if(!selected.frames[2].path.endsWith('03-v3.png'))throw Error('Expected current E03-v3');
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const page=await browser.newPage({viewport:{width:1400,height:900},deviceScaleFactor:1}),errors=[],samples=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(__dirname,'index.html')).href);
 await page.waitForFunction(()=>window.GROUNDING_PREVIEW);
 await page.locator('#play').click();
 const sources=new Map();
 for(const size of [128,256]){
  const overlays=[];
  for(const [row,variant] of ['04-v4','04-v2'].entries()){
   const data=JSON.parse(JSON.stringify(selected));
   data.frames[3].path='drafts/run/E/'+variant+'.png';
   data.frames[3].sha256=hash(path.join(char,data.frames[3].path));
   data.frames[3].status=variant==='04-v4'?'current_selection':'comparison_only_not_selected';
   await page.locator('#selection-file').setInputFiles({name:'comparison.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(data))});
   await page.waitForFunction(v=>document.getElementById('snapshot').textContent.includes('drafts/run/E/'+v+'.png'),variant);
   await page.locator('#size').selectOption(String(size));
   await page.locator('#speed').selectOption('1');await page.locator('#debug').uncheck();
   for(const f of [2,3,4,5])await page.locator('#scrub').fill(String(f));
   await page.waitForTimeout(150);await page.locator('#reset').click();
   for(const [column,frame] of [2,3,4,5].entries()){
    const sample=await page.evaluate(async target=>{
     document.getElementById('play').click();
     await new Promise(resolve=>{function check(){if(window.GROUNDING_PREVIEW.getState().frames.at(-1)===target){document.getElementById('play').click();resolve();}else requestAnimationFrame(check);}requestAnimationFrame(check);});
     const s=window.GROUNDING_PREVIEW.getState();return{frame:s.frames.at(-1)+1,timeMs:s.times.at(-1),speed:s.speed};
    },frame-1);
    if(sample.frame!==frame)throw Error('Wrong sampled frame');
    const f=data.frames[frame-1];sources.set(f.path,{path:f.path,sha256:hash(path.join(char,f.path))});
    samples.push({size,variant,path:f.path,...sample});
    const picture=await page.locator('#native-lane canvas').screenshot();
    const title=Buffer.from('<svg width="'+size+'" height="30"><rect width="100%" height="100%" fill="#182c38"/><text x="5" y="19" fill="white" font-family="Arial" font-size="12">'+path.basename(f.path,'.png')+' | 1x | '+size+'px</text></svg>');
    overlays.push({input:title,left:column*size,top:row*(size+30)},{input:picture,left:column*size,top:row*(size+30)+30});
   }
  }
  await sharp({create:{width:size*4,height:(size+30)*2,channels:3,background:'#182c38'}}).composite(overlays).png().toFile(path.join(__dirname,'e03-e04-options-'+size+'.png'));
 }
 await browser.close();
 if(errors.length)throw Error(errors.join('\n'));if(before!==hash(selectionPath))throw Error('Selection changed during review');
 const report={builtAtUtc:new Date().toISOString(),scope:'Targeted E02/E03-v3/E04 option/E05 only; previous full browser checks not repeated.',selectionSha256:before,sourceHashes:[...sources.values()],variants:['04-v4 current selection','04-v2 temporary in-memory comparison'],selectedFileMutated:false,pngPixelsMutated:false,method:'Run actual player at 1x; pause at actual frame; screenshots preserve full source canvas. Diagnostic A/B selection was loaded only in browser memory; no selection write.',samples,pageErrors:errors,clientRuntimeVerified:false};
 fs.writeFileSync(path.join(__dirname,'e03-e04-options-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
})().catch(e=>{console.error(e);process.exit(1)});

