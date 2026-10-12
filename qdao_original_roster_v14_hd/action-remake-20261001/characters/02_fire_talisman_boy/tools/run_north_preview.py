"""Private run-direction contact sheet and honest 16-slot HTML preview."""
import argparse, json, hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('--direction',required=True,choices=['W','N','NE','NW']);args=a.parse_args()
direction=args.direction
out=(ROOT/'work'/f'run-{direction}').resolve()
if not out.is_relative_to(ROOT): raise ValueError('outside character')
out.mkdir(parents=True,exist_ok=True)
available={}
for n in range(1,17):
    path=ROOT/'frames/run'/direction/f'{n:02}.png'
    if path.exists():
        im=Image.open(path);im.load()
        if im.size!=(1024,1024) or im.mode!='RGBA': raise ValueError('formal frame format mismatch')
        available[str(n)]={'src':f'../../frames/run/{direction}/{n:02}.png','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':list(im.size)}
sheet=Image.new('RGB',(1024,1136),'#263540');draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for n in range(1,17):
    x=((n-1)%4)*256;y=((n-1)//4)*284
    for cy in range(0,256,16):
        for cx in range(0,256,16):
            draw.rectangle((x+cx,y+cy,x+cx+15,y+cy+15),fill='#dde1e4' if (cx//16+cy//16)%2 else '#f4f5f6')
    if str(n) in available:
        with Image.open(ROOT/'frames/run'/direction/f'{n:02}.png') as im:
            small=im.resize((256,256),Image.Resampling.LANCZOS);sheet.paste(small,(x,y),small)
    else: draw.text((x+65,y+112),'MISSING SLOT',font=font,fill='#904129')
    draw.text((x+8,y+260),f'{direction} {n:02} / '+('candidate' if str(n) in available else 'MISSING'),font=font,fill='white')
sheet.save(out/'contact-current.png')
gif_outputs=[]
if len(available)==16:
    cards=[]
    for n in range(1,17):
        card=Image.new('RGB',(512,544),'#dfe4e8')
        with Image.open(ROOT/'frames/run'/direction/f'{n:02}.png') as im:
            small=im.resize((512,512),Image.Resampling.LANCZOS);card.paste(small,(0,0),small)
        ImageDraw.Draw(card).text((10,520),f'{direction} {n:02}/16 - CANDIDATE / REVIEW PENDING',font=font,fill='#253445')
        cards.append(card)
    # GIF stores centiseconds: alternate70/80ms for exactly1200ms; HTML is uniform75ms.
    for name,duration in [('normal',[70,80]*8),('slow',[300]*16)]:
        path=out/f'run-{direction}-{name}.gif'
        cards[0].save(path,save_all=True,append_images=cards[1:],duration=duration,loop=0,disposal=2,optimize=False)
        with Image.open(path) as im:
            durations=[]
            for n in range(im.n_frames):im.seek(n);durations.append(im.info.get('duration',0))
        gif_outputs.append({'file':path.name,'frames':len(durations),'totalMs':sum(durations),'durationsMs':durations})
data={'direction':direction,'expected':16,'available':available,'missing':[n for n in range(1,17) if str(n) not in available],'candidateOnly':True,'registrationPending':True,'frameMs':75,'cycleMs':1200,'phaseWeightsApplied':False,'timingStatus':'user_requested_uniform_1200ms_client_unconfirmed'}
data['gifs']=gif_outputs
html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>跑步方向独立验收</title><style>body{background:#162633;color:#f2f5f7;font:16px system-ui;margin:20px}button,input{font:inherit;margin:4px;padding:6px}.stage{position:relative;width:min(76vh,700px);aspect-ratio:1;background:repeating-conic-gradient(#dbe0e4 0 25%,#f1f3f5 0 50%) 0/32px 32px}.stage img{width:100%;height:100%}.empty{position:absolute;inset:0;display:grid;place-items:center;color:#753117;font-size:25px;font-weight:bold}.badge{padding:10px;background:#67451f}pre{white-space:pre-wrap}</style><h1 id="heading"></h1><p class="badge">本页是候选序列：未通过完整步态/统一画布标定。缺帧保留时长，显示空槽，不补图。</p><div class="stage"><img id="image"><div class="empty" id="empty">缺失</div></div><p id="state"></p><button onclick="play(1)">正常 1200ms/圈 · 每帧75ms</button><button onclick="play(4)">慢速×4</button><button onclick="stop()">暂停</button><button onclick="step(-1)">上一槽</button><button onclick="step(1)">下一槽</button><input type="range" id="slider" min="1" max="16" value="1" oninput="stop();show(+this.value)"><pre id="detail"></pre><script>const data=__DATA__;const id=x=>document.getElementById(x);let slot=1,timer=null,factor=1;id('heading').textContent='run / '+data.direction+' · '+Object.keys(data.available).length+'/16';function show(n){slot=n;const f=data.available[n];id('slider').value=n;id('image').style.visibility=f?'visible':'hidden';id('empty').style.display=f?'none':'grid';if(f)id('image').src=f.src;else id('image').removeAttribute('src');id('state').textContent='槽位 '+n+'/16 · 缺失 '+data.missing.join(', ');id('detail').textContent=JSON.stringify(f||{missing:true},null,2)}function stop(){clearTimeout(timer);timer=null}function tick(){show(slot%16+1);timer=setTimeout(tick,data.frameMs*factor)}function play(f){stop();factor=f;timer=setTimeout(tick,data.frameMs*factor)}function step(d){stop();show((slot+d+15)%16+1)}show(1);</script></html>'''.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c'))
(out/'preview.html').write_text(html,encoding='utf-8')
(out/'preview-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'preview':str(out/'preview.html'),'contact':str(out/'contact-current.png'),'count':len(available),'missing':data['missing']}))
