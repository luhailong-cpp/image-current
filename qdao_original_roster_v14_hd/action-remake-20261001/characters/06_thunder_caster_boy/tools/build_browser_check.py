"""Build a local, visible playback QA page, operated through the actual app browser."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
HTML=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<title>06 动作播放检查</title><style>body{font:16px system-ui;background:#182332;color:#eef3f7;margin:20px}button{font:inherit;padding:10px}iframe{width:100%;height:850px;border:1px solid #657081}pre{white-space:pre-wrap;font-size:12px}a{color:#7bddd1}</style>
<h1>06 雷法少年 · 离线播放检查</h1><p>检查当前预览的正常、慢放、暂停、逐帧和首尾切换。技术播放结果不代替美术或游戏内验收。</p>
<button id="start">检查全部14段</button> <span id="progress">尚未开始</span> <a href="index.html">返回动作预览</a>
<iframe id="viewer" src="index.html"></iframe><details open><summary>实际浏览器检查结果</summary><pre id="report">{}</pre></details>
<script>
const $=id=>document.getElementById(id), out={method:'Visible Codex in-app browser; preview iframe UI events and actual requestAnimationFrame DOM samples',clientConnected:false,visualArtAcceptance:false,runs:[],errors:[]};
function publish(){ $('report').textContent=JSON.stringify(out,null,2); }
$('start').onclick=async()=>{ $('start').disabled=true;out.startedAt=new Date().toISOString();
try{
 const w=$('viewer').contentWindow,d=w.document,get=id=>d.getElementById(id), manifest=JSON.parse(get('manifest').textContent);
 out.manifestGeneratedAt=manifest.generated_at_utc;out.sourceFrames=manifest.sequences.flatMap(s=>s.frames.map(f=>({path:f.path,sha256:f.sha256})));
 const event=(id,type,value)=>{get(id).value=String(value);get(id).dispatchEvent(new w.Event(type,{bubbles:true}));};
 const raf=()=>new Promise(r=>w.requestAnimationFrame(()=>w.requestAnimationFrame(r)));
 const state=()=>{const im=get('sprite');return {frame:Number(new URL(im.src).pathname.split('/').pop().split('.')[0]),visible:!im.hidden&&im.complete&&im.naturalWidth===1024};};
 for(const seq of manifest.sequences){
  $('progress').textContent=seq.id+' · 检查中';
  event('action','change',seq.action);event('direction','change',seq.direction);
  await Promise.all(seq.frames.map(f=>new Promise(resolve=>{const im=new w.Image();im.onload=im.onerror=resolve;im.src=f.url;})));
  const row={id:seq.id,runs:[],stepped:[]};
  for(const speed of [1,4]){
   event('speed','change',speed);event('timeline','input',0);get('play').click();
   const samples=[];let start,previousFrame,wrapCount=0;
   await new Promise((resolve,reject)=>{function tick(t){if(start===undefined)start=t;const s=state();if(previousFrame!==undefined&&s.frame<previousFrame)wrapCount++;previousFrame=s.frame;samples.push({ms:t-start,documentVisible:!d.hidden,...s});if(t-start>60000)return reject(new Error(seq.id+' playback did not complete three actual wraps'));if(wrapCount<3||t-start<Math.max(1500,seq.cycle_ms*speed*2))w.requestAnimationFrame(tick);else resolve();}w.requestAnimationFrame(tick);});
   get('play').click();
   const changes=samples.filter((x,i)=>i===0||x.frame!==samples[i-1].frame),wraps=changes.filter((x,i)=>i>0&&x.frame<changes[i-1].frame).map(x=>x.ms);
   row.runs.push({speed,seen:[...new Set(samples.map(x=>x.frame))].sort((a,b)=>a-b),expected:seq.expected_count,nonRenderable:samples.filter(x=>!x.visible).length,samples:samples.length,nominalCycleMs:seq.cycle_ms*speed,actualWrapCount:wrapCount,hiddenSamples:samples.filter(x=>!x.documentVisible).length,observedWrapIntervalsMs:wraps.slice(1).map((x,i)=>x-wraps[i]),skippedTransitions:changes.slice(1).filter((x,i)=>(x.frame-changes[i].frame+seq.expected_count)%seq.expected_count!==1),changes});
  }
  for(let n=0;n<seq.expected_count;n++){event('timeline','input',n);await raf();row.stepped.push(state());}
  row.pauseAtLastFrame=get('play').textContent==='播放';get('next').click();await raf();row.nextWrap=state().frame;get('previous').click();await raf();row.previousWrap=state().frame;
  row.passed=row.runs.every(r=>r.seen.length===seq.expected_count&&!r.nonRenderable&&!r.skippedTransitions.length)&&row.stepped.every((s,n)=>s.frame===n&&s.visible)&&row.pauseAtLastFrame&&row.nextWrap===0&&row.previousWrap===seq.expected_count-1;
  out.runs.push(row);publish();
 }
 out.completed=true;out.passed=out.runs.length===14&&out.runs.every(r=>r.passed);out.finishedAt=new Date().toISOString();$('progress').textContent=out.passed?'14段全部通过':'有未通过项，请查看结果';
}catch(e){out.errors.push(String(e));$('progress').textContent='检查失败';}
publish();};
if(location.hash==='#autostart')window.addEventListener('load',()=>$('start').click(),{once:true});
</script></html>'''
(R/'preview/browser-check.html').write_text(HTML,encoding='utf-8')
m=json.loads((R/'preview/manifest.json').read_text(encoding='utf-8'))
snapshot={'generatedAt':m['generated_at_utc'],'manifestSha256':hashlib.sha256((R/'preview/manifest.json').read_bytes()).hexdigest(),'frames':[{'path':f['path'],'sha256':f['sha256']} for s in m['sequences'] for f in s['frames']]}
(R/'records/browser_check_source_snapshot_20261004.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
print('preview/browser-check.html')
