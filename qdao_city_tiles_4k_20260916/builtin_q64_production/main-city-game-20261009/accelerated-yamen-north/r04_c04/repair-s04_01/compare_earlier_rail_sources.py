from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
B=Path(__file__).resolve().parent;ROOT=B.parents[1];D=B/'source-audit';D.mkdir(exist_ok=True)
old=ROOT.parent/'northwest/r05_c04/native/s01_01.png';S=np.array(Image.open(old).convert('RGB'))
sources=[(f'fix{i:02}', B.parent/'native'/f's04_01_fix{i:02}.png' if i<3 else B/f'fix{i:02}'/'generated.png') for i in range(1,9)]
contact=Image.new('RGB',(1134,780),(240,240,240));dr=ImageDraw.Draw(contact);records=[]
for i,(name,p) in enumerate(sources+[('actual south',old)]):
 a=np.array(Image.open(p).convert('RGB'));crop=a[1024:1254,630:1008] if i<8 else a[:230,630:1008]
 x=i%3*378;y=i//3*260;contact.paste(Image.fromarray(crop),(x,y+25));dr.text((x+4,y+5),name,fill=(0,0,0))
 if i<8:records.append({'name':name,'source':str(p),'leftMAE':float(np.abs(a[1024:1139,660:785].astype(float)-S[:115,660:785].astype(float)).mean()),'rightMAE':float(np.abs(a[1024:1139,890:950].astype(float)-S[:115,890:950].astype(float)).mean())})
contact.save(D/'earlier-rail-overlap-native.png');(D/'earlier-rail-overlap-errors.json').write_text(json.dumps(records,indent=2),encoding='utf-8');print(json.dumps(records,indent=2))
