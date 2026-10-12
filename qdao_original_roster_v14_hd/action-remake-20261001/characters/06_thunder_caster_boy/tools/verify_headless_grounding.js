/* Real local browser playback sampling; never changes runtime or preview source. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),http=require('http');
const ROOT=path.resolve(__dirname,'..');
const stamp=new Date().toISOString().replace(/[:.]/g,'-');
const OUT=path.join(ROOT,'review','headless_grounding_'+stamp);
for(const d of ['', 'profile','tmp','cache','artifacts','downloads','screenshots'])fs.mkdirSync(path.join(OUT,d),{recursive:true});
process.env.TMP=process.env.TEMP=path.join(OUT,'tmp');
const {chromium}=require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const exe='C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const URL='http://127.0.0.1:18606/preview/timing-grounding-20261003/index.html';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const json=(name,obj)=>fs.writeFileSync(path.join(OUT,name),JSON.stringify(obj,null,2));
let ownedServer,context;
const result={startedAt:new Date().toISOString(),url:URL,outputDirectory:OUT,executable:exe,playwright:require('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json').version,method:'Real Edge page playback; rAF samples DOM frame URLs. WebM uses MediaRecorder on a canvas that copies the two currently displayed DOM images on each actual rAF; no precomputed frame schedule. Screenshots are native Playwright page captures.',clientConnected:false,visualArtAcceptance:false,externalRequestsBlocked:[],pageErrors:[],requestFailures:[],runs:[]};
async function serveIfAbsent(){
 try{const r=await fetch(URL,{signal:AbortSignal.timeout(1500)});if(r.ok){result.server='existing';return;}}catch{}
 ownedServer=http.createServer((req,res)=>{
  const pathname=decodeURIComponent(new globalThis.URL(req.url,'http://127.0.0.1').pathname);
  const f=path.resolve(ROOT,'.'+pathname);
  if(f!==ROOT&&!f.startsWith(ROOT+path.sep)){res.writeHead(403).end();return;}
  fs.readFile(f,(err,data)=>{if(err){res.writeHead(404).end();return;}const type={'.html':'text/html; charset=utf-8','.png':'image/png','.json':'application/json','.webm':'video/webm'}[path.extname(f)]||'application/octet-stream';res.writeHead(200,{'Content-Type':type,'Cache-Control':'no-store'});res.end(data);});
 });
 await new Promise((resolve,reject)=>{ownedServer.once('error',reject);ownedServer.listen(18606,'127.0.0.1',resolve);});
 result.server='temporary local server owned by this verification; character ROOT only';
}
function summarize(samples,key,cycle){
 const seq=samples.map(s=>s[key]),changes=[];
 let old=null;
 for(let i=0;i<seq.length;i++){if(seq[i].frame!==old){changes.push({t:samples[i].t,frame:seq[i].frame});old=seq[i].frame;}}
 const skips=changes.slice(1).filter((x,i)=>((x.frame-changes[i].frame+16)%16)!==1);
 const wraps=[];for(let i=1;i<changes.length;i++)if(changes[i].frame<changes[i-1].frame)wraps.push(changes[i].t);
 const cycles=wraps.slice(1).map((t,i)=>t-wraps[i]);
 return {nominalCycleMs:cycle,samples:samples.length,distinctFrames:[...new Set(seq.map(x=>x.frame))].sort((a,b)=>a-b),nonRenderableSamples:seq.filter(x=>x.hidden||!x.complete||x.width!==1024||x.opacity==='0'||x.display==='none'||x.visibility==='hidden').length,metadataMismatchSamples:seq.filter(x=>x.metaFrame!==x.frame).length,transitionCount:changes.length,skippedTransitions:skips,observedWrapIntervalsMs:cycles,meanObservedCycleMs:cycles.length?cycles.reduce((a,b)=>a+b,0)/cycles.length:null};
}
(async()=>{
 try{
  if(!fs.existsSync(exe))throw Error('Existing Edge binary missing');
  await serveIfAbsent();
  result.sourceBefore=Array.from({length:16},(_,i)=>{const file='runtime/run/S/'+String(i).padStart(2,'0')+'.png';return{file,sha256:sha(path.join(ROOT,file))};});
  context=await chromium.launchPersistentContext(path.join(OUT,'profile'),{executablePath:exe,headless:true,viewport:{width:1180,height:950},deviceScaleFactor:1,artifactsDir:path.join(OUT,'artifacts'),downloadsPath:path.join(OUT,'downloads'),tracesDir:path.join(OUT,'artifacts'),env:{...process.env,TMP:path.join(OUT,'tmp'),TEMP:path.join(OUT,'tmp')},args:['--disk-cache-dir='+path.join(OUT,'cache'),'--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--no-default-browser-check','--disable-crash-reporter','--proxy-server=http://127.0.0.1:9','--proxy-bypass-list=127.0.0.1;localhost','--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost, EXCLUDE 127.0.0.1']});
  await context.route('**/*',route=>{const u=new globalThis.URL(route.request().url());if(u.protocol==='http:'&&u.hostname==='127.0.0.1'&&u.port==='18606')return route.continue();if(u.protocol==='data:'||u.protocol==='blob:')return route.continue();result.externalRequestsBlocked.push(route.request().url());return route.abort();});
  const page=await context.newPage();
  page.on('pageerror',e=>result.pageErrors.push(String(e)));
  page.on('requestfailed',r=>result.requestFailures.push({url:r.url(),error:r.failure()}));
  await page.goto(URL,{waitUntil:'load',timeout:20000});
  await page.locator('#direction').selectOption('S');
  await page.waitForFunction(()=>['old','trial'].every(id=>{const im=document.getElementById(id);return !im.hidden&&im.complete&&im.naturalWidth===1024&&im.src.includes('/run/S/');}),{timeout:15000});
  result.pageSourceFrames=await page.evaluate(()=>data.sequences.S.frames);
  result.pageSourceMatches=result.pageSourceFrames.every((f,i)=>f.sha256===result.sourceBefore[i].sha256);
  await page.screenshot({path:path.join(OUT,'screenshots','page_loaded_S.png'),fullPage:true});
  for(const cycle of [1200,4800]){
   await page.locator('#cycle').selectOption(String(cycle));
   const sampled=await page.evaluate(async({cycle,duration})=>{
    const old=document.getElementById('old'),trial=document.getElementById('trial');
    const cv=document.createElement('canvas');cv.width=560;cv.height=340;const g=cv.getContext('2d');
    const mime=['video/webm;codecs=vp9','video/webm;codecs=vp8','video/webm'].find(x=>MediaRecorder.isTypeSupported(x));
    if(!mime)throw Error('Browser MediaRecorder WebM unavailable');
    const chunks=[],stream=cv.captureStream(60),mr=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:3500000});
    mr.ondataavailable=e=>{if(e.data.size)chunks.push(e.data);};const stopped=new Promise(resolve=>mr.onstop=resolve);
    const samples=[];let first,last;
    const read=(im,meta)=>{const css=getComputedStyle(im);return{src:im.src,frame:Number(new globalThis.URL(im.src).pathname.split('/').pop().split('.')[0]),metaFrame:Number(document.getElementById(meta).textContent.slice(0,2)),hidden:im.hidden,complete:im.complete,width:im.naturalWidth,display:css.display,visibility:css.visibility,opacity:css.opacity};};
    document.getElementById('restart').click();mr.start(250);
    await new Promise((resolve,reject)=>{
     const watchdog=setTimeout(()=>reject(Error('rAF sampling exceeded 20 seconds')),20000);
     function sample(t){
      if(first===undefined)first=t;last=t;
      const a=read(old,'oldMeta'),b=read(trial,'trialMeta');samples.push({t,relativeMs:t-first,old:a,trial:b});
      g.fillStyle='#f4efdf';g.fillRect(0,0,560,340);g.fillStyle='#284c42';g.font='18px sans-serif';g.fillText('S run · actual browser playback',16,25);
      g.font='15px sans-serif';g.fillText('1200ms | frame '+a.frame.toString().padStart(2,'0'),16,49);g.fillText(cycle+'ms | frame '+b.frame.toString().padStart(2,'0'),288,49);
      g.fillStyle='#e4e6dd';g.fillRect(16,64,240,240);g.fillRect(288,64,240,240);
      if(!a.hidden&&a.complete)g.drawImage(old,16,64,240,240);if(!b.hidden&&b.complete)g.drawImage(trial,288,64,240,240);
      g.fillStyle='#284c42';g.font='12px sans-serif';g.fillText('rAF '+(t-first).toFixed(1)+'ms · offline candidate · client not connected',16,325);
      if(t-first<duration)requestAnimationFrame(sample);else {clearTimeout(watchdog);resolve();}
     }requestAnimationFrame(sample);
    });
    mr.stop();await stopped;stream.getTracks().forEach(t=>t.stop());
    document.getElementById('play').click();
    const blob=new Blob(chunks,{type:mime});const b64=await new Promise(resolve=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.readAsDataURL(blob);});
    return{samples,mime,videoBase64:b64,recordedMs:last-first};
   },{cycle,duration:12000});
   const name='S_1200_vs_'+cycle+'_actual';
   fs.writeFileSync(path.join(OUT,name+'.webm'),Buffer.from(sampled.videoBase64,'base64'));
   const report={cycle,recordedMs:sampled.recordedMs,mime:sampled.mime,video:name+'.webm',old:summarize(sampled.samples,'old',1200),trial:summarize(sampled.samples,'trial',cycle),samples:sampled.samples};
   const videoPage=await context.newPage();
   const videoUrl='http://127.0.0.1:18606/'+path.relative(ROOT,path.join(OUT,name+'.webm')).split(path.sep).join('/');
   await videoPage.setContent('<video muted autoplay style="width:560px;height:340px" src="'+videoUrl+'"></video>');
   await videoPage.waitForFunction(()=>{const v=document.querySelector('video');return v.videoWidth===560&&v.currentTime>0.2;},null,{timeout:10000});
   report.videoDecode=await videoPage.evaluate(()=>{const v=document.querySelector('video');return{width:v.videoWidth,height:v.videoHeight,currentTime:v.currentTime,readyState:v.readyState,paused:v.paused,error:v.error};});
   await videoPage.screenshot({path:path.join(OUT,'screenshots',name+'_video_decode.png')});
   await videoPage.close();await page.bringToFront();
   json(name+'.json',report);result.runs.push({...report,samples:undefined});
   await page.screenshot({path:path.join(OUT,'screenshots',name+'_end.png'),fullPage:true});
   console.log(JSON.stringify({cycle,recordedMs:report.recordedMs,oldSamples:report.old.samples,trialFrames:report.trial.distinctFrames,nonRenderable:report.trial.nonRenderableSamples,video:report.video}));
  }
  await page.locator('#large').check();
  result.stepped=[];
  for(let i=0;i<16;i++){
   await page.locator('#frame').evaluate((el,v)=>{el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}));},String(i));
   await page.waitForFunction(i=>['old','trial'].every(id=>document.getElementById(id).src.includes('/'+String(i).padStart(2,'0')+'.png')),i);
   await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   const filename='S_step_'+String(i).padStart(2,'0')+'.png';
   await page.screenshot({path:path.join(OUT,'screenshots',filename),fullPage:true});
   result.stepped.push({frame:i,screenshot:'screenshots/'+filename,dom:await page.evaluate(()=>({old:document.getElementById('old').src,trial:document.getElementById('trial').src,meta:document.getElementById('frameNo').textContent,status:document.getElementById('status').textContent}))});
  }
  result.sourceAfter=result.sourceBefore.map(x=>({...x,sha256:sha(path.join(ROOT,x.file))}));
  result.sourceUnchanged=result.sourceBefore.every((x,i)=>x.sha256===result.sourceAfter[i].sha256);
  result.browserVersion=context.browser().version();
  result.finishedAt=new Date().toISOString();result.automaticPlaybackSamplingCompleted=true;
  json('evidence.json',result);
  const html='<!doctype html><meta charset="utf-8"><title>06 南向实际浏览器播放采样</title><style>body{font:16px sans-serif;max-width:1100px;margin:24px auto;background:#f4efdf;color:#284c42}video{width:560px;max-width:100%}section{margin:24px 0}</style><h1>06 南向实际浏览器播放采样</h1><p>真实 Edge 本地页面运行时采样；左侧正常1200ms，右侧正常或四分之一慢放。MediaRecorder 按实际 rAF 抓取当时两面板图像，非预排帧视频。自动采样不等于完整美术动态通过；客户端未接入。</p>'+result.runs.map(r=>'<section><h2>1200ms / '+r.cycle+'ms</h2><video controls loop muted src="'+r.video+'"></video><p><a href="'+r.video.replace('.webm','.json')+'">rAF帧号与可绘制状态</a></p></section>').join('')+'<p><a href="evidence.json">完整环境、来源SHA与采样记录</a></p>';
  fs.writeFileSync(path.join(OUT,'index.html'),html);
  console.log(JSON.stringify({complete:true,outputDirectory:OUT,pageSourceMatches:result.pageSourceMatches,sourceUnchanged:result.sourceUnchanged,browser:result.browserVersion,stepped:result.stepped.length}));
 }catch(error){result.error=String(error);result.stack=error.stack;result.finishedAt=new Date().toISOString();json('evidence_error.json',result);console.error(JSON.stringify({complete:false,error:String(error),outputDirectory:OUT}));process.exitCode=1;}
 finally{if(context)await context.close();if(ownedServer)await new Promise(resolve=>ownedServer.close(resolve));/* Browser cache/profile retained: automated approval rejected recursive cleanup. */}
})();

