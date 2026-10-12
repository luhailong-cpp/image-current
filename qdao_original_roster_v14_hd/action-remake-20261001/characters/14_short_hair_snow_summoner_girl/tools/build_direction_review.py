from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
m=json.loads((R/'manifest.json').read_text(encoding='utf-8'))
html='''<!doctype html><meta charset="utf-8"><title>14 八方向手脚与接地复核</title>
<style>body{background:#eef2ef;color:#23443f;font:15px system-ui;margin:24px}header{display:flex;align-items:center;gap:18px;flex-wrap:wrap}button,select{padding:8px}main{display:grid;grid-template-columns:repeat(4,260px);gap:12px;margin-top:20px}.card{background:white;padding:10px;border-radius:10px}.stage{width:240px;height:240px;position:relative;background:#28303b}.stage img{width:100%;height:100%}.ground{position:absolute;top:91.9921875%;border-top:1px dashed #caaf79;width:100%}.label{font-size:13px;line-height:1.6}.big main{grid-template-columns:repeat(2,500px)}.big .stage{width:480px;height:480px}@media(max-width:700px){main{grid-template-columns:repeat(2,260px)}}</style>
<header><h2>14 唤雪少女 · 八方向跑步</h2><label>速度 <select id="speed"><option value="1">正常 · 每圈__CYCLE_MS__ms · __FRAME_MS__ms/帧</option><option value=".25">慢速 ¼</option></select></label><button id="play" disabled>加载中</button><button id="prev" disabled>上一帧</button><button id="next" disabled>下一帧</button><label><input type="checkbox" id="large">放大检查</label><a href="index.html">全部动作</a><a href="timing-grounding.html">节奏与逐帧检查</a><a href="bamboo-reference.html">竹弓少女对照</a></header><p>各方向16帧均匀__FRAME_MS__ms。本轮逐对核对：前落脚、髋下承重、稍后支撑、后前掌蹬地，每位置两帧，第9帧换脚。横线是离线近地参考；客户端位移尚未接入。</p><p id="status">正在预载128张…</p><main id="grid"></main>
<script>
const M=__DATA__,dirs=['N','NE','E','SE','S','SW','W','NW'],$=id=>document.getElementById(id);
let running=false,ready=false,elapsed=0,last=null;
const groups=dirs.map(d=>M.frames.filter(f=>f.action==='run'&&f.direction===d));
const source=f=>f.path+'?v='+f.sha256;
const cards=groups.map((g,k)=>{const card=document.createElement('section');card.className='card';card.innerHTML='<strong>'+dirs[k]+'</strong><div class="stage"><img alt="'+dirs[k]+'跑步"><div class="ground"></div></div><div class="label"></div>';$('grid').append(card);return card});
function draw(){if(!ready)return;groups.forEach((g,k)=>{const total=g.reduce((s,f)=>s+f.durationMs,0);let t=elapsed%total,n=0;while(n<g.length-1&&t>=g[n].durationMs){t-=g[n].durationMs;n++}const f=g[n],im=cards[k].querySelector('img'),src=source(f);if(im.getAttribute('src')!==src)im.src=src;cards[k].querySelector('.label').textContent=String(n+1).padStart(2,'0')+'/16 · '+f.durationMs+'ms · '+total+'ms/圈'})}
function tick(t){if(last!==null&&running)elapsed+=(t-last)*Number($('speed').value);last=t;draw();requestAnimationFrame(tick)}
$('play').onclick=()=>{running=!running;$('play').textContent=running?'暂停':'播放'};
function step(delta){running=false;$('play').textContent='播放';elapsed=((Math.floor(elapsed/M.runTiming.frameDurationMs)+delta+16)%16)*M.runTiming.frameDurationMs;draw()}
$('prev').onclick=()=>step(-1);$('next').onclick=()=>step(1);$('large').onchange=e=>document.body.classList.toggle('big',e.target.checked);
Promise.all(groups.flat().map(async f=>{const im=new Image;im.src=source(f);await im.decode();return im})).then(images=>{window.preloadedFrames=images;ready=true;running=true;elapsed=0;last=null;['play','prev','next'].forEach(id=>$(id).disabled=false);$('play').textContent='暂停';$('status').textContent='128张已加载；按当前成品版本播放。';draw()}).catch(e=>{$('status').textContent='有图片加载失败，请刷新页面。'});
requestAnimationFrame(tick);
</script>'''
(R/'all-directions.html').write_text(html.replace('__CYCLE_MS__',str(m['runTiming']['defaultCycleMs'])).replace('__FRAME_MS__',str(m['runTiming']['frameDurationMs'])).replace('__DATA__',json.dumps(m,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
