from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[1]
old=['run-S-05-v3','run-S-06-v2','run-S-07-v5','run-S-08-v4','run-S-09-v1']
new=['run-S-05-v3','run-S-06-v3','run-S-07-v6','run-S-08-v4','run-S-09-v1']
sheet=Image.new('RGB',(1200,920),(44,49,53))
draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
for row,keys in enumerate([old,new]):
 for col,key in enumerate(keys):
  im=Image.open(BASE/'staging'/f'{key}.png').convert('RGBA')
  x=col*240;y=row*280
  draw.text((x+8,y+5),('OLD ' if row==0 else 'NEW ')+key,font=font,fill='white')
  small=im.resize((240,240),Image.Resampling.LANCZOS);sheet.paste(small,(x,y+30),small)
for col,key in enumerate(new[1:]):
 im=Image.open(BASE/'staging'/f'{key}.png').convert('RGBA').crop((420,810,840,1210)).resize((300,286),Image.Resampling.LANCZOS)
 x=col*300;draw.text((x+8,575),key+' lower body',font=font,fill='white');sheet.paste(im,(x,605),im)
sheet.save(BASE/'review/grounding-S/S06-S09-sequence-comparison.png')
rows=[]
for key in dict.fromkeys(old+new):
 p=BASE/'staging'/f'{key}.png';im=Image.open(p).convert('RGBA')
 def last(x0,x1,y0,y1):
  a=im.getchannel('A');ys=[y for y in range(y0,y1) if sum(v>200 for v in a.crop((x0,y,x1,y+1)).getdata())>=15];return max(ys) if ys else None
 rows.append({'file':p.name,'frontBootRoiMaxY':last(620,845,950,1254),'rearBootRoiMaxY':last(450,610,900,1100),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out={'recordedAt':datetime.now(timezone.utc).isoformat(),'attempt':'run-S-06-v3','editBase':'run-S-07-v6','attemptCount':1,'measurementMethod':'Manual boot ROI, last row with >=15 opaque pixels alpha>200; diagnostic only, not ground calibration','rows':rows}
(BASE/'review/grounding-S/S06-S09-sequence-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows))

