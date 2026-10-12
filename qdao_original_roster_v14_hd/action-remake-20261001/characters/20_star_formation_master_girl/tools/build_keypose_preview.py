from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parents[1]
selection=json.loads((ROOT/'selection.json').read_text(encoding='utf-8-sig'))
manifest=json.loads((ROOT/'preview/manifest.json').read_text(encoding='utf-8-sig'))
frames=selection['frames']
keys=[('run','E',1),('hit','E',3),('attack','E',6),('cast','E',10)]
frames=[next(f for f in frames if (f['action'],f['direction'],f['frame'])==key) for key in keys if any((f['action'],f['direction'],f['frame'])==key for f in frames)]
w=480;h=530
sheet=Image.new('RGB',(w*len(frames),h),'#e9e6df')
draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',20)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',14)
for idx,f in enumerate(frames):
    for x in range(0,w,20):
        for y in range(0,480,20):
            col='#eeede9' if (x//20+y//20)%2==0 else '#e2e1dc'
            draw.rectangle((idx*w+x,y,idx*w+x+19,y+19),fill=col)
    im=Image.open(ROOT/f"candidate/{f['action']}/{f['direction']}/{f['frame']:02}.png").convert('RGBA')
    im=im.resize((480,480),Image.Resampling.LANCZOS)
    sheet.paste(im,(idx*w,0),im)
    action={'run':'跑步','hit':'受击','attack':'普攻','cast':'施法'}[f['action']]
    draw.text((idx*w+16,480),f"{action} {f['direction']} {f['frame']:02} · 候选",font=font,fill='#263835')
    draw.text((idx*w+16,509),'关键姿态，完整序列与动态尚未验收',font=small,fill='#675e50')
out=ROOT/'preview/keyposes.png'
sheet.save(out)
record={'file':'preview/keyposes.png','sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'operation':'现有候选的预览排版、等比缩小、透明背景检查格及文字标注；不生成或改造姿态','derivedFrom':[{'path':f"candidate/{f['action']}/{f['direction']}/{f['frame']:02}.png",'sha256':hashlib.sha256((ROOT/f"candidate/{f['action']}/{f['direction']}/{f['frame']:02}.png").read_bytes()).hexdigest(),'generationRecord':f"candidate/{f['action']}/{f['direction']}/{f['frame']:02}.png.generation.json"} for f in frames]}
out.with_suffix('.png.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)

