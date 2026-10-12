from pathlib import Path
import json, hashlib
from PIL import Image
P=Path(__file__).resolve().parent
Z=P.parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
sel=json.loads((P/'selection.json').read_text(encoding='utf-8-sig'))
q=P/'qa'/'first-row-20261011'; q.mkdir(exist_ok=True)
row=Image.new('RGB',(4096,1024))
sources=[]
for c in range(1,5):
 p=Path(sel[f's01_{c:02}']); im=Image.open(p).convert('RGB')
 row.paste(im.crop((115,115,1139,1139)),((c-1)*1024,0))
 sources.append({'file':str(p),'sha256':sha(p)})
row.save(q/'row.png')
north=Z/'r06_c06/candidate/r06_c06-candidate-hard-077556c4fb59.png'
ni=Image.open(north).convert('RGB')
entries=[]
for c in range(1,4):
 name=f'vertical-{c}'; p=q/(name+'.png')
 row.crop((c*1024-128,0,c*1024+128,1024)).save(p)
 entries.append({'name':name,'file':str(p),'sha256':sha(p)})
for c in range(4):
 name=f'north-{c+1}'; p=q/(name+'.png')
 out=Image.new('RGB',(1024,256))
 out.paste(ni.crop((c*1024,3968,(c+1)*1024,4096)),(0,0))
 out.paste(row.crop((c*1024,0,(c+1)*1024,128)),(0,128))
 out.save(p)
 entries.append({'name':name,'file':str(p),'sha256':sha(p)})
(q/'crops.json').write_text(json.dumps({'sources':sources,'north':{'file':str(north),'sha256':sha(north)},'entries':entries},indent=2),encoding='utf-8')
print(q)

