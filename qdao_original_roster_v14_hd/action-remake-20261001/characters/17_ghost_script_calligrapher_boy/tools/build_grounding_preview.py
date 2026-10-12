"""Build user-requested1200ms run diagnostic. Does not edit or export sprites."""
from pathlib import Path
import json
from datetime import datetime, timezone
BASE=Path(__file__).resolve().parents[1]
HTML=r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>17 灵篆书生 · 跑步接地与节奏</title>
<style>
*{box-sizing:border-box}body{margin:0;color:#e8eee7;background:#13201e;font:14px/1.6 "Microsoft YaHei",sans-serif}main{max-width:1500px;padding:24px;margin:auto}h1{font-size:24px;margin:0 0 8px}p{margin:8px 0;color:#b6c8c0}.bar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin:14px 0}button,select,input{font:inherit}button,select{padding:7px 12px;background:#263d35;border:1px solid #486454;border-radius:6px;color:#f4edda;cursor:pointer}button:disabled{opacity:.45}input{accent-color:#b9d7b5}label{display:flex;gap:6px;align-items:center}.cards{display:grid;grid-template-columns:minmax(250px,600px);gap:14px}.card{padding:14px;border:1px solid #476251;border-radius:12px;background:#1b2b25}.card.trial{border-color:#d7ba6e}.card h2{font-size:18px;margin:0}.card small{color:#bacbbf}.stage{position:relative;width:240px;height:240px;margin:14px auto;background:#d9ddd6;overflow:hidden}.stage.dark{background:#263333}.stage.checker{background:repeating-conic-gradient(#d1d6cb 0 25%,#f1efe4 0 50%) 0/20px 20px}.stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.ground{position:absolute;left:0;right:0;border-top:1px dashed #b7453b;pointer-events:none}.root{position:absolute;left:51.04%;top:92.105%;width:7px;height:7px;transform:translate(-50%,-50%);border:1px solid #b7453b;pointer-events:none}.phase{font-size:12px;min-height:80px;color:#d0ddcc}.meta{display:flex;justify-content:space-between}.large .cards{grid-template-columns:repeat(2,minmax(490px,1fr))}.large .stage{width:480px;height:480px}#frame{width:300px}#status{color:#e0c68a}.review{margin-top:24px;border-top:1px solid #486454;padding-top:16px}.review ol{columns:2;column-gap:40px}.review li{break-inside:avoid;margin:0 0 10px;padding-right:15px}a{color:#bbe4ce}.note{padding:12px;background:#302e23;border-left:3px solid #d7ba6e}table{border-collapse:collapse;width:100%}td,th{padding:8px;border-bottom:1px solid #476251;text-align:left}@media(max-width:1100px){.cards{grid-template-columns:repeat(2,minmax(250px,1fr))}.large .cards{grid-template-columns:1fr}}@media(max-width:580px){main{padding:14px}.cards{grid-template-columns:1fr}.large .stage{width:340px;height:340px}.review ol{columns:1}#frame{width:180px}}
</style><main>
<h1>17 灵篆书生 · 跑步接地与逐帧检查</h1>
<p>正常1×为1200ms一圈，16帧均匀75ms。240px为离线查看尺寸；客户端实际显示和位移速度尚未核验。</p>
<p class="note">已按用户最新要求采用1200ms/圈；手脚与接地继续验收。页面只显示完整16帧候选组，保留慢放、暂停和逐帧，不改动图片位置。</p>
<div class="bar"><label>方向<select id="dir"></select></label><button id="play" disabled>播放</button><button id="reset" disabled>从头播放</button><label><input id="large" type="checkbox">480px 放大</label><label>背景<select id="bg"><option value="light">浅底</option><option value="dark">深底</option><option value="checker">棋盘</option></select></label><label>速度<select id="slow"><option value="1">正常</option><option value="0.25">慢速 ×0.25</option></select></label></div>
<div class="bar"><button id="prev" disabled>上一帧</button><input id="frame" type="range" min="1" max="16" value="1" disabled><button id="next" disabled>下一帧</button><output id="frameValue">01 / 16</output><label><input id="showGround" type="checkbox">诊断参考线</label><label>高度<select id="ground"><option value="92.105">92.105%（旧提示目标）</option><option value="93.301">93.301%（E 鞋底观察附近）</option><option value="94">94%</option></select></label></div>
<p id="status">正在加载16张图片</p><div class="cards" id="cards"></div>
<div class="review"><h2>逐帧观察</h2><p>依据可见鞋底、膝踝和近远腿遮挡判断，均为待复核候选。参考线不等于地面标定；两脚在透视中也不必处于同一水平线。</p><ol id="notes"></ol>
<p class="note">验收重点：同一脚连续支撑半周期，前侧、身下、后侧第一位置、后侧第二位置各两帧，然后换脚。鞋尖沿运动方向，肩肘与手中道具连接自然；八个方向与用户确认的竹弓少女同方向对照。</p>
<p><a href="index.html">全部动作预览</a> · <a href="run-current-1200ms.webp">当前完整方向1200ms离线动图</a> · <a href="timing-grounding-data.json">本页来源与待审记录</a></p></div></main>
<script id="data" type="application/json">__DATA__</script>
<script>
'use strict';
const D=JSON.parse(document.getElementById('data').textContent),$=id=>document.getElementById(id),cycles=D.cycles_ms;
let seq=[],loaded=[],playing=false,start=0,elapsed=0,raf=0,index=0,generation=0;
$('dir').replaceChildren(...Object.keys(D.sequences).map(d=>new Option(d,d,d==='E',d==='E')));
$('cards').innerHTML=cycles.map(c=>'<section class="card"><h2>'+c+'ms / 圈</h2><small>正常1× ·75ms/帧</small><div class="stage"><img alt="跑步候选"><div class="ground" hidden></div><div class="root" hidden></div></div><div class="meta"><b class="f">01 /16</b><span>75ms</span></div><p class="phase"></p></section>').join('');
const cards=[...document.querySelectorAll('.card')];
function phase(n){return D.notes_by_direction[$('dir').value][String(n+1)]||'此帧仍待手脚与接地审查。'}
function paint(nums){nums.forEach((n,i)=>{const im=cards[i].querySelector('img');if(im.dataset.frame!==String(n)){im.src=loaded[n].src;im.dataset.frame=n;}cards[i].querySelector('.f').textContent=String(n+1).padStart(2,'0')+' / 16';cards[i].querySelector('.phase').textContent=phase(n);});index=nums[0];$('frame').value=index+1;$('frameValue').textContent=String(index+1).padStart(2,'0')+' / 16';}
function stop(){if(playing)elapsed=performance.now()-start;playing=false;cancelAnimationFrame(raf);$('play').textContent='播放';}
function tick(){if(!playing)return;elapsed=Math.max(0,performance.now()-start);const t=elapsed*Number($('slow').value);paint(cycles.map(c=>Math.floor((t%c)/(c/16))));raf=requestAnimationFrame(tick);}
function play(){if(loaded.length!==16)return;playing=true;start=performance.now()-elapsed;$('play').textContent='暂停';raf=requestAnimationFrame(tick);}
function step(n){stop();elapsed=0;index=(n+16)%16;paint(cycles.map(()=>index));$('status').textContent='逐帧检查：当前 '+seq[index].key+'，视觉待验收。';}
async function load(){const version=++generation;stop();loaded=[];elapsed=0;seq=D.sequences[$('dir').value];['play','reset','prev','next','frame'].forEach(k=>$(k).disabled=true);$('status').textContent='正在加载16张图片';try{const list=await Promise.all(seq.map(async s=>{const im=new Image();im.src=s.path;await im.decode();return im;}));if(version!==generation)return;loaded=list;['play','reset','prev','next','frame'].forEach(k=>$(k).disabled=false);paint([0]);$('status').textContent='16张真实候选已加载；未跳过缺帧。正常播放1200ms/圈，再逐帧检查承重。';$('notes').replaceChildren(...seq.map((s,n)=>{const li=document.createElement('li');li.textContent=s.key+'：'+phase(n);return li;}));}catch(e){$('status').textContent='图片加载失败，已停止：'+e.message;}}
$('play').onclick=()=>playing?stop():play();$('reset').onclick=()=>{stop();elapsed=0;play();};$('prev').onclick=()=>step(index-1);$('next').onclick=()=>step(index+1);$('frame').oninput=()=>step(Number($('frame').value)-1);$('dir').onchange=load;
$('large').onchange=()=>document.body.classList.toggle('large',$('large').checked);
$('bg').onchange=()=>document.querySelectorAll('.stage').forEach(s=>s.className='stage '+$('bg').value);
$('slow').onchange=()=>{const resume=playing;stop();elapsed=0;if(resume)play();};
function ground(){document.querySelectorAll('.ground').forEach(g=>{g.hidden=!$('showGround').checked;g.style.top=$('ground').value+'%';});document.querySelectorAll('.root').forEach(g=>g.hidden=!$('showGround').checked);}
$('showGround').onchange=ground;$('ground').onchange=ground;
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
document.addEventListener('keydown',e=>{if(['INPUT','SELECT','BUTTON'].includes(e.target.tagName))return;if(e.code==='Space'){e.preventDefault();$('play').click();}if(e.key==='ArrowLeft')step(index-1);if(e.key==='ArrowRight')step(index+1);});
load();
</script></html>'''
m=json.loads((BASE/'preview/manifest-preview.json').read_text(encoding='utf-8'))
seqs={}
for d in m['actions']['run']['directions']:
    seq=[s for s in m['slots'] if s['action']=='run' and s['direction']==d]
    if len(seq)==16 and all(s['selected'] for s in seq):
        seqs[d]=[dict(s['selected']) for s in seq]
data={'character':BASE.name,'built_at':datetime.now(timezone.utc).isoformat(),'source':'manifest-preview.json','cycles_ms':[1200],'frame_ms':75,'adopted_preview_cycle_ms':1200,'adopted_runtime_cycle_ms':None,'formal_timing_changed':False,'client_tested':False,'sequences':seqs,'contactRequirement':'../review/contact-pairs-current-20261004.json','method':'Same full canvas and selected PNGs; uniform75ms x16, normal1x1200ms; no bbox fit, no root shifts, no generated in-betweens.'}
data['notes_by_direction']={d:{str(i+1):f.get('review_notes','') for i,f in enumerate(seq)} for d,seq in seqs.items()}
(BASE/'preview/timing-grounding-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
html=HTML.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
(BASE/'preview/timing-grounding.html').write_text(html,encoding='utf-8')
print(json.dumps({'path':str(BASE/'preview/timing-grounding.html'),'complete_candidate_directions':list(seqs),'formal_timing_changed':False},ensure_ascii=False))

