from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime,timezone
import json,hashlib
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy")
O=B/"review/diagonals";O.mkdir(parents=True,exist_ok=True)
obs=json.loads((B/"audit/run-NWSW-observations.json").read_text(encoding="utf8"))
font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",18);small=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc",13)
now=datetime.now(timezone.utc).isoformat();rows=[];details=[]
for direction,slots in obs.items():
    frames=[];contact=Image.new("RGB",(1536,1720),(225,232,237))
    for j,(suffix,event,note) in enumerate(slots):
        key=f"run-{direction}-{suffix}";p=B/"sources/new"/(key+".png")
        im=Image.open(p).convert("RGBA");sha=hashlib.sha256(p.read_bytes()).hexdigest()
        gr=B/"provenance/generation"/(key+".json");assert gr.exists()
        row={"action":"run","direction":direction,"frame":j+1,"source":p.relative_to(B).as_posix(),"sha256":sha,"accepted":True,"nativeSingleFrame":True,"generationRecord":gr.relative_to(B).as_posix(),"review":{"reviewer":"/root/finish_attack_diagonals","reviewedAt":now,"notes":note+" 已逐图查看，完整动态待审。"},"event":event}
        rows.append(row)
        fr=Image.new("RGB",(512,560),(225,232,237));d=ImageDraw.Draw(fr)
        d.line((10,486,502,486),fill=(175,186,195),width=1)
        spr=im.resize((512,512),Image.Resampling.LANCZOS);fr.paste(spr,(0,0),spr)
        d.text((12,514),f"{direction} {j+1:02} /16  {event}",font=small,fill=(20,35,45))
        d.text((12,536),suffix,font=small,fill=(35,60,70))
        frames.append(fr);contact.paste(fr.resize((384,420)),(j%4*384,j//4*430))
        details.append({"slot":j+1,"direction":direction,"key":key,"event":event,"observed":note,"nativeSize":im.size,"alphaExtrema":im.getchannel("A").getextrema(),"alphaBBoxGreater8":im.getchannel("A").point(lambda v:255 if v>8 else 0).getbbox(),"sha256":sha})
    contact.save(O/f"run-{direction}-current-contact.png")
    for label,durations in [("baseline480",[30]*16),("trial640",[40]*16),("trial720",[40,50]*8),("trial800",[50]*16),("slow",[180]*16)]:
        frames[0].save(O/f"run-{direction}-{label}.gif",save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False,disposal=2)
    (O/f"run-{direction}-preview.json").write_text(json.dumps({"kind":"review_only","direction":direction,"sourceFrames":[x for x in details if x["direction"]==direction],"operation":"whole-canvas uniform downsample to512 for contact/GIF; reference line y1190 is overlay only; no sprite geometry edited","defaultTrialMs":720,"clientIntegrated":False},ensure_ascii=False,indent=2),encoding="utf8")
sel={"schemaVersion":1,"characterId":"15_water_dragon_scholar_boy","expectedFrameCount":32,"staticCandidateCount":len(rows),"dynamicAccepted":False,"clientIntegrated":False,"updatedAt":now,"frames":rows}
(B/"audit/run-NWSW-selection.json").write_text(json.dumps(sel,ensure_ascii=False,indent=2),encoding="utf8")
reviewpath=B/"audit/run-NWSW-review.json";rv=json.loads(reviewpath.read_text(encoding="utf8")) if reviewpath.exists() else {}
rv.update(reviewedAt=now,staticCandidateCount=len(rows),dynamicAccepted=False,candidateFrames=details,remaining=["正常720及慢速整组动态审查由/root继续","参考地线为画布辅助线，真实接地须结合斜视图鞋尖、鞋跟与前后深度判定"],dynamicReviewOwner="/root",timing={"oldBaselineMs":480,"trialMs":[640,720,800],"defaultTrialMs":720,"finalTimingAccepted":False})
reviewpath.write_text(json.dumps(rv,ensure_ascii=False,indent=2),encoding="utf8")
html="""<!doctype html><meta charset="utf-8"><title>水龙书生 NW/SW 跑步复核</title><style>body{background:#182634;color:#f4f8fc;font:16px system-ui;padding:20px}button,select{font:inherit;margin:8px;padding:8px}main{display:flex;gap:20px}img{max-width:45vw;background:#e1e8ed}label{display:block}</style><h1>水龙书生 NW / SW 跑步</h1><p>完整16帧候选。720ms是离线试播值，未改客户端。灰线仅作统一画布参考，斜视脚前后深度应结合鞋底方向。</p><select id="speed"><option value="trial720">720ms试播</option><option value="trial640">640ms试播</option><option value="trial800">800ms试播</option><option value="baseline480">原480ms对照</option><option value="slow">逐帧慢放2880ms</option></select><button id="restart">重播</button><main><section><label>西北 NW</label><img id="nw" src="run-NW-trial720.gif"></section><section><label>西南 SW</label><img id="sw" src="run-SW-trial720.gif"></section></main><p><a href="run-NW-current-contact.png">NW静态16帧</a> · <a href="run-SW-current-contact.png">SW静态16帧</a></p><script>function play(){let v=document.querySelector('#speed').value;for(let d of ['nw','sw'])document.getElementById(d).src='run-'+d.toUpperCase()+'-'+v+'.gif?'+Date.now()}document.getElementById('speed').onchange=play;document.getElementById('restart').onclick=play;</script>"""
(O/"index.html").write_text(html,encoding="utf8")
print(json.dumps({"selected":len(rows),"directions":{d:len(v)for d,v in obs.items()},"preview":str(O/"index.html")}))

