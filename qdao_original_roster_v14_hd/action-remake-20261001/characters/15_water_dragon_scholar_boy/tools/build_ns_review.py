from pathlib import Path
from PIL import Image,ImageDraw
import json
b=Path(__file__).resolve().parents[1]
out=b/'audit/ns-review';out.mkdir(exist_ok=True)
d=json.loads((b/'audit/run-NS-selection.json').read_text(encoding='utf-8'))
for direction in ['N','S']:
 fs=sorted([f for f in d['frames'] if f['direction']==direction],key=lambda f:f['frame'])
 sheet=Image.new('RGB',(1120,1200),(28,37,48));draw=ImageDraw.Draw(sheet)
 frames=[]
 for f in fs:
  im=Image.open(b/f['source']).convert('RGBA')
  canvas=Image.new('RGBA',(1024,1024),(0,0,0,0))
  canvas.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49))
  view=Image.new('RGBA',(384,420),(28,37,48,255));view.alpha_composite(canvas.resize((384,384)),(0,0))
  v=ImageDraw.Draw(view);v.line((0,353,384,353),fill=(130,90,65),width=1);v.text((8,392),f"{direction}{f['frame']:02d}  {f['source'].split('/')[-1]}",fill='white')
  frames.append(view.convert('RGB'))
  x=((f['frame']-1)%4)*280;y=((f['frame']-1)//4)*300
  panel=Image.new('RGBA',(280,280),(28,37,48,255));panel.alpha_composite(canvas.resize((280,280)))
  sheet.paste(panel.convert('RGB'),(x,y));draw.line((x,y+258,x+280,y+258),fill=(145,95,65))
  draw.text((x+8,y+279),f"{direction}{f['frame']:02d} {f['source'].split('/')[-1]}",fill='white')
 sheet.save(out/f'{direction}-contact.png')
 if len(fs)==16:
  frames[0].save(out/f'{direction}-30ms.gif',save_all=True,append_images=frames[1:],duration=30,loop=0,disposal=2)
  frames[0].save(out/f'{direction}-120ms.gif',save_all=True,append_images=frames[1:],duration=120,loop=0,disposal=2)
  frames[0].save(out/f'{direction}-720ms.apng',save_all=True,append_images=frames[1:],duration=45,loop=0,disposal=1,format='PNG')
  frames[0].save(out/f'{direction}-slow180ms.apng',save_all=True,append_images=frames[1:],duration=180,loop=0,disposal=1,format='PNG')
 payload={di:[{'frame':f['frame'],'src':'../../'+f['source']} for f in d['frames'] if f['direction']==di] for di in ['N','S']}
html='''<!doctype html><meta charset="utf-8"><title>N/S 跑步复核</title><style>body{background:#202a35;color:#fff;font:16px system-ui}canvas{width:384px;height:384px;border:1px solid #465361}button{padding:12px;margin:6px}</style><h2>N/S 跑步复核：固定画布，不逐帧脚底对齐</h2><button onclick="ms=30;playing=true">30ms 正常</button><button onclick="ms=120;playing=true">120ms 慢放</button><button onclick="playing=false">暂停</button><button onclick="playing=false;i=(i+1)%16;render()">逐帧下一张</button><p id="info"></p><canvas id="N" width="1024" height="1024"></canvas><canvas id="S" width="1024" height="1024"></canvas><script>const data=PAYLOAD;let ms=120,playing=true,i=0,last=0;const imgs={};Promise.all(Object.entries(data).flatMap(([d,fs])=>fs.map(f=>new Promise(r=>{let im=new Image();im.onload=r;im.onerror=r;im.src=f.src;(imgs[d]??={})[f.frame]=im})))).then(()=>requestAnimationFrame(tick));function render(){for(const d of ['N','S']){let c=document.getElementById(d),g=c.getContext('2d');g.clearRect(0,0,1024,1024);g.strokeStyle='#ac7547';g.beginPath();g.moveTo(0,49+1191*940/1254);g.lineTo(1024,49+1191*940/1254);g.stroke();let im=imgs[d]?.[i+1];if(im?.complete)g.drawImage(im,42,49,940,940);}document.getElementById('info').textContent='帧 '+(i+1)+' / 16 · '+ms+'ms';}function tick(t){if(playing&&t-last>=ms){i=(i+1)%16;last=t;render()}requestAnimationFrame(tick)}render();</script>'''.replace('PAYLOAD',json.dumps(payload))
(out/'index.html').write_text(html,encoding='utf-8')
html=html.replace('let ms=120','let ms=45').replace('30ms 正常','480ms 旧基线').replace('ms=120;playing=true','ms=180;playing=true').replace('120ms 慢放','180ms 慢放')
html=html.replace('<p id="info">','<button onclick="ms=40;playing=true">640ms</button><button onclick="ms=45;playing=true">720ms 比较</button><button onclick="ms=50;playing=true">800ms</button><button onclick="document.querySelectorAll(\'canvas\').forEach(c=>{c.style.width=\'240px\';c.style.height=\'240px\'})">240px</button><p id="info">')
(out/'index.html').write_text(html,encoding='utf-8')
print('NS review generated')

