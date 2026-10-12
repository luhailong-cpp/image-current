from PIL import Image,ImageDraw
from pathlib import Path
import json
b=Path(__file__).resolve().parents[1]
vs=[3,2,2,2,3,9,6,3,4,2,3,2,4,4,2,3]
out=b/'review'/'contact-pairs-SW';out.mkdir(exist_ok=True)
rows=[];sheet=Image.new('RGB',(4*260,4*285),(37,41,48));d=ImageDraw.Draw(sheet)
for i,v in enumerate(vs,1):
 key=f'run-SW-{i:02d}-v{v}';im=Image.open(b/'staging'/f'{key}.png').convert('RGBA');a=im.getchannel('A')
 ed=list(a.crop((0,0,im.width,1)).getdata())+list(a.crop((0,im.height-1,im.width,im.height)).getdata())+list(a.crop((0,0,1,im.height)).getdata())+list(a.crop((im.width-1,0,im.width,im.height)).getdata())
 rows.append({'key':key,'maxEdgeAlpha':max(ed),'edgePixelsGT128':sum(z>128 for z in ed),'alphaBBoxGT128':a.point(lambda p:255 if p>128 else 0).getbbox()})
 thumb=im.resize((240,240),Image.Resampling.LANCZOS);x=((i-1)%4)*260+10;y=((i-1)//4)*285+28;sheet.paste(thumb,(x,y),thumb);d.text((x,y-21),key,fill='white')
sheet.save(out/'current-240.jpg',quality=95)
(out/'edge-candidates.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps(rows))
