from pathlib import Path
from PIL import Image
import json,hashlib
R=Path(__file__).resolve().parent
coords=json.loads((R/'coordinates.json').read_text());q=R/'qa'/'external-v1';q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for t in ['r03_c05','r04_c05']:
 c=next(x for x in coords if x['tile']==t and x['subcolumn']==1);w=Path(c['westSource']);p=R/'tiles'/f'{t}_candidate-v1_4096.png';a=Image.open(w);b=Image.open(p)
 for k in range(4):
  im=Image.new('RGB',(256,1024));im.paste(a.crop((3968,k*1024,4096,(k+1)*1024)),(0,0));im.paste(b.crop((0,k*1024,128,(k+1)*1024)),(128,0));out=q/f'{t}-west-{k+1}.png';im.save(out);records.append({'image':str(out),'sources':[str(w),str(p)],'sourceHashes':[sha(w),sha(p)],'resized':False})
a=Image.open(R/'tiles'/'r03_c05_candidate-v1_4096.png');b=Image.open(R/'tiles'/'r04_c05_candidate-v1_4096.png')
for k in range(4):
 im=Image.new('RGB',(1024,256));im.paste(a.crop((k*1024,3968,(k+1)*1024,4096)),(0,0));im.paste(b.crop((k*1024,0,(k+1)*1024,128)),(0,128));out=q/f'r03-r04-{k+1}.png';im.save(out);records.append({'image':str(out),'sources':['r03_c05_candidate-v1_4096.png','r04_c05_candidate-v1_4096.png'],'resized':False})
(q/'inputs.json').write_text(json.dumps(records,indent=2));print(len(records))
