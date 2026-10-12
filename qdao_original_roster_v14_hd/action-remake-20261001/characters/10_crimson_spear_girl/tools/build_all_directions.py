from pathlib import Path
import json, argparse, re
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--candidate',action='store_true');args=parser.parse_args()
if args.candidate:
    text=(R/'preview/contact-revision.html').read_text(encoding='utf-8')
    data=json.loads(text.split('const DATA=',1)[1].split(',onlyRun=',1)[0])
else:
    data=json.loads((R/'delivery-current.json').read_text(encoding='utf-8'))
plan=json.loads((R/'RUN_CONTACT_PLAN.json').read_text(encoding='utf-8'))
groups={}
for direction in ['N','NE','E','SE','S','SW','W','NW']:
    rows=data['groups']['run/'+direction]
    groups[direction]=[f.get('candidateUrl') or f['url']+'?v='+f['sha256'][:12] for f in rows]
title='八方向接地复修 · 候选检查' if args.candidate else '赤枪少女 · 八方向跑步'
html='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title>
<style>body{margin:0;background:#172a27;color:#f7f1dd;font:15px system-ui}main{max-width:960px;margin:auto;padding:18px}h1{font-size:24px;margin:0 0 8px}p{margin:6px 0 10px}button,select{font:inherit;padding:7px 10px;margin:0 6px 10px 0}#grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}article{background:#e9e8e1;color:#263c35;padding:7px;border-radius:8px}canvas{display:block;width:100%;aspect-ratio:1}header{display:flex;justify-content:space-between}small{display:block;text-align:center;min-height:24px}a{color:#b8dfc6}@media(max-width:700px){#grid{grid-template-columns:repeat(2,1fr)}}.error{color:#f99}</style>
<main><h1>__TITLE__</h1><p>每方向16帧 × 60ms = 960ms。每个连续支撑位置两张独立姿态，沿运动方向逐点递进。</p>
<button id="play">暂停</button><button id="restart">从头播放</button><button id="prev">上一帧</button><button id="next">下一帧</button><select id="speed"><option value="1">正常1×</option><option value="4">慢放¼</option></select><span id="status">载入图片…</span>
<div id="grid"></div><p><a href="index.html">放大 / 查看全部动作</a> · <a href="timing-grounding.html">单方向逐帧检查</a></p></main>
<script>
const GROUPS=__GROUPS__,PLAN=__PLAN__,grid=document.querySelector('#grid'),status=document.querySelector('#status'),play=document.querySelector('#play');
let index=0,elapsed=0,last=performance.now(),playing=false,loaded=0,failed=0;
const rows=Object.entries(GROUPS).map(([direction,urls])=>{
 const card=document.createElement('article');card.innerHTML='<header><b>'+direction+'</b><span></span></header><canvas width="1024" height="1024"></canvas><small></small>';grid.append(card);
 const images=urls.map(url=>{const im=new Image();im.onload=()=>{loaded++;if(loaded===128){playing=true;last=performance.now()}draw()};im.onerror=()=>{failed++;draw()};im.src=url;return im});
 return {direction,images,canvas:card.querySelector('canvas'),frame:card.querySelector('span'),phase:card.querySelector('small')};
});
function draw(){
 for(const row of rows){const ctx=row.canvas.getContext('2d');ctx.clearRect(0,0,1024,1024);const im=row.images[index];if(im?.complete&&im.naturalWidth)ctx.drawImage(im,0,0);
 row.frame.textContent=String(index+1).padStart(2,'0')+'/16';
 for(const [side,pairs] of Object.entries(PLAN.groups[row.direction])){const p=pairs.findIndex(pair=>pair.includes(index+1));if(p>=0)row.phase.textContent=(side==='left'?'左':'右')+'脚支撑 · 位置 '+(p+1)+'/4'}
 }
 status.textContent=failed?'图片载入失败 '+failed:loaded<128?'已载入 '+loaded+'/128':'128/128 已载入';
 status.className=failed?'error':'';play.textContent=playing?'暂停':'播放';
}
play.onclick=()=>{playing=!playing&&loaded===128;last=performance.now();draw()};
document.querySelector('#restart').onclick=()=>{index=0;elapsed=0;playing=loaded===128;last=performance.now();draw()};
function step(d){playing=false;index=(index+d+16)%16;elapsed=index*60;draw()}
document.querySelector('#prev').onclick=()=>step(-1);document.querySelector('#next').onclick=()=>step(1);document.querySelector('#speed').onchange=()=>{last=performance.now()};
function tick(now){if(playing){elapsed+=Math.max(0,now-last)/Number(document.querySelector('#speed').value);index=Math.floor(elapsed/60)%16;draw()}last=now;requestAnimationFrame(tick)}
draw();requestAnimationFrame(tick);
</script></html>'''
html=html.replace('__TITLE__',title).replace('__GROUPS__',json.dumps(groups,ensure_ascii=False)).replace('__PLAN__',json.dumps(plan,ensure_ascii=False))
out=R/'preview'/('all-directions-candidate.html' if args.candidate else 'all-directions.html')
out.write_text(html,encoding='utf-8')
print(json.dumps({'file':str(out),'candidate':args.candidate,'slots':sum(map(len,groups.values()))}))
