'use strict';
// Local browser preview verification; no model calls or runtime edits.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const ROOT=path.resolve(__dirname,'..'),stamp=new Date().toISOString().replace(/[:.]/g,'-'),OUT=path.join(ROOT,'review','all_sequence_playback_'+stamp);
for(const d of ['','profile','tmp','cache','screenshots'])fs.mkdirSync(path.join(OUT,d),{recursive:true});
process.env.TMP=process.env.TEMP=path.join(OUT,'tmp');
const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const manifest=JSON.parse(fs.readFileSync(path.join(ROOT,'preview/manifest.json'),'utf8'));
const report={startedAt:new Date().toISOString(),clientConnected:false,visualArtAcceptance:false,manifestSha:sha(path.join(ROOT,'preview/manifest.json')),runs:[],errors:[],method:'Actual Edge preview/index.html selection, normal and quarter-speed rAF sampling; no schedule-synthesized video'};
let context,server;
(async()=>{try{
 server=http.createServer((req,res)=>{const f=path.resolve(ROOT,'.'+decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname));if(!f.startsWith(ROOT+path.sep)){res.writeHead(403).end();return;}fs.readFile(f,(e,b)=>{if(e){res.writeHead(404).end();return;}res.writeHead(200,{'Content-Type':path.extname(f)==='.html'?'text/html; charset=utf-8':path.extname(f)==='.png'?'image/png':'application/json','Cache-Control':'no-store'}).end(b);});});
 await new Promise((r,j)=>{server.once('error',j);server.listen(18607,'127.0.0.1',r);});
 context=await chromium.launchPersistentContext(path.join(OUT,'profile'),{executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',headless:true,viewport:{width:1160,height:1050},deviceScaleFactor:1,downloadsPath:path.join(OUT,'tmp'),args:['--disk-cache-dir='+path.join(OUT,'cache'),'--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--proxy-server=http://127.0.0.1:9','--proxy-bypass-list=127.0.0.1;localhost','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1']});
 await context.route('**/*',r=>{const u=new URL(r.request().url());return u.hostname==='127.0.0.1'&&u.port==='18607'?r.continue():r.abort();});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
 await page.goto('http://127.0.0.1:18607/preview/index.html',{waitUntil:'load'});
 for(const seq of manifest.sequences){
  if(process.argv[2]&&seq.id!==process.argv[2])continue;
  if(seq.missing.length)continue;
  const row={id:seq.id,sourceBefore:seq.frames.map(f=>({path:f.path,sha256:sha(path.join(ROOT,f.path))})),runs:[]};
  await page.locator('#action').selectOption(seq.action);await page.locator('#direction').selectOption(seq.direction);
  await page.evaluate(async()=>{await Promise.all([...imageCache.values()].map(im=>im.decode().catch(()=>null)));});
  for(const speed of [1,4]){
   await page.locator('#speed').selectOption(String(speed));
   await page.locator('#timeline').evaluate(el=>{el.value='0';el.dispatchEvent(new Event('input',{bubbles:true}));});
   await page.locator('#play').click();
   const samples=await page.evaluate(async duration=>{const out=[];let start;await new Promise(resolve=>{function tick(t){if(start===undefined)start=t;const im=document.getElementById('sprite');out.push({ms:t-start,frame:Number(new URL(im.src).pathname.split('/').pop().split('.')[0]),visible:!im.hidden&&im.complete&&im.naturalWidth===1024,sequence:document.getElementById('sequence-title').textContent});if(t-start<duration)requestAnimationFrame(tick);else resolve();}requestAnimationFrame(tick);});return out;},Math.max(1500,seq.cycle_ms*speed*2));
   await page.locator('#play').click();
   const seen=[...new Set(samples.map(x=>x.frame))].sort((a,b)=>a-b),bad=samples.filter(x=>!x.visible).length;
   const fn=seq.action+'_'+seq.direction+'_'+(speed===1?'normal':'slow');
   fs.writeFileSync(path.join(OUT,fn+'.json'),JSON.stringify({samples,speed,nominalCycleMs:seq.cycle_ms*speed},null,2));
   await page.screenshot({path:path.join(OUT,'screenshots',fn+'.png'),fullPage:true});
   const changes=samples.filter((x,i)=>i===0||x.frame!==samples[i-1].frame);
   const wraps=changes.filter((x,i)=>i>0&&x.frame<changes[i-1].frame).map(x=>x.ms);
   const wrapIntervals=wraps.slice(1).map((x,i)=>x-wraps[i]);
   row.runs.push({speed,seen,expected:seq.expected_count,nonRenderable:bad,samples:samples.length,evidence:fn+'.json',nominalCycleMs:seq.cycle_ms*speed,observedWrapIntervalsMs:wrapIntervals,skippedTransitions:changes.slice(1).filter((x,i)=>(x.frame-changes[i].frame+seq.expected_count)%seq.expected_count!==1)});
  }
  row.stepped=[];
  for(let frame=0;frame<seq.expected_count;frame++){
   await page.locator('#timeline').evaluate((el,v)=>{el.value=String(v);el.dispatchEvent(new Event('input',{bubbles:true}));},frame);
   await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
   row.stepped.push(await page.locator('#sprite').evaluate(im=>({frame:Number(new URL(im.src).pathname.split('/').pop().split('.')[0]),visible:!im.hidden&&im.complete&&im.naturalWidth===1024})));
  }
  row.pauseAtLastFrame=await page.locator('#play').textContent()==='播放';
  await page.locator('#next').click();row.nextWrap=await page.locator('#sprite').evaluate(im=>Number(new URL(im.src).pathname.split('/').pop().split('.')[0]));
  await page.locator('#previous').click();row.previousWrap=await page.locator('#sprite').evaluate(im=>Number(new URL(im.src).pathname.split('/').pop().split('.')[0]));
  row.sourceUnchanged=row.sourceBefore.every(f=>sha(path.join(ROOT,f.path))===f.sha256);row.manifestMatches=row.sourceBefore.every((f,i)=>seq.frames[i].sha256===f.sha256);report.runs.push(row);console.log(JSON.stringify({id:row.id,normal:row.runs[0].seen.length,slow:row.runs[1].seen.length,nonRenderable:row.runs.reduce((a,x)=>a+x.nonRenderable,0),sourceUnchanged:row.sourceUnchanged,steps:row.stepped.length}));
 }
 report.browserVersion=context.browser().version();report.finishedAt=new Date().toISOString();report.completed=true;
}catch(e){report.errors.push(String(e));process.exitCode=1;}finally{if(context)await context.close();if(server)await new Promise(r=>server.close(r));fs.writeFileSync(path.join(OUT,'evidence.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({output:OUT,completed:report.completed,sequences:report.runs.length,errors:report.errors}));}})();
