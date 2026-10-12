from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(__file__).resolve().parent
Q=T/'qa/first-row-v20261013';Q.mkdir(exist_ok=True)
sources=[]
cores=[]
for c in range(1,5):
 f=T/'native'/f'p1{c}-v20261013.png'
 im=Image.open(f).convert('RGB');cores.append(im.crop((115,115,1139,1139)));sources.append({'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
for c in range(1,4):
 out=Q/f'join-p1{c}-p1{c+1}.png';assert not out.exists()
 win=Image.new('RGB',(384,1024));win.paste(cores[c-1].crop((832,0,1024,1024)),(0,0));win.paste(cores[c].crop((0,0,192,1024)),(192,0));win.save(out)
(Q/'source-manifest.json').write_text(json.dumps({'sources':sources,'operation':'integer core crops for actual seams only'},indent=2)+'\n',encoding='utf-8')
