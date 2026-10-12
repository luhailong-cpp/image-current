from pathlib import Path
from PIL import Image
import json,hashlib
W=Path(__file__).resolve().parent
p=W/'output/r04_c03.candidate.png';im=Image.open(p);out=W/'qa/candidate';out.mkdir(exist_ok=True);records=[]
for axis in ['vertical','horizontal']:
 for boundary in range(1,4):
  for segment in range(1,5):
   a=boundary*1024;b=(segment-1)*1024
   box=(a-200,b,a+200,b+1024) if axis=='vertical' else (b,a-200,b+1024,a+200)
   name=f'{axis}-b{boundary}-s{segment}.png';im.crop(box).save(out/name);records.append({'file':name,'axis':axis,'boundary':boundary,'segment':segment,'box':box,'scale':1})
for row in range(1,4):
 for col in range(1,4):
  x,y=col*1024,row*1024;box=(x-230,y-230,x+230,y+230);name=f'cross-r{row}-c{col}.png';im.crop(box).save(out/name);records.append({'file':name,'box':box,'scale':1})
Path(out/'manifest.json').write_text(json.dumps({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'integer crops only, no scaling, painting, feather or tone adjustment','images':records},indent=2)+'\n')
print(json.dumps({'crops':len(records),'qaDirectory':str(out),'candidateSha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
