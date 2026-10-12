"""Build the current uniform run timing inspector from actual selected PNG files without touching pixels."""
import json, html, os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
registered='--registered' in sys.argv
formal='--final' in sys.argv
selectionFile='final-selection.json' if formal else 'registered-selection.json' if registered else 'candidate-selection.json'
selection=json.loads((ROOT/selectionFile).read_text(encoding='utf-8-sig'))
timing=json.loads((ROOT/'animation-timing.json').read_text(encoding='utf-8-sig'))['run']
assert timing['frames']==16 and timing['frameMs']>0 and timing['frameMs']*16==timing['cycleMs']
seq={}
for e in selection:
    if e['action']!='run':continue
    frames=seq.setdefault(e['direction'],[None]*16)
    frames[e['frame']-1]={'src':'../'+e['file']+('?v='+e['sha256'][:12] if e.get('sha256') else ''),'file':e['file'],'review':e.get('reviewStatus','offline_passed' if formal else 'candidate'),'notes':e.get('visualStatus','')}
data=json.dumps(seq,ensure_ascii=False).replace('</','<\\/')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>05 天音少女 · 跑步节奏与接地检查</title><style>
*{box-sizing:border-box}body{font:15px/1.55 system-ui;margin:24px;color:#263d38;background:#f7f4eb}h1{font-size:24px}button,select,input{font:inherit}button,select{padding:7px;border:1px solid #abbbb1;border-radius:6px;background:white;color:#28483e}header{max-width:1100px}.controls{display:flex;gap:15px;flex-wrap:wrap;align-items:center;padding:18px 0}.cards{display:grid;grid-template-columns:minmax(290px,640px);gap:12px}.card{background:white;border:1px solid #cbd7cc;border-radius:12px;padding:14px;min-width:0}.stage{height:290px;display:flex;align-items:center;justify-content:center;background:#273b3c;border-radius:8px}.box{position:relative;width:160px;height:160px}.box img{width:100%;height:100%;object-fit:contain}.guide{position:absolute;left:0;right:0;top:95%;border-top:1px dashed #e8cd89;display:none}.info{font-size:13px;min-height:90px;overflow-wrap:anywhere}small{color:#586f67}#frameButtons{display:flex;gap:5px;flex-wrap:wrap;padding:12px 0}.active{background:#2c6758;color:white}aside{margin:20px 0;padding:14px;background:#eee9d8}#observed{white-space:pre-wrap}@media(max-width:900px){.cards{grid-template-columns:minmax(290px,1fr)}}
</style><header><h1>05 天音少女 · 跑步节奏与接地检查</h1><p>完整16帧，正常__CYCLE_MS__ms一圈，每帧均匀__FRAME_MS__ms。客户端移动速度匹配尚未验证。图片不做逐帧位移或贴地处理。</p></header>
<div class="controls"><label>方向 <select id="direction"></select></label><label>角色显示画布 <select id="size"><option value="128">128px</option><option value="160" selected>160px</option><option value="256">256px</option><option value="512">512px 放大逐帧</option></select></label><label>背景 <select id="background"><option value="#273b3c">深色</option><option value="#ffffff">白色</option><option value="#777777">中灰</option></select></label><label>播放速度 <select id="speed"><option value="1">正常 1× · __CYCLE_MS__ms</option><option value="0.5">慢放 ½×</option><option value="0.25">慢放 ¼×</option></select></label><button id="play">暂停</button><button id="playOnce">播放一圈</button><button id="restart">回到首帧</button><label><input type="checkbox" id="guide">诊断地面</label><label>画布 Y% <input id="ground" type="number" min="0" max="100" step="0.1" value="95" style="width:70px"></label></div>
<div id="frameButtons"></div><div class="cards"></div><aside><strong>验收边界：</strong>数量齐全不等于跑步修复。地面线仅供诊断，未作客户端标定；透视中的远近脚不强行落在同一屏幕水平线。检查着地鞋底、膝踝压缩、重心、另一腿回收以及肩肘握琴连续。受击、普攻、施法不受此页面的速度设置影响。</aside><h2>当前选帧实查备注</h2><div id="observed"></div>
<script>
const seq=__DATA__, durations=[__CYCLE_MS__], direction=document.getElementById('direction'),cards=document.querySelector('.cards');
for(const d of ['E','W','N','NE','SE','S','SW','NW']){const option=document.createElement('option');option.value=d;option.textContent=d+' · '+(seq[d]||[]).filter(Boolean).length+'/16';direction.append(option)}
const views=durations.map(ms=>{const el=document.createElement('section');el.className='card';el.innerHTML='<h2>'+ms+'ms / 圈</h2><small>'+ms/16+'ms / 帧 · '+'正常 1×，均匀逐帧'+'</small><div class="stage"><div class="box"><img alt="跑步帧"><div class="guide"></div></div></div><div class="info"></div>';cards.append(el);return {ms,img:el.querySelector('img'),info:el.querySelector('.info'),last:-1}});
let running=true,start=performance.now(),pausedElapsed=0,forced=null,once=false;const cache=[];
for(const frames of Object.values(seq))for(const f of frames)if(f){const im=new Image;im.src=f.src;cache.push(im)}
function draw(v,index){const f=(seq[direction.value]||[])[index];if(v.last===index&&v.dir===direction.value)return;v.last=index;v.dir=direction.value;if(f){v.img.src=f.src;v.img.style.visibility='visible'}else{v.img.removeAttribute('src');v.img.style.visibility='hidden'}v.info.textContent='第 '+String(index+1).padStart(2,'0')+'/16 帧'+(f?' · '+f.review+'\\n'+f.file:' · 缺图空槽');}
function timedIndex(v,elapsed){return Math.floor((elapsed%v.ms)/(v.ms/16))}
function tick(now){let elapsed=running?(now-start)*Number(document.getElementById('speed').value):pausedElapsed;if(once&&elapsed>=durations[0]){elapsed=durations[0];pausedElapsed=elapsed;running=false;forced=15;once=false;document.getElementById('play').textContent='播放'}for(const v of views)draw(v,forced===null?timedIndex(v,elapsed):forced);requestAnimationFrame(tick)}
function reset(){start=performance.now();pausedElapsed=0;forced=null;views.forEach(v=>v.last=-1);renderNotes()}
function renderNotes(){document.getElementById('observed').textContent=(seq[direction.value]||[]).map((f,i)=>String(i+1).padStart(2,'0')+'：'+(f?f.notes:'缺图')).join('\\n')}
for(let i=0;i<16;i++){const b=document.createElement('button');b.textContent=String(i+1).padStart(2,'0');b.onclick=()=>{running=false;forced=i;once=false;pausedElapsed=i*durations[0]/16;document.getElementById('play').textContent='播放';document.querySelectorAll('#frameButtons button').forEach(n=>n.classList.remove('active'));b.classList.add('active')};document.getElementById('frameButtons').append(b)}
direction.onchange=reset;document.getElementById('restart').onclick=reset;
document.getElementById('play').onclick=()=>{if(running){pausedElapsed=(performance.now()-start)*Number(document.getElementById('speed').value);running=false}else{start=performance.now()-pausedElapsed/Number(document.getElementById('speed').value);forced=null;once=false;running=true}document.getElementById('play').textContent=running?'暂停':'播放'};
document.getElementById('playOnce').onclick=()=>{reset();once=true;running=true;document.getElementById('play').textContent='暂停'};
document.getElementById('speed').onchange=()=>{reset();once=false};
document.getElementById('size').onchange=e=>{const px=Number(e.target.value);document.querySelectorAll('.box').forEach(el=>{el.style.width=px+'px';el.style.height=px+'px'});document.querySelectorAll('.stage').forEach(el=>el.style.height=Math.max(290,px+24)+'px')};
document.getElementById('background').onchange=e=>document.querySelectorAll('.stage').forEach(el=>el.style.background=e.target.value);
document.getElementById('guide').onchange=e=>document.querySelectorAll('.guide').forEach(el=>el.style.display=e.target.checked?'block':'none');
document.getElementById('ground').oninput=e=>document.querySelectorAll('.guide').forEach(el=>el.style.top=e.target.value+'%');
renderNotes();requestAnimationFrame(tick);
</script></html>'''.replace('__DATA__',data).replace('__CYCLE_MS__',str(timing['cycleMs'])).replace('__FRAME_MS__',str(timing['frameMs']))
stem='timing-grounding-final' if formal else 'timing-grounding-registered' if registered else 'timing-grounding'
if registered or formal:
    page=page.replace('同一组真实候选帧','同一组1024固定配准复核帧').replace('图片不做逐帧位移或贴地处理。','全角色统一比例、整段固定根；不做逐帧位移或贴地处理。').replace('value="95"','value="91.9921875"').replace('top:95%','top:91.9921875%')
if formal:
    page=page.replace('同一组1024固定配准复核帧','同一组1024正式素材帧').replace('数量齐全不等于跑步修复。地面线仅供诊断，未作客户端标定；','离线手脚、持琴和透明合成已复核；地面线未作客户端标定。').replace('待验试播','离线交付默认')
(ROOT/f'preview/{stem}.html').write_text(page,encoding='utf-8')
(ROOT/f'preview/{stem}-data.json').write_text(json.dumps({'status':'formal_uniform_run_timing' if formal else 'trial_not_final','selectionFile':selectionFile,'uniformCycleDurationsMs':[timing['cycleMs']],'frameMs':timing['frameMs'],'speedMultipliers':timing['speedOptions'],'phaseWeightsApplied':False,'normalDisplayCanvasPx':160,'pageAppliesImageTransforms':False,'registeredInputs':registered or formal,'clientValidated':False,'sequences':seq},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'preview/{stem}.html')

