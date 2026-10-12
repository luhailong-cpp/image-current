"""八方向同一960ms周期，按经过时间取帧；只构建角色内离线预览。"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, hashlib, shutil, subprocess
from timing import RUN_TIMING
ROOT=Path(__file__).resolve().parents[1]
DIRECTIONS=["N","NE","E","SE","S","SW","W","NW"]
selection=json.loads((ROOT/"selection.json").read_text(encoding="utf-8-sig"))
lookup={(f["direction"],int(f["frame"])):f for f in selection["frames"] if f["action"]=="run"}
assetRoot="runtime" if selection.get("status")=="offline_delivery" else "candidate"
groups=[{"direction":d,"frames":[{"frame":i,"url":f"../{assetRoot}/run/{d}/{i:02}.png","source":lookup.get((d,i),{}).get("source"),"exists":(ROOT/f"{assetRoot}/run/{d}/{i:02}.png").exists()} for i in range(1,17)]} for d in DIRECTIONS]
visual=json.loads((ROOT/"provenance/offline-visual-review.json").read_text(encoding="utf-8-sig"))
for g in groups:
 audit=next((r.get("grounding4",{}) for r in visual["groups"] if r["action"]=="run" and r["direction"]==g["direction"]),{})
 g["contactSegments"]=audit.get("contactSegments",[])
 g["positionPairs"]=audit.get("positionPairs",[])
 g["groundingReviewed"]=audit.get("offlineReviewed",False)
HELPER="function frameAt(elapsed,slow=1){return Math.floor((((elapsed%(960*slow))+(960*slow))%(960*slow))/(60*slow))%16;}"
HTML=r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>星阵少女 · 八方向跑步</title>
<style>:root{color-scheme:dark;--size:256px}*{box-sizing:border-box}body{margin:0;background:#152c2b;color:#fff0d2;font:15px/1.55 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1500px;margin:auto;padding:22px}h1{font-size:24px;margin:0}p{margin:8px 0}button,select{font:inherit;border:1px solid #718a7d;background:#274740;color:#fff0d2;border-radius:5px;padding:7px 10px}button:disabled{opacity:.4}.controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:12px 0}.grid{display:flex;flex-wrap:wrap;gap:14px}article{width:calc(var(--size) + 24px);padding:11px;border:1px solid #5a7766;border-radius:8px;background:#203d36}canvas{display:block;width:var(--size);height:var(--size);background:repeating-conic-gradient(#e5e2d3 0 25%,#d3d3c5 0 50%) 0 0/24px 24px}h2{font-size:18px;margin:0 0 7px}.meta{font-size:12px;word-break:break-all;min-height:44px}.grounding{font-size:12px;overflow-wrap:anywhere}.muted{color:#bbcbbf}.status{padding:10px;border-left:3px solid #b99a61;background:#203d36}a{color:#ebc17a}input{width:220px}</style></head><body><main>
<h1>20 星阵少女 · 八方向跑步</h1><p>正常1×：960毫秒一圈，16帧均匀60毫秒。相位设计：前落、身下、后侧、后蹬各2帧，8帧换脚；长袍遮髋处不能仅凭标签确认腿别。脚向与承重对照竹弓少女。</p>
<div class="controls"><button id="play" disabled>播放</button><button id="reset" disabled>第1帧</button><button id="prev" disabled>上一帧</button><button id="next" disabled>下一帧</button>
<label>速度 <select id="speed"><option value="1">正常1× · 960ms/圈</option><option value="4">慢放 · 3840ms/圈</option></select></label>
<label>尺寸 <select id="size"><option>128</option><option selected>256</option><option>512</option></select>px</label>
<label><input id="guides" type="checkbox" style="width:auto">根点参考线</label><button id="reload">重新载入图片</button></div>
<div class="controls"><label>逐帧 <input id="scrub" type="range" min="0" max="15" value="0" disabled></label><span id="frameLabel">1 / 16</span></div>
<p id="loadStatus" class="status">正在预载……</p><section class="grid" id="groups"></section>
<p class="muted">完整1024×1024画布统一显示；固定根点(512,922)，不按每帧最低像素贴地。参考线不等于脚已着地。缺失图片显示空槽。</p>
<p><a href="index.html">四动作完整预览与逐图来源</a> · <a href="../animation-timing.json">当前时长</a> · <a href="../MERGE_HANDOFF.md">合并交接</a></p><p class="muted">素材离线检查；客户端未接入、未运行。</p></main>
<script>'use strict';const DATA=__DATA__;__HELPER__
const $=id=>document.getElementById(id);let playing=false,base=0,anchor=0,slow=1,ready=false,epoch=0,current=0;
const panels=DATA.map(g=>{const a=document.createElement('article');const segments=g.contactSegments.map(s=>(s.supportFoot==='right'?'右':'左')+'脚 '+String(s.frames[0]).padStart(2,'0')+'–'+String(s.frames[s.frames.length-1]).padStart(2,'0')).join(' / ');a.innerHTML='<h2>'+g.direction+'</h2><p class="grounding">'+(segments?'设计脚序：'+segments:'连续接地复核中')+'</p><canvas width="1024" height="1024" aria-label="'+g.direction+'方向跑步"></canvas><p class="meta"></p>';$('groups').append(a);return{...g,images:Array(16).fill(null),canvas:a.querySelector('canvas'),meta:a.querySelector('.meta'),last:-1}});
function elapsed(now=performance.now()){return base+(playing?now-anchor:0)}
function draw(index){for(const p of panels){if(p.last===index)continue;const ctx=p.canvas.getContext('2d');ctx.clearRect(0,0,1024,1024);if(p.images[index])ctx.drawImage(p.images[index],0,0,1024,1024);else{ctx.fillStyle='#743b2c';ctx.font='40px system-ui';ctx.fillText('缺帧 '+String(index+1).padStart(2,'0'),80,512)}if($('guides').checked){ctx.strokeStyle='#00868b';ctx.lineWidth=3;ctx.setLineDash([10,10]);ctx.beginPath();ctx.moveTo(0,922);ctx.lineTo(1024,922);ctx.moveTo(512,0);ctx.lineTo(512,1024);ctx.stroke();ctx.setLineDash([])}p.meta.textContent=(index+1)+' / 16 · '+(60*slow)+'ms ｜ '+(p.frames[index].source||'待补');p.last=index}current=index;$('scrub').value=index;$('frameLabel').textContent=(index+1)+' / 16'}
function paint(now){draw(frameAt(elapsed(now),slow))}
function pause(){if(playing){base=elapsed();playing=false}$('play').textContent='播放';paint(performance.now())}
function seek(i){pause();base=(((i%16)+16)%16)*60*slow;panels.forEach(p=>p.last=-1);paint(performance.now())}
$('play').onclick=()=>{if(!ready)return;if(playing)pause();else{anchor=performance.now();playing=true;$('play').textContent='暂停'}};
$('reset').onclick=()=>seek(0);$('prev').onclick=()=>seek(current-1);$('next').onclick=()=>seek(current+1);$('scrub').oninput=e=>seek(Number(e.target.value));
$('speed').onchange=()=>{const i=frameAt(elapsed(),slow);pause();slow=Number($('speed').value);seek(i)};
$('size').onchange=()=>document.documentElement.style.setProperty('--size',$('size').value+'px');
$('guides').onchange=()=>{panels.forEach(p=>p.last=-1);paint(performance.now())};
async function preload(){pause();ready=false;const id=++epoch,cache=Date.now();for(const k of ['play','reset','prev','next','scrub'])$(k).disabled=true;$('reload').disabled=true;
const outcomes=await Promise.all(panels.flatMap(p=>p.frames.map((f,i)=>new Promise(resolve=>{const im=new Image();im.onload=()=>{if(id===epoch)p.images[i]=im;resolve(true)};im.onerror=()=>{if(id===epoch)p.images[i]=null;resolve(false)};im.src=f.url+'?reload='+cache}))));
if(id!==epoch)return;const count=outcomes.filter(Boolean).length;ready=true;$('loadStatus').textContent=count+'/128 已载入。正常每帧60ms；可暂停逐帧检查脚向、支撑、摆腿和16→01衔接。';for(const k of ['play','reset','prev','next','scrub'])$(k).disabled=false;$('reload').disabled=false;seek(current)}
$('reload').onclick=preload;document.addEventListener('visibilitychange',()=>{if(document.hidden)pause()});function tick(now){paint(now);requestAnimationFrame(tick)}requestAnimationFrame(tick);preload();
</script></body></html>'''
html=HTML.replace("__DATA__",json.dumps(groups,ensure_ascii=False)).replace("__HELPER__",HELPER)
page=ROOT/"preview/run-E-grounding.html";page.write_text(html,encoding="utf-8")
(ROOT/"animation-timing.json").write_text(json.dumps({"character":ROOT.name,"run":RUN_TIMING,"hit":{"frameMs":40,"frames":6},"attack":{"frameMs":30,"frames":12},"cast":{"frameMs":45,"frames":16},"clientIntegrated":False},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
checks={}
node=shutil.which("node")
if node:
 js=html.split("<script>",1)[1].split("</script>",1)[0]
 r=subprocess.run([node,"--check"],input=js,text=True,capture_output=True,encoding="utf-8");checks["syntax"]={"passed":r.returncode==0,"stderr":r.stderr}
 test=HELPER+"const assert=require('node:assert/strict');for(const s of [1,4]){for(let i=0;i<16;i++){assert.equal(frameAt(i*60*s,s),i);assert.equal(frameAt((i+1)*60*s-0.001,s),i)}assert.equal(frameAt(960*s,s),0);assert.equal(frameAt(960*s*50+60*s,s),1)}console.log('passed');"
 r=subprocess.run([node,"-e",test],text=True,capture_output=True,encoding="utf-8");checks["timingBoundaries"]={"passed":r.returncode==0,"stderr":r.stderr,"loopMs":960,"frameMs":60,"extraEndPauseMs":0}
record={"builtAt":datetime.now(ZoneInfo("America/New_York")).isoformat(),"page":page.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(page.read_bytes()).hexdigest(),"runTiming":RUN_TIMING,"checks":checks,"browserObserved":False,"clientIntegrated":False,"groups":groups}
(ROOT/"provenance/run-playback-uniform-check.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"page":str(page),"checks":checks},ensure_ascii=False))
