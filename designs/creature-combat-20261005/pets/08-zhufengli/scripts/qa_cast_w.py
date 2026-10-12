import json, hashlib
from pathlib import Path
from PIL import Image, ImageDraw
base=Path(__file__).resolve().parents[1]
rows=[]; frames=[]
sheet=Image.new('RGB',(1280,1360),'#263a40'); d=ImageDraw.Draw(sheet)
for i in range(1,17):
 p=base/'runtime/cast/W'/f'{i:02d}.png'; im=Image.open(p).convert('RGBA'); a=im.getchannel('A'); data=p.read_bytes()
 r={'frame':i,'file':str(p),'size':list(im.size),'mode':im.mode,'sha256':hashlib.sha256(data).hexdigest(),'alphaExtrema':list(a.getextrema()),'alphaBBoxes':{str(t):a.point(lambda v:255 if v>=t else 0).getbbox() for t in [1,8,32,128,254]},'recordExists':p.with_name(p.name+'.generation.json').exists()}
 rows.append(r); thumb=im.resize((320,320),Image.Resampling.LANCZOS); x=((i-1)%4)*320; y=((i-1)//4)*340; sheet.paste(thumb,(x,y+20),thumb); d.text((x+8,y+4),f'cast W {i:02d} / 45ms',fill='white')
 frames.append(im)
q=base/'qa';q.mkdir(exist_ok=True)
sheet.save(q/'cast-W-contact.png')
report={'frameCount':len(rows),'expected':16,'uniqueSHA':len(set(x['sha256'] for x in rows)),'all1024RGBA':all(r['size']==[1024,1024] and r['mode']=='RGBA' for r in rows),'allAlpha':all(r['alphaExtrema']==[0,255] for r in rows),'frames':rows,'notes':['No pixel duplicate, mirror, interpolation, per-frame crop or foot re-alignment used. Whole-native-canvas resize to 1024.','Frame13 independently regenerated with frame12/frame14 references; old image overwritten, text evidence retained.','Tool model/quality selectors and return metadata absent; actual values null.']}
(q/'cast-W-technical.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='frames'},ensure_ascii=False))
